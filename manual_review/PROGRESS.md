# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page-reviewed records: 110
- Strict commercial candidates: 0
- Watchlist: 14
- Market-reference cases: 33
- Rejected: 63
- Remaining: 10,390

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

## Batch 011 self-check

- Ten current or canonical product pages were read together with seller stores, adjacent product families and category or external-supplier evidence where useful.
- One record entered the watchlist: the 10-inch 10U open-frame rack. It is an independent physical product with a clear compact-homelab use case, but the page exposes no order or review evidence and the seller currently shows only one product; shipping, compatibility and load validation remain unresolved.
- Three records were retained only as market references: the 0.23-inch and 0.6-inch micro-OLED items are two variants of the same professional near-eye-display supply family, while the 10-LED EMF-meter PCB shows a fan-prop product ladder from a $10 PCB to $229-$289 assembled replicas. None is counted as a new strict opportunity.
- Six records were rejected: engineering pill boxes, a standard round TFT/CTP, a low-cost 10G MagJack, an obsolete generic 10-DOF breakout, an IP66 box plus perfboard kit and a $1 1206 breakout.
- The two micro-display rows are linked to one opportunity family instead of being counted as independent opportunities. The 1206 breakout is explicitly linked to the previously rejected 0402/0603/0805 package-breakout family.
- The round TFT and micro-display hero-image verdicts preserve model/size ambiguity. The 0.6-inch micro-OLED remains `无合格英雄图`; no related display image was substituted.
- The EMF-meter row distinguishes the $10 PCB from the assembled prop images and records the entertainment-IP risk rather than treating it as a measurement instrument.
- Every verdict reason is project-specific and the final bucket is consistent with the recorded market evidence, dependency and risk fields.

## Cross-batch self-check

- Reviewed IDs: 110 unique IDs across 110 rows.
- Every reviewed row records `review_status`, product form, opportunity family, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- No page-inaccessible item is marked `已逐页阅读`.
- Product-family variants are retained for evidence but are not counted as separate commercial opportunities.
- The inaccessible `1201 Bandpass Filter Eurorack Synthesizer Module` and `0-10v Analogue To RS485 Modbus RTU Converter DIN` remain unreviewed and unscored.
- The Cherry M81F keyswitch and M31 astro-filter pages also remain unreviewed because the exact product pages were not reliably retrievable in this run.
- PR #9 remains draft and unmerged.
