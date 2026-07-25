# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 140
- Strict commercial candidates: 0
- Watchlist: 15
- Market-reference cases: 43
- Rejected: 82
- Remaining: 10,360

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

## Batch 014 self-check

- Ten records were checked against live product pages or clearly identified canonical product-page caches, with seller stores, alternative storefronts and adjacent product families used for cross-checking. Cache-based reviews carry a distinct review status and are not presented as unrestricted live-page reads.
- Six rows are retained only as market references: a Eurorack band-pass filter, an astronomy filter, an 08xx arcade-chip replacement, two micro-OLED display configurations and a retro-computer NFC accessory. None qualifies as a strict candidate because the defensible value lies in a mature product family, specialised supply/test capability or a very small platform community rather than an isolated open design.
- Four rows are rejected: a Raspberry Pi Pico round-LCD HAT, a bulk Arduino-compatible shield, a two-dollar generic touch-switch pack and a mains smart-light switch with weak sales evidence and extreme certification/support burden.
- Product-family logic prevents double counting. The two micro-OLED rows are evidence for one near-eye-display supply family, while 08xx is another SKU in the previously identified long-tail arcade-repair family rather than a separate large opportunity.
- Hero-image review found three important issues: the 08xx row shares its automatic image with the 083 replacement; the 0.39-inch micro-OLED points to a BirdBath optics filename; and the 1.28-inch Pico HAT shares `ARDI BACK.png` with the previously rejected 1.14-inch LCD breakout. The 0.71-inch dual-display row has no qualified hero image. None of these was silently treated as verified.
- Every verdict separately records product form, opportunity family, customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, licence, image status and project-specific reasoning.

## Cross-batch self-check

- Reviewed IDs: 140 unique IDs across 140 rows.
- No inaccessible item is silently marked as a normal direct-page review; canonical-cache and cross-checked reviews use distinct statuses.
- Product-family variants are retained as evidence but are not counted as separate commercial opportunities.
- No forced score normalisation is used, and no project is admitted to the strict shortlist without page-level evidence.
- Automatic image labels are not accepted as human verification; mismatches and unresolved images remain explicitly marked.
- PR #9 remains draft and unmerged.
