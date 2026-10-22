# TOACD: AI/ML System Updates & Changelog

This document details all recent algorithmic, architectural, and evaluation enhancements made to elevate the **C++ AI Tutor (TOACD)** into an academically defensible, production-grade AI/ML project.

---

## 1. Summary of Changes & Additions

| File | Status | Description of Enhancements |
| :--- | :--- | :--- |
| [`evaluate.py`](file:///c:/Users/dasar/Downloads/TOACD-Compiler-Error-Message-Rewriting-AI-Tutor-/TOACD/evaluate.py) | **New File** | Complete offline quantitative evaluation suite implementing $Pass@1$ (compilation testing via `g++ -fsyntax-only`), Root-Cause Localization Accuracy (RCA), Token F1/Precision/Recall, and automated JSON reporting. Includes a `--mock` verification mode. |
| [`architecture_guide.md`](file:///c:/Users/dasar/Downloads/TOACD-Compiler-Error-Message-Rewriting-AI-Tutor-/TOACD/architecture_guide.md) | **Major Overhaul** | Rewritten as a master **AI/ML Architecture & Interview Defense Guide**. Adds mathematical formulations of Seq2Seq objectives, trade-off comparison matrices (CodeT5 vs Decoder-Only/BERT), LoRA PEFT formulations, multi-task loss designs, and top 10 technical interview Q&A. |
| [`inference.py`](file:///c:/Users/dasar/Downloads/TOACD-Compiler-Error-Message-Rewriting-AI-Tutor-/TOACD/inference.py) | **Bug Fix & Optimization** | 1. Synchronized the prompt prefix with `train.py` (`"explain this C++ compiler error..."`) to eliminate out-of-distribution prompt drift.<br>2. Fixed memory churn by caching the model and tokenizer globally rather than reloading weights from disk on every invocation. |
| [`README.md`](file:///c:/Users/dasar/Downloads/TOACD-Compiler-Error-Message-Rewriting-AI-Tutor-/TOACD/README.md) | **Updated** | Added the model evaluation workflow, benchmark metrics overview, and execution instructions for `evaluate.py`. |
| [`evaluation_report.json`](file:///c:/Users/dasar/Downloads/TOACD-Compiler-Error-Message-Rewriting-AI-Tutor-/TOACD/evaluation_report.json) | **New Artifact** | Benchmark output recording $Pass@1$, RCA, F1, precision, and sample volume. |

---

## 2. Deep Dive: What Was Added & Why

### A. Quantitative Evaluation Suite (`evaluate.py`)
* **Problem Solved**: Previously, the repository only tracked training and validation cross-entropy loss. In code synthesis and diagnostics, cross-entropy is uninformative—a model can achieve low loss while generating code that fails compilation due to a single syntax error.
* **New Capability**:
  * **$Pass@1$ (Functional Execution Check)**: Spawns a sandboxed subprocess running `g++ -fsyntax-only -std=c++17` on generated C++ patches to verify syntactic correctness deterministically.
  * **Root-Cause Accuracy (RCA)**: Classifies whether the natural language explanation accurately diagnoses the compiler failure phase (Undeclared Identifier, Syntax Delimiter, Type Coercion, Missing Header, Linker Error).
  * **Token F1, Precision, and Recall**: Measures diagnostic semantic overlap against reference explanations.
  * **Mock Mode (`--mock`)**: Allows instant dry-run testing and demonstration on systems without GPU acceleration or pre-loaded model weights.

### B. Prompt Synchronization & Inference Optimization (`inference.py`)
* **Problem Solved**:
  1. `train.py` trained the model with:  
     `prefix = "explain this C++ compiler error, detailing the specific cause and a solution: "`  
     While `inference.py` queried it with:  
     `prefix = "explain C++ error: "`  
     In sequence-to-sequence transformers, this prompt divergence degrades generation quality due to mismatched conditioning prefixes.
  2. In `inference.py`, `explain_error()` was re-instantiating the tokenizer and model from disk on every function call.
* **Fix**: Standardized the prefix string and reused global in-memory model instances, eliminating I/O latency and memory churn.

### C. Formal AI/ML Interview Defense Framework (`architecture_guide.md`)
* **Problem Solved**: Standard student project documentation often lacks theoretical depth, making it difficult to defend in competitive machine learning interviews.
* **New Additions**:
  1. **Formal Seq2Seq Formulation**: Conditional log-likelihood optimization under teacher forcing.
  2. **Architectural Justification Matrix**: Detailed trade-offs explaining why Encoder-Decoder (CodeT5) was chosen over Decoder-Only (LLaMA/Mistral) and Encoder-Only (BERT), and why Beam Search ($K=4$) was chosen over Nucleus Sampling.
  3. **Advanced Scaling Proposals**: Formulations for Parameter-Efficient Fine-Tuning (LoRA), Multi-Task Classification Heads ($\mathcal{L}_{\text{total}}$), and Direct Preference Optimization (DPO).
  4. **Top 10 Technical Interview Q&A**: Ready-to-use answers covering exposure bias, hallucination mitigation, class imbalance, and edge deployment via INT8 quantization.

---

## 3. Resume Framing Recommendations

For complete recommendations on how to update your resume, including bullet points formatted using the XYZ formula and target skills keywords, refer to the accompanying interview defense notes.
