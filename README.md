# SECD — String Ensemble Chord Dataset: Experiments

This repository provides the public GitHub companion materials for the SECD benchmark experiments, including Mini-SECD, benchmark notebooks, metrics, figures, and lightweight reproducibility/demo materials; the official full SECD dataset release is archived on Zenodo at https://doi.org/10.5281/zenodo.15547207, and the accompanying SECD paper citation remains pending publication.

---

## Repository Structure

```
SECD/
├── dataset/                        ← Dataset description & access info
├── mini_secd_demo/                 ← GitHub-friendly demo dataset
├── experiments/
│   ├── EXP1_ensemble_size/         ← Classify duo / trio / quartet
│   ├── EXP2_chord_quality/         ← Classify chord quality
│   ├── EXP3_dynamics/              ← Classify dynamics
│   └── EXP4_tec_fam/              ← Classify playing technique family
└── requirements.txt
```

---

## Experiments Summary

| Exp | Task | Classes | Test Acc | Test Macro F1 |
|---|---|---|---|---|
| [EXP1](experiments/EXP1_ensemble_size/) | Ensemble size | duo / trio / quartet | 98.67% | 98.64% |
| [EXP2](experiments/EXP2_chord_quality/) | Chord quality | major / minor / diminished / augmented | 93.73% | 93.73% |
| [EXP3](experiments/EXP3_dynamics/) | Dynamics classification (arco, per-instrument) | pp / p / mp / f / ff | 98.19% | 98.01% |
| [EXP4](experiments/EXP4_tec_fam/) | Technique family | bowed / col_legno / harmonic / plucked | 99.39% | 97.29% |

---

## Setup

```bash
git clone https://github.com/ageroul/SECD.git
cd SECD
pip install -r requirements.txt
```

The experiments are provided as Jupyter/Colab notebooks. They require the Python dependencies in `requirements.txt`, access to the AST backbone weights, and either the included Mini-SECD demo dataset or the full SECD dataset.

---

## Mini-SECD Demo Dataset

This repository includes a small demo dataset at `mini_secd_demo/`. **Mini-SECD is for notebook execution and pipeline validation only. It is not a reproducibility dataset and should not be used to report or compare scientific metrics.**

Mini-SECD contains real precomputed SECD mel-spectrogram tensors (`.npy`) copied from the full SECD mel cache. The WAV files in `mini_secd_demo/` are tiny valid silent placeholders; they exist only because the original notebooks check for audio-path existence before loading cached mel tensors. They are not the source audio used in the paper.

The CSV metadata in Mini-SECD is reconstructed from mel filenames and SECD schema conventions for demo execution. It is not copied from the original experiment CSV metadata. Use Mini-SECD to verify that data loading, filtering, splitting, label extraction, dataset construction, and short demo-mode execution work end to end.

---

## Reproducibility

The metrics shown above come from the full experimental setup. Reproducing those results requires the official full SECD release on Zenodo:

https://doi.org/10.5281/zenodo.15547207

Full metric reproduction also requires:

- the full SECD dataset,
- the full precomputed SECD mel cache,
- the original/full metadata,
- the required Python dependencies,
- access to the pretrained AST backbone weights,
- and a suitable GPU runtime.

The notebooks preserve the original experiment definitions: tasks, labels, model architectures, losses, and evaluation metrics are unchanged. Demo mode changes only runtime settings such as dataset root, device selection, dataloader workers, batch size, and the number of training steps. These changes make the notebooks easier to execute on normal machines, but they do not turn Mini-SECD into a paper-results reproduction package.

---

## Quick Start

Install dependencies, then open any notebook under `experiments/`.

```bash
pip install -r requirements.txt
```

By default, when `mini_secd_demo/` is present, notebooks run in demo mode:

```python
RUN_MODE = "demo"
SECD_BASE = "./mini_secd_demo"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

Demo mode is suitable for checking that the notebooks execute and that the pipeline is wired correctly. It is not suitable for reproducing or validating the reported paper scores.

To use the full dataset instead, set `SECD_RUN_MODE=full` and point `SECD_BASE` at the full SECD dataset root before running the notebooks:

```bash
export SECD_RUN_MODE=full
export SECD_BASE=/path/to/full/SECD
```

CPU execution is supported for demo runs. Full training remains GPU-oriented and can be slow or impractical on CPU.

---

## Model Backbone

All experiments use the [Audio Spectrogram Transformer (AST)](https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593) pretrained on AudioSet.

---

## Citation

```bibtex
@misc{secd_dataset_2026,
  title = {SECD: String Ensemble Chord Dataset},
  note  = {Official full dataset release archived on Zenodo. Paper citation pending publication.},
  year  = {2026},
  doi   = {10.5281/zenodo.15547207},
  url   = {https://doi.org/10.5281/zenodo.15547207}
}
```
