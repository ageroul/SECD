# SECD — String Ensemble Chord Dataset

The SECD dataset is introduced in the accompanying paper (see citation below).

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

Dataset access instructions and download links will be provided upon paper publication.
