"""
Originele Gradio app volgens het blueprint - simpel en werkend.
"""

import gradio as gr
import tempfile
import os
import traceback
import conversion_service_original as conversion_service

async def process_pdf(uploaded_file):
    """
    An async generator function that handles the Gradio UI updates and
    triggers the PDF conversion. It yields dictionaries of gr.update()
    calls to manage the UI state.
    """
    if uploaded_file is None:
        yield {
            output_markdown: gr.update(value="Please upload a PDF file first."),
            download_button: gr.update(visible=False),
            error_details: gr.update(visible=False)
        }
        return

    # --- 1. Set UI to "Processing" state ---
    processing_updates = {
        file_input: gr.update(interactive=False),
        output_markdown: gr.update(value="⏳ Converting document, please wait... This may take a moment."),
        download_button: gr.update(visible=False),
        error_accordion: gr.update(visible=False)
    }
    yield processing_updates

    output_md_path = None
    try:
        # --- 2. Perform the conversion ---
        # The uploaded_file object has a.name attribute with the temp path
        markdown_content = await conversion_service.convert_pdf_to_markdown(uploaded_file.name)

        # --- 3. Set UI to "Success" state ---
        # Save the markdown content to a temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".md", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
            output_md_path = md_file.name

        success_updates = {
            output_markdown: gr.update(value=markdown_content),
            download_button: gr.update(visible=True, value=output_md_path),
        }
        yield success_updates

    except Exception as e:
        # --- 4. Set UI to "Error" state ---
        tb_str = traceback.format_exc()
        error_message = f"### ❌ Conversion Failed\n\nAn unexpected error occurred: {e}"
        error_updates = {
            output_markdown: gr.update(value=error_message),
            error_details: gr.update(value=f"```\n{tb_str}\n```"),
            error_accordion: gr.update(visible=True)
        }
        yield error_updates
    finally:
        # --- 5. Always re-enable the file input ---
        yield {file_input: gr.update(interactive=True)}

# --- Gradio UI Layout using gr.Blocks ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📄 PDF to Markdown Converter")
    gr.Markdown("Upload a PDF file to convert it into clean, LLM-ready Markdown. Powered by the Marker library.")

    with gr.Row():
        file_input = gr.File(label="Upload PDF", file_types=['.pdf'])

    with gr.Tabs():
        with gr.TabItem("Converted Markdown"):
            output_markdown = gr.Markdown(show_copy_button=True)
        with gr.TabItem("Download"):
            download_button = gr.DownloadButton(label="Download.md File", visible=False)
    
    with gr.Accordion("Error Details", open=False, visible=False) as error_accordion:
        error_details = gr.Markdown()

    # Bind the process_pdf function to the file upload event
    file_input.upload(
        fn=process_pdf,
        inputs=[file_input],
        outputs=[file_input, output_markdown, download_button, error_accordion, error_details]
    )

if __name__ == "__main__":
    demo.launch()
