# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 90
- Strict commercial candidates: 0
- Watchlist: 11
- Market-reference cases: 28
- Rejected: 51
- Remaining: 10,410

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
| 008 | 10 | 0 | 1 | 3 | 6 | `batch_008_tindie_components_wireless_frequency_and_displays.csv` |
| 009 | 10 | 0 | 1 | 4 | 5 | `batch_009_tindie_displays_components_rf_and_bms.csv` |

## Batch 009 self-check

- Ten exact or current canonical Tindie product pages were read. Seller stores, related product families, inventory, prices and direct category/search evidence were checked where available.
- The old `0.49 Inch Micro OLED Birdbath AR Glasses Pglass` URL now resolves through a current canonical Display Components product page. This source change is recorded instead of pretending the old URL was independently verified.
- The teTra 24S–96S high-voltage BMS main board is the only new watchlist item. It has a clear professional use case and an $860 price, but both main and sub boards are out of stock and no sales, reviews, specifications, safety tests or certification evidence were found.
- Four specialized display items were retained only as market-reference cases: the 0.49-inch Birdbath optics module, 0.62-inch Micro OLED, 0.8-inch transparent LCD and 0.49-inch 3000-nit Micro OLED. They represent specialized component-supply models, not independent open-hardware opportunities.
- Five commodity or non-product opportunities were rejected: the 1.28-inch round LCD breakout, acupuncture needles, 100mW serial RF module, USB-A connector lot and ten-pack 1602 I2C LCD modules.
- One definite hero-image problem was added: the 100mW RF data module points to an `Irrigation Xinjiang` application-scene image rather than the module body.
- Two records from the previous queue remain unreviewed because their product pages were inaccessible: `1201 Bandpass Filter Eurorack Synthesizer Module` and `0-10v Analogue To RS485 Modbus RTU Converter DIN`. Neither is marked page-reviewed or scored.
- Product-specific verdict reasons were used. Similar Micro OLED variants are grouped into one opportunity family and are not counted as separate commercial opportunities.

## Cross-batch self-check

- Reviewed IDs: 90 unique IDs across 90 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- PR #9 remains draft and unmerged.
