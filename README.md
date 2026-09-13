# C++ AI Tutor: The Smart Compiler

This project is a Python-based diagnostic tool designed to intercept C++ compiler errors and provide clear, human-readable explanations alongside actionable code fixes. Rather than surfacing cryptic syntax traces, the system offers an intuitive explanation of the failure cause and a direct resolution.

The core of the system is powered by a fine-tuned `CodeT5` (a code-aware Transformer model) trained on a hybrid dataset of synthetically generated compilation errors and real-world developer issues.

---

## Features

*   **AI-Powered Diagnostics**: Utilizes a fine-tuned Salesforce/codet5-base model to deliver context-aware solutions to C++ compilation errors.
*   **Compiler CLI Wrapper (tutor.py)**: A drop-in replacement script for `g++`. It can be used exactly like the standard compiler to process files, while returning instant, natural language explanations upon build failure.
*   **Web Application Interface (app.py)**: A Gradio-based web interface. Developers can input C++ code directly into the browser to compile it and review interactive diagnostic feedback.
*   **Automated Data Collection Pipelines**:
    *   **generate_dataset.py**: Compiles incomplete C++ snippets locally using `g++` to generate structured synthetic `(error, explanation, suggested_fix)` datasets.
    *   **scrape_stack.py**: Interfaces with the Stack Exchange API to fetch real-world Stack Overflow discussions tagged `c++` and `compiler-errors`, along with their accepted resolutions.
*   **Visual Training Dashboards**: Integrated with TensorBoard to monitor model training and validation loss metrics during the fine-tuning phase.
*   **Architecture Reference**: Includes a comprehensive architecture_guide.md detailing the core components, data structures, and algorithmic trade-offs.

---

## Architecture and Workflow

1.  **Data Collection**:
    *   *Synthetic Data*: The `generate_dataset.py` script compiles broken code to yield clean pairs in `generated_dataset.json`.
    *   *Real-World Data*: The `scrape_stack.py` script fetches real Stack Overflow data and serializes it in `scraped_dataset.json`.
    *   *Pre-built Datasets*: A preliminary dataset of compiler errors is provided in `error_dataset.json`.
2.  **Model Training**: The `train.py` script splits the aggregated data (80% training, 20% validation) and executes the fine-tuning of the CodeT5 model.
3.  **CLI Execution**: The `tutor.py` wrapper intercepts compilation errors, filters out compiler path noise, and queries the fine-tuned model via `inference.py`.
4.  **Web Execution**: The `app.py` script initializes a Gradio interface. It handles temporary file compilation and renders side-by-side error listings alongside AI-generated feedback.

---

## Project Structure

```text
.
├── app.py                  # Gradio Web Application interface
├── tutor.py                # Command-line compiler wrapper
├── inference.py            # Model loading and text generation logic
├── train.py                # Script for training and fine-tuning the model
├── generate_dataset.py     # Script for generating synthetic error data
├── scrape_stack.py         # Stack Overflow API data scraper
├── error_dataset.json      # Large repository of compiler errors
├── generated_dataset.json  # Synthetically generated training data
├── scraped_dataset.json    # Training data aggregated from the Stack Overflow API
├── architecture_guide.md   # System architecture and technical reference documentation
├── requirements.txt        # Python package dependencies
├── main.cpp                # Sample C++ file for diagnostic testing
└── Progress_readme.md      # Internal development progress log
```

---

## Installation Guidelines

### 1. Prerequisites
A C++ compiler must be installed on your operating system:
*   **Windows**: Install MinGW (which provides `g++`).
*   **macOS**: Install Xcode Command Line Tools (`xcode-select --install`).
*   **Linux (Ubuntu)**: Run `sudo apt install build-essential g++`.

### 2. Virtual Environment Setup
```bash
# Initialize the environment
python -m venv venv

# Activate (Windows PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Dependency Installation
Ensure that PyTorch is installed according to your specific hardware configuration (e.g., CUDA capabilities for NVIDIA GPUs). Refer to the official PyTorch installation guide for detailed setup instructions.
Next, install the required packages:
```bash
pip install transformers sentencepiece gradio requests scikit-learn tensorboard
```

---

## Usage Instructions

### Step 1: Data Aggregation

*   **Option A: Generate Synthetic Data**
    Execute the compiler issue simulator to produce `generated_dataset.json`:
    ```bash
    python generate_dataset.py
    ```
*   **Option B: Scrape Real-World Data**
    Execute the API scraper to collect Stack Overflow data into `scraped_dataset.json`:
    ```bash
    python scrape_stack.py --limit 30
    ```
    *Note: The Stack Exchange API permits 300 free requests per day. An optional `--api-key <key>` parameter can be supplied to increase this quota.*

### Step 2: Model Training
Execute the fine-tuning script. The target dataset and hyperparameters can be passed as arguments:
```bash
python train.py --dataset scraped_dataset.json --epochs 10 --batch_size 4 --lr 5e-5
```
*   *(Optional)* Launch TensorBoard to monitor training metrics:
    ```bash
    tensorboard --logdir=runs
    ```
    Navigate to `http://localhost:6006/` in a web browser.

### Step 3: Running the AI Tutor

*   **Option A: CLI Compiler Wrapper**
    Execute `tutor.py` in place of `g++` to compile source code:
    ```bash
    python tutor.py main.cpp -o main
    ```
*   **Option B: Web Interface**
    Launch the interactive web application:
    ```bash
    python app.py
    ```
    Navigate to `http://127.0.0.1:7860` in a web browser.

---

## Future Development

*   **Telemetry and Feedback Logging**: Introduce feedback mechanisms (e.g., accept/reject buttons) in the Gradio web interface to record user satisfaction and capture corrections.
*   **Continuous Fine-Tuning**: Implement periodic model retraining pipelines utilizing the aggregated user correction logs.
*   **IDE Integration**: Develop native extensions for standard editors such as VS Code or CLion to wrap the diagnostic endpoints directly within the developer environment.
