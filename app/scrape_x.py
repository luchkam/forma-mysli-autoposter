# app/scrape_x.py
import os, json, subprocess, pathlib, re, time
import feedparser, requests

X_USERNAME   = os.getenv("X_USERNAME", "visualizevalue")
MIRRORS_ENV  = os.getenv("NITTER_MIRRORS", "https://nitter.net")
NITTERS      = [m.strip().rstrip("/") for m in MIRRORS_ENV.split(",") if m.strip()]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"

def _try_snscrape(max_results:int, out_path):
    cmd = ["snscrape", "--jsonl", f"--max-results={max_results}", "twitter-user", X_USERNAME]
    out = pathlib.Path(out_path)
    with out.open("w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f, check=True)
    with out.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def _fetch(url, timeout=15):
    for attempt in range(3):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
            if r.status_code == 200 and r.content:
                return r.content
        except Exception:
            pass
        time.sleep(1 + attempt)
    raise RuntimeError(f"fetch failed: {url}")

def _from_nitter_rss(max_results:int=60):
    items = []
    for base in NITTERS:
        rss_url = f"{base}/{X_USERNAME}/rss"
        try:
            raw = _fetch(rss_url, timeout=15)
            # парсим из байтов, не давая feedparser ничего грузить сам
            d = feedparser.parse(raw)
            if not getattr(d, "entries", None):
                continue

            for entry in d.entries[:max_results]:
                text = (entry.title or "").strip()
                media_urls = []

                # enclosures
                for enc in entry.get("enclosures", []):
                    url = enc.get("href") or enc.get("url")
                    if url and any(x in url.lower() for x in [".jpg", ".jpeg", ".png"]):
                        media_urls.append(url)

                # из summary как fallback
                summary = entry.get("summary", "")
                for m in re.findall(r'src="([^"]+)"', summary):
                    if any(x in m.lower() for x in [".jpg", ".jpeg", ".png"]):
                        media_urls.append(m)

                media_urls = list(dict.fromkeys(media_urls))  # dedup
                if media_urls:
                    items.append({"content": text, "media": [{"type":"photo","url":u} for u in media_urls]})

            if items:
                return items  # успех на этом зеркале
        except Exception:
            # пробуем следующее зеркало
            continue
    return items  # может быть пусто

def scrape_to_json(max_results:int=60, out_path="vv.json"):
    # 1) пробуем snscrape
    try:
        return _try_snscrape(max_results, out_path)
    except Exception as e:
        print("snscrape failed, switching to Nitter mirrors:", e)

    # 2) fallback через зеркала Nitter
    items = _from_nitter_rss(max_results=max_results)

    # сохраняем vv.json для совместимости
    out = pathlib.Path(out_path)
    with out.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return items
