import gradio as gr
from tutor import explain_error, load_model  # <-- Import BOTH functions

# --- 1. LOAD THE MODEL (ONCE!) ---
# This line runs when you start `python app.py`
# It will be slow here, but that's what we want.
load_model()

# --- 2. Create the Web Interface ---
iface = gr.Interface(
    fn=explain_error,  # <-- This just calls the FAST inference function
    inputs=gr.Textbox(lines=10, placeholder="Paste your compiler error here...", label="Compiler Error"),
    outputs=gr.Textbox(label="Friendly Explanation"),
    title="C++ AI Tutor",
    description="Get simple, easy-to-understand explanations for C++ compiler errors."
)

# --- 3. Launch the App ---
iface.launch()