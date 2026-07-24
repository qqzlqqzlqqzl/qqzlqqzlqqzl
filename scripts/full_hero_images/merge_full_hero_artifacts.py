#!/usr/bin/env python3
"""Merge image shard artifacts and Chinese translations into one offline package.

This step intentionally produces CSV + image files, not XLSX. The final XLSX
is built locally with artifact_tool after the artifact is downloaded.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ORIGINAL_FIELDS = [
    "project_id", "name", "platform", "url", "source_domain", "thumbnail_url",
    "thumbnail_type", "published_date", "updated_date", "description", "keywords",
    "category", "stars_or_support", "hardware_license", "software_license",
    "open_source_completeness", "market_validation", "typical_competitors",
    "commercial_value", "improvement_direction", "target_customer",
    "suggested_price_low_cny", "suggested_price_high_cny", "manufacturing_difficulty",
    "after_sales_risk", "compliance_risk", "raw_commercial_score",
    "normalized_commercial_score", "score_reason", "data_quality", "review_status",
    "crawl_time",
]

EXTRA_FIELDS = [
    "hero_image_source_url", "hero_image_local_filename", "hero_image_status",
    "hero_image_reason", "candidate_count", "image_processed_at",
    "description_zh", "keywords_zh", "description_translation_status",
    "keywords_translation_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def find_files(root: Path, filename: str) -> list[Path]:
    return sorted(path for path in root.rglob(filename) if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", required=True)
    parser.add_argument("--image-artifacts", required=True)
    parser.add_argument("--translation-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    source_path = Path(args.source_csv)
    image_root = Path(args.image_artifacts)
    translation_path = Path(args.translation_csv)
    output = Path(args.output_dir)
    images_out = output / "hero_images"
    output.mkdir(parents=True, exist_ok=True)
    images_out.mkdir(parents=True, exist_ok=True)

    source_rows = read_csv(source_path)
    if len(source_rows) != 10_500:
        raise RuntimeError(f"Expected 10500 source rows, got {len(source_rows)}")
    translations = {row["project_id"]: row for row in read_csv(translation_path)}

    image_results: dict[str, dict[str, str]] = {}
    duplicate_image_rows = 0
    for result_csv in find_files(image_root, "image_results.csv"):
        for row in read_csv(result_csv):
            project_id = row.get("project_id", "")
            if project_id in image_results:
                duplicate_image_rows += 1
            image_results[project_id] = row

    if len(image_results) != len(source_rows):
        missing = [row["project_id"] for row in source_rows if row["project_id"] not in image_results]
        raise RuntimeError(
            f"Image shard coverage incomplete: {len(image_results)}/{len(source_rows)}; "
            f"missing sample={missing[:10]}"
        )

    image_file_index: dict[str, Path] = {}
    for path in image_root.rglob("*.jpg"):
        image_file_index[path.name] = path

    final_rows: list[dict[str, Any]] = []
    copied_images = 0
    per_platform = defaultdict(lambda: {"rows": 0, "images": 0})
    status_counts: Counter[str] = Counter()
    translation_counts: Counter[str] = Counter()

    for source in source_rows:
        project_id = source["project_id"]
        image = image_results[project_id]
        translation = translations.get(project_id, {})
        local_filename = image.get("hero_image_local_filename", "")
        if local_filename:
            source_image = image_file_index.get(local_filename)
            if source_image and source_image.exists():
                target_name = f"{project_id}.jpg"
                shutil.copy2(source_image, images_out / target_name)
                local_filename = target_name
                copied_images += 1
            else:
                local_filename = ""
                image["hero_image_status"] = "图像文件缺失"
                image["hero_image_reason"] = "image_results.csv 指向的图片未出现在分片产物中"

        row = {field: source.get(field, "") for field in ORIGINAL_FIELDS}
        row.update({
            "hero_image_source_url": image.get("hero_image_source_url", ""),
            "hero_image_local_filename": local_filename,
            "hero_image_status": image.get("hero_image_status", ""),
            "hero_image_reason": image.get("hero_image_reason", ""),
            "candidate_count": image.get("candidate_count", "0"),
            "image_processed_at": image.get("processed_at", ""),
            "description_zh": translation.get("description_zh", source.get("description", "")),
            "keywords_zh": translation.get("keywords_zh", source.get("keywords", "")),
            "description_translation_status": translation.get("description_translation_status", "missing"),
            "keywords_translation_status": translation.get("keywords_translation_status", "missing"),
        })
        final_rows.append(row)

        platform = source.get("platform", "")
        per_platform[platform]["rows"] += 1
        if local_filename:
            per_platform[platform]["images"] += 1
        status_counts[row["hero_image_status"]] += 1
        translation_counts[row["description_translation_status"]] += 1

    fieldnames = ORIGINAL_FIELDS + EXTRA_FIELDS
    full_csv = output / "hardware_opportunities_full_hero_images.csv"
    with full_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    platform_rows = []
    for platform, counts in sorted(per_platform.items(), key=lambda item: (-item[1]["rows"], item[0])):
        platform_rows.append({
            "platform": platform,
            "rows": counts["rows"],
            "hero_images": counts["images"],
            "hero_image_rate": round(counts["images"] / max(1, counts["rows"]), 4),
        })
    with (output / "hero_image_platform_summary.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["platform", "rows", "hero_images", "hero_image_rate"])
        writer.writeheader()
        writer.writerows(platform_rows)

    summary = {
        "rows": len(final_rows),
        "hero_images_copied": copied_images,
        "hero_image_rate": round(copied_images / len(final_rows), 4),
        "image_status_counts": dict(status_counts),
        "description_translation_counts": dict(translation_counts),
        "image_result_rows": len(image_results),
        "translation_rows": len(translations),
        "duplicate_image_rows": duplicate_image_rows,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "README.txt").write_text(
        "全量英雄图中间产物\n"
        "==================\n"
        "hardware_opportunities_full_hero_images.csv 保留原 32 字段，并增加英雄图与中文翻译字段。\n"
        "hero_images/ 存放经过严格筛选与统一压缩的真实硬件主图。\n"
        "没有高置信度真实硬件图的项目会保持空白，不会用 Logo、favicon、项目卡或渲染图替代。\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
