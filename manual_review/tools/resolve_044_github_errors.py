import csv
import hashlib
import json
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "manual_review" / "queue_next_200.csv"
CACHE = ROOT / "manual_review" / "page_cache" / "queue_044_20260726.jsonl"


def gh_raw(endpoint):
    proc = subprocess.run(
        ["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout
    return None


def path_from_tree(url):
    parts = urllib.parse.urlsplit(url).path.strip("/").split("/")
    if len(parts) >= 5 and parts[2] == "tree":
        return parts[0], parts[1], "/".join(parts[4:])
    return None


def main():
    queue = {r["project_id"]: r for r in csv.DictReader(QUEUE.open(encoding="utf-8-sig", newline=""))}
    rows = [json.loads(line) for line in CACHE.open(encoding="utf-8")]
    resolved = 0
    for row in rows:
        if row.get("platform") not in {"GitHub", "Hack Club OnBoard"}:
            continue
        if row.get("readme_status") != "error":
            continue
        url = row["requested_url"]
        tree = path_from_tree(url)
        if tree:
            owner, repo, project = tree
            endpoints = [
                f"repos/{owner}/{repo}/contents/{urllib.parse.quote(project + '/README.md', safe='/')}",
                f"repos/{owner}/{repo}/contents/{urllib.parse.quote(project + '/readme.md', safe='/')}",
                f"repos/{owner}/{repo}/contents/{urllib.parse.quote(project + '/README.MD', safe='/')}",
            ]
        else:
            parts = urllib.parse.urlsplit(url).path.strip("/").split("/")
            if len(parts) < 2:
                continue
            endpoints = [f"repos/{parts[0]}/{parts[1]}/readme"]
        endpoint = None
        text = None
        for candidate in endpoints:
            text = gh_raw(candidate)
            if text:
                endpoint = candidate
                break
        if text:
            row["readme_url"] = f"https://api.github.com/{endpoint}"
            row["readme_status"] = "ok (GitHub API raw)"
            row["readme"] = text
            row.pop("error", None)
            row["content_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            resolved += 1
    with CACHE.open("w", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"resolved": resolved, "remaining_errors": sum(1 for r in rows if r.get("error") or r.get("readme_status") == "error")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
