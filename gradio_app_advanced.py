"""
Uitgebreide Gradio web application voor PDF naar Markdown conversie.

Deze module implementeert een geavanceerde web interface met alle configuratie
opties van de Marker library. Gebruikers kunnen OCR-instellingen, LLM-verbetering,
output formaten en verwerkingsopties aanpassen.
"""

import gradio as gr
import tempfile
import traceback

# Import de werkende single-threaded conversion service
import conversion_service_original as conversion_service

def process_pdf(uploaded_file, progress=gr.Progress(track_tqdm=True), *settings_inputs):
    """
    Een eenvoudige async functie voor PDF-conversie.
    """
    if uploaded_file is None:
        return (
            "### Upload eerst een PDF-bestand.",
            "",
            gr.update(visible=False),
            gr.update(visible=False),
            ""
        )

    # --- 1. Verzamel instellingen van de UI-componenten ---
    keys = [
        "output_format", "paginate_output", "extract_images", "force_ocr", 
        "ocr_engine", "langs", "use_llm", "llm_service", "gemini_api_key", 
        "start_page", "max_pages", "batch_multiplier"
    ]
    settings = dict(zip(keys, settings_inputs))
    
    # Verwerk lege strings voor numerieke waarden
    if not settings["start_page"]: 
        settings["start_page"] = None
    if not settings["max_pages"]: 
        settings["max_pages"] = None
    if settings["langs"] == "": 
        settings["langs"] = None
    
    # Converteer naar lijst indien nodig
    if settings["langs"] and isinstance(settings["langs"], str):
        settings["langs"] = [lang.strip() for lang in settings["langs"].split(',')]

    # --- 2. Voer de conversie uit ---
    print(f"🔍 Debug: Starting conversion for file: {uploaded_file.name}")
    print(f"🔍 Debug: Settings: {settings}")
    
    try:
        import asyncio
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        converted_content = loop.run_until_complete(
            conversion_service.convert_pdf_with_settings(uploaded_file.name, settings)
        )
        loop.close()
        
        output_format = settings.get("output_format", "markdown")
        print(f"🔍 Debug: Conversion completed, output format: {output_format}")
        
        # --- 3. Zet UI in "Succes"-staat ---
        file_extension = f".{output_format}"
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=file_extension, encoding="utf-8") as out_file:
            out_file.write(converted_content)
            output_file_path = out_file.name
        
        return (
            converted_content,
            converted_content,
            gr.update(visible=True, value=output_file_path),
            gr.update(visible=False),
            ""
        )
        
    except Exception as e:
        # --- 4. Zet UI in "Fout"-staat ---
        print(f"🔍 Debug: Error occurred: {e}")
        tb_str = traceback.format_exc()
        print(f"🔍 Debug: Traceback: {tb_str}")
        
        error_message = f"### ❌ Conversie Mislukt\n\nEr is een onverwachte fout opgetreden: {e}"
        return (
            error_message,
            "",
            gr.update(visible=False),
            gr.update(visible=True),
            f"```\n{tb_str}\n```"
        )

# --- Gradio UI Layout met gr.Blocks ---
with gr.Blocks(theme=gr.themes.Soft(), title="Geavanceerde PDF Converter") as demo:
    gr.Markdown("# 📄 Geavanceerde PDF naar Markdown Converter")
    gr.Markdown("Upload een PDF en configureer de geavanceerde instellingen om het te converteren. Aangedreven door de Marker-bibliotheek.")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload PDF", file_types=['.pdf'])
            
            with gr.Accordion("Geavanceerde Instellingen", open=False) as settings_accordion:
                with gr.Tabs():
                    with gr.TabItem("Algemeen"):
                        output_format = gr.Radio(
                            ["markdown", "html", "json"], 
                            label="Output Formaat", 
                            value="markdown", 
                            info="Kies het gewenste outputformaat."
                        )
                        paginate_output = gr.Checkbox(
                            label="Voeg paginascheidingen toe", 
                            value=False, 
                            info="Voegt een horizontale lijn toe tussen de pagina's in de output."
                        )
                        extract_images = gr.Checkbox(
                            label="Extraheer afbeeldingen", 
                            value=True, 
                            info="Sla afbeeldingen uit de PDF op in de outputmap."
                        )
                    
                    with gr.TabItem("OCR"):
                        force_ocr = gr.Checkbox(
                            label="Forceer OCR op alle pagina's", 
                            value=False, 
                            info="Handig voor PDF's met onleesbare of 'garbled' tekst."
                        )
                        ocr_engine = gr.Radio(
                            ["surya", "ocrmypdf"], 
                            label="OCR Engine", 
                            value="surya", 
                            info="Surya is nauwkeuriger, ocrmypdf kan sneller zijn."
                        )
                        langs = gr.Textbox(
                            label="Talen voor OCR", 
                            placeholder="bv. en,nl,de", 
                            info="Door komma's gescheiden lijst. Optioneel voor Surya."
                        )

                    with gr.TabItem("LLM Verbetering"):
                        use_llm = gr.Checkbox(
                            label="Gebruik LLM voor hogere nauwkeurigheid", 
                            value=False, 
                            info="Verbetert tabel- en formuleverwerking. Vereist een API-sleutel."
                        )
                        with gr.Group(visible=False) as llm_settings_group:
                            llm_service = gr.Dropdown(
                                ["gemini"], 
                                label="LLM Service", 
                                value="gemini", 
                                info="Momenteel wordt alleen Gemini ondersteund in deze demo."
                            )
                            gemini_api_key = gr.Textbox(
                                label="Gemini API Key", 
                                type="password", 
                                placeholder="Voer uw Google AI Studio API-sleutel in"
                            )
                        
                        use_llm.change(lambda x: gr.update(visible=x), use_llm, llm_settings_group)

                    with gr.TabItem("Verwerking"):
                        start_page = gr.Number(
                            label="Startpagina", 
                            value=None, 
                            precision=0, 
                            info="Pagina om de conversie te starten (optioneel)."
                        )
                        max_pages = gr.Number(
                            label="Maximaal aantal pagina's", 
                            value=None, 
                            precision=0, 
                            info="Beperk het aantal te verwerken pagina's (optioneel)."
                        )
                        batch_multiplier = gr.Slider(
                            label="Batch Multiplier", 
                            minimum=1, 
                            maximum=8, 
                            step=1, 
                            value=2, 
                            info="Verhoog als u meer VRAM heeft voor snellere verwerking."
                        )

            convert_button = gr.Button("Converteer PDF", variant="primary")

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("Geformatteerde Output"):
                    output_markdown = gr.Markdown(show_copy_button=True, label="Resultaat")
                with gr.TabItem("Ruwe Output"):
                    output_raw = gr.Code(label="Broncode", language="markdown")
                with gr.TabItem("Download"):
                    download_button = gr.DownloadButton(label="Download Bestand", visible=False)
            
            with gr.Accordion("Foutdetails", open=False, visible=False) as error_accordion:
                error_details = gr.Markdown()

    # Bundel alle instellingen voor de functie-aanroep
    settings_components = [
        output_format, paginate_output, extract_images, force_ocr, ocr_engine, 
        langs, use_llm, llm_service, gemini_api_key, start_page, max_pages, batch_multiplier
    ]
    
    convert_button.click(
        fn=process_pdf,
        inputs=[file_input] + settings_components,
        outputs=[output_markdown, output_raw, download_button, error_accordion, error_details]
    )

if __name__ == "__main__":
    print("🌐 Starting Advanced Gradio web application...")
    print("📋 Features:")
    print("   - Drag & drop PDF upload")
    print("   - Advanced configuration options")
    print("   - OCR settings (Surya/ocrmypdf)")
    print("   - LLM enhancement (Gemini)")
    print("   - Multiple output formats")
    print("   - Batch processing options")
    print("   - Real-time progress feedback")
    print("   - Error handling with detailed logs")
    print()
    
    demo.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        share=False,  # Set to True if you want a public link
        show_error=True
    )
