"""
Originele conversion service volgens het blueprint - simpel en werkend.
Met threading fixes uit Marker scripts.
"""

import asyncio
import tempfile
import os

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
        
        try:
            config_parser = ConfigParser(filtered_settings)
            config_dict = config_parser.generate_config_dict()
            
            # Force single-threaded operation
            config_dict["pdftext_workers"] = 1
            config_dict["disable_multiprocessing"] = True
            
            # Maak een nieuwe converter met de configuratie
            converter = PdfConverter(
                config=config_dict,
                artifact_dict=models,
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service(),
            )
            
            rendered_document = converter(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            return text
            
        except Exception as e:
            print(f"Error creating converter with settings: {e}")
            # Fallback naar standaard converter
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
