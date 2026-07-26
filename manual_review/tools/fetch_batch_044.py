import csv
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "manual_review" / "queue_next_200.csv"
OUT = ROOT / "manual_review" / "page_cache" / "queue_044_20260726.jsonl"


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            data = " ".join(data.split())
            if data:
                self.parts.append(data)

    def text(self):
        return " ".join(self.parts)


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "qqzlqqzlqqzl-commercial-v3-review/1.0",
            "Accept": "text/plain,text/html,application/json,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        body = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        return response.status, body.decode(charset, errors="replace")


def github_parts(url):
    parts = urllib.parse.urlsplit(url).path.strip("/").split("/")
    if len(parts) < 2:
        return None
    owner, repo = parts[:2]
    if parts[2:3] == ["tree"] and len(parts) >= 5:
        branch = parts[3]
        project = "/".join(parts[4:])
        return owner, repo, branch, project
    return owner, repo, "HEAD", None


def fetch_item(item):
    pid = item["project_id"]
    url = item["url"]
    base = {
        "project_id": pid,
        "requested_url": url,
        "platform": item["platform"],
        "name": item["name"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        if item["platform"] in {"GitHub", "Hack Club OnBoard"}:
            parsed = github_parts(url)
            if not parsed:
                raise ValueError("无法解析GitHub URL")
            owner, repo, branch, project = parsed
            if project:
                candidates = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{urllib.parse.quote(project)}/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{urllib.parse.quote(project)}/README.md",
                ]
            else:
                candidates = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md",
                ]
            last_error = None
            for readme_url in candidates:
                try:
                    status, text = fetch(readme_url)
                    if status == 200 and text.strip():
                        base.update(
                            {
                                "repo": f"{owner}/{repo}",
                                "readme_url": readme_url,
                                "readme_status": "ok",
                                "readme": text,
                                "http_status": status,
                            }
                        )
                        break
                except Exception as exc:
                    last_error = repr(exc)
            else:
                base.update(
                    {
                        "repo": f"{owner}/{repo}",
                        "readme_status": "error",
                        "error": last_error or "README 404/empty",
                    }
                )
        elif item["platform"] == "GitLab":
            parsed = urllib.parse.urlsplit(url).path.strip("/").split("/")
            if len(parsed) < 2:
                raise ValueError("无法解析GitLab URL")
            project_path = "/".join(parsed[:2])
            api_url = (
                "https://gitlab.com/api/v4/projects/"
                + urllib.parse.quote(project_path, safe="")
            )
            status, meta_text = fetch(api_url)
            meta = json.loads(meta_text)
            branch = meta.get("default_branch") or "main"
            readme_url = (
                api_url
                + "/repository/files/README.md/raw?ref="
                + urllib.parse.quote(branch)
            )
            readme_status, readme = fetch(readme_url)
            base.update(
                {
                    "api_url": api_url,
                    "api_name": meta.get("name"),
                    "description": meta.get("description"),
                    "default_branch": branch,
                    "stars": meta.get("star_count"),
                    "forks": meta.get("forks_count"),
                    "readme_url": readme_url,
                    "readme_status": "ok" if readme_status == 200 else "error",
                    "extracted_text": readme if readme_status == 200 else "",
                    "http_status": status,
                }
            )
        else:
            status, html = fetch(url)
            parser = TextParser()
            parser.feed(html)
            text = parser.text()
            base.update(
                {
                    "http_status": status,
                    "source_type": {
                        "OSHWA认证目录": "oshwa-certification-page",
                        "PCBWay共享项目": "pcbway-project-page",
                        "嘉立创开源硬件平台": "oshwhub-project-page",
                    }.get(item["platform"], "exact-html-page"),
                    "page_text": text,
                    "title": text[:180],
                }
            )
    except Exception as exc:
        base["error"] = repr(exc)
    payload = base.get("readme") or base.get("extracted_text") or base.get("page_text") or ""
    base["content_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return base


def main():
    queue = list(csv.DictReader(QUEUE.open(encoding="utf-8-sig", newline="")))
    results = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_item, item): item["project_id"] for item in queue}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    with OUT.open("w", encoding="utf-8", newline="") as f:
        for item in queue:
            f.write(json.dumps(results[item["project_id"]], ensure_ascii=False) + "\n")
    errors = sum(1 for x in results.values() if x.get("error") or x.get("readme_status") == "error")
    print(json.dumps({"rows": len(queue), "cached": len(results), "errors": errors, "out": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
