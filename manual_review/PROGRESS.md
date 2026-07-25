# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 210
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 73
- Rejected: 121
- Remaining: 10,290

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
| 018 | 10 | 0 | 0 | 7 | 3 | `batch_018_tindie_arcade_microdisplays_supplies_frequency_rf_connectors_and_eurorack.csv` |
| 019 | 10 | 0 | 0 | 3 | 7 | `batch_019_tindie_qrp_components_rpi_displays_arcade_and_connectors.csv` |
| 020 | 20 | 0 | 0 | 6 | 14 | `batch_020_tindie_components_microdisplays_props_and_adapters.csv` |

## Batch 020 self-check

- All 20 records were read from exact product-page caches and supporting seller/catalogue pages after direct page fetches returned cache misses; the review status records this evidence path and does not present it as an unrestricted live-page fetch.
- Six records are retained only as market references: five microdisplay specifications are collapsed into the existing microdisplay/driver/optics supply family, and the assembled 10-LED EMF prop is retained as an IP-dependent high-value prop productisation example.
- Fourteen records are rejected as commodity buzzers, USB/IR adapters, standard displays, GPIO test boards, NOS Soviet components, spring antennas, connector catalogue parts or low-value breakout boards.
- Product-family variants are not counted as independent opportunities: the microdisplay listings, NifteeCircuits package breakouts, Electronics16 NOS parts and Casco Logix RF adapters are explicitly collapsed into existing families.
- Hero-image checks found decisive or high-risk mismatches for the 0.99-inch round TFT (`OLED` filename), the 868 MHz spring antenna (`lora1280.jpg`) and the 0.5-inch microdisplay (`OPTICAL-PRISM-12X`). Records without qualified images remain without images; no neighbouring specification image was substituted.
- Each row separately records product form, family model, customer, pain point, price/evidence, crowding, dependencies, manufacturing, after-sales, compliance, licensing and image status. No template-only verdict was used.

## Cross-batch self-check

- Reviewed IDs: 210 unique IDs across 210 rows. The queue workflow excludes exact project IDs already present in every `batch_*.csv`; semantic duplicate products and interface/specification variants are additionally collapsed during human review.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache, seller-directory, manufacturer/OEM-page and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No project is admitted to the strict shortlist without page-level evidence, and no strict candidate has been found in the first 210 records.
- Automatic image labels are not accepted as human verification; mismatches, duplicates, version risks and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
