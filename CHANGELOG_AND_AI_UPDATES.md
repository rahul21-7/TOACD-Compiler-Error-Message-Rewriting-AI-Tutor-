# TOACD: AI/ML System Updates & Changelog

This document details all algorithmic, architectural, and evaluation enhancements made to elevate the **C++ AI Tutor (TOACD)** into an academically defensible, production-grade AI/ML project.

---

## 1. Summary of Changes & Additions

| File | Status | Description of Enhancements |
| :--- | :--- | :--- |
| [`src/train.py`](src/train.py) | **Upgraded (Approach 1)** | Implemented **Execution-Guided Validation Checkpointing (Approach 1)**: at the end of each epoch, evaluates $Pass@1$ syntax execution via `g++ -fsyntax-only` on validation samples and saves the model checkpoint prioritizing highest functional compilation rate (tie-breaking with validation loss). Logs `Metrics/Validation_Pass@1` to TensorBoard. |
| [`src/evaluate.py`](src/evaluate.py) | **New File** | Complete offline quantitative evaluation suite implementing $Pass@1$ (compilation testing via `g++ -fsyntax-only`), Root-Cause Localization Accuracy (RCA), Token F1/Precision/Recall, and automated JSON reporting. Includes a `--mock` verification mode. |
| [`architecture_guide.md`](architecture_guide.md) | **Major Overhaul** | Rewritten as a master **AI/ML Architecture & Interview Defense Guide**. Adds mathematical formulations of Seq2Seq objectives, trade-off comparison matrices (CodeT5 vs Decoder-Only/BERT), LoRA PEFT formulations, multi-task loss designs, and top 10 technical interview Q&A. |
| [`src/inference.py`](src/inference.py) | **Bug Fix & Optimization** | 1. Synchronized the prompt prefix with `train.py` (`"explain this C++ compiler error..."`) to eliminate out-of-distribution prompt drift.<br>2. Fixed memory churn by caching the model and tokenizer globally rather than reloading weights from disk on every invocation. |
| [`README.md`](README.md) | **Updated** | Added the model evaluation workflow, updated the project structure tree with `src/`, benchmark metrics overview, and execution instructions for `evaluate.py`. |
| [`evaluation_report.json`](evaluation_report.json) | **New Artifact** | Benchmark output recording $Pass@1$, RCA, F1, precision, and sample volume. |

---

## 2. Deep Dive: What Was Added & Why

### A. Execution-Guided Validation Checkpointing in `src/train.py` (Approach 1)
* **Problem Solved**: Standard neural training saves checkpoints based solely on minimal cross-entropy validation loss. Because cross-entropy is a token-level surrogate loss that is blind to C++ compiler validity, the checkpoint with the lowest validation loss does not necessarily produce the highest percentage of compiling C++ fixes.
* **New Capability**:
  * Evaluates functional $Pass@1$ execution on a validation slice after each epoch using `model.generate()`.
  * Runs candidate fixes through `g++ -fsyntax-only` via `test_syntax_compilation()`.
  * Saves the best model checkpoint based on:
    $$	ext{Save Checkpoint if } 	ext{Pass@1}_{	ext{epoch}} > 	ext{Pass@1}_{	ext{best}} \quad 	ext{or} \quad (	ext{Pass@1}_{	ext{epoch}} == 	ext{Pass@1}_{	ext{best}} \;\wedge\; \mathcal{L}_{	ext{val}} < \mathcal{L}_{	ext{best}})$$
  * Logs both `Loss/Validation` and `Metrics/Validation_Pass@1` to TensorBoard.

### B. Quantitative Evaluation Suite (`src/evaluate.py`)
* **Problem Solved**: Previously, the repository only tracked training and validation cross-entropy loss. In code synthesis and diagnostics, cross-entropy is uninformative—a model can achieve low loss while generating code that fails compilation due to a single syntax error.
* **New Capability**:
  * **$Pass@1$ (Functional Execution Check)**: Spawns a sandboxed subprocess running `g++ -fsyntax-only -std=c++17` on generated C++ patches to verify syntactic correctness deterministically.
  * **Root-Cause Accuracy (RCA)**: Classifies whether the natural language explanation accurately diagnoses the compiler failure phase (Undeclared Identifier, Syntax Delimiter, Type Coercion, Missing Header, Linker Error).
  * **Token F1, Precision, and Recall**: Measures diagnostic semantic overlap against reference explanations.
  * **Mock Mode (`--mock`)**: Allows instant dry-run testing and demonstration on systems without GPU acceleration or pre-loaded model weights.

### C. Prompt Synchronization & Inference Optimization (`src/inference.py`)
* **Problem Solved**:
  1. `train.py` trained the model with:  
     `prefix = "explain this C++ compiler error, detailing the specific cause and a solution: "`  
     While `inference.py` queried it with:  
     `prefix = "explain C++ error: "`  
     In sequence-to-sequence transformers, this prompt divergence degrades generation quality due to mismatched conditioning prefixes.
  2. In `inference.py`, `explain_error()` was re-instantiating the tokenizer and model from disk on every function call.
* **Fix**: Standardized the prefix string and reused global in-memory model instances, eliminating I/O latency and memory churn.

### D. Formal AI/ML Interview Defense Framework (`architecture_guide.md`)
* **Problem Solved**: Standard student project documentation often lacks theoretical depth, making it difficult to defend in competitive machine learning interviews.
* **New Additions**:
  1. **Formal Seq2Seq Formulation**: Conditional log-likelihood optimization under teacher forcing.
  2. **Architectural Justification Matrix**: Detailed trade-offs explaining why Encoder-Decoder (CodeT5) was chosen over Decoder-Only (LLaMA/Mistral) and Encoder-Only (BERT), and why Beam Search ($K=4$) was chosen over Nucleus Sampling.
  3. **Advanced Scaling Proposals**: Formulations for Parameter-Efficient Fine-Tuning (LoRA), Multi-Task Classification Heads ($\mathcal{L}_{	ext{total}}$), and Direct Preference Optimization (DPO).
  4. **Top 10 Technical Interview Q&A**: Ready-to-use answers covering exposure bias, hallucination mitigation, class imbalance, and edge deployment via INT8 quantization.
