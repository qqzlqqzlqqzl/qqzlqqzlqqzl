#!/usr/bin/env python3
"""Validate a generated open-hardware opportunity output directory."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FILES = (
    "开源硬件商业化机会库_10000条.xlsx",
    "hardware_opportunities.csv",
    "hardware_opportunities.jsonl",
    "source_status.csv",
    "score_distribution.csv",
    "summary.json",
    "SCORING_METHOD.md",
    "progress.json",
)

REQUIRED_COLUMNS = {
    "project_id",
    "name",
    "platform",
    "url",
    "category",
    "raw_commercial_score",
    "normalized_commercial_score",
    "score_reason",
    "data_quality",
    "review_status",
}

REQUIRED_SHEETS = {"项目机会库", "摘要", "来源状态", "评分方法"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="Output directory, for example output_v2")
    parser.add_argument("--min-records", type=int, default=10000)
    parser.add_argument("--min-platforms", type=int, default=25)
    parser.add_argument("--max-top4-share", type=float, default=0.72)
    return parser.parse_args()


def workbook_sheet_names(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("xl/workbook.xml"))
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return {sheet.attrib["name"] for sheet in root.findall("x:sheets/x:sheet", namespace)}


def finite_score(value: str) -> float:
    score = float(value)
    if not math.isfinite(score):
        raise ValueError(f"non-finite score: {value!r}")
    return score


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    errors: list[str] = []

    if not output.is_dir():
        print(f"ERROR: output directory does not exist: {output}", file=sys.stderr)
        return 2

    missing = [name for name in REQUIRED_FILES if not (output / name).is_file()]
    if missing:
        errors.append("missing files: " + ", ".join(missing))

    summary: dict[str, Any] = {}
    summary_path = output / "summary.json"
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"summary.json unreadable: {exc}")

    rows: list[dict[str, str]] = []
    csv_path = output / "hardware_opportunities.csv"
    if csv_path.is_file():
        try:
            with csv_path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                columns = set(reader.fieldnames or [])
                absent_columns = sorted(REQUIRED_COLUMNS - columns)
                if absent_columns:
                    errors.append("CSV missing columns: " + ", ".join(absent_columns))
                rows = list(reader)
        except Exception as exc:
            errors.append(f"CSV unreadable: {exc}")

    ids = [row.get("project_id", "").strip() for row in rows]
    urls = [row.get("url", "").strip() for row in rows]
    platforms = Counter(row.get("platform", "").strip() for row in rows if row.get("platform", "").strip())

    duplicate_ids = len(ids) - len(set(ids))
    duplicate_urls = len(urls) - len(set(urls))
    blank_ids = sum(not value for value in ids)
    blank_urls = sum(not value for value in urls)
    top4_share = sum(count for _, count in platforms.most_common(4)) / max(1, len(rows))

    if len(rows) < args.min_records:
        errors.append(f"records {len(rows)} < {args.min_records}")
    if len(platforms) < args.min_platforms:
        errors.append(f"platforms {len(platforms)} < {args.min_platforms}")
    if top4_share > args.max_top4_share:
        errors.append(f"top4 share {top4_share:.4%} > {args.max_top4_share:.2%}")
    if duplicate_ids:
        errors.append(f"duplicate project_id rows: {duplicate_ids}")
    if duplicate_urls:
        errors.append(f"duplicate URL rows: {duplicate_urls}")
    if blank_ids:
        errors.append(f"blank project_id rows: {blank_ids}")
    if blank_urls:
        errors.append(f"blank URL rows: {blank_urls}")

    invalid_scores = 0
    for row in rows:
        try:
            raw = finite_score(row["raw_commercial_score"])
            normalized = finite_score(row["normalized_commercial_score"])
            if not 0 <= raw <= 10 or not 0 <= normalized <= 10:
                invalid_scores += 1
        except Exception:
            invalid_scores += 1
    if invalid_scores:
        errors.append(f"invalid score rows: {invalid_scores}")

    if summary:
        if int(summary.get("records", -1)) != len(rows):
            errors.append(f"summary records {summary.get('records')} != CSV rows {len(rows)}")
        if int(summary.get("platforms", -1)) != len(platforms):
            errors.append(f"summary platforms {summary.get('platforms')} != calculated {len(platforms)}")
        reported_share = float(summary.get("top4_platform_share", -1))
        if not math.isclose(reported_share, top4_share, rel_tol=0, abs_tol=1e-6):
            errors.append(f"summary top4 share {reported_share} != calculated {top4_share:.6f}")

    xlsx_path = output / "开源硬件商业化机会库_10000条.xlsx"
    sheet_names: set[str] = set()
    if xlsx_path.is_file():
        try:
            sheet_names = workbook_sheet_names(xlsx_path)
            missing_sheets = sorted(REQUIRED_SHEETS - sheet_names)
            if missing_sheets:
                errors.append("Excel missing sheets: " + ", ".join(missing_sheets))
        except Exception as exc:
            errors.append(f"Excel unreadable: {exc}")

    report = {
        "output": str(output),
        "records": len(rows),
        "platforms": len(platforms),
        "top4_platform_share": round(top4_share, 6),
        "duplicate_project_ids": duplicate_ids,
        "duplicate_urls": duplicate_urls,
        "invalid_score_rows": invalid_scores,
        "excel_sheets": sorted(sheet_names),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors:
        print("VALIDATION FAILED", file=sys.stderr)
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
