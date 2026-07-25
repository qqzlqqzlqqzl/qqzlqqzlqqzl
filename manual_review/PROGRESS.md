# V3 manual page-review progress

Updated: 2026-07-25

## Current totals

- Raw records: 10,500
- Page/source-reviewed records: 290
- Strict commercial candidates: 0
- Watchlist: 17
- Market-reference cases: 103
- Rejected: 170
- Remaining: 10,210

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
| 021A | 10 | 0 | 0 | 3 | 7 | `batch_021a_tindie_wires_adc_displays_signal_conditioning_and_rf.csv` |
| 021B | 10 | 0 | 0 | 3 | 7 | `batch_021b_tindie_adc_oscillators_microdisplays_oled_cables_and_rpi.csv` |
| 022A | 10 | 0 | 0 | 3 | 7 | `batch_022a_tindie_connectors_supplies_rpi_adc_motor_microdisplay_and_arcade.csv` |
| 022B | 10 | 0 | 0 | 4 | 6 | `batch_022b_tindie_surplus_microdisplays_cables_round_tft_led_controls_and_arcade.csv` |
| 023A | 10 | 0 | 1 | 4 | 5 | `batch_023a_tindie_microdisplays_rpi_rf_led_arcade_antenna_camera.csv` |
| 023B | 10 | 0 | 0 | 4 | 6 | `batch_023b_tindie_microdisplay_power_components_cables_testaccessory_hats.csv` |
| 024 | 20 | 0 | 0 | 9 | 11 | `batch_024_tindie_oled_components_debug_tools_rack_and_neopixel.csv` |

## Batch 024 self-check

- All 20 records were reviewed against exact Tindie product-page caches or exact product/store pages; no title-only record was silently promoted to ordinary direct-page review.
- Four microdisplay records were folded into the existing microdisplay/driver/near-eye-optics supply family and do not create four independent opportunities.
- Generic OLED/TFT screens, pogo pins, pin headers, optocouplers, an RGB strip and old ADC breakouts were rejected as mature commodity categories rather than scored as new opportunities.
- The FPC passthrough board, 12-channel 12V level shifter, PS4 USB-C cable, differential NeoPixel transceiver and 10-inch patch panel remain product-family references; their value comes from a catalog, compatibility data or system documentation, not from an isolated low-price PCB or cable.
- The Soviet 142EN3 record was confirmed as a one-off vintage inventory sale at 27 USD with one unit left, so it is not treated as a reproducible manufacturing opportunity.
- Hero-image review identified explicit mismatches for the 0.96-inch OLED, pin headers, round TFT, 0.5-inch micro-OLED, 1.18-inch round OLED and I2C ADC. Automatic labels were not inherited as human verification.

## Cross-batch self-check

- Reviewed IDs: 290 unique IDs across 290 rows. Exact project IDs are excluded from refreshed queues, while semantic duplicate specifications and product-family variants are collapsed during review.
- No inaccessible item is silently marked as an ordinary direct-page review; exact-cache and cross-checked reviews use explicit statuses.
- Product-family variants remain evidence and are not counted as separate commercial opportunities.
- No project has entered the strict shortlist without page-level evidence; no strict candidate has been found in the first 290 records.
- Automatic image labels are not accepted as human verification; mismatches, duplicate/version risks and unresolved images remain marked.
- PR #9 remains draft and unmerged.
