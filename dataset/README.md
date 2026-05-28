# SECD — String Ensemble Chord Dataset

The official full SECD dataset release is archived on Zenodo:

https://doi.org/10.5281/zenodo.15547207

The accompanying SECD paper is pending publication. Final paper metadata will be added when available.

## Format

Each sample is a short audio clip of a polyphonic string ensemble performing a chord.
Metadata is provided as CSV files, one per subset, with the following fields:

| Field | Description |
|---|---|
| `wav_stem` | Filename stem of the audio clip |
| `group` | Dataset subset (e.g. `harmonic_intervals_loose`, `triads_loose`, …) |
| `ensemble_size` | Number of instruments: `duo`, `trio`, or `quartet` |
| `instrument_*` | Per-instrument technique labels |

## Access

Use the Zenodo archive above as the official full SECD release.

The GitHub repository contains a separate Mini-SECD demo package at `mini_secd_demo/`. Mini-SECD is intended for lightweight notebook execution and pipeline validation only; it is not the full dataset and should not be used to reproduce or compare the reported benchmark metrics.
