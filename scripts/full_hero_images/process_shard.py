from __future__ import annotations

import argparse
import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from .common import (
    MAX_CANDIDATES_TO_DOWNLOAD, Candidate, Result, fetch_html,
    parse_content_images,
)
from .github_source import github_candidates
from .image_quality import validate_candidate


def collect_candidates(project_url: str) -> list[Candidate]:
    parsed = urlparse(project_url)
    if parsed.netloc.lower() in {"github.com", "www.github.com"}:
        try:
            candidates = github_candidates(project_url)
            if candidates:
                return candidates
        except Exception:
            pass
    html_text, final_url = fetch_html(project_url)
    return parse_content_images(html_text, final_url)


def safe_filename(project_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", project_id)[:80] + ".jpg"


def process_project(row: dict[str, str], output_images: Path) -> Result:
    project_id = row.get("project_id", "")
    result = Result(
        project_id=project_id,
        project_name=row.get("name", ""),
        project_url=row.get("url", ""),
        platform=row.get("platform", ""),
        processed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    try:
        candidates = collect_candidates(result.project_url)
        result.candidate_count = len(candidates)
    except Exception as exc:
        result.hero_image_reason = f"候选收集失败 {type(exc).__name__}: {exc}"
        return result

    best: tuple[float, Candidate, str, bytes] | None = None
    rejected_reasons: list[str] = []
    for candidate in candidates[:MAX_CANDIDATES_TO_DOWNLOAD]:
        try:
            valid, score, reason, prepared = validate_candidate(candidate)
        except Exception as exc:
            rejected_reasons.append(f"{candidate.source}:download {type(exc).__name__}")
            continue
        if not valid or prepared is None:
            rejected_reasons.append(reason)
            continue
        if best is None or score > best[0]:
            best = (score, candidate, reason, prepared)

    if best is None:
        result.hero_image_reason = "; ".join(rejected_reasons[:4]) or "未找到合格候选图"
        return result

    _, candidate, reason, prepared = best
    filename = safe_filename(project_id)
    (output_images / filename).write_bytes(prepared)
    result.hero_image_source_url = candidate.url
    result.hero_image_local_filename = filename
    result.hero_image_status = "已核验：真实硬件主图（自动严格筛选）"
    result.hero_image_reason = reason
    return result


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_results(path: Path, results: Iterable[Result]) -> None:
    fields = list(Result.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_row())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-size", type=int, default=500)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    source = Path(args.source_csv)
    output = Path(args.output_dir)
    images = output / "images"
    images.mkdir(parents=True, exist_ok=True)

    rows = read_rows(source)
    start = args.shard_index * args.shard_size
    end = min(len(rows), start + args.shard_size)
    selected = rows[start:end]
    print(
        f"shard={args.shard_index} range={start}:{end} "
        f"rows={len(selected)} workers={args.workers}",
        flush=True,
    )

    ordered: list[Result | None] = [None] * len(selected)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_index = {
            executor.submit(process_project, row, images): index
            for index, row in enumerate(selected)
        }
        completed = 0
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                ordered[index] = future.result()
            except Exception as exc:
                row = selected[index]
                ordered[index] = Result(
                    project_id=row.get("project_id", ""),
                    project_name=row.get("name", ""),
                    project_url=row.get("url", ""),
                    platform=row.get("platform", ""),
                    hero_image_reason=f"worker异常 {type(exc).__name__}: {exc}",
                    processed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                )
            completed += 1
            if completed % 25 == 0 or completed == len(selected):
                print(
                    f"shard={args.shard_index} progress={completed}/{len(selected)}",
                    flush=True,
                )

    results = [item for item in ordered if item is not None]
    write_results(output / "image_results.csv", results)
    success = sum(1 for item in results if item.hero_image_local_filename)
    summary = {
        "shard_index": args.shard_index,
        "start": start,
        "end": end,
        "rows": len(results),
        "hero_images": success,
        "success_rate": round(success / max(1, len(results)), 4),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
