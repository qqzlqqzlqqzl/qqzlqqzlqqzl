# V3 review archive manifest

Updated: 2026-07-26

## Durable recovery handles

- Repository: `qqzlqqzlqqzl/qqzlqqzlqqzl`
- Draft pull request: `#9` (`rebuild: strict commercial screening V3`)
- Working branch: `agent/commercial-v3-strict-rebuild`
- Canonical progress checkpoint: batch 044 integration (pending commit)
- Canonical progress ledger: `manual_review/PROGRESS.md`
- Review policy: `commercial_v3/REBUILD_SPEC.md`
- Hourly task title: `千条人工复核批次`

## Current checkpoint

- Raw records: 10,500
- Page/source-reviewed records: 1,041
- Strict commercial candidates: 0
- Watchlist: 49
- Market-reference cases: 254
- Rejected: 738
- Deferred unresolved: 51
- Remaining unreviewed or deferred: 9,408

## Persisted review data

- Structured review batches are stored under `manual_review/`.
- Completed files currently span `batch_001_...csv` through `batch_044_exact_page_v3.csv`, including the three batch-042 checkpoint files.
- `manual_review/deferred_unresolved.csv` contains records whose exact source evidence could not yet be resolved.
- `manual_review/queue_next_20.csv` and `manual_review/queue_next_200.csv` are resumable work queues.
- `manual_review/PROGRESS.md` records batch totals, cross-batch checks and the latest checkpoint.

Each reviewed CSV row is intended to preserve the project ID, source URL, review status, product form, paying customer, pain point, price/market evidence, competition, dependencies, manufacturing/after-sales/compliance/IP risk, license status, hero-image verdict, final bucket, verdict and evidence URLs.

## What is not yet a complete durable archive

- Full HTML bodies, screenshots and binary copies of every reviewed external page have **not** all been committed to this repository. The durable record currently consists mainly of source/evidence URLs plus structured review conclusions.
- External pages may change or disappear. Records that could not be reliably retrieved are kept in `deferred_unresolved.csv` rather than being guessed.
- Chat sandbox download links and locally generated XLSX files are temporary and must not be treated as the source of truth.
- The final consolidated V3 Excel has not been generated because the full 10,500-record review is unfinished.

## Resume procedure

1. Open PR #9 and use branch `agent/commercial-v3-strict-rebuild`.
2. Read `manual_review/PROGRESS.md` and collect all project IDs from `manual_review/batch_*.csv`.
3. Exclude IDs in completed batches and `deferred_unresolved.csv` from the active queue.
4. Continue from `queue_next_200.csv`, regenerating the queue when necessary.
5. Do not mark a row reviewed without page-level or explicitly labelled reliable cached/cross-checked evidence.
6. Update the batch CSV and `PROGRESS.md` in the same checkpoint commit.

This manifest is a recovery index, not evidence that all 10,500 records are complete.
