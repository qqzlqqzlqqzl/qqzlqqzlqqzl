# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 130
- Strict commercial candidates: 0
- Watchlist: 15
- Market-reference cases: 37
- Rejected: 78
- Remaining: 10,370

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
| 011 | 10 | 0 | 1 | 3 | 6 | `batch_011_tindie_storage_displays_components_imu_rack_and_prop.csv` |
| 012 | 10 | 0 | 1 | 3 | 6 | `batch_012_tindie_rc_components_retro_rf_and_displays.csv` |
| 013 | 10 | 0 | 0 | 1 | 9 | `batch_013_tindie_components_displays_rack_mounts_and_camera.csv` |

## Batch 013 self-check

- Ten records were checked against live Tindie product pages or clearly identified canonical product-page index caches together with seller stores and adjacent product families. Four rows whose live pages returned access/cache failures are explicitly labelled `已逐页阅读（原页索引缓存）`; they are not silently represented as direct live-page reads.
- One item was retained only as a market reference: the 120 mm fan mount for 10-inch racks. It is a complete use-oriented physical accessory with a clear cooling pain point and a coherent seller family of 10-inch/19-inch device mounts. It remains a reference rather than a strict candidate because it is easy to copy, the licence on the linked Printables design could not be confirmed, and the defensible value lies in continuous device-fit coverage rather than this one model.
- Nine records were rejected: a Grove encoder bulk pack, two low-price component packs, a generic ST7789 LCD breakout, three RJ45/MagJack catalogue components, a commodity SSD1306 OLED and a stale USB camera module. Demand may exist, but product value comes from established distribution/manufacturing catalogues rather than an open-hardware opportunity suitable for a small entrant.
- Product-family logic prevents double counting: the three RJ45 rows are evidence for mature connector-manufacturer catalogues rather than three opportunities; EL817 and buzzers are component-resale evidence; the LCD and OLED rows belong to already-saturated generic display-module families.
- Hero-image checks found five concrete defects or high-risk mismatches: Grove Encoder points to `PWM to Voltage Converter.1.JPG`; the 1.14-inch LCD shares `ARDI BACK.png` with a different round-LCD HAT; the 0.96-inch OLED uses an `alicdn.com` rating image; the 2x4 MagJack image filename names `ARJC02-111008B` while the product is `YKG-832419NL`; and the USB camera points to `Comprehensive development-board-for-iot (2).jpg`. The 0879 connector image is too generically named to confirm and remains unapproved.
- Every verdict is project-specific and separately records customer, pain point, price, seller evidence, market crowding, dependency, manufacturing, after-sales, compliance, licence and image status.

## Cross-batch self-check

- Reviewed IDs: 130 unique IDs across 130 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache reviews carry a distinct status.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- The inaccessible `1201 Bandpass Filter Eurorack Synthesizer Module`, `0-10v Analogue To RS485 Modbus RTU Converter DIN`, Cherry M81F keyswitch and M31 astro-filter pages remain unreviewed and unscored.
- The `08Xx Replacement`, 0.39-inch, 0.71-inch and 0.6-inch microdisplay pages also remain unreviewed because their exact pages were not reliably retrievable; related products were not substituted.
- The 1.28-inch round LCD HAT and ESPea Dual Shield remain in the pending queue for a later run; they were not scored from names or shared images alone.
- PR #9 remains draft and unmerged.
