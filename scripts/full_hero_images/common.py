from __future__ import annotations

import html
import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "OpenHardwareHeroImageBuilder/2.0 (+https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl)"
TIMEOUT = 25
MAX_CANDIDATES_TO_DOWNLOAD = 10
OUTPUT_SIZE = (240, 140)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_session_local = threading.local()

REJECT_PATTERNS = [
    r"favicon", r"logo", r"avatar", r"icon[-_.]", r"/icons?/", r"badge[-_ ]?status",
    r"shields?\.io", r"opengraph", r"open[-_ ]?graph", r"social[-_ ]?(card|preview|image)",
    r"repo[-_ ]?card", r"repository[-_ ]?card", r"githubassets\.com/.*opengraph",
    r"certification.*(logo|mark)", r"license", r"sponsor", r"donate", r"button",
    r"schematic", r"block[-_ ]?diagram", r"flow[-_ ]?chart", r"wiring", r"pinout",
    r"pcb[-_ ]?(layout|drawing)", r"gerber", r"board[-_ ]?view", r"dimension",
    r"render", r"rendered", r"3d[-_ ]?(front|back|view|render)", r"cad", r"step[-_ ]?preview",
    r"screenshot", r"screen[-_ ]?shot", r"settings", r"heatmap", r"terminal", r"serial[-_ ]?monitor",
    r"ui[-_ ]", r"dashboard[-_ ]?screenshot", r"browser", r"app[-_ ]?screen",
    r"qr[-_ ]?code", r"banner", r"header[-_ ]?graphic", r"cover[-_ ]?art",
]

REAL_PHOTO_HINTS = [
    r"\bphoto\b", r"\bproduct\b", r"\bhero\b", r"\boverview\b", r"\bassembled\b",
    r"\bprototype\b", r"\bhardware\b", r"\bdevice\b", r"\bboard\b", r"\bpcb\b",
    r"\bbadge\b", r"\bkeychain\b", r"\bpendant\b", r"\bmacropad\b", r"\bkeyboard\b",
    r"\boled\b", r"\btft\b", r"\bfront\b", r"\bback\b", r"\btop\b", r"\bbottom\b",
    r"\bcase\b", r"\benclosure\b", r"\bfinished\b", r"\bfinal\b", r"\bdemo\b",
    r"pxl_\d+", r"img[_-]?\d+", r"dsc[_-]?\d+", r"photo[_-]?\d+",
]
NEGATIVE_ALT_HINTS = [
    "logo", "icon", "badge status", "build status", "license", "screenshot", "schematic",
    "diagram", "render", "3d render", "pcb layout", "wiring", "pinout", "interface",
]
POSITIVE_ALT_HINTS = [
    "hardware", "product", "device", "assembled", "prototype", "board", "pcb", "badge",
    "keychain", "pendant", "macropad", "oled", "front", "back", "overview", "photo",
]


@dataclass
class Candidate:
    url: str
    alt: str
    source: str
    order: int
    score: float


@dataclass
class Result:
    project_id: str
    project_name: str
    project_url: str
    platform: str
    hero_image_source_url: str = ""
    hero_image_local_filename: str = ""
    hero_image_status: str = "无合格英雄图"
    hero_image_reason: str = ""
    candidate_count: int = 0
    processed_at: str = ""

    def to_row(self) -> dict[str, Any]:
        return self.__dict__.copy()


def get_session() -> requests.Session:
    session = getattr(_session_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6",
        })
        _session_local.session = session
    return session


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def clean_url(url: str) -> str:
    return html.unescape((url or "").strip())


def reject_text(text: str) -> bool:
    lower = unquote(clean_url(text)).lower()
    return any(re.search(pattern, lower) for pattern in REJECT_PATTERNS)


def positive_hint_score(text: str) -> float:
    lower = unquote(clean_url(text)).lower()
    searchable = re.sub(r"[^a-z0-9]+", " ", lower)
    score = 0.0
    for pattern in REAL_PHOTO_HINTS:
        if re.search(pattern, lower) or re.search(pattern, searchable):
            score += 1.6
    if re.search(r"(?:^|[/_.-])(pxl|img|dsc|photo)[_-]?\d+", lower):
        score += 3.5
    if lower.endswith((".jpg", ".jpeg")):
        score += 2.5
    elif lower.endswith(".webp"):
        score += 1.0
    elif lower.endswith(".png"):
        score += 0.2
    return score


def alt_score(alt: str) -> float:
    lower = (alt or "").strip().lower()
    if any(hint in lower for hint in NEGATIVE_ALT_HINTS):
        return -12.0
    return sum(1.5 for hint in POSITIVE_ALT_HINTS if hint in lower)


def normalize_image_url(base_url: str, ref: str) -> str:
    ref = clean_url(ref)
    if not ref or ref.startswith("data:"):
        return ""
    if ref.startswith("//"):
        return "https:" + ref
    return urljoin(base_url, ref)


def add_candidate(
    candidates: list[Candidate], seen: set[str], url: str, alt: str,
    source: str, order: int, base_score: float,
) -> None:
    url = clean_url(url)
    if not url or url in seen or reject_text(url) or reject_text(alt):
        return
    ext = Path(urlparse(url).path).suffix.lower()
    if ext and ext not in IMAGE_EXTENSIONS:
        return
    score = base_score + positive_hint_score(url) + alt_score(alt) - min(order, 20) * 0.15
    candidates.append(Candidate(url, alt or "", source, order, score))
    seen.add(url)


def select_src_from_img(img: Any) -> str:
    for attr in ("src", "data-src", "data-original", "data-canonical-src"):
        ref = img.get(attr)
        if ref:
            return str(ref)
    srcset = img.get("srcset")
    if srcset:
        parts = [part.strip().split()[0] for part in str(srcset).split(",") if part.strip()]
        if parts:
            return parts[-1]
    return ""


def fetch_html(url: str) -> tuple[str, str]:
    response = get_session().get(url, timeout=TIMEOUT, allow_redirects=True)
    response.raise_for_status()
    ctype = response.headers.get("content-type", "")
    if "html" not in ctype.lower() and not response.text.lstrip().startswith("<"):
        raise ValueError(f"not html: {ctype}")
    return response.text, response.url


def parse_content_images(html_text: str, final_url: str) -> list[Candidate]:
    soup = BeautifulSoup(html_text, "html.parser")
    candidates: list[Candidate] = []
    seen: set[str] = set()
    containers = []
    for selector in (
        "article.markdown-body", "article", "main", ".project-description", ".project-content",
        ".content", "#content", ".entry-content", ".post-content", ".readme", ".wiki",
    ):
        containers.extend(soup.select(selector))
    if not containers:
        containers = [soup]

    order = 0
    for container_idx, container in enumerate(containers[:8]):
        for img in container.find_all("img"):
            ref = select_src_from_img(img)
            if not ref:
                continue
            alt = str(img.get("alt") or img.get("title") or "")
            full = normalize_image_url(final_url, ref)
            if full:
                add_candidate(candidates, seen, full, alt, f"content:{container_idx}", order, 18.0)
                order += 1

    for selector, attr in (
        ('meta[property="og:image"]', "content"),
        ('meta[name="twitter:image"]', "content"),
    ):
        for node in soup.select(selector):
            full = normalize_image_url(final_url, str(node.get(attr) or ""))
            add_candidate(candidates, seen, full, "", "metadata", order, 2.0)
            order += 1

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates
