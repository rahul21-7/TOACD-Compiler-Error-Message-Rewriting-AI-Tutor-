import gradio as gr
from tutor import explain_error  # <-- Import your existing function!

# Define the function for Gradio to call
# This is just a simple wrapper around your function
def get_explanation(compiler_error):
    # The 'explain_error' function returns the AI's text
    try:
        return explain_error(compiler_error)
    except Exception as e:
        return f"Error running model: {e}"

# --- Create the Web Interface ---
iface = gr.Interface(
    fn=get_explanation,           # The function to call
    inputs=gr.Textbox(lines=10, placeholder="Paste your compiler error here...", label="Compiler Error"),
    outputs=gr.Textbox(label="Friendly Explanation"),
    title="C++ AI Tutor",
    description="Get simple, easy-to-understand explanations for C++ compiler errors."
)

# --- Launch the App ---
iface.launch()