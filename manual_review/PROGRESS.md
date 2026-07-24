# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 40
- Strict commercial candidates: 0
- Watchlist: 8
- Market-reference cases: 13
- Rejected: 19
- Remaining: 10,460

## Completed batches

| Batch | Records | Strict | Watchlist | Market reference | Rejected | File |
|---|---:|---:|---:|---:|---:|---|
| 001 | 10 | 0 | 2 | 3 | 5 | `batch_001_tindie_vertical_hardware.csv` |
| 002 | 10 | 0 | 6 | 3 | 1 | `batch_002_tindie_arcade_family_and_controls.csv` |
| 003 | 10 | 0 | 0 | 3 | 7 | `batch_003_tindie_modules_sensors_and_macropads.csv` |
| 004 | 10 | 0 | 0 | 4 | 6 | `batch_004_tindie_components_kits_and_rc2014.csv` |

## Batch 004 self-check

- All 10 rows have `review_status=已逐页阅读` and page/store/competition evidence URLs.
- No duplicate `project_id` appears within batch 004 or batches 001–003.
- No kit or generic module entered the strict shortlist merely because it was sold on Tindie.
- Component packs, commodity sensors, a generic PIR board, a commodity touch monitor and low-value modules were rejected.
- Four rows were retained only as market-reference cases: the Terrain-Tronics tabletop-terrain product family, the open-source function-generator kit, the historical PixelFlood family and the mature RC2014/RCBus ecosystem.
- The Terrain-Tronics SKU was explicitly merged into the previously identified tabletop-terrain opportunity family rather than counted as a new independent opportunity.
- Three clear hero-image problems were identified: the potentiometer row used a Christmas-tree image; the vibration-sensor row duplicated the PIR image; the 11.6-inch monitor row used a Raspberry Pi mini-PC-case image.
- Hero images marked `基本匹配` still require final-workbook visual sampling; automatic image flags are not treated as human approval.
- Verdict reasons are project-specific and no forced score normalization is used.

PR #9 remains draft and unmerged.
