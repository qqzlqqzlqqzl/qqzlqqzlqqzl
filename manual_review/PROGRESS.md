# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 100
- Strict commercial candidates: 0
- Watchlist: 13
- Market-reference cases: 30
- Rejected: 57
- Remaining: 10,400

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
| 010 | 10 | 0 | 2 | 2 | 6 | `batch_010_tindie_repair_parts_modules_rf_testgear_and_displays.csv` |

## Batch 010 self-check

- Ten current or canonical Tindie product pages were read, together with seller stores, reviews, product families and category/search evidence where available.
- Two records entered the watchlist: ALFTEL's 1000–1400 MHz 14 dBi helix antenna and EastwoodLab's 0.015% / 10 ppm programmable resistance module. Both have clear professional use and high prices, but neither has enough product-specific sales, independent validation or open-license evidence for strict-candidate status.
- Two records were retained only as market references: the `051550` arcade custom-IC replacement is additional evidence for an already-counted long-tail repair-product family, while the 1016 LED message board demonstrates better kit/assembled-product packaging but remains a crowded hobbyist product.
- Six records were rejected: a copied Surface Pro replacement-screen listing, a $1 0402 breakout, a commodity 0.42-inch SSD1306 OLED module, a generic MCP3008 Raspberry Pi HAT, an uncertified $200 mains smart switch with almost no sales evidence, and another standard round AMOLED component already represented by the display-supply family.
- The Surface Pro LCD page includes an Amazon ASIN, generic best-seller rank and incompatible-looking catalogue wording, supporting classification as third-party repair-part resale rather than an original hardware design.
- The Raspberry Pi ADC HAT has two positive reviews and comes from a seller with more than 1,200 orders, but this validates the seller's mature HAT/product-family operation rather than proving a new opportunity in the already-saturated MCP3008 HAT category.
- The precision-resistance module was not treated as a generic small board: its relay-resistor network, four-wire output, DIN mounting, isolated RS-232/RS-485/CAN options, 10 mΩ steps and stated accuracy were read from the actual page. It remains watchlist because calibration traceability, long-term drift, customer evidence and commercial-reuse license are missing.
- Every verdict reason is project-specific. Display variants and arcade-replacement variants are linked to previously identified opportunity families and are not counted as new independent opportunities.
- Hero-image verdicts remain explicit visual-review states. No automatically selected image was silently upgraded to fully verified status.

## Cross-batch self-check

- Reviewed IDs: 100 unique IDs across 100 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- The previously inaccessible `1201 Bandpass Filter Eurorack Synthesizer Module` and `0-10v Analogue To RS485 Modbus RTU Converter DIN` remain unreviewed; they are not scored.
- PR #9 remains draft and unmerged.
