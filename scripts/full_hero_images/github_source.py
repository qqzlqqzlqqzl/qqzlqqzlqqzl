from __future__ import annotations

import base64
import html
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, urlparse

from .common import (
    Candidate, IMAGE_EXTENSIONS, TIMEOUT, add_candidate, clean_url, get_session,
    github_headers, positive_hint_score, reject_text,
)


def parse_github_url(project_url: str) -> tuple[str, str, str | None, str]:
    parsed = urlparse(project_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("invalid GitHub URL")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    ref: str | None = None
    subpath = ""
    if len(parts) >= 4 and parts[2] in {"tree", "blob"}:
        ref = parts[3]
        subpath = "/".join(parts[4:])
        if parts[2] == "blob" and subpath:
            subpath = str(PurePosixPath(subpath).parent)
            if subpath == ".":
                subpath = ""
    return owner, repo, ref, subpath.strip("/")


def github_api_json(path: str, params: dict[str, str] | None = None) -> Any:
    response = get_session().get(
        "https://api.github.com" + path,
        headers=github_headers(), params=params, timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def decode_github_content(item: dict[str, Any]) -> str:
    content = item.get("content") or ""
    if item.get("encoding") == "base64" and content:
        return base64.b64decode(content).decode("utf-8", "replace")
    download_url = item.get("download_url")
    if download_url:
        response = get_session().get(download_url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    return ""


def markdown_image_refs(text: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for match in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)", text):
        refs.append((html.unescape(match.group(2)), html.unescape(match.group(1))))
    for match in re.finditer(r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>", text, flags=re.I):
        tag = match.group(0)
        alt_match = re.search(r"alt=[\"']([^\"']*)[\"']", tag, flags=re.I)
        refs.append((html.unescape(match.group(1)), html.unescape(alt_match.group(1) if alt_match else "")))
    return refs


def github_raw_url(owner: str, repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{quote(ref, safe='/')}/{quote(path, safe='/')}"


def resolve_markdown_ref(owner: str, repo: str, ref: str, readme_dir: str, image_ref: str) -> str:
    image_ref = clean_url(image_ref)
    if image_ref.startswith(("http://", "https://")):
        return image_ref
    if image_ref.startswith("/"):
        path = image_ref.lstrip("/")
    else:
        path = str(PurePosixPath(readme_dir) / image_ref)
    path = str(PurePosixPath(path.split("#", 1)[0].split("?", 1)[0]))
    return github_raw_url(owner, repo, ref, path)


def github_candidates(project_url: str) -> list[Candidate]:
    owner, repo, ref, subpath = parse_github_url(project_url)
    if not ref:
        repo_meta = github_api_json(f"/repos/{owner}/{repo}")
        ref = str(repo_meta.get("default_branch") or "main")

    candidates: list[Candidate] = []
    seen: set[str] = set()
    order = 0
    readme_item: dict[str, Any] | None = None

    try:
        if subpath:
            listing = github_api_json(
                f"/repos/{owner}/{repo}/contents/{quote(subpath, safe='/')}", {"ref": ref}
            )
            if isinstance(listing, list):
                for item in listing:
                    name = str(item.get("name") or "").lower()
                    if name.startswith("readme") and item.get("type") == "file":
                        readme_item = github_api_json(
                            f"/repos/{owner}/{repo}/contents/{quote(str(item['path']), safe='/')}",
                            {"ref": ref},
                        )
                        break
        if readme_item is None:
            readme_item = github_api_json(f"/repos/{owner}/{repo}/readme", {"ref": ref})
    except Exception:
        readme_item = None

    if readme_item:
        text = decode_github_content(readme_item)
        readme_path = str(readme_item.get("path") or "README.md")
        readme_dir = str(PurePosixPath(readme_path).parent)
        if readme_dir == ".":
            readme_dir = ""
        for image_ref, alt in markdown_image_refs(text):
            url = resolve_markdown_ref(owner, repo, ref, readme_dir, image_ref)
            add_candidate(candidates, seen, url, alt, "github-readme", order, 30.0)
            order += 1

    try:
        tree = github_api_json(
            f"/repos/{owner}/{repo}/git/trees/{quote(ref, safe='/')}", {"recursive": "1"}
        )
        ranked: list[tuple[float, str]] = []
        for item in tree.get("tree", []):
            if item.get("type") != "blob":
                continue
            path = str(item.get("path") or "")
            if Path(path).suffix.lower() not in IMAGE_EXTENSIONS or reject_text(path):
                continue
            score = positive_hint_score(path)
            lower = path.lower()
            if any(part in lower for part in ("docs/", "images/", "image/", "assets/", "photos/", "media/")):
                score += 4.0
            if Path(path).suffix.lower() in {".jpg", ".jpeg"}:
                score += 2.0
            if score >= 6.0:
                ranked.append((score, path))
        ranked.sort(reverse=True)
        for tree_score, path in ranked[:12]:
            add_candidate(
                candidates, seen, github_raw_url(owner, repo, ref, path), Path(path).stem,
                "github-tree", order, 12.0 + tree_score,
            )
            order += 1
    except Exception:
        pass

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates
