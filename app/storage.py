from pathlib import Path
import hashlib, json

DATA = Path("processed")
DATA.mkdir(exist_ok=True)
SEEN = DATA / "seen.txt"

def key_from(url:str, text:str) -> str:
    return hashlib.md5((url + "||" + text).encode("utf-8")).hexdigest()

def seen_load() -> set[str]:
    if SEEN.exists():
        return set(SEEN.read_text().splitlines())
    return set()

def seen_add(k:str):
    s = seen_load()
    s.add(k)
    SEEN.write_text("\n".join(sorted(s)))
