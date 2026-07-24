#!/usr/bin/env python3
"""Build an offline-readable Excel workbook with real embedded thumbnails.

The input CSV remains the source of truth. Thumbnail URLs are downloaded,
resized and compressed into a disk cache, then inserted as actual XLSX drawing
objects. Excel and WPS therefore do not need IMAGE() formula support or network
access to display the thumbnails.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests
import xlsxwriter
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = "OpenHardwareEmbeddedThumbnailBuilder/1.0"
IMAGE_SIZE = (160, 90)
_thread_local = threading.local()


def session() -> requests.Session:
    current = getattr(_thread_local, "session", None)
    if current is not None:
        return current
    current = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    current.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=32, pool_maxsize=32))
    current.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.5"})
    _thread_local.session = current
    return current


def cache_path(cache_dir: Path, url: str) -> Path:
    return cache_dir / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.jpg"


def placeholder(path: Path, platform: str, reason: str = "") -> None:
    image = Image.new("RGB", IMAGE_SIZE, "#EEF3F8")
    draw = ImageDraw.Draw(image)
    label = (platform or "NO IMAGE")[:22]
    draw.rectangle((0, 0, IMAGE_SIZE[0] - 1, IMAGE_SIZE[1] - 1), outline="#9FB3C8", width=2)
    draw.text((10, 31), label, fill="#2B5C85")
    if reason:
        draw.text((10, 56), reason[:24], fill="#64748B")
    image.save(path, format="JPEG", quality=72, optimize=True)


def normalize_image(content: bytes, destination: Path) -> None:
    with Image.open(io.BytesIO(content)) as source:
        source.load()
        if source.mode in ("RGBA", "LA"):
            background = Image.new("RGBA", source.size, "white")
            background.alpha_composite(source.convert("RGBA"))
            source = background.convert("RGB")
        else:
            source = source.convert("RGB")
        source = ImageOps.contain(source, IMAGE_SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", IMAGE_SIZE, "white")
        x = (IMAGE_SIZE[0] - source.width) // 2
        y = (IMAGE_SIZE[1] - source.height) // 2
        canvas.paste(source, (x, y))
        canvas.save(destination, format="JPEG", quality=72, optimize=True, progressive=True)


def fetch_one(url: str, platform: str, cache_dir: Path, timeout: float) -> tuple[str, Path, bool, str]:
    path = cache_path(cache_dir, url)
    if path.exists() and path.stat().st_size > 500:
        return url, path, True, "cached"
    try:
        response = session().get(url, timeout=(8, timeout), allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "image" not in content_type and len(response.content) < 256:
            raise ValueError(f"not image: {content_type}")
        if len(response.content) > 12 * 1024 * 1024:
            raise ValueError("image exceeds 12MB")
        normalize_image(response.content, path)
        return url, path, True, "downloaded"
    except (requests.RequestException, UnidentifiedImageError, OSError, ValueError) as exc:
        placeholder(path, platform, type(exc).__name__)
        return url, path, False, f"{type(exc).__name__}: {exc}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def download_thumbnails(rows: list[dict[str, str]], cache_dir: Path, workers: int, timeout: float) -> tuple[dict[str, Path], dict[str, str]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    unique: dict[str, str] = {}
    for row in rows:
        url = row.get("thumbnail_url", "").strip()
        if url:
            unique.setdefault(url, row.get("platform", ""))

    print(f"[images] unique thumbnail URLs: {len(unique):,}", flush=True)
    mapping: dict[str, Path] = {}
    errors: dict[str, str] = {}
    completed = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(fetch_one, url, platform, cache_dir, timeout): url for url, platform in unique.items()}
        for future in as_completed(futures):
            url, path, ok, detail = future.result()
            mapping[url] = path
            if not ok:
                errors[url] = detail
            completed += 1
            if completed % 250 == 0 or completed == len(unique):
                print(f"[images] {completed:,}/{len(unique):,}; failures={len(errors):,}", flush=True)
    return mapping, errors


def to_number(value: str, integer: bool = False) -> int | float | str:
    if value == "":
        return ""
    try:
        return int(float(value)) if integer else float(value)
    except ValueError:
        return value


def build_workbook(
    rows: list[dict[str, str]],
    images: dict[str, Path],
    failures: dict[str, str],
    source_status_path: Path | None,
    scoring_method_path: Path | None,
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(output, {"constant_memory": True})
    workbook.set_properties({
        "title": "开源硬件商业化机会库（内嵌缩略图版）",
        "comments": "缩略图作为真实图片嵌入；无需IMAGE公式和联网显示",
    })

    projects = workbook.add_worksheet("项目机会库")
    summary = workbook.add_worksheet("摘要")
    status = workbook.add_worksheet("来源状态")
    method = workbook.add_worksheet("评分方法")

    title_fmt = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#17365D", "align": "left", "valign": "vcenter"})
    header_fmt = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "border": 1, "align": "center", "valign": "vcenter", "text_wrap": True})
    text_fmt = workbook.add_format({"valign": "top", "text_wrap": True, "border": 1, "border_color": "#D9E2F3"})
    center_fmt = workbook.add_format({"valign": "vcenter", "align": "center", "border": 1, "border_color": "#D9E2F3"})
    link_fmt = workbook.add_format({"font_color": "#0563C1", "underline": True, "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    number_fmt = workbook.add_format({"num_format": "0.00", "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    integer_fmt = workbook.add_format({"num_format": "0", "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    note_fmt = workbook.add_format({"font_color": "#666666", "italic": True, "text_wrap": True})

    columns: list[tuple[str, str | None, str]] = [
        ("项目ID", "project_id", "text"), ("缩略图", None, "image"), ("名称", "name", "text"),
        ("平台", "platform", "text"), ("原始链接", "url", "url"), ("发布时间", "published_date", "text"),
        ("最近更新", "updated_date", "text"), ("类别", "category", "text"), ("描述", "description", "text"),
        ("核心关键词", "keywords", "text"), ("市场验证", "market_validation", "text"), ("典型竞品", "typical_competitors", "text"),
        ("商业价值", "commercial_value", "text"), ("建议改进", "improvement_direction", "text"), ("目标客户", "target_customer", "text"),
        ("建议售价下限(元)", "suggested_price_low_cny", "int"), ("建议售价上限(元)", "suggested_price_high_cny", "int"),
        ("量产难度", "manufacturing_difficulty", "number"), ("售后风险", "after_sales_risk", "number"), ("合规风险", "compliance_risk", "number"),
        ("原始商业评分", "raw_commercial_score", "number"), ("正态化商业评分", "normalized_commercial_score", "number"),
        ("评分理由", "score_reason", "text"), ("硬件许可", "hardware_license", "text"), ("软件许可", "software_license", "text"),
        ("开源完整度", "open_source_completeness", "text"), ("数据质量", "data_quality", "text"), ("审核状态", "review_status", "text"),
        ("缩略图URL", "thumbnail_url", "urltext"), ("缩略图类型", "thumbnail_type", "text"), ("抓取时间", "crawl_time", "text"),
    ]

    projects.merge_range(0, 0, 0, len(columns) - 1, f"开源硬件商业化机会库（{len(rows):,}条，图片已内嵌）", title_fmt)
    projects.write(1, 0, "说明：缩略图是工作簿内嵌图片，WPS/Excel离线可见；缩略图URL列仅保留来源。评分仍为自动初筛，开发前必须人工核验许可、专利、商标和合规。", note_fmt)
    for col, (header, _, _) in enumerate(columns):
        projects.write(2, col, header, header_fmt)

    numeric_int = {"suggested_price_low_cny", "suggested_price_high_cny"}
    for idx, row in enumerate(rows, start=3):
        projects.set_row(idx, 72)
        for col, (_, key, kind) in enumerate(columns):
            if kind == "image":
                projects.write_blank(idx, col, None, center_fmt)
                url = row.get("thumbnail_url", "").strip()
                image_path = images.get(url)
                if image_path and image_path.exists():
                    projects.insert_image(idx, col, str(image_path), {
                        "x_scale": 0.70,
                        "y_scale": 0.70,
                        "x_offset": 4,
                        "y_offset": 4,
                        "object_position": 1,
                        "description": f"{row.get('name', '')} thumbnail",
                        "decorative": False,
                    })
                continue
            value = row.get(key or "", "")
            if kind == "url" and value:
                projects.write_url(idx, col, value, link_fmt, "打开项目")
            elif kind == "int":
                converted = to_number(value, integer=True)
                projects.write_number(idx, col, converted, integer_fmt) if isinstance(converted, int) else projects.write(idx, col, converted, text_fmt)
            elif kind == "number":
                converted = to_number(value)
                projects.write_number(idx, col, converted, number_fmt) if isinstance(converted, float) else projects.write(idx, col, converted, text_fmt)
            else:
                projects.write(idx, col, value, text_fmt)
        if idx % 500 == 0:
            print(f"[xlsx] wrote {idx - 2:,}/{len(rows):,} rows", flush=True)

    widths = [18, 18, 26, 18, 14, 12, 12, 20, 44, 24, 24, 36, 42, 42, 30, 13, 13, 11, 11, 11, 13, 15, 52, 18, 18, 30, 10, 20, 40, 12, 22]
    for index, width in enumerate(widths):
        projects.set_column(index, index, width)
    projects.freeze_panes(3, 2)
    projects.autofilter(2, 0, 2 + len(rows), len(columns) - 1)
    score_col = [header for header, _, _ in columns].index("正态化商业评分")
    projects.conditional_format(3, score_col, 2 + len(rows), score_col, {"type": "3_color_scale", "min_color": "#F8696B", "mid_color": "#FFEB84", "max_color": "#63BE7B"})

    platform_counts = Counter(row.get("platform", "") for row in rows)
    category_counts = Counter(row.get("category", "") for row in rows)
    quality_counts = Counter(row.get("data_quality", "") for row in rows)
    embedded = sum(1 for row in rows if row.get("thumbnail_url", "").strip() in images)
    summary.merge_range("A1:H1", "开源硬件商业化机会库 — 内嵌图片版摘要", title_fmt)
    metrics = [
        ("项目总数", len(rows)), ("平台数量", len(platform_counts)),
        ("内嵌图片行数", embedded), ("图片下载失败URL", len(failures)),
        ("8分以上", sum(float(row.get("normalized_commercial_score") or 0) >= 8 for row in rows)),
    ]
    for i, (name, value) in enumerate(metrics, start=2):
        summary.write(i, 0, name, header_fmt)
        summary.write_number(i, 1, value, integer_fmt)
    summary.write(2, 3, "平台", header_fmt); summary.write(2, 4, "条数", header_fmt)
    for i, (name, count) in enumerate(platform_counts.most_common(), start=3):
        summary.write(i, 3, name, text_fmt); summary.write_number(i, 4, count, integer_fmt)
    summary.write(2, 6, "类别", header_fmt); summary.write(2, 7, "条数", header_fmt)
    for i, (name, count) in enumerate(category_counts.most_common(), start=3):
        summary.write(i, 6, name, text_fmt); summary.write_number(i, 7, count, integer_fmt)
    summary.set_column("A:A", 24); summary.set_column("B:B", 14); summary.set_column("D:D", 30); summary.set_column("E:E", 12); summary.set_column("G:G", 30); summary.set_column("H:H", 12)

    if source_status_path and source_status_path.exists():
        status_rows = read_csv(source_status_path)
        if status_rows:
            headers = list(status_rows[0])
            for col, header in enumerate(headers): status.write(0, col, header, header_fmt)
            for r, item in enumerate(status_rows, start=1):
                for c, header in enumerate(headers): status.write(r, c, item.get(header, ""), text_fmt)
            status.freeze_panes(1, 0)
            status.set_column(0, len(headers) - 1, 24)

    method.write("A1", "评分与图片说明", title_fmt)
    method.set_column("A:A", 120)
    notes = [
        "本文件的缩略图是XLSX内部真实图片对象，不是IMAGE()公式。",
        "因此Microsoft Excel、WPS表格在离线状态下也应显示图片。",
        "缩略图下载失败时会嵌入带平台名称的占位图；缩略图URL仍保留用于追溯。",
        "图片被统一缩放到160×90并压缩，以控制10,500张图片造成的文件体积。",
    ]
    if scoring_method_path and scoring_method_path.exists():
        notes.append(scoring_method_path.read_text(encoding="utf-8", errors="replace"))
    for row_index, note in enumerate(notes, start=2):
        method.write(row_index, 0, note, text_fmt)

    workbook.close()
    print(f"[done] workbook: {output} ({output.stat().st_size / 1024 / 1024:.1f} MB)", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--source-status", type=Path)
    parser.add_argument("--scoring-method", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", type=Path, default=Path("thumbnail_cache"))
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    rows = read_csv(args.csv)
    if not rows:
        print("input CSV has no records", file=sys.stderr)
        return 2
    images, failures = download_thumbnails(rows, args.cache_dir, args.workers, args.timeout)
    build_workbook(rows, images, failures, args.source_status, args.scoring_method, args.output)
    report = {
        "records": len(rows),
        "unique_thumbnail_urls": len(images),
        "failed_thumbnail_urls": len(failures),
        "output": str(args.output),
        "output_bytes": args.output.stat().st_size,
    }
    args.output.with_suffix(".images.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
