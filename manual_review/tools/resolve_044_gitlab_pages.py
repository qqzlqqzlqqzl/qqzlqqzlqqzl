import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "manual_review" / "page_cache" / "queue_044_20260726.jsonl"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "svg", "noscript"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg", "noscript"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            data = " ".join(data.split())
            if data:
                self.parts.append(data)


def main():
    rows = [json.loads(line) for line in CACHE.open(encoding="utf-8")]
    resolved = 0
    for row in rows:
        if row.get("platform") != "GitLab" or not row.get("error"):
            continue
        try:
            req = urllib.request.Request(
                row["requested_url"],
                headers={"User-Agent": "qqzlqqzlqqzl-commercial-v3-review/1.0"},
            )
            with urllib.request.urlopen(req, timeout=25) as response:
                html = response.read().decode("utf-8", errors="replace")
                status = response.status
            parser = Parser()
            parser.feed(html)
            text = " ".join(parser.parts)
            row["page_http_status"] = status
            row["page_text"] = text
            row["source_type"] = "gitlab-project-page"
            if len(text) >= 300:
                row["readme_status"] = "exact GitLab project page"
                row.pop("error", None)
                row["content_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
                resolved += 1
            else:
                row["page_shell_only"] = True
        except Exception as exc:
            row["page_error"] = repr(exc)
    with CACHE.open("w", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"resolved": resolved, "remaining_errors": sum(1 for r in rows if r.get("error") or r.get("readme_status") == "error")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
