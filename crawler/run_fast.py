#!/usr/bin/env python3
"""Fast GitHub Actions entrypoint.

It keeps the core scoring/export pipeline but bounds slow third-party sites and
uses concurrency for the broad platform pass. Public APIs remain rate-limited.
"""
from __future__ import annotations

import concurrent.futures
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

import main as core

FAST = requests.Session()
FAST.headers.update({"User-Agent": core.UA, "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6"})


def get(url: str, timeout: float = 7.0):
    return FAST.get(url, timeout=timeout, allow_redirects=True)


def sitemap_candidates(source: core.WebSource) -> list[str]:
    candidates: list[str] = []
    queue = list(source.sitemap)
    seen: set[str] = set()
    while queue and len(seen) < 3 and len(candidates) < source.max_rows * 3:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            response = get(url)
            if not response.ok:
                continue
            root = ET.fromstring(response.content)
            if root.tag.lower().endswith("sitemapindex"):
                queue.extend([node.text.strip() for node in root.findall(".//{*}loc") if node.text][:3])
            else:
                for item in root.findall(".//{*}url"):
                    loc = item.find("{*}loc")
                    last = item.find("{*}lastmod")
                    if loc is None or not loc.text or not core.recent_enough(last.text if last is not None else ""):
                        continue
                    candidate = core.canonical_url(loc.text.strip())
                    if any(re.search(pattern, candidate, re.I) for pattern in source.patterns):
                        candidates.append(candidate)
        except Exception:
            continue
    return candidates


def seed_candidates(source: core.WebSource) -> list[str]:
    candidates: list[str] = []
    for seed in source.seeds:
        try:
            response = get(seed)
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                candidate = core.canonical_url(urllib.parse.urljoin(seed, link["href"]))
                if any(re.search(pattern, candidate, re.I) for pattern in source.patterns):
                    candidates.append(candidate)
        except Exception:
            continue
    return candidates


def parse_detail_fast(platform: str, url: str):
    try:
        response = get(url, 8.0)
        if not response.ok:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = ""
        for selector in ('meta[property="og:title"]', 'meta[name="twitter:title"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                title = core.clean_text(tag["content"], 180)
                break
        if not title and soup.title:
            title = core.clean_text(soup.title.get_text(" "), 180)
        description = ""
        for selector in ('meta[property="og:description"]', 'meta[name="description"]', 'meta[name="twitter:description"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                description = core.clean_text(tag["content"], 600)
                break
        image = ""
        for selector in ('meta[property="og:image"]', 'meta[name="twitter:image"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                image = urllib.parse.urljoin(url, tag["content"])
                break
        published = ""
        for selector in ('meta[property="article:published_time"]', 'meta[name="date"]', 'time[datetime]'):
            tag = soup.select_one(selector)
            if tag:
                published = core.parse_date(tag.get("content") or tag.get("datetime"))
                if published:
                    break
        if published and published < core.CUTOFF.date().isoformat():
            return None
        keywords = soup.select_one('meta[name="keywords"]')
        return core.make_record(
            platform, url, title or core.slug_title(url),
            thumbnail_url=image or f"https://www.google.com/s2/favicons?domain={urllib.parse.urlsplit(url).netloc}&sz=128",
            thumbnail_type="产品图" if image else "平台图",
            published_date=published,
            description=description,
            keywords=core.clean_text(keywords.get("content", "") if keywords else "", 300),
            hardware_license="页面待核验",
            software_license="页面待核验",
            open_source_completeness="公开项目页；设计文件与许可需二次核验",
            market_validation=f"收录于{platform}公开项目/商品目录",
        )
    except Exception:
        return None


def fetch_web_source_fast(source: core.WebSource):
    candidates = list(dict.fromkeys(sitemap_candidates(source) + seed_candidates(source)))
    candidates = candidates[: max(12, min(source.max_rows * 3, 90))]
    if not candidates:
        return []
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(parse_detail_fast, source.name, url) for url in candidates]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            if record:
                records.append(record)
            if len(records) >= source.max_rows:
                break
    return records[: source.max_rows]


original_github = core.fetch_github
original_gitlab = core.fetch_gitlab
core.fetch_github = lambda _limit=0: original_github(2350)
core.fetch_gitlab = lambda _limit=0: original_gitlab(550)
core.fetch_web_source = fetch_web_source_fast

if __name__ == "__main__":
    raise SystemExit(core.main())
