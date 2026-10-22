# C++ AI Tutor: The Smart Compiler

This project is a Python-based diagnostic tool designed to intercept C++ compiler errors and provide clear, human-readable explanations alongside actionable code fixes. Rather than surfacing cryptic syntax traces, the system offers an intuitive explanation of the failure cause and a direct resolution.

The core of the system is powered by a fine-tuned CodeT5 (a code-aware Transformer model) trained on a hybrid dataset of synthetically generated compilation errors and real-world developer issues.

---

## Features

*   **AI-Powered Diagnostics**: Utilizes a fine-tuned Salesforce/codet5-base model to deliver context-aware solutions to C++ compilation errors.
*   **Compiler CLI Wrapper (src/tutor.py)**: A drop-in replacement script for g++. It can be used exactly like the standard compiler to process files, while returning instant, natural language explanations upon build failure.
*   **Web Application Interface (src/app.py)**: A Gradio-based web interface. Developers can input C++ code directly into the browser to compile it and review interactive diagnostic feedback.
*   **Automated Data Collection Pipelines**:
    *   **src/generate_dataset.py**: Compiles incomplete C++ snippets locally using g++ to generate structured synthetic (error, explanation, suggested_fix) datasets.
    *   **src/scrape_stack.py**: Interfaces with the Stack Exchange API to fetch real-world Stack Overflow discussions tagged c++ and compiler-errors, along with their accepted resolutions.
*   **Quantitative Evaluation Benchmark (src/evaluate.py)**: Domain-specific AI/ML evaluation suite measuring Pass@1 syntax execution via g++ -fsyntax-only, Root-Cause Localization Accuracy (RCA), and token F1 scores.
*   **Visual Training Dashboards**: Integrated with TensorBoard to monitor model training and validation loss metrics during the fine-tuning phase.
*   **Architecture & Interview Defense Guide**: Comprehensive technical guide detailing Seq2Seq formulations, CodeT5 trade-offs, and ML interview Q&A.

---

## Architecture and Workflow

1.  **Data Collection**:
    *   *Synthetic Data*: The src/generate_dataset.py script compiles broken code to yield clean pairs in generated_dataset.json.
    *   *Real-World Data*: The src/scrape_stack.py script fetches real Stack Overflow data and serializes it in scraped_dataset.json.
    *   *Pre-built Datasets*: A preliminary dataset of compiler errors is provided in error_dataset.json.
2.  **Model Training**: The src/train.py script splits the aggregated data (80% training, 20% validation) and executes the fine-tuning of the CodeT5 model.
3.  **Model Evaluation**: The src/evaluate.py script verifies performance against compiler execution checks (Pass@1) and semantic root-cause metrics.
4.  **CLI Execution**: The src/tutor.py wrapper intercepts compilation errors, filters out compiler path noise, and queries the fine-tuned model via src/inference.py.
5.  **Web Execution**: The src/app.py script initializes a Gradio interface. It handles temporary file compilation and renders side-by-side error listings alongside AI-generated feedback.

---

## Project Structure

`	ext
.
├── src/
│   ├── app.py                  # Gradio Web Application interface
│   ├── tutor.py                # Command-line compiler wrapper
│   ├── inference.py            # Model loading and text generation logic
│   ├── train.py                # Script for training and fine-tuning the model
│   ├── evaluate.py             # Quantitative AI/ML benchmark (Pass@1, RCA, F1)
│   ├── generate_dataset.py     # Script for generating synthetic error data
│   └── scrape_stack.py         # Stack Overflow API data scraper
├── architecture_guide.md       # AI/ML Architecture & Interview Defense Guide
├── CHANGELOG_AND_AI_UPDATES.md # System Evolution & Changelog
├── error_dataset.json          # Repository of compiler errors
├── generated_dataset.json      # Synthetically generated training data
├── scraped_dataset.json        # Training data aggregated from Stack Overflow API
├── evaluation_report.json      # Quantitative benchmark output
├── main.cpp                    # Sample C++ file for diagnostic testing
├── requirements.txt            # Python package dependencies
├── toacd-project.ipynb         # Jupyter notebook for experiments
└── README.md                   # Project documentation
`

---

## Installation Guidelines

### 1. Prerequisites
A C++ compiler must be installed on your operating system:
*   **Windows**: Install MinGW (which provides g++).
*   **macOS**: Install Xcode Command Line Tools (xcode-select --install).
*   **Linux (Ubuntu)**: Run sudo apt install build-essential g++.

### 2. Virtual Environment Setup
`ash
# Initialize the environment
python -m venv venv

# Activate (Windows PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
`

### 3. Dependency Installation
`ash
pip install transformers sentencepiece gradio requests scikit-learn tensorboard
`

---

## Usage Instructions

### Step 1: Data Aggregation

*   **Option A: Generate Synthetic Data**
    `ash
    python src/generate_dataset.py
    `
*   **Option B: Scrape Real-World Data**
    `ash
    python src/scrape_stack.py --limit 30
    `

### Step 2: Model Training
Execute the fine-tuning script:
`ash
python src/train.py --dataset scraped_dataset.json --epochs 10 --batch_size 4 --lr 5e-5
`
*   *(Optional)* Launch TensorBoard:
    `ash
    tensorboard --logdir=runs
    `

### Step 3: Model Evaluation & Benchmarking
Run the quantitative benchmark suite:
`ash
# Run benchmark on generated dataset
python src/evaluate.py --dataset generated_dataset.json --eval_samples 50

# Run mock simulation (verification without requiring GPU/weights)
python src/evaluate.py --mock
`

### Step 4: Running the AI Tutor

*   **Option A: CLI Compiler Wrapper**
    `ash
    python src/tutor.py main.cpp -o main
    `
*   **Option B: Web Interface**
    `ash
    python src/app.py
    `
    Navigate to http://127.0.0.1:7860 in a web browser.

---

## Documentation & Interview Preparation
* **[AI/ML Architecture & Interview Defense Guide](architecture_guide.md)**: Deep-dive into Seq2Seq formulation, model trade-offs, and technical interview Q&A.
* **[Changelog & AI/ML Updates](CHANGELOG_AND_AI_UPDATES.md)**: Full history of recent enhancements and benchmark results.
