C++ AI Tutor: The Smart CompilerThis project is a Python-based tool that intercepts C++ compiler errors and provides simple, human-readable explanations and suggested fixes. Instead of a cryptic message like `expected ';' before '}' token`, users get a friendly explanation of what went wrong and how to fix it.

It's powered by a fine-tuned `CodeT5` (a code-aware Transformer model) trained on a hybrid dataset of synthetically generated errors and real-world examples from Stack Overflow.

Features
* ###AI-Powered Diagnostics: Uses a fine-tuned Salesforce/codet5-base model to provide specific, context-aware explanations for compiler errors.
* ###Compiler Wrapper (tutor.py): A command-line tool that acts as a wrapper around g++. You can use it as a drop-in replacement to get instant, friendly feedback.
* ###Web App GUI (app.py): A simple, user-friendly web app built with Gradio. Users can paste their C++ code, and the app will compile it and explain any errors.
* ###Hybrid Dataset Generation: *Includes two scripts*:
    `generate_dataset.py`:Creates thousands of "clean" examples by deliberately breaking C++ code and capturing the compiler output.
    `scrape_stack.py`: Fetches thousands of "noisy" real-world examples from the Stack Exchange API.
* ###Live Training Dashboard: Uses TensorBoard to visualize the model's training loss in real-time.

###How It Works:Architecture
1. *Data Collection:* A large-scale "hybrid" dataset is created by merging two sources:
    * *Synthetic Data:* `generate_dataset.py` runs g++ against thousands of deliberately broken C++ snippets to get perfect, clean `(error, explanation)` pairs.
    * *Real-World Data:* `scrape_stack.py` queries the Stack Exchange API for questions tagged `[c++]` and `[compiler-error]` and parses the accepted answers.
2. *Training:* The `train.py` script fine-tunes a `Salesforce/codet5-base model` on this hybrid dataset. It learns the pattern between a compiler error and its corresponding human-friendly explanation.
3. *Inference (Wrapper)*: The `tutor.py` script is called from the command line (e.g., `python tutor.py main.cpp)`.
    * It executes the real `g++` compiler using `subprocess`.
    * It captures the `stderr` output (the error message).
    * It "cleans" the error message to remove system-specific noise.
    * It feeds the clean error to the fine-tuned model.
    * It prints the original error, followed by the model's friendly explanation
4. *Inference (Web App):* The `app.py` script loads the model once and provides a Gradio interface. It takes the user's C++ code, saves it to a temp file, runs the `g++` subprocess, and returns the error and explanation to the UI.

###Project Structure
```
.
├── app.py             # Gradio Web App GUI
├── tutor.py           # The compiler wrapper (CLI tool)
├── train.py           # Script to train the model
├── generate_dataset.py # Script to create synthetic data
├── scrape_stack.py    # Script to scrape Stack Overflow
├── merge_datasets.py  # Script to combine the datasets
├── requirements.txt   # Python dependencies
├── main.cpp           # A sample C++ file for testing
└── .venv/             # Your local Python virtual environment
```
Installation
1. Clone the Repository
```
git clone [https://github.com/your-username/your-project-name.git](https://github.com/your-username/your-project-name.git)
cd your-project-name
```
2. *Install C++ Compiler* You must have a C++ compiler installed on your system.
    * On Windows: Install MinGW (which provides `g++`).
    * On macOS: Install Xcode Command Line Tools (`xcode-select --install`).
    * On Linux (Ubuntu): `sudo apt install build-essential g++3`. 
3. *Create and Activate a Python Virtual Environment*
```
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
4. *Install Python Dependencies* You must install PyTorch first, specifying the correct command for your CUDA setup (if you have an NVIDIA GPU).
```
# 1. Install PyTorch (This example is for CUDA 12.1)
# See [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) for the right command for your system
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)

# 2. Install the rest of the requirements
pip install transformers sentencepiece gradio requests PySimpleGUI tensorboard
```
###Usage: A 4-Step Workflow
*Step 1: Create the Dataset*
You need data to train on. You have two options.
    * *Option A: Generate Synthetic Data (Fast & Clean)*Run the generator script. This will create `generated_dataset.json` with 50+ high-quality examples.
    `(venv) $ python generate_dataset.py`
    * *Option B: Scrape Real-World Data (Large & Messy)*
    1. Get a Stack Exchange API Key from stackapps.com/apps/register.
    2. Paste your key into the `API_KEY` variable in `scrape_stack.py`.
    3. Run the script (this will take a few minutes).
    `(venv) $ python scrape_stack.py`
    * *Option C: The Hybrid Dataset (Recommended)*Run both scripts, then merge them.(venv) $ python merge_datasets.py
*Step 2: Train the Model*
1. Open train.py and make sure the `MODEL_NAME` is set to `"Salesforce/codet5-base"` and the `FILE_PATH` points to your dataset (e.g., `hybrid_dataset.json`).
2. Run the training script. This will take a long time and requires a CUDA-enabled GPU.`
    `(venv) $ python train.py`
3. *(Optional) Watch the Training Live*:While Step 2 is running, open a second terminal, activate your venv, and run:
    `(venv) $ tensorboard --logdir=runs`
Open `http://localhost:6006/` in your browser to see the live loss curve.
*Step 3: Use the AI Tutor (Choose one)*
Once your model is trained (a `fine_tuned_t5_compiler_tutor` folder exists), you can use the tool.
* *Option A: As a Command-Line Tool* Use `python tutor.py` as a replacement for `g++`.
    `(venv) $ python tutor.py main.cpp -o main`
Output:
```
--- Running compiler : g++ main.cpp -o main ---
--- Original Compiler error ---
main.cpp:6:1: error: expected ';' before '}' token
  }
  ^
--- Friendly explanation ---
This is a syntax error. It looks like you missed a semicolon (;) on the line
before the closing brace '}' on line 6.
```
* *Option B: As a Web AppRun the Gradio app script*.
    `(venv) $ python app.py`
    Now open `http://127.0.0.1:7860` in your web browser to use the GUI.
###Future Work
* Feedback Loop: Add (👍 / 👎) buttons to the Gradio app to log user feedback.
* Continuous Improvement: Periodically re-train the model with the user-submitted feedback to create a "human-in-the-loop" system.
* VS Code Extension: Re-build the logic as a proper VS Code extension for real-time, in-editor diagnostics.

###License
This project is licensed under the MIT License.