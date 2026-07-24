# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 80
- Strict commercial candidates: 0
- Watchlist: 10
- Market-reference cases: 24
- Rejected: 46
- Remaining: 10,420

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

## Batch 008 self-check

- Ten exact Tindie product pages were read; seller stores, product families, category/search pages, customer feedback and vendor specifications were used where relevant.
- The inaccessible `1201 Bandpass Filter Eurorack Synthesizer Module` page and the currently unretrievable `0-10v Analogue To RS485 Modbus RTU Converter DIN` page were not marked `已逐页阅读`, were not scored, and remain in the queue.
- No commodity item was promoted merely because it had a listed price or inventory. The GPS-disciplined 10MHz reference is the only new watchlist item because it is a complete professional-use instrument with a $99 price and real user feedback; key metrology evidence is still missing.
- FSC-BP119, the 0.23-inch micro-AMOLED supply product and the GPIO Labs TCXO were retained only as market-reference cases. Their value comes from product completion, specialized supply or an established RF product family—not a market gap in a bare module.
- Six commodity, resale or inventory-only items were rejected: the Vishay lot, FSC-BT909 module, ICStation 0–10V/4–20mA board, 0805 breakout, SSD1306 OLED module and generic screw assortment.
- One definite hero-image error was recorded: the FSC-BT909 row points to an `ESP32 CH340C WiFi Bluetooth Development Board` image and must not appear in the final workbook.
- One important source-data conflict was preserved rather than silently corrected: the Vishay product page says 4.7KΩ while the old title/URL says 47K.
- Project-specific verdict reasons were used; no forced score normalization or template-only commercial reason was added.

## Cross-batch self-check

- Reviewed IDs: 80 unique IDs across 80 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- PR #9 remains draft and unmerged.
