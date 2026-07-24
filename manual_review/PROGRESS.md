# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page-reviewed records: 120
- Strict commercial candidates: 0
- Watchlist: 15
- Market-reference cases: 36
- Rejected: 69
- Remaining: 10,380

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

## Batch 012 self-check

- Ten product pages or their reliably indexed canonical product records were read together with seller stores and adjacent product families. Items that remained inaccessible or model-ambiguous were not included simply to fill the batch.
- One record entered the watchlist: the Atari 400 1056K memory upgrade. It has a clear compatibility pain point, a $77.42 price, a seller with 273 orders and a coherent Atari upgrade/reproduction family, but the total market is small, installation requires disassembly and soldering, and no reusable design licence was found.
- Three records were retained only as market references: the 1/10 RC F1 rain light demonstrates a validated low-price hobby-accessory product family; the 1268 MHz RF filter demonstrates a measured frequency-product family; the $558 micro-OLED/BirdBath module is another specification in the already-linked near-eye display supply family and is not counted as a separate opportunity.
- Six records were rejected: flickering 3 mm LEDs, a PoE+ MagJack, transparent potentiometers, CAT5e/CAT6 crimp plugs, a 490 MHz spring antenna and a 0.91-inch SSD1306 breakout. Each is a commodity component, reseller item or mature generic module whose apparent value comes from the seller's broader catalogue rather than a defensible standalone product.
- Hero-image checks found three concrete defects: the transparent-potentiometer row points to a `10 LED EMF PCB` image; the spring-antenna row points to `lora1280.jpg`; the 0.91-inch SSD1306 row points to a 2.26-inch character-OLED image. These are explicitly marked as mismatches instead of being accepted by the earlier automatic image status.
- Product-family logic prevents double counting: the 0.49-inch BirdBath item remains part of the existing microdisplay/near-eye-optics family; the low-price connectors, antennas and display breakouts remain component-directory evidence rather than new opportunities.
- Every verdict reason is project-specific and separately records customer, pain point, price, seller evidence, crowding, dependency, manufacturing, after-sales, compliance, licence and hero-image status.

## Cross-batch self-check

- Reviewed IDs: 120 unique IDs across 120 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- The inaccessible `1201 Bandpass Filter Eurorack Synthesizer Module`, `0-10v Analogue To RS485 Modbus RTU Converter DIN`, Cherry M81F keyswitch and M31 astro-filter pages remain unreviewed and unscored.
- The `08Xx Replacement`, 0.39-inch and 0.71-inch microdisplay pages also remain unreviewed in this batch because their exact pages were not reliably retrievable; related products were not substituted.
- PR #9 remains draft and unmerged.
