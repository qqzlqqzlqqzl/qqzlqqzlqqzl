# V3 manual page-review progress

Updated: 2026-07-24

## Current totals

- Raw records: 10,500
- Page-reviewed records: 50
- Strict commercial candidates: 0
- Watchlist: 8
- Market-reference cases: 16
- Rejected: 26
- Remaining: 10,450

## Completed batches

| Batch | Records | Strict | Watchlist | Market reference | Rejected | File |
|---|---:|---:|---:|---:|---:|---|
| 001 | 10 | 0 | 2 | 3 | 5 | `batch_001_tindie_vertical_hardware.csv` |
| 002 | 10 | 0 | 6 | 3 | 1 | `batch_002_tindie_arcade_family_and_controls.csv` |
| 003 | 10 | 0 | 0 | 3 | 7 | `batch_003_tindie_modules_sensors_and_macropads.csv` |
| 004 | 10 | 0 | 0 | 4 | 6 | `batch_004_tindie_components_kits_and_rc2014.csv` |
| 005 | 10 | 0 | 0 | 3 | 7 | `batch_005_tindie_components_testgear_midi_and_audio.csv` |

## Batch 005 self-check

- All 10 rows were reviewed using the original Tindie product page plus store, review, manufacturer or competition pages where available.
- The inaccessible `1201 Bandpass Filter` product page was not falsely marked reviewed; it remains in the queue for a later retry. The accessible `10HP 3U DIY Eurorack Blank Panel` was reviewed instead.
- No duplicate `project_id` appears in batch 005 or batches 001–004.
- No standard component, Arduino shield, generic RF/audio module or accessory entered the strict shortlist merely because it was sold by an established seller.
- Three rows were retained only as market-reference cases: the low-cost calibrated OCXO/test-equipment-upgrade model, the existing arcade-replacement family, and the MIDI Thru product-family model.
- The `007340` row was merged conceptually into the previously identified arcade replacement opportunity family rather than counted as an independent opportunity.
- The resistor assortment, Arduino Shield kit, RJ45 connector, generic LNA, high-speed DAC breakout, TDA7498 amplifier board and Eurorack blank panel were rejected.
- One clear hero-image problem was confirmed: the 10HP blank-panel row used a 4-channel-mixer PCB image and must be replaced. Other images remain `基本匹配` pending final-workbook visual sampling.
- Verdict reasons are project-specific; no forced score normalization or template-only score reason was used.

## Cross-batch self-check

- Reviewed IDs: 50 unique IDs across 50 rows.
- Every reviewed row records `review_status`, product form, paying customer, pain point, price, market evidence, crowding, dependency, manufacturing, after-sales, compliance, license, hero-image verdict, final bucket, project-specific verdict reason and evidence URLs.
- PR #9 remains draft and unmerged.
