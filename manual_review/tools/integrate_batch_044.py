import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BATCH_PATH = ROOT / "manual_review" / "batch_044_exact_page_v3.csv"
QUEUE_PATH = ROOT / "manual_review" / "queue_next_200.csv"
DEFERRED_PATH = ROOT / "manual_review" / "deferred_unresolved.csv"
SHARD_DIR = ROOT / "manual_review" / "shards"

FIELDS = [
    "project_id",
    "name",
    "original_url",
    "review_status",
    "product_form",
    "opportunity_family",
    "family_business_model",
    "commercialization_mode",
    "actual_product",
    "paying_customer",
    "pain_point",
    "price_usd",
    "market_evidence",
    "market_crowding",
    "third_party_dependency",
    "manufacturing_risk",
    "after_sales_risk",
    "compliance_risk",
    "license_status",
    "hero_image_verdict",
    "final_bucket",
    "verdict_reason",
    "evidence_urls",
    "reviewed_at",
]

DEFERRED_IDS = {
    "b383fb5982f6b4fc",
    "6b2dc67b6043485b",
    "7b2240c7f7606ea3",
    "e6c3fdee67f39920",
    "d980f935c1732d31",
    "52d6df67c7e83dd7",
    "603de0c4d59e67ce",
    "5318c5d0e318147f",
    "cb3a999668e235ef",
    "ae2a8609fbc3a1ed",
}

# The shard reviewers used the wrong cache field or were deliberately
# conservative for these rows.  The exact cache contains readable, specific
# page_text/readme content, so the integrator keeps the baseline row instead of
# turning a readable record into deferred.
BASELINE_IDS = {
    "aabda3f0f9c75545",  # OSHWA page_text is present
    "e4c0578a52340240",  # GitLab README/API body is present
    "c66f45eb565bf893",  # SDR-STK README identifies the hardware/software scope
    "60e282e85609c912",  # EurorackButtonBoard README identifies the system
    "eeb60ad507964f3c",  # OSHWA page_text is present
    "a25f220d636f7917",  # PCBWay page is a concrete project page with description, files and order metadata
    "c807ba6145c96004",  # GitLab README/API body is present
    "c599bd35232b19a7",  # 嘉立创 page_text contains full project, BOM and license notice
    "0e2bae50548ed35d",  # shard CSV has a malformed quote; baseline row is schema-valid
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    baseline = {row["project_id"]: row for row in read_csv(BATCH_PATH)}
    queue = {row["project_id"]: row for row in read_csv(QUEUE_PATH)}

    shard_rows = {}
    for path in sorted(SHARD_DIR.glob("044_[abcde].csv")):
        for row in read_csv(path):
            if row["project_id"] in shard_rows:
                raise SystemExit(f"duplicate shard id: {row['project_id']}")
            shard_rows[row["project_id"]] = row

    expected = set(queue) - DEFERRED_IDS
    missing_baseline = expected - set(baseline)
    if missing_baseline:
        raise SystemExit(f"baseline missing reviewed ids: {sorted(missing_baseline)}")

    merged = {}
    for pid in expected:
        row = baseline[pid] if pid in BASELINE_IDS or pid not in shard_rows else shard_rows[pid]
        if row["final_bucket"] not in {"严格商业候选", "观察名单", "市场参考案例", "淘汰"}:
            # DSH-AEGIS is explicitly designed but not built; it is a rejected
            # technical reference, not a fifth bucket.
            if pid == "0e2bae50548ed35d":
                row["final_bucket"] = "淘汰"
            else:
                raise SystemExit(f"invalid final_bucket for {pid}: {row['final_bucket']}")
        if len(row) != len(FIELDS) or set(row) != set(FIELDS):
            raise SystemExit(f"schema mismatch for {pid}")
        merged[pid] = row

    if len(merged) != 190:
        raise SystemExit(f"expected 190 reviewed rows, got {len(merged)}")

    # Preserve source queue order for a stable batch and deterministic diffs.
    ordered = [merged[pid] for pid in queue if pid in merged]
    with BATCH_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(ordered)

    deferred = read_csv(DEFERRED_PATH)
    by_id = {row["project_id"]: row for row in deferred}
    # Remove accidental shard-level additions for readable pages.  Keep every
    # prior deferred record and only the ten evidence-unresolved queue IDs.
    by_id = {
        pid: row
        for pid, row in by_id.items()
        if pid not in queue or pid in DEFERRED_IDS
    }
    for pid in DEFERRED_IDS:
        if pid not in by_id:
            item = queue[pid]
            by_id[pid] = {
                "project_id": pid,
                "name": item["name"],
                "original_url": item["url"],
                "defer_reason": "044 集成时确认精确页面为 404、空壳或分类目录，未取得该项目的可核验正文。",
                "last_checked": "2026-07-26",
            }
    deferred_fields = ["project_id", "name", "original_url", "defer_reason", "last_checked"]
    deferred_ordered = sorted(by_id.values(), key=lambda row: (row["last_checked"], row["project_id"]))
    with DEFERRED_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=deferred_fields)
        writer.writeheader()
        writer.writerows(deferred_ordered)

    print(f"integrated {len(ordered)} rows")
    print(f"deferred total {len(deferred_ordered)}")
    print(f"shard rows used {len(shard_rows) - len(BASELINE_IDS & set(shard_rows))}")


if __name__ == "__main__":
    main()
