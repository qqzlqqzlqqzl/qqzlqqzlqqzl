# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 180
- Strict commercial candidates: 0
- Watchlist: 16
- Market-reference cases: 64
- Rejected: 100
- Remaining: 10,320

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

## Batch 018 self-check

- Eight records were read from usable original product pages. The GPS L5 filter and 1–20HP blind panel used explicitly labelled Tindie product-index, seller-directory and catalogue cross-checks because their original page fetches temporarily returned errors.
- Three records were rejected: standard antistatic bags, a discontinued HP E1938A OCXO resale item and a duplicate/mature 12-channel infrared relay bare board.
- Seven records are retained only as market references. The Namco 04xx replacement belongs to the existing arcade-repair family; the GPS filter belongs to GPIO Labs' 129-SKU RF catalogue; the miniature cable and Eurorack panel demonstrate accessory-catalogue methods rather than defensible standalone opportunities.
- The three micro-OLED listings were not counted as three independent opportunities. Two Hicenda listings use the same ECX331DB-6 panel with CVBS versus HDMI controllers, while the 0.4-inch listing is another specification inside an already established microdisplay/driver/optics supply family.
- Page credibility was checked rather than copied blindly: the 0.4-inch micro-OLED title says 1440×1080 while its body claims 1920×1080, and the GPS L5 price appears as 63 dollars in one current index and 51 dollars in the seller catalogue.
- Hero-image review found two decisive failures: the antistatic-bag image filename points to an LH12A laser-holder product, and the 04xx entry reuses the same automatic image as the earlier 07xx record. Rows without qualified microdisplay images remain unresolved; generic filenames are not treated as human verification.
- Each verdict is project-specific and separately records product form, customer, pain point, evidence, crowding, dependencies, manufacturing, after-sales, compliance, licensing and image status.

## Cross-batch self-check

- Reviewed IDs: 180 unique IDs across 180 rows. The queue workflow excludes exact project IDs already present in every `batch_*.csv`; semantic duplicate products and interface/specification variants are additionally collapsed during human review.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache, seller-directory, manufacturer-page and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No project is admitted to the strict shortlist without page-level evidence, and no strict candidate has been found in the first 180 records.
- Automatic image labels are not accepted as human verification; mismatches, duplicates and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
