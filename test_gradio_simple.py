"""
Eenvoudige test Gradio app om het probleem te debuggen.
"""

import gradio as gr
import tempfile
import traceback

# Import Windows fix first
import windows_fix
import conversion_service_subprocess as conversion_service

async def simple_process_pdf(uploaded_file):
    """Eenvoudige PDF verwerking functie."""
    print(f"🔍 Debug: Function called with file: {uploaded_file}")
    
    if uploaded_file is None:
        print("🔍 Debug: No file uploaded")
        return "Geen bestand geüpload"
    
    print(f"🔍 Debug: File name: {uploaded_file.name}")
    print(f"🔍 Debug: File exists: {os.path.exists(uploaded_file.name)}")
    
    try:
        # Test de conversie
        settings = {"output_format": "markdown"}
        print(f"🔍 Debug: Starting conversion with settings: {settings}")
        
        converted_content, output_format = await conversion_service.convert_pdf_with_subprocess(
            uploaded_file.name, settings
        )
        
        print(f"🔍 Debug: Conversion successful, length: {len(converted_content)}")
        return converted_content
        
    except Exception as e:
        print(f"🔍 Debug: Error occurred: {e}")
        import traceback
        print(f"🔍 Debug: Traceback: {traceback.format_exc()}")
        return f"Fout: {e}"

# Import os for file checking
import os

# Create simple Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Test PDF Converter")
    
    file_input = gr.File(label="Upload PDF", file_types=['.pdf'])
    output_text = gr.Textbox(label="Resultaat", lines=10)
    
    convert_button = gr.Button("Converteer")
    
    convert_button.click(
        fn=simple_process_pdf,
        inputs=[file_input],
        outputs=[output_text]
    )

if __name__ == "__main__":
    demo.launch()

