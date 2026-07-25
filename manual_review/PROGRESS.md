# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 150
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 49
- Rejected: 85
- Remaining: 10,350

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

## Batch 015 self-check

- Ten records were checked against directly indexed product pages or explicitly labelled original-page index caches, with seller catalogues, alternative storefronts and direct competitors used for cross-checking. Records whose exact live page could not be fully retrieved are not described as unrestricted direct-page reads.
- The 0-10V-to-RS485 DIN converter is the only new watchlist item. Its customer and industrial pain point are credible, but price, orders, isolation, accuracy, EMC evidence and a complete manual are missing; mature analogue-to-Modbus competitors prevent a premature high-value verdict.
- Six rows are retained only as market references: three microdisplay/near-eye-optics configurations, the 083 arcade-chip replacement, a 10-inch rack blank and another near-eye HMD lens-group entry. Product-family logic prevents these specifications and SKUs from inflating the number of independent opportunities.
- Three rows are rejected: a discontinued Cherry key-switch stock pack, a commodity Gigabit MagJack and a standard 5.08-mm pluggable terminal-block pack. These are inventory/channel businesses or mature industrial components rather than reproducible open-hardware product opportunities.
- Hero-image checking found one explicit mismatch: the terminal-block row points to an Epson PVC card-tray filename. The 083 image is shared with other replacement-family rows, the two exact optics entries have no qualified image, and generic filenames remain unresolved rather than being silently accepted.
- Every verdict separately records product form, opportunity family, customer, pain point, price or missing-price status, market evidence, crowding, dependency, manufacturing, after-sales, compliance, licence, image status and project-specific reasoning.

## Cross-batch self-check

- Reviewed IDs: 150 unique IDs across 150 rows.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No forced score normalisation is used, and no project is admitted to the strict shortlist without page-level evidence.
- Automatic image labels are not accepted as human verification; mismatches and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
