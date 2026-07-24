# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 70
- Strict commercial candidates: 0
- Watchlist: 9
- Market-reference cases: 21
- Rejected: 40
- Remaining: 10,430

## Completed batches

| Batch | Records | Strict | Watchlist | Market reference | Rejected | File |
|---|---:|---:|---:|---:|---:|---|
| 001 | 10 | 0 | 2 | 3 | 5 | `batch_001_tindie_vertical_hardware.csv` |
| 002 | 10 | 0 | 6 | 3 | 1 | `batch_002_tindie_arcade_family_and_controls.csv` |
| 003 | 10 | 0 | 0 | 3 | 7 | `batch_003_tindie_modules_sensors_and_macropads.csv` |
| 004 | 10 | 0 | 0 | 4 | 6 | `batch_004_tindie_components_kits_and_rc2014.csv` |
| 005 | 10 | 0 | 0 | 3 | 7 | `batch_005_tindie_components_testgear_midi_and_audio.csv` |
| 006 | 10 | 0 | 0 | 4 | 6 | `batch_006_tindie_rf_eurorack_arcade_and_components.csv` |
| 007 | 10 | 0 | 1 | 1 | 8 | `batch_007_tindie_power_components_and_rf.csv` |

## Batch 007 self-check

- Ten original Tindie product pages were read; seller stores, reviews, category/search pages and related retired products were used where relevant.
- No item was promoted merely because it had a listed price, inventory count or a high-order seller.
- The Sourcery ±12V supply was retained only as a market-reference case: its ecosystem and documentation are commercially meaningful, but the $2 board is long sold out and one detailed review reports ripple/crosstalk and a missing mounting hole.
- The YIHANG 100W SDR T/R switch is the only new watchlist item. It is a complete-use-case product rather than a bare module, but it remains blocked by missing insertion-loss, isolation, VSWR, switching-time, hot-switching and full-power evidence.
- The MMM999 voice board, Synthrotek screws, generic grow COB, SMD cases, RJ45 component, PCB business-card service, portable soldering iron and ESPea LoRa shield were rejected as commodity modules/components, low-value accessories, custom services, resale items or obsolete-ecosystem add-ons.
- One definite hero-image error was recorded: `100 X Eurorack Module Screws` points to `PCB-4-Channel_Mixer.jpg`; it must not remain in the final workbook.
- Ambiguous product images were not falsely approved. They remain marked for final visual inspection where filenames are generic or nearby SKUs are visually similar.
- Project-specific verdict reasons were used; no forced score normalization or template-only commercial reason was added.

## Cross-batch self-check

- Reviewed IDs: 70 unique IDs across 70 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- PR #9 remains draft and unmerged.
