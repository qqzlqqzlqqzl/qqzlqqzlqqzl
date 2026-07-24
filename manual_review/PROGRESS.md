# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 60
- Strict commercial candidates: 0
- Watchlist: 8
- Market-reference cases: 20
- Rejected: 32
- Remaining: 10,440

## Completed batches

| Batch | Records | Strict | Watchlist | Market reference | Rejected | File |
|---|---:|---:|---:|---:|---:|---|
| 001 | 10 | 0 | 2 | 3 | 5 | `batch_001_tindie_vertical_hardware.csv` |
| 002 | 10 | 0 | 6 | 3 | 1 | `batch_002_tindie_arcade_family_and_controls.csv` |
| 003 | 10 | 0 | 0 | 3 | 7 | `batch_003_tindie_modules_sensors_and_macropads.csv` |
| 004 | 10 | 0 | 0 | 4 | 6 | `batch_004_tindie_components_kits_and_rc2014.csv` |
| 005 | 10 | 0 | 0 | 3 | 7 | `batch_005_tindie_components_testgear_midi_and_audio.csv` |
| 006 | 10 | 0 | 0 | 4 | 6 | `batch_006_tindie_rf_eurorack_arcade_and_components.csv` |

## Batch 006 self-check

- Ten rows were reviewed from their original Tindie product pages, with seller, review, competing-product or category pages used where available.
- The inaccessible `1201 Bandpass Filter` page was not falsely marked as reviewed and remains in the queue.
- No row was promoted merely because it had a price, stock count or an established seller.
- The three Caius Arcade rows were merged conceptually into the already identified old-arcade replacement family; they were not counted as independent opportunities.
- The validated Sourcery Eurorack power board was retained only as a market-reference case because its value comes from a 30-product ecosystem, documentation and reputation, not an isolated $8.50 PCB.
- Generic YIHANG/Cirket wideband amplifiers, the generic 100W VHF amplifier, the standard speaker and the Eurorack blank panel were rejected.
- Hero-image issues were explicitly recorded: the 12HP blank panel points to a `PCB-4-Channel_Mixer` image; the speaker points to an IoT development-board image; the 100W VHF amplifier shares its image URL with a grow-light SKU. These images cannot remain in the final workbook.
- Project-specific verdict reasons were used; no forced score normalization or template-only commercial reason was added.

## Cross-batch self-check

- Reviewed IDs: 60 unique IDs across 60 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- PR #9 remains draft and unmerged.
