# SECD — String Ensemble Chord Dataset: Experiments

This repository contains the experiment notebooks and results accompanying the paper:

> **[Paper title]**
> [Authors] · [Venue, Year]
> [DOI / arXiv link]

---

## Repository Structure

```
SECD/
├── dataset/                        ← Dataset description & access info
├── experiments/
│   ├── EXP1_ensemble_size/         ← Classify duo / trio / quartet
│   ├── EXP2_chord_quality/         ← Classify chord quality
│   ├── EXP3_chord_root/            ← Classify chord root
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
git clone https://github.com/[your-username]/SECD.git
cd SECD
pip install -r requirements.txt
```

All experiments are self-contained Google Colab notebooks.
Open each `.ipynb` directly in Colab — no local setup required beyond the dataset path configuration in **Cell 0**.

---

## Model Backbone

All experiments use the [Audio Spectrogram Transformer (AST)](https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593) pretrained on AudioSet.

---

## Citation

```bibtex
@article{[cite_key],
  title   = {[Paper title]},
  author  = {[Authors]},
  journal = {[Venue]},
  year    = {[Year]},
  url     = {[URL]}
}
```
