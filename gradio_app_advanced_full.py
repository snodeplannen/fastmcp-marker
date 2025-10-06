"""
Geavanceerde Gradio web application voor PDF naar Markdown conversie.
Implementeert alle belangrijke Marker library opties met logische indeling.
"""

import gradio as gr
import traceback
import asyncio
from typing import Any

# Import de nieuwe zip-enabled conversion service
import conversion_service_zip as conversion_service

def process_pdf(uploaded_files: Any, progress: Any = gr.Progress(track_tqdm=True), *settings_inputs: Any) -> Any:
    """
    Een functie voor PDF-conversie met alle geavanceerde instellingen.
    Ondersteunt nu zowel enkele als meerdere PDF-bestanden.
    """
    if uploaded_files is None or len(uploaded_files) == 0:
        return (
            "### Upload eerst een of meerdere PDF-bestanden.",
            "",
            gr.update(visible=False),
            gr.update(visible=False),
            ""
        )
    
    # Normaliseer naar lijst voor consistente verwerking
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]

    # Update UI to show processing state
    file_count = len(uploaded_files)
    file_names = [f.name for f in uploaded_files]
    
    yield (
        f"### ⏳ PDF Conversie Gestart\n\n**{file_count} bestand{'en' if file_count > 1 else ''}** worden verwerkt:\n" +
        "\n".join([f"• {name}" for name in file_names]) +
        "\n\nDe conversie is begonnen. Dit kan even duren...",
        "",
        gr.update(visible=False),
        gr.update(visible=False),
        ""
    )

    # --- Verzamel alle instellingen ---
    keys = [
        # Basis instellingen
        "output_format", "page_range", "debug", "output_dir",
        # OCR instellingen
        "force_ocr", "strip_existing_ocr", "disable_ocr", "languages",
        "ocr_space_threshold", "ocr_newline_threshold", "ocr_alphanum_threshold",
        # LLM instellingen - Provider selectie
        "use_llm", "llm_provider",
        # Gemini instellingen
        "google_api_key", "gemini_model_name",
        # OpenAI instellingen
        "openai_api_key", "openai_model_name", "openai_base_url",
        # Anthropic instellingen
        "anthropic_api_key", "anthropic_model_name",
        # Azure instellingen
        "azure_api_key", "azure_endpoint", "azure_deployment", "azure_api_version",
        # Ollama instellingen
        "ollama_base_url", "ollama_model_name",
        # Custom instellingen
        "custom_api_key", "custom_base_url", "custom_model_name",
        # Algemene LLM instellingen
        "max_retries", "max_concurrency", "timeout", "temperature", "max_tokens",
        # LLM Functionaliteit
        "use_llm_layout", "use_llm_table", "use_llm_equation", "use_llm_handwriting",
        "use_llm_complex_region", "use_llm_form", "use_llm_image_description", 
        "use_llm_table_merge", "use_llm_text",
        # LLM Prompts
        "layout_prompt", "table_prompt", "equation_prompt", "handwriting_prompt",
        "complex_relabeling_prompt", "table_rewriting_prompt", "table_merge_prompt", "image_description_prompt",
        # LLM Thresholds & Instellingen
        "confidence_threshold", "picture_height_threshold", "min_equation_height", "equation_image_expansion_ratio",
        "max_rows_per_batch", "table_image_expansion_ratio", "table_height_threshold",
        "table_start_threshold", "vertical_table_height_threshold", "vertical_table_distance_threshold",
        "horizontal_table_width_threshold", "horizontal_table_distance_threshold", "column_gap_threshold",
        "image_expansion_ratio",
        # Layout instellingen
        "lowres_image_dpi", "highres_image_dpi", "layout_coverage_threshold", "document_ocr_threshold",
        # Tabel instellingen
        "detect_boxes", "max_table_rows", "row_split_threshold", "column_gap_ratio",
        # Performance instellingen
        "pdftext_workers", "batch_size", "recognition_batch_size", "detection_batch_size",
        # Output instellingen
        "extract_images", "paginate_output", "page_separator", "disable_links",
        # Debug instellingen
        "debug_layout_images", "debug_pdf_images", "debug_json", "debug_data_folder"
    ]
    
    settings = dict(zip(keys, settings_inputs))
    
    # Verwerk lege strings en None waarden
    for key in ["page_range", "output_dir", "languages", "page_separator", "debug_data_folder",
                "google_api_key", "gemini_model_name", "openai_api_key", "openai_model_name", "openai_base_url",
                "anthropic_api_key", "anthropic_model_name", "azure_api_key", "azure_endpoint", 
                "azure_deployment", "azure_api_version", "ollama_base_url", "ollama_model_name",
                "custom_api_key", "custom_base_url", "custom_model_name",
                "layout_prompt", "table_prompt", "equation_prompt", "handwriting_prompt",
                "complex_relabeling_prompt", "table_rewriting_prompt", "table_merge_prompt", "image_description_prompt"]:
        if settings[key] == "":
            settings[key] = None
    
    # Converteer numerieke waarden
    for key in ["ocr_space_threshold", "ocr_newline_threshold", "ocr_alphanum_threshold", 
                "layout_coverage_threshold", "document_ocr_threshold", "row_split_threshold", 
                "column_gap_ratio", "lowres_image_dpi", "highres_image_dpi", "max_table_rows",
                "pdftext_workers", "max_retries", "max_concurrency", "timeout", "max_tokens",
                "temperature", "confidence_threshold", "picture_height_threshold", "min_equation_height",
                "equation_image_expansion_ratio", "max_rows_per_batch", "table_image_expansion_ratio",
                "table_height_threshold", "table_start_threshold", "vertical_table_height_threshold",
                "vertical_table_distance_threshold", "horizontal_table_width_threshold",
                "horizontal_table_distance_threshold", "column_gap_threshold", "image_expansion_ratio"]:
        if settings[key] is None or settings[key] == "":
            settings[key] = None
        else:
            try:
                settings[key] = float(settings[key]) if "." in str(settings[key]) else int(settings[key])
            except (ValueError, TypeError):
                settings[key] = None
    
    # KRITIEK: Forceer pdftext_workers altijd op 1 voor stabiliteit
    settings["pdftext_workers"] = 1
    print("🔒 Forced pdftext_workers to 1 for stability")
    
    # Converteer boolean waarden
    for key in ["debug", "force_ocr", "strip_existing_ocr", "disable_ocr", "use_llm", 
                "detect_boxes", "extract_images", "paginate_output", "disable_links",
                "debug_layout_images", "debug_pdf_images", "debug_json",
                "use_llm_layout", "use_llm_table", "use_llm_equation", "use_llm_handwriting",
                "use_llm_complex_region", "use_llm_form", "use_llm_image_description", 
                "use_llm_table_merge", "use_llm_text"]:
        settings[key] = bool(settings[key])
    
    # Converteer talen naar lijst
    if settings["languages"] and isinstance(settings["languages"], str):
        settings["languages"] = [lang.strip() for lang in settings["languages"].split(',')]

    # Filter LLM instellingen op basis van geselecteerde provider
    llm_provider = settings.get("llm_provider", "gemini")
    use_llm = settings.get("use_llm", False)
    
    # Verwijder LLM instellingen van niet-geselecteerde providers
    providers = ["gemini", "openai", "anthropic", "azure", "ollama", "custom"]
    for provider in providers:
        if provider != llm_provider:
            # Verwijder API keys en instellingen van andere providers
            if provider == "gemini":
                settings.pop("google_api_key", None)
                settings.pop("gemini_model_name", None)
            elif provider == "openai":
                settings.pop("openai_api_key", None)
                settings.pop("openai_model_name", None)
                settings.pop("openai_base_url", None)
            elif provider == "anthropic":
                settings.pop("anthropic_api_key", None)
                settings.pop("anthropic_model_name", None)
            elif provider == "azure":
                settings.pop("azure_api_key", None)
                settings.pop("azure_endpoint", None)
                settings.pop("azure_deployment", None)
                settings.pop("azure_api_version", None)
            elif provider == "ollama":
                settings.pop("ollama_base_url", None)
                settings.pop("ollama_model_name", None)
            elif provider == "custom":
                settings.pop("custom_api_key", None)
                settings.pop("custom_base_url", None)
                settings.pop("custom_model_name", None)
    
    # Als LLM niet gebruikt wordt, verwijder alle LLM-specifieke instellingen
    if not use_llm:
        llm_specific_keys = [
            "llm_provider", "google_api_key", "gemini_model_name",
            "openai_api_key", "openai_model_name", "openai_base_url",
            "anthropic_api_key", "anthropic_model_name",
            "azure_api_key", "azure_endpoint", "azure_deployment", "azure_api_version",
            "ollama_base_url", "ollama_model_name",
            "custom_api_key", "custom_base_url", "custom_model_name",
            "max_retries", "max_concurrency", "timeout", "temperature", "max_tokens",
            "use_llm_layout", "use_llm_table", "use_llm_equation", "use_llm_handwriting",
            "use_llm_complex_region", "use_llm_form", "use_llm_image_description", 
            "use_llm_table_merge", "use_llm_text",
            "layout_prompt", "table_prompt", "equation_prompt", "handwriting_prompt",
            "complex_relabeling_prompt", "table_rewriting_prompt", "table_merge_prompt", "image_description_prompt",
            "confidence_threshold", "picture_height_threshold", "min_equation_height", "equation_image_expansion_ratio",
            "max_rows_per_batch", "table_image_expansion_ratio", "table_height_threshold",
            "table_start_threshold", "vertical_table_height_threshold", "vertical_table_distance_threshold",
            "horizontal_table_width_threshold", "horizontal_table_distance_threshold", "column_gap_threshold",
            "image_expansion_ratio"
        ]
        for key in llm_specific_keys:
            settings.pop(key, None)

    print(f"🔍 Debug: Starting batch conversion for {file_count} files")
    print(f"🔍 Debug: LLM Provider: {llm_provider}, Use LLM: {use_llm}")
    print(f"🔍 Debug: Settings count after filtering: {len(settings)}")
    print("🔍 Debug: Key settings:")
    for key, value in settings.items():
        if value is not None and value != "" and value:
            print(f"  {key}: {value}")
    
    # Update UI to show detailed processing
    llm_info = "Nee"
    if use_llm:
        provider_name = llm_provider.title()
        if llm_provider == "gemini":
            model_name = settings.get("gemini_model_name", "gemini-2.0-flash")
        elif llm_provider == "openai":
            model_name = settings.get("openai_model_name", "gpt-4o")
        elif llm_provider == "anthropic":
            model_name = settings.get("anthropic_model_name", "claude-3-5-sonnet-20241022")
        elif llm_provider == "azure":
            model_name = settings.get("azure_deployment", "azure-model")
        elif llm_provider == "ollama":
            model_name = settings.get("ollama_model_name", "llama3.2:latest")
        elif llm_provider == "custom":
            model_name = settings.get("custom_model_name", "custom-model")
        else:
            model_name = "unknown"
        llm_info = f"Ja ({provider_name}: {model_name})"
    
    yield (
        "### 🔄 PDF Conversie in Uitvoering\n\n" +
        f"**Bestanden:** {file_count} bestand{'en' if file_count > 1 else ''}\n" +
        f"**Output Formaat:** {settings.get('output_format', 'markdown')}\n" +
        f"**LLM Gebruik:** {llm_info}\n" +
        f"**OCR:** {'Geforceerd' if settings.get('force_ocr') else 'Automatisch'}\n" +
        f"**Instellingen:** {len(settings)} parameters\n\n" +
        "⏳ De conversie is bezig... Dit kan 30 seconden tot enkele minuten duren.",
        "",
        gr.update(visible=False),
        gr.update(visible=False),
        ""
    )
    
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        progress(0.1, desc="Conversie gestart...")
        
        # Gebruik de nieuwe zip-enabled conversion service
        zip_path, combined_content = loop.run_until_complete(
            conversion_service.convert_multiple_pdfs_with_zip(
                uploaded_files, 
                settings,
                include_debug=settings.get("include_debug_in_zip", False),
                include_images=settings.get("include_images_in_zip", True)
            )
        )
        
        loop.close()
        
        progress(0.9, desc="Conversie voltooid, verwerken van resultaat...")
        
        print(f"🔍 Debug: Conversion completed, zip created: {zip_path}")
        
        progress(1.0, desc="Conversie succesvol voltooid!")
        
        # Update status message
        status_message = "### ✅ Conversie Voltooid\n\n"
        status_message += f"**{file_count}** bestand{'en' if file_count > 1 else ''} succesvol geconverteerd.\n\n"
        status_message += "Alle gegenereerde bestanden zijn opgeslagen in het ZIP-bestand, inclusief:\n"
        status_message += "• Geconverteerde tekst (Markdown/HTML/JSON)\n"
        if settings.get("include_images_in_zip", True):
            status_message += "• Geëxtraheerde afbeeldingen\n"
        if settings.get("include_debug_in_zip", False):
            status_message += "• Debug bestanden en afbeeldingen\n"
        status_message += "\nDownload het ZIP-bestand om alle bestanden te bekijken."
        
        yield (
            combined_content,
            combined_content,
            gr.update(visible=True, value=zip_path),
            gr.update(visible=False),
            ""
        )
        
    except Exception as e:
        # --- Zet UI in "Fout"-staat ---
        print(f"🔍 Debug: Error occurred: {e}")
        tb_str = traceback.format_exc()
        print(f"🔍 Debug: Traceback: {tb_str}")
        
        error_message = f"### ❌ Conversie Mislukt\n\nEr is een onverwachte fout opgetreden: {e}"
        yield (
            error_message,
            "",
            gr.update(visible=False),
            gr.update(visible=True),
            f"```\n{tb_str}\n```"
        )

# --- Gradio UI Layout met uitgebreide instellingen ---
with gr.Blocks(theme=gr.themes.Soft(), title="Geavanceerde PDF Converter") as demo:
    gr.Markdown("# 📄 Geavanceerde PDF naar Markdown Converter")
    gr.Markdown("Upload één of meerdere PDF-bestanden en configureer alle Marker library opties voor optimale conversie. "
                "Alle gegenereerde bestanden (tekst, afbeeldingen, debug data) worden automatisch verpakt in een ZIP-bestand voor download. "
                "Je kunt ook alleen de geconverteerde tekst bekijken in de preview.")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="Upload PDF(s)", 
                file_types=['.pdf'],
                file_count="multiple"
            )
            
            with gr.Accordion("⚙️ Basis Instellingen", open=True) as basic_settings:
                output_format = gr.Radio(
                    ["markdown", "html", "json"], 
                    label="Output Formaat", 
                    value="markdown", 
                    info="Kies het gewenste outputformaat."
                )
                page_range = gr.Textbox(
                    label="Pagina Bereik", 
                    placeholder="bv. 0,5-10,20 of leeg voor alle pagina's",
                    info="Comma gescheiden pagina nummers of ranges."
                )
                debug = gr.Checkbox(
                    label="Debug Modus", 
                    value=False,
                    info="Activeer debug output voor troubleshooting."
                )
                output_dir = gr.Textbox(
                    label="Output Directory", 
                    placeholder="Leeg voor standaard locatie",
                    info="Directory om output op te slaan."
                )
            
            with gr.Accordion("🔍 OCR & Tekst Verwerking", open=False) as ocr_settings:
                force_ocr = gr.Checkbox(
                    label="Forceer OCR", 
                    value=False,
                    info="Forceer OCR op het hele document."
                )
                strip_existing_ocr = gr.Checkbox(
                    label="Strip Bestaande OCR", 
                    value=False,
                    info="Verwijder bestaande OCR tekst en her-OCR."
                )
                disable_ocr = gr.Checkbox(
                    label="Schakel OCR Uit", 
                    value=False,
                    info="Schakel OCR verwerking uit."
                )
                languages = gr.Textbox(
                    label="Talen voor OCR", 
                    placeholder="bv. en,nl,de",
                    info="Comma gescheiden lijst van talen."
                )
                ocr_space_threshold = gr.Number(
                    label="OCR Space Threshold", 
                    value=0.7,
                    info="Minimum ratio van spaties voor slechte tekst detectie."
                )
                ocr_newline_threshold = gr.Number(
                    label="OCR Newline Threshold", 
                    value=0.6,
                    info="Minimum ratio van newlines voor slechte tekst detectie."
                )
                ocr_alphanum_threshold = gr.Number(
                    label="OCR Alphanumeric Threshold", 
                    value=0.3,
                    info="Minimum ratio van alfanumerieke karakters."
                )
            
            with gr.Accordion("🤖 LLM & AI Verbetering", open=False) as llm_settings:
                use_llm = gr.Checkbox(
                    label="Gebruik LLM", 
                    value=True,
                    info="Activeer LLM voor hogere kwaliteit verwerking."
                )
                
                llm_provider = gr.Radio(
                    ["gemini", "openai", "anthropic", "azure", "ollama", "custom"],
                    label="LLM Provider",
                    value="ollama",
                    info="Kies de LLM provider voor AI verbetering."
                )
                
                with gr.Group(visible=False) as gemini_settings:
                    google_api_key = gr.Textbox(
                        label="Google API Key", 
                        type="password",
                        placeholder="Voer uw Google AI Studio API-sleutel in",
                        info="Vereist voor Gemini functionaliteit."
                    )
                    gemini_model_name = gr.Dropdown(
                        ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                        label="Gemini Model", 
                        value="gemini-2.0-flash",
                        info="Gemini model versie."
                    )
                
                with gr.Group(visible=False) as openai_settings:
                    openai_api_key = gr.Textbox(
                        label="OpenAI API Key", 
                        type="password",
                        placeholder="sk-...",
                        info="Vereist voor OpenAI functionaliteit."
                    )
                    openai_model_name = gr.Dropdown(
                        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                        label="OpenAI Model", 
                        value="gpt-4o",
                        info="OpenAI model versie."
                    )
                    openai_base_url = gr.Textbox(
                        label="OpenAI Base URL", 
                        placeholder="https://api.openai.com/v1",
                        info="Custom OpenAI API endpoint (optioneel)."
                    )
                
                with gr.Group(visible=False) as anthropic_settings:
                    anthropic_api_key = gr.Textbox(
                        label="Anthropic API Key", 
                        type="password",
                        placeholder="sk-ant-...",
                        info="Vereist voor Anthropic functionaliteit."
                    )
                    anthropic_model_name = gr.Dropdown(
                        ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                        label="Anthropic Model", 
                        value="claude-3-5-sonnet-20241022",
                        info="Anthropic model versie."
                    )
                
                with gr.Group(visible=False) as azure_settings:
                    azure_api_key = gr.Textbox(
                        label="Azure API Key", 
                        type="password",
                        placeholder="Azure API key",
                        info="Vereist voor Azure OpenAI functionaliteit."
                    )
                    azure_endpoint = gr.Textbox(
                        label="Azure Endpoint", 
                        placeholder="https://your-resource.openai.azure.com/",
                        info="Azure OpenAI endpoint URL."
                    )
                    azure_deployment = gr.Textbox(
                        label="Azure Deployment", 
                        placeholder="gpt-4-deployment",
                        info="Azure deployment naam."
                    )
                    azure_api_version = gr.Textbox(
                        label="Azure API Version", 
                        value="2024-02-15-preview",
                        info="Azure API versie."
                    )
                
                with gr.Group(visible=True) as ollama_settings:
                    ollama_base_url = gr.Textbox(
                        label="Ollama Base URL", 
                        value="http://localhost:11434",
                        info="Ollama server URL."
                    )
                    ollama_model_name = gr.Textbox(
                        label="Ollama Model", 
                        value="llama3.2:latest",
                        placeholder="llama3.2:latest, codellama, mistral, etc.",
                        info="Ollama model naam."
                    )
                
                with gr.Group(visible=False) as custom_settings:
                    custom_api_key = gr.Textbox(
                        label="Custom API Key", 
                        type="password",
                        placeholder="Custom API key",
                        info="API key voor custom provider."
                    )
                    custom_base_url = gr.Textbox(
                        label="Custom Base URL", 
                        placeholder="https://api.custom-provider.com/v1",
                        info="Custom provider endpoint."
                    )
                    custom_model_name = gr.Textbox(
                        label="Custom Model", 
                        placeholder="custom-model-name",
                        info="Custom model naam."
                    )
                
                # Algemene LLM instellingen
                with gr.Group():
                    max_retries = gr.Number(
                        label="Max Retries", 
                        value=3,
                        precision=0,
                        info="Maximum aantal retries voor LLM requests."
                    )
                    max_concurrency = gr.Number(
                        label="Max Concurrency", 
                        value=3,
                        precision=0,
                        info="Maximum aantal gelijktijdige requests."
                    )
                    timeout = gr.Number(
                        label="Timeout (seconden)", 
                        value=60,
                        precision=0,
                        info="Timeout voor LLM requests."
                    )
                    temperature = gr.Slider(
                        label="Temperature", 
                        minimum=0.0, 
                        maximum=2.0, 
                        value=0.1,
                        step=0.1,
                        info="Creativiteit van de LLM (0.0 = deterministisch, 2.0 = zeer creatief)."
                    )
                    max_tokens = gr.Number(
                        label="Max Tokens", 
                        value=4096,
                        precision=0,
                        info="Maximum aantal tokens in response."
                    )
                
                # LLM-specifieke functionaliteit
                with gr.Group():
                    gr.Markdown("### 🔧 LLM Functionaliteit")
                    use_llm_layout = gr.Checkbox(
                        label="LLM Layout Builder", 
                        value=False,
                        info="Gebruik LLM voor layout detectie en verbetering."
                    )
                    use_llm_table = gr.Checkbox(
                        label="LLM Table Processor", 
                        value=False,
                        info="Gebruik LLM voor tabel verwerking en verbetering."
                    )
                    use_llm_equation = gr.Checkbox(
                        label="LLM Equation Processor", 
                        value=False,
                        info="Gebruik LLM voor vergelijkingen en LaTeX generatie."
                    )
                    use_llm_handwriting = gr.Checkbox(
                        label="LLM Handwriting Processor", 
                        value=False,
                        info="Gebruik LLM voor handschrift OCR."
                    )
                    use_llm_complex_region = gr.Checkbox(
                        label="LLM Complex Region Processor", 
                        value=False,
                        info="Gebruik LLM voor complexe regio's en afbeeldingen."
                    )
                    use_llm_form = gr.Checkbox(
                        label="LLM Form Processor", 
                        value=False,
                        info="Gebruik LLM voor formulier verwerking."
                    )
                    use_llm_image_description = gr.Checkbox(
                        label="LLM Image Description", 
                        value=False,
                        info="Gebruik LLM voor afbeelding beschrijvingen."
                    )
                    use_llm_table_merge = gr.Checkbox(
                        label="LLM Table Merge", 
                        value=False,
                        info="Gebruik LLM voor tabel samenvoeging."
                    )
                    use_llm_text = gr.Checkbox(
                        label="LLM Text Processor", 
                        value=False,
                        info="Gebruik LLM voor tekst verbetering en verwerking."
                    )
                
                # LLM-specifieke prompts
                with gr.Group():
                    gr.Markdown("### 🎯 LLM Prompts")
                    layout_prompt = gr.Textbox(
                        label="Layout Prompt", 
                        placeholder="Custom prompt voor layout detectie",
                        lines=3,
                        info="Custom prompt voor layout model."
                    )
                    table_prompt = gr.Textbox(
                        label="Table Prompt", 
                        placeholder="Custom prompt voor tabel verwerking",
                        lines=3,
                        info="Custom prompt voor tabel processing."
                    )
                    equation_prompt = gr.Textbox(
                        label="Equation Prompt", 
                        placeholder="Custom prompt voor vergelijkingen",
                        lines=3,
                        info="Custom prompt voor equation processing."
                    )
                    handwriting_prompt = gr.Textbox(
                        label="Handwriting Prompt", 
                        placeholder="Custom prompt voor handschrift",
                        lines=3,
                        info="Custom prompt voor handwriting OCR."
                    )
                    complex_relabeling_prompt = gr.Textbox(
                        label="Complex Relabeling Prompt", 
                        placeholder="Custom prompt voor complexe relabeling",
                        lines=3,
                        info="Custom prompt voor complexe regio relabeling."
                    )
                    table_rewriting_prompt = gr.Textbox(
                        label="Table Rewriting Prompt", 
                        placeholder="Custom prompt voor tabel herschrijving",
                        lines=3,
                        info="Custom prompt voor tabel herschrijving."
                    )
                    table_merge_prompt = gr.Textbox(
                        label="Table Merge Prompt", 
                        placeholder="Custom prompt voor tabel samenvoeging",
                        lines=3,
                        info="Custom prompt voor tabel samenvoeging."
                    )
                    image_description_prompt = gr.Textbox(
                        label="Image Description Prompt", 
                        placeholder="Custom prompt voor afbeelding beschrijvingen",
                        lines=3,
                        info="Custom prompt voor afbeelding beschrijvingen."
                    )
                
                # LLM-specifieke thresholds en instellingen
                with gr.Group():
                    gr.Markdown("### 📊 LLM Thresholds & Instellingen")
                    confidence_threshold = gr.Number(
                        label="Confidence Threshold", 
                        value=0.7,
                        info="Confidence threshold voor relabeling (alles onder wordt herlabeld)."
                    )
                    picture_height_threshold = gr.Number(
                        label="Picture Height Threshold", 
                        value=0.8,
                        info="Hoogte threshold voor afbeeldingen die complexe regio's kunnen zijn."
                    )
                    min_equation_height = gr.Number(
                        label="Min Equation Height", 
                        value=0.08,
                        info="Minimum ratio tussen vergelijking hoogte en pagina hoogte."
                    )
                    equation_image_expansion_ratio = gr.Number(
                        label="Equation Image Expansion Ratio", 
                        value=0.05,
                        info="Ratio om afbeelding uit te breiden bij cropping voor vergelijkingen."
                    )
                    max_rows_per_batch = gr.Number(
                        label="Max Rows Per Batch", 
                        value=60,
                        precision=0,
                        info="Maximum aantal rijen per batch voor tabel processing."
                    )
                    max_table_rows = gr.Number(
                        label="Max Table Rows", 
                        value=175,
                        precision=0,
                        info="Maximum aantal rijen in een tabel voor LLM processing."
                    )
                    table_image_expansion_ratio = gr.Number(
                        label="Table Image Expansion Ratio", 
                        value=0.0,
                        info="Ratio om afbeelding uit te breiden bij cropping voor tabellen."
                    )
                    table_height_threshold = gr.Number(
                        label="Table Height Threshold", 
                        value=0.6,
                        info="Minimum hoogte ratio voor tabel samenvoeging."
                    )
                    table_start_threshold = gr.Number(
                        label="Table Start Threshold", 
                        value=0.2,
                        info="Maximum percentage op pagina waar tweede tabel kan beginnen."
                    )
                    vertical_table_height_threshold = gr.Number(
                        label="Vertical Table Height Threshold", 
                        value=0.25,
                        info="Hoogte tolerance voor 2 aangrenzende tabellen om samen te voegen."
                    )
                    vertical_table_distance_threshold = gr.Number(
                        label="Vertical Table Distance Threshold", 
                        value=20,
                        precision=0,
                        info="Maximum afstand tussen tabel randen voor adjacency."
                    )
                    horizontal_table_width_threshold = gr.Number(
                        label="Horizontal Table Width Threshold", 
                        value=0.25,
                        info="Breedte tolerance voor 2 aangrenzende tabellen om samen te voegen."
                    )
                    horizontal_table_distance_threshold = gr.Number(
                        label="Horizontal Table Distance Threshold", 
                        value=20,
                        precision=0,
                        info="Maximum afstand tussen tabel randen voor adjacency."
                    )
                    column_gap_threshold = gr.Number(
                        label="Column Gap Threshold", 
                        value=50,
                        precision=0,
                        info="Maximum gap tussen kolommen om tabellen samen te voegen."
                    )
                    image_expansion_ratio = gr.Number(
                        label="Image Expansion Ratio", 
                        value=0.01,
                        info="Ratio om afbeelding uit te breiden bij cropping."
                    )
                
                # Provider visibility logic
                def update_provider_visibility(provider: str) -> list:
                    return [
                        gr.update(visible=provider == "gemini"),
                        gr.update(visible=provider == "openai"),
                        gr.update(visible=provider == "anthropic"),
                        gr.update(visible=provider == "azure"),
                        gr.update(visible=provider == "ollama"),
                        gr.update(visible=provider == "custom")
                    ]
                
                llm_provider.change(
                    fn=update_provider_visibility,
                    inputs=[llm_provider],
                    outputs=[gemini_settings, openai_settings, anthropic_settings, azure_settings, ollama_settings, custom_settings]
                )
            
            with gr.Accordion("📐 Layout & Document Verwerking", open=False) as layout_settings:
                lowres_image_dpi = gr.Number(
                    label="Low-res Image DPI", 
                    value=96,
                    precision=0,
                    info="DPI voor layout en line detection."
                )
                highres_image_dpi = gr.Number(
                    label="High-res Image DPI", 
                    value=192,
                    precision=0,
                    info="DPI voor OCR verwerking."
                )
                layout_coverage_threshold = gr.Number(
                    label="Layout Coverage Threshold", 
                    value=0.1,
                    info="Minimum coverage ratio voor layout model."
                )
                document_ocr_threshold = gr.Number(
                    label="Document OCR Threshold", 
                    value=0.8,
                    info="Minimum ratio van pagina's die layout check moeten passen."
                )
            
            with gr.Accordion("📊 Tabel Verwerking", open=False) as table_settings:
                detect_boxes = gr.Checkbox(
                    label="Detecteer Boxes", 
                    value=False,
                    info="Detecteer boxes voor tabel recognition model."
                )
                max_table_rows = gr.Number(
                    label="Max Tabel Rijen", 
                    value=175,
                    precision=0,
                    info="Maximum aantal rijen in een tabel voor LLM processing."
                )
                row_split_threshold = gr.Number(
                    label="Row Split Threshold", 
                    value=0.5,
                    info="Percentage rijen die gesplitst moeten worden."
                )
                column_gap_ratio = gr.Number(
                    label="Column Gap Ratio", 
                    value=0.02,
                    info="Minimum ratio van pagina breedte voor column break."
                )
            
            with gr.Accordion("⚡ Performance & Workers", open=False) as performance_settings:
                pdftext_workers = gr.Number(
                    label="PDFText Workers", 
                    value=1,
                    precision=0,
                    info="Aantal workers voor pdftext verwerking. (ALTIJD 1 voor stabiliteit)",
                    interactive=False  # Disable editing - altijd 1
                )
                batch_size = gr.Number(
                    label="Batch Size", 
                    value=None,
                    precision=0,
                    info="Batch size voor layout model (None voor default)."
                )
                recognition_batch_size = gr.Number(
                    label="Recognition Batch Size", 
                    value=None,
                    precision=0,
                    info="Batch size voor recognition model."
                )
                detection_batch_size = gr.Number(
                    label="Detection Batch Size", 
                    value=None,
                    precision=0,
                    info="Batch size voor detection model."
                )
            
            with gr.Accordion("📤 Output & Render Instellingen", open=False) as output_settings:
                extract_images = gr.Checkbox(
                    label="Extraheer Afbeeldingen", 
                    value=True,
                    info="Extraheer afbeeldingen uit het document."
                )
                paginate_output = gr.Checkbox(
                    label="Pagina Output", 
                    value=False,
                    info="Voeg paginascheidingen toe aan output."
                )
                page_separator = gr.Textbox(
                    label="Pagina Separator", 
                    value="-" * 48,
                    info="Separator tussen pagina's."
                )
                disable_links = gr.Checkbox(
                    label="Schakel Links Uit", 
                    value=False,
                    info="Schakel link detectie uit."
                )
            
            with gr.Accordion("📦 ZIP Output Instellingen", open=True) as zip_settings:
                include_images_in_zip = gr.Checkbox(
                    label="Inclusief Afbeeldingen in ZIP", 
                    value=True,
                    info="Voeg geëxtraheerde afbeeldingen toe aan het ZIP-bestand."
                )
                include_debug_in_zip = gr.Checkbox(
                    label="Inclusief Debug Bestanden in ZIP", 
                    value=False,
                    info="Voeg debug bestanden en afbeeldingen toe aan het ZIP-bestand."
                )
                zip_description = gr.Markdown(
                    "**ZIP Output:** Alle gegenereerde bestanden worden automatisch verpakt in een ZIP-bestand. "
                    "Dit omvat geconverteerde tekst, afbeeldingen (indien geëxtraheerd) en debug bestanden (indien geactiveerd). "
                    "Je kunt ook alleen de geconverteerde tekst bekijken in de preview hiernaast."
                )
            
            with gr.Accordion("🐛 Debug & Troubleshooting", open=False) as debug_settings:
                debug_layout_images = gr.Checkbox(
                    label="Debug Layout Images", 
                    value=False,
                    info="Dump layout debug images."
                )
                debug_pdf_images = gr.Checkbox(
                    label="Debug PDF Images", 
                    value=False,
                    info="Dump PDF debug images."
                )
                debug_json = gr.Checkbox(
                    label="Debug JSON", 
                    value=False,
                    info="Dump block debug data."
                )
                debug_data_folder = gr.Textbox(
                    label="Debug Data Folder", 
                    value="debug_data",
                    info="Folder voor debug data dump."
                )

            convert_button = gr.Button("🚀 Converteer PDF(s)", variant="primary", size="lg")

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("📄 Geformatteerde Output"):
                    output_markdown = gr.Markdown(show_copy_button=True, label="Resultaat")
                with gr.TabItem("📝 Ruwe Output"):
                    output_raw = gr.Code(label="Broncode", language="markdown")
                with gr.TabItem("💾 Download"):
                    download_button = gr.DownloadButton(label="📦 Download ZIP Bestand", visible=False)
            
            with gr.Accordion("❌ Foutdetails", open=False, visible=False) as error_accordion:
                error_details = gr.Markdown()

    # Bundel alle instellingen voor de functie-aanroep
    settings_components = [
        # Basis instellingen
        output_format, page_range, debug, output_dir,
        # OCR instellingen
        force_ocr, strip_existing_ocr, disable_ocr, languages,
        ocr_space_threshold, ocr_newline_threshold, ocr_alphanum_threshold,
        # LLM instellingen - Provider selectie
        use_llm, llm_provider,
        # Gemini instellingen
        google_api_key, gemini_model_name,
        # OpenAI instellingen
        openai_api_key, openai_model_name, openai_base_url,
        # Anthropic instellingen
        anthropic_api_key, anthropic_model_name,
        # Azure instellingen
        azure_api_key, azure_endpoint, azure_deployment, azure_api_version,
        # Ollama instellingen
        ollama_base_url, ollama_model_name,
        # Custom instellingen
        custom_api_key, custom_base_url, custom_model_name,
        # Algemene LLM instellingen
        max_retries, max_concurrency, timeout, temperature, max_tokens,
        # LLM Functionaliteit
        use_llm_layout, use_llm_table, use_llm_equation, use_llm_handwriting,
        use_llm_complex_region, use_llm_form, use_llm_image_description, 
        use_llm_table_merge, use_llm_text,
        # LLM Prompts
        layout_prompt, table_prompt, equation_prompt, handwriting_prompt,
        complex_relabeling_prompt, table_rewriting_prompt, table_merge_prompt, image_description_prompt,
        # LLM Thresholds & Instellingen
        confidence_threshold, picture_height_threshold, min_equation_height, equation_image_expansion_ratio,
        max_rows_per_batch, table_image_expansion_ratio, table_height_threshold,
        table_start_threshold, vertical_table_height_threshold, vertical_table_distance_threshold,
        horizontal_table_width_threshold, horizontal_table_distance_threshold, column_gap_threshold,
        image_expansion_ratio,
        # Layout instellingen
        lowres_image_dpi, highres_image_dpi, layout_coverage_threshold, document_ocr_threshold,
        # Tabel instellingen
        detect_boxes, max_table_rows, row_split_threshold, column_gap_ratio,
        # Performance instellingen
        pdftext_workers, batch_size, recognition_batch_size, detection_batch_size,
        # Output instellingen
        extract_images, paginate_output, page_separator, disable_links,
        # ZIP instellingen
        include_images_in_zip, include_debug_in_zip,
        # Debug instellingen
        debug_layout_images, debug_pdf_images, debug_json, debug_data_folder
    ]

    # Bind de functie aan de convert button
    convert_button.click(
        fn=process_pdf,
        inputs=[file_input] + settings_components,  # type: ignore
        outputs=[output_markdown, output_raw, download_button, error_accordion, error_details]
    )

if __name__ == "__main__":
    demo.launch(show_api=True, show_error=True)
