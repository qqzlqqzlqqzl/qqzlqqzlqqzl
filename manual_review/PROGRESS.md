# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 160
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 54
- Rejected: 90
- Remaining: 10,340

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

## Batch 016 self-check

- Ten records were checked against indexed product pages, seller catalogues and category/competitor pages. The 10W LED light and the 0.72-inch HMD lens-group entry have incomplete exact-page text and are explicitly labelled as cross-checked rather than unrestricted direct-page reads.
- Five commodity or mature items were rejected: a $4.95 SMA cable pack, a weakly documented 24V LED light, an Arduino MCP3208 ADC Shield, a paused-store IR relay bare board and a standard 1.22-inch round TFT.
- Five rows are retained only as market references: three microdisplay specifications, one HMD optics configuration and the Namco 06xx replacement. They belong to previously identified product families and do not increase the count of independent opportunities.
- Hero-image review found two strong faults: the 1.22-inch TFT points to a filename containing `OLED`, and the 0.5-inch bare microdisplay points to a BirdBath-lens image. The 06xx and 07xx replacement rows share the same image URL, so neither image is treated as exact-model verification.
- Every verdict separately records product form, opportunity family, customer, pain point, price or missing-price status, evidence, crowding, dependency, manufacturing, after-sales, compliance, licence, hero-image status and project-specific reasoning.

## Cross-batch self-check

- Reviewed IDs: 160 unique IDs across 160 rows.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No forced score normalisation is used, and no project is admitted to the strict shortlist without page-level evidence.
- Automatic image labels are not accepted as human verification; mismatches and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
