"""
Originele conversion service volgens het blueprint - simpel en werkend.
Met threading fixes uit Marker scripts.
"""

import asyncio
import tempfile
import os
import traceback

# Environment variables uit Marker scripts om threading problemen te voorkomen
os.environ["MKL_DYNAMIC"] = "FALSE"
os.environ["OMP_DYNAMIC"] = "FALSE"
os.environ["OMP_NUM_THREADS"] = "1"  # Single thread to avoid multiprocessing issues
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["IN_STREAMLIT"] = "true"  # Avoid multiprocessing inside surya

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Initialize the converter and models once when the module is loaded.
# This is a heavy operation and should not be done on every function call.
try:
    models = create_model_dict()
    # Configure for single-threaded operation
    config_dict = {
        "pdftext_workers": 1,  # Single worker
        "disable_multiprocessing": True,  # Disable multiprocessing
    }
    CONVERTER = PdfConverter(artifact_dict=models, config=config_dict)
    print("Marker PDF Converter initialized successfully (single-threaded).")
except Exception as e:
    print(f"Error initializing Marker PDF Converter: {e}")
    CONVERTER = None

async def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Asynchronously converts a PDF file to a Markdown string.

    This function uses the marker-pdf library to perform the conversion.
    The synchronous, blocking conversion call is run in a separate thread
    to avoid blocking the main asyncio event loop.

    Args:
        pdf_path: The absolute path to the PDF file to be converted.

    Returns:
        A string containing the converted Markdown text.
    
    Raises:
        RuntimeError: If the Marker converter failed to initialize.
        Exception: Propagates exceptions from the conversion process.
    """
    if CONVERTER is None:
        raise RuntimeError("Marker PDF Converter is not available. Check initialization logs.")

    def blocking_conversion():
        """
        A synchronous wrapper for the marker conversion call.
        This function will be run in a separate thread.
        """
        # The converter takes a file path and returns a rendered object
        rendered_document = CONVERTER(pdf_path)
        # The text_from_rendered function extracts the markdown string
        text, _, _ = text_from_rendered(rendered_document)
        return text

    try:
        # Run the blocking function in a separate thread
        markdown_text = await asyncio.to_thread(blocking_conversion)
        return markdown_text
    except Exception as e:
        print(f"An error occurred during PDF conversion: {e}")
        # Re-raise the exception to be handled by the calling interface
        raise

async def convert_pdf_with_settings(pdf_path: str, settings: dict) -> str:
    """
    Converteert een PDF met geavanceerde instellingen.
    
    Args:
        pdf_path: Het pad naar het PDF bestand
        settings: Dictionary met Marker configuratie opties
        
    Returns:
        Een string met de geconverteerde tekst
    """
    if CONVERTER is None:
        raise RuntimeError("Marker PDF Converter is not available. Check initialization logs.")

    def blocking_conversion():
        """
        Een synchrone wrapper voor de marker-conversieaanroep met instellingen.
        """
        # Maak een nieuwe converter met de specifieke instellingen
        from marker.config.parser import ConfigParser
        
        # Filter None waarden uit settings
        filtered_settings = {k: v for k, v in settings.items() if v is not None}
        
        # Skip ConfigParser en gebruik direct PdfConverter met correcte LLM configuratie
        print(f"🔍 Debug: Creating converter with {len(filtered_settings)} settings")
        print(f"🔍 Debug: Filtered settings: {filtered_settings}")
        
        # Maak een basis config dict
        direct_config = {
            "pdftext_workers": 1,
            "disable_multiprocessing": True,
        }
        
        # Voeg alle basis instellingen toe (exclusief LLM instellingen)
        basic_settings = [
            # Basis instellingen
            "output_format", "page_range", "debug", "output_dir",
            
            # OCR instellingen
            "force_ocr", "strip_existing_ocr", "disable_ocr", "languages",
            "ocr_space_threshold", "ocr_newline_threshold", "ocr_alphanum_threshold",
            
            # Layout & Document instellingen
            "lowres_image_dpi", "highres_image_dpi", "layout_coverage_threshold", 
            "document_ocr_threshold",
            
            # Tabel instellingen
            "detect_boxes", "max_table_rows", "row_split_threshold", "column_gap_ratio",
            
            # Performance instellingen (exclusief batch_size om division by zero te voorkomen)
            "pdftext_workers", "recognition_batch_size", "detection_batch_size",
            
            # Output instellingen
            "extract_images", "paginate_output", "page_separator", "disable_links",
            
            # Debug instellingen
            "debug_layout_images", "debug_pdf_images", "debug_json", "debug_data_folder",
            
            # Algemene instellingen
            "image_threshold", "strip_existing_ocr", "disable_links", "paginate_output"
        ]
        
        # Voeg basis instellingen toe (filter batch_size waarden die 0 zijn)
        added_basic = 0
        for key in basic_settings:
            if key in filtered_settings:
                value = filtered_settings[key]
                # Skip batch_size waarden die 0 zijn om division by zero te voorkomen
                if key in ["batch_size", "recognition_batch_size", "detection_batch_size"] and value == 0:
                    continue
                direct_config[key] = value
                added_basic += 1
        
        print(f"🔍 Debug: Added {added_basic} basic settings to config")
        
        # Handle LLM instellingen correct
        use_llm = filtered_settings.get("use_llm", True)  # Standaard LLM aan
        llm_provider = filtered_settings.get("llm_provider", "ollama")  # Standaard Ollama
        
        # Configureer LLM instellingen op basis van provider
        if use_llm:
            llm_provider = filtered_settings.get("llm_provider", "gemini")
            print(f"🔍 Debug: Configuring LLM with provider: {llm_provider}")
            
            # Configureer LLM service op basis van provider
            if llm_provider == "gemini":
                if "google_api_key" in filtered_settings and filtered_settings["google_api_key"]:
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "marker.services.gemini.GoogleGeminiService",
                        "google_api_key": filtered_settings["google_api_key"],
                        "gemini_model_name": filtered_settings.get("gemini_model_name", "gemini-2.0-flash")
                    })
                else:
                    print(f"🔍 Debug: Gemini API key missing, disabling LLM")
                    use_llm = False
                    
            elif llm_provider == "openai":
                if "openai_api_key" in filtered_settings and filtered_settings["openai_api_key"]:
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "marker.services.openai.OpenAIService",
                        "openai_api_key": filtered_settings["openai_api_key"],
                        "openai_model_name": filtered_settings.get("openai_model_name", "gpt-4o"),
                        "openai_base_url": filtered_settings.get("openai_base_url", None)
                    })
                else:
                    print(f"🔍 Debug: OpenAI API key missing, disabling LLM")
                    use_llm = False
                    
            elif llm_provider == "anthropic":
                if "anthropic_api_key" in filtered_settings and filtered_settings["anthropic_api_key"]:
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "marker.services.claude.ClaudeService",
                        "anthropic_api_key": filtered_settings["anthropic_api_key"],
                        "anthropic_model_name": filtered_settings.get("anthropic_model_name", "claude-3-5-sonnet-20241022")
                    })
                else:
                    print(f"🔍 Debug: Anthropic API key missing, disabling LLM")
                    use_llm = False
                    
            elif llm_provider == "azure":
                if "azure_api_key" in filtered_settings and filtered_settings["azure_api_key"]:
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "marker.services.azure_openai.AzureOpenAIService",
                        "azure_api_key": filtered_settings["azure_api_key"],
                        "azure_endpoint": filtered_settings.get("azure_endpoint", ""),
                        "azure_deployment": filtered_settings.get("azure_deployment", ""),
                        "azure_api_version": filtered_settings.get("azure_api_version", "2024-02-15-preview")
                    })
                else:
                    print(f"🔍 Debug: Azure API key missing, disabling LLM")
                    use_llm = False
                    
            elif llm_provider == "ollama":
                # Ollama heeft geen API key nodig, alleen URL en model
                direct_config.update({
                    "use_llm": True,
                    "llm_service": "marker.services.ollama.OllamaService",
                    "ollama_base_url": filtered_settings.get("ollama_base_url", "http://localhost:11434"),
                    "ollama_model": filtered_settings.get("ollama_model_name", "llama3.2:latest")
                })
                print(f"🔍 Debug: Ollama configured with URL: {direct_config['ollama_base_url']}, Model: {direct_config['ollama_model']}")
                
            elif llm_provider == "custom":
                if "custom_api_key" in filtered_settings and filtered_settings["custom_api_key"]:
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "custom",
                        "custom_api_key": filtered_settings["custom_api_key"],
                        "custom_base_url": filtered_settings.get("custom_base_url", ""),
                        "custom_model_name": filtered_settings.get("custom_model_name", "")
                    })
                else:
                    print(f"🔍 Debug: Custom API key missing, disabling LLM")
                    use_llm = False
            
        # Voeg alle LLM-specifieke instellingen toe (altijd, ongeacht use_llm status)
        llm_settings = [
            # Algemene LLM instellingen
            "max_retries", "max_concurrency", "timeout", "temperature", "max_tokens",
            
            # LLM Functionaliteit
            "use_llm_layout", "use_llm_table", "use_llm_equation", "use_llm_handwriting",
            "use_llm_complex_region", "use_llm_form", "use_llm_image_description", 
            "use_llm_table_merge", "use_llm_text",
            
            # LLM Prompts
            "layout_prompt", "table_prompt", "equation_prompt", "handwriting_prompt",
            "complex_relabeling_prompt", "table_rewriting_prompt", "table_merge_prompt", 
            "image_description_prompt",
            
            # LLM Thresholds & Instellingen
            "confidence_threshold", "picture_height_threshold", "min_equation_height",
            "equation_image_expansion_ratio", "max_rows_per_batch", "table_image_expansion_ratio",
            "table_height_threshold", "table_start_threshold", "vertical_table_height_threshold",
            "vertical_table_distance_threshold", "horizontal_table_width_threshold",
            "horizontal_table_distance_threshold", "column_gap_threshold", "image_expansion_ratio",
            
            # Extra LLM instellingen
            "topk_relabelling_prompt", "gap_threshold", "list_gap_threshold", 
            "min_x_indent", "x_start_tolerance", "x_end_tolerance",
            "render_font", "font_dl_path", "model_max_length", "texify_batch_size",
            "token_buffer", "common_element_threshold", "common_element_min_blocks",
            "max_streak", "text_match_threshold", "strip_numbers_threshold",
            "min_lines_in_block", "min_line_length", "level_count", "merge_threshold",
            "default_level", "height_tolerance", "detector_batch_size", "table_rec_batch_size",
            "image_count", "flatten_pdf", "ocr_space_threshold", "ocr_newline_threshold",
            "ocr_alphanum_threshold", "image_threshold", "strip_existing_ocr"
        ]
        
        added_llm = 0
        for key in llm_settings:
            if key in filtered_settings:
                value = filtered_settings[key]
                # Skip batch_size waarden die 0 zijn om division by zero te voorkomen
                if key in ["batch_size", "recognition_batch_size", "detection_batch_size"] and value == 0:
                    continue
                direct_config[key] = value
                added_llm += 1
        
        print(f"🔍 Debug: Added {added_llm} LLM settings to config")
        
        print(f"🔍 Debug: Final config: {direct_config}")
        
        # Genereer equivalente Marker commandline
        marker_cmd = generate_marker_commandline(direct_config, pdf_path)
        print(f"🔍 Debug: Equivalent Marker commandline:")
        print(f"🔍 Debug: {marker_cmd}")
        
        try:
            # Extract llm_service from config if present
            llm_service = direct_config.get("llm_service")
            
            converter = PdfConverter(
                config=direct_config,
                artifact_dict=models,
                llm_service=llm_service
            )
            
            print(f"🔍 Debug: Converter created successfully")
            rendered_document = converter(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            return text
            
        except Exception as e:
            print(f"🔍 Debug: Converter failed: {e}")
            print(f"🔍 Debug: Traceback: {traceback.format_exc()}")
            
            # Final fallback naar standaard converter
            print(f"🔍 Debug: Using fallback standard converter")
            rendered_document = CONVERTER(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            return text
    
    try:
        # Run the blocking function in a separate thread
        markdown_text = await asyncio.to_thread(blocking_conversion)
        return markdown_text
    except Exception as e:
        print(f"An error occurred during PDF conversion: {e}")
        raise

def generate_marker_commandline(config: dict, pdf_path: str) -> str:
    """
    Genereert een equivalente Marker commandline op basis van de configuratie.
    """
    cmd_parts = ["marker", "convert", pdf_path]
    
    # Basis instellingen
    if config.get("output_format") and config["output_format"] != "markdown":
        cmd_parts.append(f"--output_format={config['output_format']}")
    
    if config.get("output_dir"):
        cmd_parts.append(f"--output_dir={config['output_dir']}")
    
    # OCR instellingen
    if config.get("force_ocr"):
        cmd_parts.append("--force_ocr")
    
    if config.get("strip_existing_ocr"):
        cmd_parts.append("--strip_existing_ocr")
    
    if config.get("disable_ocr"):
        cmd_parts.append("--disable_ocr")
    
    if config.get("languages"):
        if isinstance(config["languages"], list):
            langs = ",".join(config["languages"])
        else:
            langs = config["languages"]
        cmd_parts.append(f"--langs={langs}")
    
    # OCR thresholds
    if config.get("ocr_space_threshold"):
        cmd_parts.append(f"--ocr_space_threshold={config['ocr_space_threshold']}")
    
    if config.get("ocr_newline_threshold"):
        cmd_parts.append(f"--ocr_newline_threshold={config['ocr_newline_threshold']}")
    
    if config.get("ocr_alphanum_threshold"):
        cmd_parts.append(f"--ocr_alphanum_threshold={config['ocr_alphanum_threshold']}")
    
    # Layout instellingen
    if config.get("lowres_image_dpi"):
        cmd_parts.append(f"--lowres_image_dpi={config['lowres_image_dpi']}")
    
    if config.get("highres_image_dpi"):
        cmd_parts.append(f"--highres_image_dpi={config['highres_image_dpi']}")
    
    if config.get("layout_coverage_threshold"):
        cmd_parts.append(f"--layout_coverage_threshold={config['layout_coverage_threshold']}")
    
    if config.get("document_ocr_threshold"):
        cmd_parts.append(f"--document_ocr_threshold={config['document_ocr_threshold']}")
    
    # Tabel instellingen
    if config.get("detect_boxes"):
        cmd_parts.append("--detect_boxes")
    
    if config.get("max_table_rows"):
        cmd_parts.append(f"--max_table_rows={config['max_table_rows']}")
    
    if config.get("row_split_threshold"):
        cmd_parts.append(f"--row_split_threshold={config['row_split_threshold']}")
    
    if config.get("column_gap_ratio"):
        cmd_parts.append(f"--column_gap_ratio={config['column_gap_ratio']}")
    
    # Performance instellingen
    if config.get("pdftext_workers"):
        cmd_parts.append(f"--pdftext_workers={config['pdftext_workers']}")
    
    if config.get("batch_size"):
        cmd_parts.append(f"--batch_size={config['batch_size']}")
    
    if config.get("recognition_batch_size"):
        cmd_parts.append(f"--recognition_batch_size={config['recognition_batch_size']}")
    
    if config.get("detection_batch_size"):
        cmd_parts.append(f"--detection_batch_size={config['detection_batch_size']}")
    
    # Output instellingen
    if config.get("extract_images"):
        cmd_parts.append("--extract_images")
    
    if config.get("paginate_output"):
        cmd_parts.append("--paginate_output")
    
    if config.get("page_separator"):
        cmd_parts.append(f"--page_separator={config['page_separator']}")
    
    if config.get("disable_links"):
        cmd_parts.append("--disable_links")
    
    # Debug instellingen
    if config.get("debug"):
        cmd_parts.append("--debug")
    
    if config.get("debug_layout_images"):
        cmd_parts.append("--debug_layout_images")
    
    if config.get("debug_pdf_images"):
        cmd_parts.append("--debug_pdf_images")
    
    if config.get("debug_json"):
        cmd_parts.append("--debug_json")
    
    if config.get("debug_data_folder"):
        cmd_parts.append(f"--debug_data_folder={config['debug_data_folder']}")
    
    # LLM instellingen
    if config.get("use_llm"):
        cmd_parts.append("--use_llm")
        
        # LLM Provider specifieke instellingen
        if config.get("llm_service") == "google":
            if config.get("google_api_key"):
                cmd_parts.append(f"--google_api_key={config['google_api_key']}")
            if config.get("gemini_model_name"):
                cmd_parts.append(f"--gemini_model_name={config['gemini_model_name']}")
        
        elif config.get("llm_service") == "openai":
            if config.get("openai_api_key"):
                cmd_parts.append(f"--openai_api_key={config['openai_api_key']}")
            if config.get("openai_model_name"):
                cmd_parts.append(f"--openai_model_name={config['openai_model_name']}")
            if config.get("openai_base_url"):
                cmd_parts.append(f"--openai_base_url={config['openai_base_url']}")
        
        elif config.get("llm_service") == "anthropic":
            if config.get("anthropic_api_key"):
                cmd_parts.append(f"--anthropic_api_key={config['anthropic_api_key']}")
            if config.get("anthropic_model_name"):
                cmd_parts.append(f"--anthropic_model_name={config['anthropic_model_name']}")
        
        elif config.get("llm_service") == "azure":
            if config.get("azure_api_key"):
                cmd_parts.append(f"--azure_api_key={config['azure_api_key']}")
            if config.get("azure_endpoint"):
                cmd_parts.append(f"--azure_endpoint={config['azure_endpoint']}")
            if config.get("azure_deployment"):
                cmd_parts.append(f"--azure_deployment={config['azure_deployment']}")
            if config.get("azure_api_version"):
                cmd_parts.append(f"--azure_api_version={config['azure_api_version']}")
        
        elif config.get("llm_service") == "ollama":
            if config.get("ollama_base_url"):
                cmd_parts.append(f"--ollama_base_url={config['ollama_base_url']}")
            if config.get("ollama_model_name"):
                cmd_parts.append(f"--ollama_model_name={config['ollama_model_name']}")
        
        elif config.get("llm_service") == "custom":
            if config.get("custom_api_key"):
                cmd_parts.append(f"--custom_api_key={config['custom_api_key']}")
            if config.get("custom_base_url"):
                cmd_parts.append(f"--custom_base_url={config['custom_base_url']}")
            if config.get("custom_model_name"):
                cmd_parts.append(f"--custom_model_name={config['custom_model_name']}")
        
        # Algemene LLM instellingen
        if config.get("max_retries"):
            cmd_parts.append(f"--max_retries={config['max_retries']}")
        
        if config.get("max_concurrency"):
            cmd_parts.append(f"--max_concurrency={config['max_concurrency']}")
        
        if config.get("timeout"):
            cmd_parts.append(f"--timeout={config['timeout']}")
        
        if config.get("temperature"):
            cmd_parts.append(f"--temperature={config['temperature']}")
        
        if config.get("max_tokens"):
            cmd_parts.append(f"--max_tokens={config['max_tokens']}")
        
        # LLM Functionaliteit
        if config.get("use_llm_layout"):
            cmd_parts.append("--use_llm_layout")
        
        if config.get("use_llm_table"):
            cmd_parts.append("--use_llm_table")
        
        if config.get("use_llm_equation"):
            cmd_parts.append("--use_llm_equation")
        
        if config.get("use_llm_handwriting"):
            cmd_parts.append("--use_llm_handwriting")
        
        if config.get("use_llm_complex_region"):
            cmd_parts.append("--use_llm_complex_region")
        
        if config.get("use_llm_form"):
            cmd_parts.append("--use_llm_form")
        
        if config.get("use_llm_image_description"):
            cmd_parts.append("--use_llm_image_description")
        
        if config.get("use_llm_table_merge"):
            cmd_parts.append("--use_llm_table_merge")
        
        if config.get("use_llm_text"):
            cmd_parts.append("--use_llm_text")
        
        # LLM Thresholds
        if config.get("confidence_threshold"):
            cmd_parts.append(f"--confidence_threshold={config['confidence_threshold']}")
        
        if config.get("picture_height_threshold"):
            cmd_parts.append(f"--picture_height_threshold={config['picture_height_threshold']}")
        
        if config.get("min_equation_height"):
            cmd_parts.append(f"--min_equation_height={config['min_equation_height']}")
        
        if config.get("equation_image_expansion_ratio"):
            cmd_parts.append(f"--equation_image_expansion_ratio={config['equation_image_expansion_ratio']}")
        
        if config.get("max_rows_per_batch"):
            cmd_parts.append(f"--max_rows_per_batch={config['max_rows_per_batch']}")
        
        if config.get("table_image_expansion_ratio"):
            cmd_parts.append(f"--table_image_expansion_ratio={config['table_image_expansion_ratio']}")
        
        if config.get("table_height_threshold"):
            cmd_parts.append(f"--table_height_threshold={config['table_height_threshold']}")
        
        if config.get("table_start_threshold"):
            cmd_parts.append(f"--table_start_threshold={config['table_start_threshold']}")
        
        if config.get("vertical_table_height_threshold"):
            cmd_parts.append(f"--vertical_table_height_threshold={config['vertical_table_height_threshold']}")
        
        if config.get("vertical_table_distance_threshold"):
            cmd_parts.append(f"--vertical_table_distance_threshold={config['vertical_table_distance_threshold']}")
        
        if config.get("horizontal_table_width_threshold"):
            cmd_parts.append(f"--horizontal_table_width_threshold={config['horizontal_table_width_threshold']}")
        
        if config.get("horizontal_table_distance_threshold"):
            cmd_parts.append(f"--horizontal_table_distance_threshold={config['horizontal_table_distance_threshold']}")
        
        if config.get("column_gap_threshold"):
            cmd_parts.append(f"--column_gap_threshold={config['column_gap_threshold']}")
        
        if config.get("image_expansion_ratio"):
            cmd_parts.append(f"--image_expansion_ratio={config['image_expansion_ratio']}")
    
    return " ".join(cmd_parts)


async def convert_pdf_bytes_to_markdown(pdf_bytes: bytes) -> str:
    """
    A convenience wrapper that takes PDF content as bytes, saves it to a
    temporary file, and then calls the main conversion function.

    Args:
        pdf_bytes: The binary content of the PDF file.

    Returns:
        A string containing the converted Markdown text.
    """
    # Use a temporary file to handle the byte stream
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf_path = temp_pdf.name

    try:
        # Await the conversion of the temporary file
        markdown_result = await convert_pdf_to_markdown(temp_pdf_path)
        return markdown_result
    finally:
        # Ensure the temporary file is always cleaned up
        os.unlink(temp_pdf_path)
