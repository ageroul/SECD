#!/usr/bin/env python3
"""
Create a compact, real Mini-SECD demo from the full SECD cache.

This exporter copies only existing mel .npy tensors from the full dataset.  The
source composition CSVs are not present in this SECD copy, so CSV rows are
reconstructed from the real cache path, cache stem, and notebook-observed schema
conventions.  WAV files are tiny valid silent placeholders unless real WAVs are
found under the full dataset root.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import random
import re
import shutil
import struct
import wave
from collections import Counter, defaultdict
from pathlib import Path


GROUP_CSVS = {
    "harmonic_intervals_loose": [
        "cello_viola_loose",
        "cello_violin_loose",
        "viola_violin_loose",
    ],
    "harmonic_intervals_strict": [
        "cello_viola_strict",
        "cello_violin_strict",
        "viola_violin_strict",
    ],
    "triads_loose": [
        "triads_major_loose",
        "triads_minor_loose",
        "triads_diminished_loose",
        "triads_augmented_loose",
    ],
    "triads_strict": [
        "triads_major_strict",
        "triads_minor_strict",
        "triads_diminished_strict",
        "triads_augmented_strict",
    ],
    "7th_chords_loose": [
        "major_seventh_loose",
        "minor_seventh_loose",
        "dominant_seventh_loose",
        "half_diminished_seventh_loose",
    ],
    "7th_chords_strict": [
        "major_seventh_strict",
        "minor_seventh_strict",
        "dominant_seventh_strict",
        "half_diminished_seventh_strict",
    ],
}

INSTRUMENTS_BY_KIND = {
    "duo": ["cello", "viola"],
    "trio": ["cello", "viola", "violin1"],
    "quartet": ["cello", "viola", "violin2", "violin1"],
}

TECHNIQUE_CODE_TO_NAME = {
    "08": "arco-minor-trill",
    "09": "arco-normal",
    "10": "arco-sul-ponticello",
    "11": "arco-sul-tasto",
    "14": "arco-tremolo",
    "15": "arco-col-legno-battuto",
    "16": "arco-harmonic",
    "17": "non-vibrato",
    "19": "pizz-normal",
    "21": "natural-harmonic",
}

TECHNIQUE_TO_FAMILY = {
    "arco-normal": "bowed",
    "arco-minor-trill": "bowed",
    "arco-sul-ponticello": "bowed",
    "arco-sul-tasto": "bowed",
    "arco-tremolo": "bowed",
    "non-vibrato": "bowed",
    "arco-col-legno-battuto": "col_legno",
    "arco-harmonic": "harmonic",
    "natural-harmonic": "harmonic",
    "pizz-normal": "plucked",
}

DYNAMIC_CODE_TO_NAME = {
    "02": "pianissimo",
    "03": "piano",
    "04": "fortissimo",
    "05": "mezzo-forte",
    "06": "mezzo-piano",
    "07": "forte",
    "08": "piano",
    "09": "forte",
    "10": "mezzo-forte",
    "14": "fortissimo",
    "15": "pianissimo",
    "17": "mezzo-piano",
    "19": "piano",
}


def ensemble_kind(group: str) -> str:
    if group.startswith("harmonic_intervals"):
        return "duo"
    if group.startswith("triads"):
        return "trio"
    return "quartet"


def tokenise(stem: str) -> list[str]:
    return re.findall(r"\d{6}", stem)


def deterministic_split(stem: str) -> str:
    n = int(hashlib.sha1(stem.encode("utf-8")).hexdigest()[:8], 16) % 10
    if n < 7:
        return "train"
    if n < 8:
        return "val"
    return "test"


def chord_type(csv_stem: str) -> str:
    name = csv_stem.replace("_loose", "").replace("_strict", "")
    name = name.replace("triads_", "")
    return name


def technique_from_token(tok: str) -> str:
    return TECHNIQUE_CODE_TO_NAME.get(tok[-2:], "arco-normal")


def dynamic_from_token(tok: str) -> str:
    return DYNAMIC_CODE_TO_NAME.get(tok[2:4], DYNAMIC_CODE_TO_NAME.get(tok[-2:], "forte"))


def family_from_token(tok: str) -> str:
    return TECHNIQUE_TO_FAMILY.get(technique_from_token(tok), "bowed")


def instrument_for_duo(csv_stem: str) -> list[str]:
    base = csv_stem.replace("_loose", "").replace("_strict", "")
    parts = base.split("_")
    if parts == ["cello", "viola"]:
        return ["cello", "viola"]
    if parts == ["cello", "violin"]:
        return ["cello", "violin1"]
    if parts == ["viola", "violin"]:
        return ["viola", "violin1"]
    return ["cello", "viola"]


def instruments_for(group: str, csv_stem: str) -> list[str]:
    kind = ensemble_kind(group)
    if kind == "duo":
        return instrument_for_duo(csv_stem)
    return INSTRUMENTS_BY_KIND[kind]


def silent_wav(path: Path, sample_rate: int = 16000, frames: int = 160) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(struct.pack("<" + "h" * frames, *([0] * frames)))


def group_fieldnames(kind: str) -> list[str]:
    cols: list[str] = []
    insts = INSTRUMENTS_BY_KIND[kind]
    for inst in insts:
        cols.append(f"{inst}_pitch")
    if kind == "duo":
        cols += ["interval", "semitones", "dynamic", "technique"]
    else:
        cols += ["chord_type", "dynamic", "technique"]
    for inst in insts:
        cols += [
            f"{inst}_file",
            f"{inst}_instrument_code",
            f"{inst}_pitch_code",
            f"{inst}_technique_code",
            f"{inst}_dynamic_code",
            f"{inst}_audible_duration",
            f"{inst}_dynamic",
            f"{inst}_technique",
            f"{inst}_family",
        ]
    cols += ["wav_filename", "chord_filename"]
    return cols


def make_row(group: str, csv_stem: str, npy_path: Path) -> dict[str, str]:
    stem = npy_path.stem
    kind = ensemble_kind(group)
    all_insts = INSTRUMENTS_BY_KIND[kind]
    present = instruments_for(group, csv_stem)
    toks = tokenise(stem)
    row = {k: "" for k in group_fieldnames(kind)}
    row["wav_filename"] = f"{stem}.wav"
    row["chord_filename"] = f"{stem}.wav"
    if kind == "duo":
        row["interval"] = csv_stem.replace("_loose", "").replace("_strict", "").replace("_", " ")
        row["semitones"] = ""
    else:
        row["chord_type"] = chord_type(csv_stem)
    row["dynamic"] = dynamic_from_token(toks[0]) if toks else "forte"
    row["technique"] = technique_from_token(toks[0]) if toks else "arco-normal"

    for idx, inst in enumerate(present):
        tok = toks[idx] if idx < len(toks) else "000009"
        tech = technique_from_token(tok)
        dyn = dynamic_from_token(tok)
        row[f"{inst}_pitch"] = tok[:2]
        row[f"{inst}_file"] = f"solo_wavs/solo_{inst}/{inst}_{tok}_{dyn}_{tech}.wav"
        row[f"{inst}_instrument_code"] = str(idx + 1)
        row[f"{inst}_pitch_code"] = tok[:2]
        row[f"{inst}_technique_code"] = tok[-2:]
        row[f"{inst}_dynamic_code"] = tok[2:4]
        row[f"{inst}_audible_duration"] = "0.01"
        row[f"{inst}_dynamic"] = dyn
        row[f"{inst}_technique"] = tech
        row[f"{inst}_family"] = family_from_token(tok)
    for inst in all_insts:
        row.setdefault(f"{inst}_file", "")
    return row


def list_candidates(cache_root: Path, max_per_csv: int) -> dict[tuple[str, str], list[Path]]:
    out: dict[tuple[str, str], list[Path]] = {}
    for group, stems in GROUP_CSVS.items():
        for csv_stem in stems:
            d = cache_root / group / csv_stem
            if not d.exists():
                out[(group, csv_stem)] = []
                continue
            out[(group, csv_stem)] = [
                d / entry.name
                for entry in os.scandir(d)
                if entry.is_file() and entry.name.endswith(".npy")
            ]
            out[(group, csv_stem)].sort(key=lambda p: p.name)
            if max_per_csv and len(out[(group, csv_stem)]) > max_per_csv:
                files = out[(group, csv_stem)]
                step = len(files) / max_per_csv
                out[(group, csv_stem)] = [files[int(i * step)] for i in range(max_per_csv)]
    return out


def pick_balanced(candidates: dict[tuple[str, str], list[Path]], seed: int, target: int) -> list[tuple[str, str, Path]]:
    rng = random.Random(seed)
    buckets: dict[str, list[tuple[str, str, Path]]] = defaultdict(list)
    for (group, csv_stem), files in candidates.items():
        kind = ensemble_kind(group)
        for f in files:
            buckets[f"EXP1:{kind}"].append((group, csv_stem, f))
            if group.startswith("triads"):
                buckets[f"EXP2:{chord_type(csv_stem)}"].append((group, csv_stem, f))
            toks = tokenise(f.stem)
            if toks and all(technique_from_token(t) == "arco-normal" for t in toks):
                buckets[f"EXP3:{dynamic_from_token(toks[0])}"].append((group, csv_stem, f))
            for fam in sorted({family_from_token(t) for t in toks}):
                buckets[f"EXP4:{fam}"].append((group, csv_stem, f))

    wants = {
        "EXP1:duo": 220,
        "EXP1:trio": 220,
        "EXP1:quartet": 220,
        "EXP2:major": 120,
        "EXP2:minor": 120,
        "EXP2:diminished": 120,
        "EXP2:augmented": 120,
        "EXP3:pianissimo": 80,
        "EXP3:mezzo-piano": 80,
        "EXP3:forte": 80,
        "EXP3:fortissimo": 80,
        "EXP4:bowed": 120,
        "EXP4:col_legno": 60,
        "EXP4:harmonic": 60,
        "EXP4:plucked": 60,
    }
    selected: dict[Path, tuple[str, str, Path]] = {}
    for key, want in wants.items():
        pool = list(dict.fromkeys(buckets.get(key, [])))
        rng.shuffle(pool)
        for item in pool:
            selected.setdefault(item[2], item)
            if sum(1 for p in selected.values() if p in pool) >= want:
                break
    all_items = [(g, c, f) for (g, c), fs in candidates.items() for f in fs]
    rng.shuffle(all_items)
    for item in all_items:
        if len(selected) >= target:
            break
        selected.setdefault(item[2], item)
    return sorted(selected.values(), key=lambda x: (x[0], x[1], x[2].name))[:target]


def build_wav_index(full_base: Path) -> dict[str, Path]:
    """Index likely WAV folders once. This SECD copy usually has no real WAVs."""
    roots = [
        full_base / "solo_wavs",
        full_base / "harmonic_intervals_loose" / "wav",
        full_base / "harmonic_intervals_strict" / "wav",
        full_base / "triads_loose" / "wav",
        full_base / "triads_strict" / "wav",
        full_base / "7th_chords_loose" / "wav",
        full_base / "7th_chords_strict" / "wav",
    ]
    index: dict[str, Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for wav in root.rglob("*.wav"):
            index.setdefault(wav.stem, wav)
    return index


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def write_csv(path: Path, rows: list[dict[str, str]], kind: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = group_fieldnames(kind)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full-secd-base", default=".", help="Full SECD dataset root")
    ap.add_argument("--seed", type=int, default=20260425)
    ap.add_argument("--target", type=int, default=1600)
    ap.add_argument("--max-per-csv", type=int, default=1200)
    ap.add_argument("--output", default=None, help="Output folder; defaults to this script directory")
    args = ap.parse_args()

    full_base = Path(args.full_secd_base).resolve()
    out = Path(args.output).resolve() if args.output else Path(__file__).resolve().parent
    cache_root = full_base / "mel_cache_ast16k_256"
    if not cache_root.exists():
        raise FileNotFoundError(cache_root)

    print(f"Indexing mel cache under {cache_root} ...", flush=True)
    candidates = list_candidates(cache_root, args.max_per_csv)
    print("Selecting balanced subset ...", flush=True)
    selected = pick_balanced(candidates, args.seed, args.target)
    print(f"Selected {len(selected)} samples; indexing WAVs once ...", flush=True)
    wav_index = build_wav_index(full_base)
    rows_by_csv: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    missing_files = []
    wav_strategy = Counter()

    print("Copying mel files and writing WAV placeholders ...", flush=True)
    for group, csv_stem, src in selected:
        if not src.exists():
            missing_files.append(str(src))
            continue
        mel_dst = out / "mel_cache_ast16k_256" / group / csv_stem / src.name
        mel_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, mel_dst)

        wav_dst = out / group / "wav" / csv_stem / f"{src.stem}.wav"
        real = wav_index.get(src.stem)
        if real and real.stat().st_size < 256_000:
            wav_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(real, wav_dst)
            wav_strategy["real_small_wav"] += 1
        else:
            silent_wav(wav_dst)
            wav_strategy["silent_placeholder"] += 1

        rows_by_csv[(group, csv_stem)].append(make_row(group, csv_stem, src))

    for (group, csv_stem), rows in rows_by_csv.items():
        write_csv(out / group / "csv" / f"{csv_stem}.csv", rows, ensemble_kind(group))

    group_counts = Counter(g for g, _, _ in selected)
    csv_counts = Counter((g, c) for g, c, _ in selected)
    validation = {
        "selected_samples": len(selected),
        "missing_mel": len(missing_files),
        "csv_files": len(rows_by_csv),
        "all_selected_mels_exist": all(
            (out / "mel_cache_ast16k_256" / g / c / p.name).exists()
            for g, c, p in selected
        ),
        "split_counts": Counter(deterministic_split(p.stem) for _, _, p in selected),
    }

    report = out / "MINI_SECD_REPORT.txt"
    with report.open("w", encoding="utf-8") as f:
        f.write("Mini-SECD demo report\n")
        f.write("=====================\n")
        f.write(f"Output folder: {out}\n")
        f.write(f"Seed: {args.seed}\n")
        f.write(f"Total samples: {len(selected)}\n")
        f.write(f"Total size bytes: {dir_size(out)}\n")
        f.write(f"WAV strategy: {dict(wav_strategy)}\n")
        f.write(f"Missing mel files: {len(missing_files)}\n")
        f.write("\nCounts per group:\n")
        for k, v in sorted(group_counts.items()):
            f.write(f"  {k}: {v}\n")
        f.write("\nCounts per CSV:\n")
        for (g, c), v in sorted(csv_counts.items()):
            f.write(f"  {g}/{c}.csv: {v}\n")
        f.write("\nValidation:\n")
        for k, v in validation.items():
            f.write(f"  {k}: {v}\n")
        f.write("\nLimitations:\n")
        f.write("  Original composition CSV files were not present in this dataset copy.\n")
        f.write("  CSV rows are reconstructed from real mel cache filenames and notebook-observed schema conventions.\n")
        f.write("  Real solo WAV files were not present; silent valid WAV placeholders are used.\n")

    print(f"Output folder: {out}")
    print(f"Total samples: {len(selected)}")
    print("Counts per group:")
    for k, v in sorted(group_counts.items()):
        print(f"  {k}: {v}")
    print("Counts per CSV:")
    for (g, c), v in sorted(csv_counts.items()):
        print(f"  {g}/{c}.csv: {v}")
    print(f"Missing files: {len(missing_files)}")
    print(f"Total size bytes: {dir_size(out)}")
    print(f"WAV strategy: {dict(wav_strategy)}")
    print(f"Validation: {validation}")
    return 0 if not missing_files and validation["all_selected_mels_exist"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
