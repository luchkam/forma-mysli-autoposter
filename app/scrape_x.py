import json, os, subprocess, sys, tempfile, pathlib

def scrape_to_json(max_results:int=60, out_path="vv.json"):
    cmd = [
        "snscrape", "--jsonl", f"--max-results={max_results}",
        "twitter-user", "visualizevalue"
    ]
    out = pathlib.Path(out_path)
    with out.open("w", encoding="utf-8") as f:
        try:
            subprocess.run(cmd, stdout=f, check=True)
        except Exception as e:
            raise RuntimeError(f"snscrape failed: {e}")
    with out.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]
