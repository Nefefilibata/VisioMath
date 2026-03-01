下面是一个可直接复制到 `README.md` 的版本（我在需要插入图片的地方都打了 **PDF 标记**）。README 中的关键数字/结论都来自你上传的 ICLR 2026 论文。    


# VisioMath (ICLR 2026) — Benchmarking Figure-based Mathematical Reasoning in LMMs

[![Conference](https://img.shields.io/badge/ICLR-2026-blue)](#)

**VisioMath** is a curated benchmark for **figure-based, multi-image mathematical reasoning** where **all answer choices are diagrams** and distractors are **highly visually similar**—a common setting in real-world K–12 exams. The benchmark is designed to stress-test **fine-grained comparative reasoning** and **multi-image–text alignment** in Large Multimodal Models (LMMs).


---

## 🔥 Introduction

Large Multimodal Models (LMMs) have achieved strong progress on many vision-language tasks, yet **reasoning over multiple, highly similar images** remains underexplored and surprisingly difficult. In real K–12 exam settings, a large portion of multiple-choice math problems present **diagrammatic answer options** (e.g., geometry figures, function graphs) that differ only in subtle visual details. Solving such problems requires:
- **Fine-grained visual discrimination** among near-duplicate candidates
- **Comparative reasoning** across multiple images
- **Precise option-to-image grounding (image–text alignment)**, rather than positional heuristics

VisioMath is built to faithfully capture this setting.

<!-- [FIGURE | PDF] Figure 1: Dataset examples (highly similar visual options; stem may include 0/1/multiple images) -->
[![Figure 1: Dataset examples](assets/example1.png)]

---

## ✨ Key Features

- **Image-option math reasoning**: all A–D options are *independent images* (one image per option).
- **Multi-image input**: each problem contains option images + optional stem image(s).
- **High visual similarity distractors**: options are intentionally confusable to test fine-grained discrimination.
- **Alignment stress-test**: controlled experiments reveal models’ reliance on shallow positional priors.

---

## 🔥 Comparisons with Existing Benchmarks

Most multimodal math benchmarks follow a **single-image** setting (one diagram + text options). Multi-image benchmarks exist, but often **lack figure-based options** or provide options in **composite layouts** rather than independent, semantically meaningful images. VisioMath explicitly targets the underexplored but ubiquitous “**image-option**” exam scenario.

### Table: VisioMath vs. representative benchmarks (from the paper)

| Dataset | Multi-image | Language | #Problems (FO) | #Problems | #Images | AvgImg |
|---|---:|---|---:|---:|---:|---:|
| We-Math | ✘ | EN | – | 6500 | 6500 | 1.00 |
| MMMU-Math | ✘ | EN | – | 540 | 540 | 1.00 |
| Math-Vista | ✘ | EN | – | 6141 | 6141 | 1.00 |
| Math-Verse | ✘ | EN | – | 2612 | 2612 | 1.00 |
| Math-Vision | ✘ | EN | – | 3040 | 3040 | 1.00 |
| MM-Math | ✘ | EN | – | 5929 | 5929 | 1.00 |
| CMMU-MATH | ✘ | CN | – | 778 | 778 | 1.00 |
| MathExplain | ✘ | EN | – | 997 | 997 | 1.00 |
| MathGlance | ✘ | EN | – | 1609 | 1609 | 1.00 |
| Gaokao-MM-Math | ✔ | CN | 17 | 80 | 142 | 1.78 |
| CMM-Math-test | ✔ | CN | 245 | 5821 | 3794 | 2.26 |
| MathVerse-mv | ✔ | EN | 0 | 788 | 6304 | 8.00 |
| MV-Math | ✔ | CN, EN | 595 | 2009 | 6061 | 3.02 |
| **VisioMath (Ours)** | ✔ | CN, EN | **1800** | **1800** | **8070** | **4.48** |

<!-- [FIGURE | PDF] (Optional) Put a PDF snapshot of Table 1 from the paper here -->
**[Insert PDF here]** `assets/tab1_benchmark_comparison.pdf`

---

## 📦 Dataset overview

- **#Problems:** 1,800 high-quality K–12 math multiple-choice questions  
- **#Option images:** 8,070 (strictly **one image per option**, cropped and cleaned)
- **Avg. images per problem:** 4.48 (options + optional stem images)
- **Languages:** Chinese & English (bilingual stems available for many questions)
- **Source:** real Chinese high school & college entrance exam questions (2002–2023)
- **Annotation:** each question is independently annotated and cross-validated by at least **two expert annotators**
- **Bias control:** ground-truth options are balanced across A–D (roughly uniform)
- **Visual similarity:** quantified by the **minimum pairwise cosine similarity** across option image embeddings (computed via a diagram-friendly multimodal embedding model)

<!-- [FIGURE | PDF] Figure 2: Data processing pipeline (text extraction/LaTeX, cropping, filtering, similarity integration) -->
**[Insert PDF here]** `assets/fig2_data_pipeline.pdf`

<!-- [FIGURE | PDF] Figure 3: Dataset statistics (subjects, question length, similarity distribution) -->
**[Insert PDF here]** `assets/fig3_dataset_statistics.pdf`

---

## 🧪 Observation

We highlight three consistent findings reported in the paper:

1. **Stems containing images are harder**  
   When both the stem and options contain visual content, models must integrate multiple visual sources, increasing difficulty.

2. **Accuracy degrades as inter-option similarity increases**  
   Higher similarity among candidate diagrams leads to a clear performance drop, indicating limited fine-grained discrimination.

3. **Human vs. LMM failure modes differ**  
   Humans degrade moderately under higher similarity, while LMMs often fail on distinctions humans rarely confuse—suggesting a dominant role of **image–text misalignment** rather than pure reasoning depth.

<!-- [FIGURE | PDF] (Optional) Put a PDF snapshot of Table 2 / Table 3 (main results) -->
**[Insert PDF here]** `assets/tab2_tab3_main_results.pdf`

---

## 🧪 ANALYSIS

### Error taxonomy
A representative error analysis categorizes model failures into:
- Vision recognition errors
- Reasoning errors
- Knowledge errors
- **Image–text misalignment** (often the largest share)

### Option shuffling diagnostic
To test reliance on positional priors, we keep image order fixed but permute the textual option-to-image mapping. Performance drops consistently under this manipulation, indicating that many models do not robustly bind “Option A/B/C/D” to the correct image.

<!-- [FIGURE | PDF] Figure 5: Error distribution + performance under Original vs Shuffling vs strategy variants -->
**[Insert PDF here]** `assets/fig5_error_and_shuffling.pdf`

---

## 🧪 STRATEGIES FOR PERFORMANCE ENHANCEMENT

We provide three alignment-oriented strategies:

### Strategy 1: Consolidated single-image layout (training-free)
Concatenate all stem/option images into one composite image to simplify attention distribution.

### Strategy 2: Explicit visual–textual anchors (training-free)
Add a visible label (A/B/C/D) directly onto each option image to strengthen the option-to-image correspondence.

### Strategy 3: Alignment-oriented multi-image CoT fine-tuning (training-based)
Construct a specialized multi-image CoT dataset with explicit per-image descriptions and aligned reasoning traces, then fine-tune models with SFT. Even small amounts of such data yield strong gains.

<!-- [FIGURE | PDF] Figure 6: Input formats for Original vs Strategy 1 vs Strategy 2 -->
**[Insert PDF here]** `assets/fig6_input_formats.pdf`

<!-- [FIGURE | PDF] (Optional) Put a PDF snapshot of Table 5 (strategy gains) -->
**[Insert PDF here]** `assets/tab5_strategy_gains.pdf`

---

## 📦 Core Modules

1. `function.py` - Core functionality:
   - Strategy 1 and strategy 2 (image formatting / stitching / anchors)
   - Answer extraction and evaluation
   - JSON data handling
   - Accuracy calculation

2. `test.py` - Evaluation framework:
   - Main execution flow
   - Batch processing with periodic saving
   - Result aggregation

3. `cot_data_gen.py` - Data Generation:
   - Generate multi-image CoT data (for Strategy 3)
   - Option shuffling prompt / augmentation utilities

---

## 🚀 Getting started

### 1) Environment
```bash
pip install -r requirements.txt
````

### 2) Prepare data

* Put dataset JSON and images under `data/` (see repository release / data card for the exact structure).
* Recommended layout:

```
data/
  visiomath.json
  images/
    ... (stem + option images)
assets/
  ... (pdf figures for README)
```

### 3) Configure API keys (if using closed-source APIs)

Edit `function.py` and set the required keys / endpoints.

### 4) Run evaluation

```bash
python test.py
```

Results will be saved to `baseline.json`.

---

## 📌 Reproducibility Notes

* Use deterministic decoding (e.g., `temperature=0`) when comparing against paper numbers.
* Use the same prompt template across models to reduce prompt-induced variance.
* If you use an external LLM to normalize/extract final answers (A/B/C/D), keep the extraction rule consistent.

---

## 📝 Citation

If you use VisioMath in your research, please cite:

```bibtex
@inproceedings{li2026visiomath,
  title     = {VisioMath: Benchmarking Figure-based Mathematical Reasoning in LMMs},
  author    = {Li, Can and Liu, Ying and Zhang, Ting and Wang, Mei and Huang, Hua},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026}
}
```

---

## 📄 License

* Code: (to be filled)
* Dataset: (to be filled)

---

## 🙏 Acknowledgement

This work is supported by relevant grants and institutional funds (see paper for details).

```

如果你希望我把 README 里 “PDF 插图占位符” 的文件名一次性对齐成你论文里的 Figure 编号（比如 `Figure_1.pdf / Figure_2.pdf ...`），我也可以按你仓库的 `assets/` 实际命名规则再帮你统一一版。
```
