# app/scrape_x.py
import os, json, subprocess, pathlib, feedparser, re

NITTER_BASE = os.getenv("NITTER_BASE", "https://nitter.net")
X_USERNAME  = os.getenv("X_USERNAME", "visualizevalue")

def _try_snscrape(max_results:int=60, out_path="vv.json"):
    """Пробуем snscrape. Бросаем исключение при неудаче."""
    cmd = [
        "snscrape", "--jsonl", f"--max-results={max_results}",
        "twitter-user", X_USERNAME
    ]
    out = pathlib.Path(out_path)
    with out.open("w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f, check=True)
    with out.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def _from_nitter_rss(max_results:int=60):
    """Фолбэк: берём RSS с Nitter и приводим к формату, похожему на snscrape."""
    feed_url = f"{NITTER_BASE.rstrip('/')}/{X_USERNAME}/rss"
    d = feedparser.parse(feed_url)

    items = []
    for entry in d.entries[:max_results]:
        text = (entry.title or "").strip()
        # в RSS от Nitter медиа может быть в содержимом или в enclosure
        media_urls = []

        # enclosure
        if "enclosures" in entry:
            for enc in entry.enclosures:
                url = enc.get("href") or enc.get("url")
                if url and any(x in url for x in ["/pic/", ".jpg", ".png", ".jpeg"]):
                    media_urls.append(url)

        # попытка вытащить картинки из summary/detail (на всякий)
        summary = entry.get("summary", "")
        for m in re.findall(r'src="([^"]+)"', summary):
            if any(x in m for x in ["/pic/", ".jpg", ".png", ".jpeg"]):
                media_urls.append(m)

        media = [{"type": "photo", "url": u} for u in media_urls]
        if media:
            items.append({"content": text, "media": media})

    return items

def scrape_to_json(max_results:int=60, out_path="vv.json"):
    """Сначала пробуем snscrape, если упало — Nitter RSS."""
    try:
        return _try_snscrape(max_results=max_results, out_path=out_path)
    except Exception as e:
        print("snscrape failed, using Nitter RSS fallback:", e)
        items = _from_nitter_rss(max_results=max_results)
        # сохраним для совместимости vv.json (наши «псевдо‑твитты»)
        out = pathlib.Path(out_path)
        with out.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        return items
