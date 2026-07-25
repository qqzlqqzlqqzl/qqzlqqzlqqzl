# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 190
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 67
- Rejected: 107
- Remaining: 10,310

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

## Batch 019 self-check

- Eight records were read from usable original product pages. The power-inductor pack used an explicitly labelled product-cache and seller-page cross-check because the current page cache missed; the round TFT used product indexes, its duplicate listing and the seller catalogue because the page was anti-bot blocked; the iLens page returned 502 and was cross-checked using the exact product name, image filename, seller catalogue and current OEM/supply pages. These statuses are recorded separately and are not presented as normal direct-page reviews.
- Seven records were rejected: an incomplete oil-immersed dummy-load PCB kit based on a mature DIY method, a 2-dollar power-inductor pack, Soviet old-stock regulator chips, a mature Raspberry Pi ADC HAT, a standard round TFT component, standard B10K potentiometers and a standard integrated-magnetics RJ45 connector.
- Three records are retained only as market references: the iLens finished OEM smart-glasses product, the 054574 item inside the existing arcade long-tail replacement family, and the 1.03-inch micro-OLED inside the established microdisplay/driver/optics supply family. None is counted as a new independent commercial opportunity.
- Hero-image review found one decisive high-risk failure: the round-TFT image filename says OLED and the same URL is reused for a later 0.99-inch record. The ADC HAT image predates the stated v3.0 redesign; the iLens image is not proven to be the exact delivered version; generic component photos remain unresolved. No automatic image label was promoted to human verification.
- Each verdict is project-specific and separately records product form, customer, pain point, price/evidence, market crowding, dependencies, manufacturing, after-sales, compliance, licensing and image status.

## Cross-batch self-check

- Reviewed IDs: 190 unique IDs across 190 rows. The queue workflow excludes exact project IDs already present in every `batch_*.csv`; semantic duplicate products and interface/specification variants are additionally collapsed during human review.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache, seller-directory, manufacturer/OEM-page and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No project is admitted to the strict shortlist without page-level evidence, and no strict candidate has been found in the first 190 records.
- Automatic image labels are not accepted as human verification; mismatches, duplicates, version risks and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
