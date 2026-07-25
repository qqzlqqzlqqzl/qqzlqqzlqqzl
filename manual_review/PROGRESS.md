# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 170
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 57
- Rejected: 97
- Remaining: 10,330

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
| 014 | 10 | 0 | 0 | 6 | 4 | `batch_014_tindie_eurorack_optics_microdisplays_modules_and_retro.csv` |
| 015 | 10 | 0 | 1 | 6 | 3 | `batch_015_tindie_industrial_converter_retro_parts_microdisplays_rack_and_connectors.csv` |
| 016 | 10 | 0 | 0 | 5 | 5 | `batch_016_tindie_cables_lighting_modules_displays_retro_and_optics.csv` |
| 017 | 10 | 0 | 0 | 3 | 7 | `batch_017_tindie_arcade_oled_cables_wearables_touchscreen_led_and_devboards.csv` |

## Batch 017 self-check

- Ten records were checked using direct product-page reads where available; the PIC cable and the 0.39-inch micro-OLED use explicitly labelled manufacturer/catalogue cross-checks because their direct Tindie pages were incomplete or temporarily inaccessible.
- Seven entries were rejected: two commodity 0.96-inch OLED modules, one PIC cable, an Arduino tutorial PCB pack for RGB shades, a generic SBC touchscreen, an educational 10x10 RGB matrix kit and a narrow AVR/Arduino-compatible development board.
- Three entries are retained only as market references: the Namco 07xx replacement and two microdisplay specifications. They belong to previously identified long-tail repair and microdisplay supply families and do not increase the count of independent opportunities.
- The 10.6-inch touchscreen was not mistaken for a new product opportunity: the seller has zero recorded Tindie orders, the SKU is out of stock, and mature suppliers offer supported/certified alternatives at lower prices.
- Hero-image review identified one strong mismatch and one duplicate-model failure: the 1284 board image filename is `k6502_kit2.jpg`, while the 07xx and 04xx entries use the same image URL. Rows without a qualified microdisplay image remain explicitly unresolved rather than borrowing a neighbouring SKU image.
- Product-specific verdicts were written separately; no shared boilerplate score reason or forced score normalisation was introduced.

## Cross-batch self-check

- Reviewed IDs: 170 unique IDs across 170 rows. The queue workflow excludes IDs already present in every `batch_*.csv` before selecting the next records.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache, manufacturer-page and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No project is admitted to the strict shortlist without page-level evidence, and no strict candidate has been found in the first 170 records.
- Automatic image labels are not accepted as human verification; mismatches, duplicates and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
