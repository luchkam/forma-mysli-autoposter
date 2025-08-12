import os, json, requests, traceback
from pathlib import Path
from dotenv import load_dotenv

from app.scrape_x import scrape_to_json
from app.ocr_text import has_text
from app.invert import invert_image
from app.translate import translate_meaning
from app.tg import post_photo
from app.storage import key_from, seen_load, seen_add

load_dotenv()

POSTS_PER_RUN = int(os.getenv("POSTS_PER_RUN","1"))
X_MAX_RESULTS = int(os.getenv("X_MAX_RESULTS","60"))

DATASET = Path("processed")
INBOX   = Path("manual_inbox")
DATASET.mkdir(exist_ok=True)
INBOX.mkdir(exist_ok=True)

def download(url:str, path:Path):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)

def process_from_x():
    tweets = scrape_to_json(max_results=X_MAX_RESULTS, out_path=DATASET/"vv.json")
    seen = seen_load()
    posted = 0

    for t in tweets:
        text = (t.get("content") or "").strip()
        media = t.get("media") or []
        photos = [m.get("url") for m in media if isinstance(m,dict) and m.get("type")=="photo"]
        if not photos: continue

        for url in photos:
            key = key_from(url, text)
            if key in seen: continue

            post_dir = DATASET / key
            post_dir.mkdir(exist_ok=True)
            img_path = post_dir / "orig.jpg"
            inv_path = post_dir / "inv.jpg"

            try:
                download(url, img_path)
            except Exception as e:
                print("download error:", e); seen_add(key); continue

            try:
                if has_text(str(img_path)):
                    print("skip with-text:", url)
                    seen_add(key)
                    continue
            except Exception:
                print("OCR error but continue")

            try:
                invert_image(img_path, inv_path)
            except Exception as e:
                print("invert error:", e); seen_add(key); continue

            # перевод подписи близко по смыслу
            try:
                ru = translate_meaning(text) if text else ""
                (post_dir/"caption_en.txt").write_text(text, encoding="utf-8")
                (post_dir/"caption_ru.txt").write_text(ru, encoding="utf-8")
            except Exception as e:
                print("translate error:", e)
                ru = ""

            # публикуем
            try:
                post_photo(str(inv_path), ru if ru else None)
                print("posted:", key)
                posted += 1
            except Exception as e:
                print("tg post error:", e)

            seen_add(key)
            if posted >= POSTS_PER_RUN:
                return posted
    return posted

def process_manual_inbox():
    posted = 0
    seen = seen_load()
    for img in sorted(INBOX.glob("*.jpg")) + sorted(INBOX.glob("*.png")):
        stem = img.stem
        cap_en_path = INBOX / f"{stem}_en.txt"
        text = cap_en_path.read_text(encoding="utf-8") if cap_en_path.exists() else ""

        key = key_from(str(img), text)
        if key in seen: continue

        post_dir = DATASET / key
        post_dir.mkdir(exist_ok=True)
        inv_path = post_dir / "inv.jpg"

        try:
            if has_text(str(img)):
                print("manual skip (has text):", img)
                seen_add(key); continue
        except Exception:
            pass

        invert_image(img, inv_path)

        try:
            ru = translate_meaning(text) if text else ""
            (post_dir/"caption_en.txt").write_text(text, encoding="utf-8")
            (post_dir/"caption_ru.txt").write_text(ru, encoding="utf-8")
        except Exception as e:
            print("translate error:", e)
            ru = ""

        try:
            post_photo(str(inv_path), ru if ru else None)
            print("posted manual:", key); posted += 1
        except Exception as e:
            print("tg post error:", e)

        seen_add(key)
        if posted >= POSTS_PER_RUN:
            break
    return posted

if __name__ == "__main__":
    try:
        total = process_from_x()
        if total < POSTS_PER_RUN:
            total += process_manual_inbox()
        print("done, posted:", total)
    except Exception as e:
        traceback.print_exc()
        print("run failed:", e)
