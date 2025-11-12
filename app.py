import gradio as gr
from tutor import explain_error, load_model
import subprocess
import os

# --- 1. LOAD THE MODEL (ONCE!) ---
load_model()

# --- Configuration ---
TEMP_FILE = "_app_temp.cpp"  # A temporary file to compile
COMPILER = "g++"             # The compiler to use

def compile_and_explain(code_string):
    """
    This new function will:
    1. Take the user's C++ code as a string.
    2. Save it to a temp file.
    3. Run g++ and capture the error.
    4. Clean the error.
    5. Call your AI model for the explanation.
    """
    
    # 1. Save code to a temp file
    try:
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(code_string)
    except Exception as e:
        return f"Error writing temp file: {e}", ""

    # 2. Run the compiler
    result = subprocess.run(
        [COMPILER, TEMP_FILE],
        capture_output=True,
        text=True
    )
    
    # 3. Clean up the temp file
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
            
    full_error = result.stderr
    
    # 4. Check if compilation was successful
    if not full_error:
        return "--- Compile Successful! ---", "No errors found."
            
    # 5. Clean the error (to remove system noise)
    clean_error = ""
    for line in full_error.splitlines():
        if TEMP_FILE in line: # Only keep lines that reference our temp file
            clean_error += line.replace(TEMP_FILE, "your_code.cpp") + "\n"
    
    if not clean_error: # Fallback if no lines matched (e.g., linker error)
        clean_error = full_error
            
    # 6. Get the AI explanation
    try:
        friendly_explanation = explain_error(clean_error)
        # Return both the original error and the friendly one
        return full_error, friendly_explanation
    except Exception as e:
        return full_error, f"Error calling AI model: {e}"

# --- 2. Create the Web Interface (V2) ---
iface = gr.Interface(
    fn=compile_and_explain,  # <-- Use our new all-in-one function
    
    # Use gr.Code for C++ syntax highlighting
    inputs=gr.Code(language="cpp", lines=15, label="Your C++ Code"),
    
    # Use two outputs: one for the raw error, one for the AI
    outputs=[
        gr.Textbox(label="Original Compiler Error"),
        gr.Markdown(label="Friendly Explanation") # Use Markdown for nice formatting
    ],
    
    title="C++ AI Tutor (v2.0)",
    description="Write your C++ code, and this will compile it and explain any errors.",
    examples=[
        ["#include <iostream>\n\nint main() {\n    cout << \"Hello\";\n    return 0;\n}"],
        ["int main() {\n    x = 5;\n    return 0\n}"]
    ]
)

# --- 3. Launch the App ---
iface.launch()