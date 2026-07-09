# C++ AI Tutor: The Smart Compiler

This project is a Python-based diagnostic tool that intercepts C++ compiler errors and provides simple, human-readable explanations alongside suggested code fixes. Instead of a cryptic message like `expected ';' before '}' token`, users get an intuitive, friendly explanation of what went wrong and how to fix it.

It is powered by a fine-tuned `CodeT5` (a code-aware Transformer model) trained on a hybrid dataset of synthetically generated errors and real-world compiler issues.

---

## 🚀 Features

*   **AI-Powered Diagnostics**: Uses a fine-tuned [Salesforce/codet5-base](https://huggingface.co/Salesforce/codet5-base) model to provide context-aware solutions to C++ compilation errors.
*   **Compiler CLI Wrapper ([tutor.py](file:///c:/Users/dasar/Desktop/git%20demo/tutor.py))**: A drop-in wrapper around `g++`. Use it exactly like `g++` to compile files and get instant human-readable explanations on failure.
*   **Web App GUI ([app.py](file:///c:/Users/dasar/Desktop/git%20demo/app.py))**: A Gradio web app interface. Paste C++ code directly into the browser to compile it and read interactive diagnostic fixes.
*   **Active Data Collection Pipelines**:
    *   [generate_dataset.py](file:///c:/Users/dasar/Desktop/git%20demo/generate_dataset.py): Compiles broken C++ snippets locally using `g++` to generate clean synthetic `(error, explanation, suggested_fix)` datasets.
    *   [scrape_stack.py](file:///c:/Users/dasar/Desktop/git%20demo/scrape_stack.py): Queries the Stack Exchange API to fetch real-world Stack Overflow questions tagged `c++` and `compiler-errors` along with their accepted answer resolutions.
*   **Visual Training Dashboards**: Integrated with TensorBoard to monitor model training and validation loss metrics in real-time.
*   **Architecture Reference**: Features a complete [architecture_guide.md](file:///c:/Users/dasar/Desktop/git%20demo/architecture_guide.md) mapping core components and data structures.

---

## 🛠️ How It Works & Architecture

1.  **Data Collection**:
    *   *Synthetic Data*: [generate_dataset.py](file:///c:/Users/dasar/Desktop/git%20demo/generate_dataset.py) compiles broken code to yield clean pairs in [generated_dataset.json](file:///c:/Users/dasar/Desktop/git%20demo/generated_dataset.json).
    *   *Real-World Data*: [scrape_stack.py](file:///c:/Users/dasar/Desktop/git%20demo/scrape_stack.py) fetches real Stack Overflow Q&As and saves them in [scraped_dataset.json](file:///c:/Users/dasar/Desktop/git%20demo/scraped_dataset.json).
    *   *Pre-built Datasets*: A 2MB dataset of compiler errors is provided in [error_dataset.json](file:///c:/Users/dasar/Desktop/git%20demo/error_dataset.json).
2.  **Training**: The [train.py](file:///c:/Users/dasar/Desktop/git%20demo/train.py) script splits the data (80% train, 20% validation) and fine-tunes the CodeT5 model.
3.  **CLI Wrapper**: [tutor.py](file:///c:/Users/dasar/Desktop/git%20demo/tutor.py) intercepts compilation errors, filters compiler path noise, and queries the fine-tuned model via [inference.py](file:///c:/Users/dasar/Desktop/git%20demo/inference.py).
4.  **Web App**: [app.py](file:///c:/Users/dasar/Desktop/git%20demo/app.py) runs a Gradio interface. It handles temporary file compilation and returns side-by-side error listings and AI feedback.

---

## 📂 Project Structure

```text
.
├── app.py                  # Gradio Web App GUI
├── tutor.py                # Compiler CLI wrapper
├── inference.py            # Model loader & text generation logic
├── train.py                # Script to train/fine-tune the model
├── generate_dataset.py      # Script to create synthetic error data
├── scrape_stack.py         # Stack Overflow API Q&A scraper
├── error_dataset.json      # Large compiler error dataset
├── generated_dataset.json  # Synthetically generated dataset file
├── scraped_dataset.json    # Dataset fetched from Stack Overflow API
├── architecture_guide.md   # System architecture & code symbol reference
├── requirements.txt        # Python package dependencies
├── main.cpp                # Sample C++ file for diagnostics testing
└── Progress_readme.md      # Internal team progress log
```

---

## 💻 Installation

### 1. Prerequisites
You must have a C++ compiler installed on your system:
*   **Windows**: Install MinGW (providing `g++`).
*   **macOS**: Install Xcode Command Line Tools (`xcode-select --install`).
*   **Linux (Ubuntu)**: `sudo apt install build-essential g++`

### 2. Create and Activate Python Virtual Environment
```bash
# Create the environment
python -m venv venv

# Activate it (Windows PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# Activate it (Windows Command Prompt)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Make sure to install PyTorch matching your platform (e.g., CUDA capabilities if an NVIDIA GPU is available). See [PyTorch Locally](https://pytorch.org/get-started/locally/) for setup instructions.
Then install requirements:
```bash
pip install transformers sentencepiece gradio requests scikit-learn tensorboard
```

---

## 📖 Usage Workflow

### Step 1: Collect/Generate Data

*   **Option A: Generate Synthetic Data (Fast & Clean)**
    Run the compiler issue simulator to produce [generated_dataset.json](file:///c:/Users/dasar/Desktop/git%20demo/generated_dataset.json):
    ```bash
    python generate_dataset.py
    ```
*   **Option B: Scrape Real-World Data (Stack Overflow)**
    Run the API scraper to collect real Q&As into [scraped_dataset.json](file:///c:/Users/dasar/Desktop/git%20demo/scraped_dataset.json):
    ```bash
    python scrape_stack.py --limit 30
    ```
    *Note: Stack Exchange API allows 300 free requests per day. You can supply an optional `--api-key <key>` to raise query quotas.*

### Step 2: Train the Model
Run the fine-tuning script. You can pass the dataset to train on along with hyperparameters:
```bash
python train.py --dataset scraped_dataset.json --epochs 10 --batch_size 4 --lr 5e-5
```
*   *(Optional)* Run TensorBoard to view training curves:
    ```bash
    tensorboard --logdir=runs
    ```
    Open `http://localhost:6006/` in your browser.

### Step 3: Run the AI Tutor

*   **Option A: CLI Compiler Wrapper**
    Run [tutor.py](file:///c:/Users/dasar/Desktop/git%20demo/tutor.py) instead of `g++` to compile source code:
    ```bash
    python tutor.py main.cpp -o main
    ```
*   **Option B: Gradio Web App GUI**
    Launch the interactive web tool:
    ```bash
    python app.py
    ```
    Open `http://127.0.0.1:7860` in your web browser.

---

## 🔮 Future Work

*   **Human-in-the-Loop Logging**: Add 👍/👎 buttons in the Gradio web UI to log user satisfaction and corrections.
*   **Continuous Finetuning**: Periodically retrain models using the compiled user corrections log.
*   **Editor Extensions**: Build standard VS Code or CLion extensions wrapping the tutor endpoints.

---

## 📄 License

This project is licensed under the MIT License.