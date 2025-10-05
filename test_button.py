"""
Super eenvoudige test om te zien of de knop überhaupt werkt.
"""

import gradio as gr

def test_function():
    """Test functie die alleen tekst teruggeeft."""
    print("🔍 BUTTON CLICKED!")
    return "✅ Knop werkt! Dit is een test."

# Create super simple interface
with gr.Blocks() as demo:
    gr.Markdown("# Test Interface")
    
    test_button = gr.Button("Test Knop", variant="primary")
    output_text = gr.Textbox(label="Resultaat")
    
    test_button.click(
        fn=test_function,
        inputs=[],
        outputs=[output_text]
    )

if __name__ == "__main__":
    print("🔍 Starting Button Test...")
    demo.launch()
