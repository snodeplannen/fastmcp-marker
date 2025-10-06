"""
Conversion service die alle gegenereerde bestanden verzamelt en in een zip file verpakt.
Ondersteunt zowel enkele als meerdere PDF bestanden met volledige output verzameling.
"""

import asyncio
import tempfile
import os
import traceback
import zipfile
import io
import shutil
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path

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
from typing import Optional

# Initialize the converter and models once when the module is loaded.
CONVERTER: Optional[PdfConverter] = None

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

class ConversionResult:
    """Resultaat van een PDF conversie met alle gegenereerde bestanden."""
    
    def __init__(self, pdf_name: str):
        self.pdf_name = pdf_name
        self.markdown_content = ""
        self.html_content = ""
        self.json_content = ""
        self.output_files: List[str] = []  # Alle gegenereerde bestanden
        self.debug_files: List[str] = []  # Debug bestanden
        self.image_files: List[str] = []   # Geëxtraheerde afbeeldingen
        self.success = False
        self.error: str = ""
        self.output_dir: Optional[str] = None

async def convert_pdf_with_zip_output(pdf_path: str, settings: dict) -> ConversionResult:
    """
    Converteert een PDF en verzamelt alle gegenereerde bestanden voor zip output.
    
    Args:
        pdf_path: Het pad naar het PDF bestand
        settings: Dictionary met Marker configuratie opties
        
    Returns:
        ConversionResult object met alle gegenereerde bestanden
    """
    if CONVERTER is None:
        raise RuntimeError("Marker PDF Converter is not available. Check initialization logs.")

    result = ConversionResult(os.path.basename(pdf_path))
    
    def blocking_conversion() -> ConversionResult:
        """
        Een synchrone wrapper voor de marker-conversieaanroep met volledige output verzameling.
        """
        try:
            # Maak een tijdelijke output directory voor deze conversie
            temp_output_dir = tempfile.mkdtemp(prefix=f"marker_output_{os.path.splitext(result.pdf_name)[0]}_")
            result.output_dir = temp_output_dir
            
            # Filter None waarden uit settings
            filtered_settings = {k: v for k, v in settings.items() if v is not None}
            
            # Maak een basis config dict
            direct_config: dict[str, Any] = {
                "pdftext_workers": 1,
                "disable_multiprocessing": True,
                "output_dir": temp_output_dir,  # Zet output directory
            }
            
            # Voeg alle basis instellingen toe (exclusief LLM instellingen)
            basic_settings = [
                # Basis instellingen
                "output_format", "page_range", "debug", 
                
                # OCR instellingen
                "force_ocr", "strip_existing_ocr", "disable_ocr", "languages",
                "ocr_space_threshold", "ocr_newline_threshold", "ocr_alphanum_threshold",
                
                # Layout & Document instellingen
                "lowres_image_dpi", "highres_image_dpi", "layout_coverage_threshold", 
                "document_ocr_threshold",
                
                # Tabel instellingen
                "detect_boxes", "max_table_rows", "row_split_threshold", "column_gap_ratio",
                
                # Performance instellingen
                "pdftext_workers", "recognition_batch_size", "detection_batch_size",
                
                # Output instellingen
                "extract_images", "paginate_output", "page_separator", "disable_links",
                
                # Debug instellingen
                "debug_layout_images", "debug_pdf_images", "debug_json", "debug_data_folder",
            ]
            
            # Voeg basis instellingen toe
            for key in basic_settings:
                if key in filtered_settings:
                    value = filtered_settings[key]
                    # Skip batch_size waarden die 0 zijn om division by zero te voorkomen
                    if key in ["batch_size", "recognition_batch_size", "detection_batch_size"] and value == 0:
                        continue
                    direct_config[key] = value
            
            # Handle LLM instellingen correct
            use_llm = filtered_settings.get("use_llm", True)
            llm_provider = filtered_settings.get("llm_provider", "ollama")
            
            # Configureer LLM instellingen op basis van provider
            if use_llm:
                print(f"🔍 Debug: Configuring LLM with provider: {llm_provider}")
                
                if llm_provider == "gemini":
                    if "google_api_key" in filtered_settings and filtered_settings["google_api_key"]:
                        direct_config.update({
                            "use_llm": True,
                            "llm_service": "marker.services.gemini.GoogleGeminiService",
                            "google_api_key": filtered_settings["google_api_key"],
                            "gemini_model_name": filtered_settings.get("gemini_model_name", "gemini-2.0-flash")
                        })
                    else:
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
                        use_llm = False
                        
                elif llm_provider == "ollama":
                    direct_config.update({
                        "use_llm": True,
                        "llm_service": "marker.services.ollama.OllamaService",
                        "ollama_base_url": filtered_settings.get("ollama_base_url", "http://localhost:11434"),
                        "ollama_model": filtered_settings.get("ollama_model_name", "llama3.2:latest")
                    })
                    
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
                        use_llm = False
            
            # Voeg alle LLM-specifieke instellingen toe
            llm_settings = [
                "max_retries", "max_concurrency", "timeout", "temperature", "max_tokens",
                "use_llm_layout", "use_llm_table", "use_llm_equation", "use_llm_handwriting",
                "use_llm_complex_region", "use_llm_form", "use_llm_image_description", 
                "use_llm_table_merge", "use_llm_text",
                "layout_prompt", "table_prompt", "equation_prompt", "handwriting_prompt",
                "complex_relabeling_prompt", "table_rewriting_prompt", "table_merge_prompt", 
                "image_description_prompt",
                "confidence_threshold", "picture_height_threshold", "min_equation_height",
                "equation_image_expansion_ratio", "max_rows_per_batch", "table_image_expansion_ratio",
                "table_height_threshold", "table_start_threshold", "vertical_table_height_threshold",
                "vertical_table_distance_threshold", "horizontal_table_width_threshold",
                "horizontal_table_distance_threshold", "column_gap_threshold", "image_expansion_ratio",
            ]
            
            for key in llm_settings:
                if key in filtered_settings:
                    value = filtered_settings[key]
                    if key in ["batch_size", "recognition_batch_size", "detection_batch_size"] and value == 0:
                        continue
                    direct_config[key] = value
            
            print(f"🔍 Debug: Converting {result.pdf_name} with output directory: {temp_output_dir}")
            
            # Extract llm_service from config if present
            llm_service = direct_config.get("llm_service")
            
            converter = PdfConverter(
                config=direct_config,
                artifact_dict=models,
                llm_service=llm_service
            )
            
            # Voer de conversie uit
            rendered_document = converter(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            
            # Sla de hoofdtekst op
            result.markdown_content = str(text)
            
            # Verzamel alle gegenereerde bestanden
            result.output_files = collect_output_files(temp_output_dir)
            result.debug_files = collect_debug_files(temp_output_dir)
            result.image_files = collect_image_files(temp_output_dir)
            
            result.success = True
            print(f"✅ Successfully converted {result.pdf_name} with {len(result.output_files)} output files")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to convert {result.pdf_name}: {e}")
            result.error = str(e)
            result.success = False
            return result
    
    try:
        # Run the blocking function in a separate thread
        result = await asyncio.to_thread(blocking_conversion)
        return result
    except Exception as e:
        print(f"An error occurred during PDF conversion: {e}")
        result.error = str(e)
        result.success = False
        return result

def collect_output_files(output_dir: str) -> List[str]:
    """Verzamel alle output bestanden uit de output directory."""
    files: List[str] = []
    if not os.path.exists(output_dir):
        return files
    
    for root, dirs, filenames in os.walk(output_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Skip tijdelijke bestanden
            if not filename.startswith('.') and not filename.endswith('.tmp'):
                files.append(file_path)
    
    return files

def collect_debug_files(output_dir: str) -> List[str]:
    """Verzamel debug bestanden (images, JSON, etc.)."""
    debug_files: List[str] = []
    if not os.path.exists(output_dir):
        return debug_files
    
    # Zoek naar debug directories
    debug_dirs = ['debug_data', 'debug_images', 'layout_images', 'pdf_images']
    
    for debug_dir in debug_dirs:
        debug_path = os.path.join(output_dir, debug_dir)
        if os.path.exists(debug_path):
            for root, dirs, filenames in os.walk(debug_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    debug_files.append(file_path)
    
    return debug_files

def collect_image_files(output_dir: str) -> List[str]:
    """Verzamel geëxtraheerde afbeeldingen."""
    image_files: List[str] = []
    if not os.path.exists(output_dir):
        return image_files
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    
    for root, dirs, filenames in os.walk(output_dir):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                file_path = os.path.join(root, filename)
                image_files.append(file_path)
    
    return image_files

def create_zip_from_results(results: List[ConversionResult], include_debug: bool = True, include_images: bool = True) -> str:
    """
    Maak een zip bestand van alle conversie resultaten.
    
    Args:
        results: Lijst van ConversionResult objecten
        include_debug: Of debug bestanden moeten worden opgenomen
        include_images: Of afbeeldingen moeten worden opgenomen
        
    Returns:
        Pad naar het gemaakte zip bestand
    """
    # Maak een tijdelijke zip file
    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_path = zip_file.name
    zip_file.close()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Voeg elk resultaat toe
        for i, result in enumerate(results):
            if not result.success:
                continue
                
            # Maak een directory voor dit PDF bestand
            pdf_base_name = os.path.splitext(result.pdf_name)[0]
            pdf_dir = f"{i+1:02d}_{pdf_base_name}"
            
            # Voeg de hoofdtekst toe
            if result.markdown_content:
                zipf.writestr(f"{pdf_dir}/converted_text.md", result.markdown_content)
            
            # Voeg alle output bestanden toe
            for file_path in result.output_files:
                if os.path.exists(file_path):
                    # Bepaal de relatieve naam binnen de zip
                    rel_path = os.path.relpath(file_path, result.output_dir)
                    zip_path_in_zip = f"{pdf_dir}/output/{rel_path}"
                    zipf.write(file_path, zip_path_in_zip)
            
            # Voeg debug bestanden toe (optioneel)
            if include_debug and result.debug_files:
                for file_path in result.debug_files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, result.output_dir)
                        zip_path_in_zip = f"{pdf_dir}/debug/{rel_path}"
                        zipf.write(file_path, zip_path_in_zip)
            
            # Voeg afbeeldingen toe (optioneel)
            if include_images and result.image_files:
                for file_path in result.image_files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, result.output_dir)
                        zip_path_in_zip = f"{pdf_dir}/images/{rel_path}"
                        zipf.write(file_path, zip_path_in_zip)
        
        # Voeg een overzicht toe
        overview_content = create_overview_content(results)
        zipf.writestr("00_OVERVIEW.md", overview_content)
    
    return zip_path

def create_overview_content(results: List[ConversionResult]) -> str:
    """Maak een overzicht van alle conversies."""
    content = "# PDF Conversie Overzicht\n\n"
    content += f"**Totaal bestanden:** {len(results)}\n"
    content += f"**Succesvol:** {sum(1 for r in results if r.success)}\n"
    content += f"**Mislukt:** {sum(1 for r in results if not r.success)}\n\n"
    
    for i, result in enumerate(results, 1):
        content += f"## {i}. {result.pdf_name}\n\n"
        if result.success:
            content += f"✅ **Status:** Succesvol geconverteerd\n"
            content += f"📄 **Output bestanden:** {len(result.output_files)}\n"
            content += f"🐛 **Debug bestanden:** {len(result.debug_files)}\n"
            content += f"🖼️ **Afbeeldingen:** {len(result.image_files)}\n"
        else:
            content += f"❌ **Status:** Mislukt\n"
            content += f"**Fout:** {result.error}\n"
        content += "\n"
    
    return content

def cleanup_temp_directories(results: List[ConversionResult]) -> None:
    """Ruim tijdelijke directories op."""
    for result in results:
        if result.output_dir and os.path.exists(result.output_dir):
            try:
                shutil.rmtree(result.output_dir)
                print(f"🧹 Cleaned up temporary directory: {result.output_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean up {result.output_dir}: {e}")

async def convert_multiple_pdfs_with_zip(uploaded_files: List[Any], settings: dict, 
                                       include_debug: bool = True, include_images: bool = True) -> Tuple[str, str]:
    """
    Converteer meerdere PDF's en maak een zip bestand.
    
    Args:
        uploaded_files: Lijst van geüploade bestanden
        settings: Conversie instellingen
        include_debug: Of debug bestanden moeten worden opgenomen
        include_images: Of afbeeldingen moeten worden opgenomen
        
    Returns:
        Tuple van (zip_file_path, combined_markdown_content)
    """
    results = []
    
    # Converteer elk bestand
    for uploaded_file in uploaded_files:
        result = await convert_pdf_with_zip_output(uploaded_file.name, settings)
        results.append(result)
    
    # Maak zip bestand
    zip_path = create_zip_from_results(results, include_debug, include_images)
    
    # Maak gecombineerde markdown content
    combined_content = create_overview_content(results)
    combined_content += "\n\n# Geconverteerde Teksten\n\n"
    
    for i, result in enumerate(results, 1):
        if result.success:
            combined_content += f"## {i}. {result.pdf_name}\n\n"
            combined_content += result.markdown_content + "\n\n"
            combined_content += "---\n\n"
    
    # Cleanup (optioneel - kan worden uitgesteld)
    # cleanup_temp_directories(results)
    
    return zip_path, combined_content
