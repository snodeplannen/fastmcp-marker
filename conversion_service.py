"""
Core PDF to Markdown conversion service using marker-pdf library.

This module provides the business logic for PDF conversion, completely decoupled
from any interface technology (FastMCP or Gradio). It handles the computationally
intensive marker-pdf conversion process asynchronously to avoid blocking the
main event loop.
"""

import asyncio
import tempfile
import os
from typing import Optional, Tuple

# Import Windows fix first
#import windows_fix

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
# Note: config_from_dict might not be available in all versions
# We'll create a simple config dict instead

# Global models - initialized once when module is loaded
# These are used by converter instances for efficiency
MODELS: Optional[dict] = None

def initialize_models() -> None:
    """Initialize the Marker models once for efficiency."""
    global MODELS
    try:
        print("Initializing Marker models...")
        MODELS = create_model_dict()
        print("✅ Marker models initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing Marker models: {e}")
        MODELS = None

# Initialize models when module is imported
initialize_models()

async def convert_pdf_with_settings(pdf_path: str, settings: dict) -> Tuple[str, str]:
    """
    Asynchronously converts a PDF file to text with specified settings.

    This function creates a new PdfConverter instance based on the
    provided settings for each conversion.

    Args:
        pdf_path: The absolute path to the PDF file to be converted.
        settings: A dictionary with configuration options for Marker.

    Returns:
        A tuple with the converted text and output format ('markdown', 'html', 'json').
    
    Raises:
        RuntimeError: If the Marker models failed to initialize.
        Exception: Propagates exceptions from the conversion process.
    """
    if MODELS is None:
        raise RuntimeError("Marker models are not available. Check initialization logs.")

    output_format = settings.get("output_format", "markdown")

    def blocking_conversion() -> str:
        """
        A synchronous wrapper for the marker conversion call.
        This function will be run in a separate thread.
        """
        # Create a converter with the specific settings for this call
        # Note: We'll use default config for now since config_from_dict is not available
        # Set single-threaded mode for Windows compatibility
        converter = PdfConverter(artifact_dict=MODELS)
        
        rendered_document = converter(pdf_path)
        text, _, _ = text_from_rendered(rendered_document)
        return str(text)

    try:
        # Run the blocking function in a separate thread
        print(f"🔄 Starting PDF conversion with settings for: {os.path.basename(pdf_path)}")
        converted_text = await asyncio.to_thread(blocking_conversion)
        print("✅ PDF conversion completed successfully")
        return converted_text, output_format
    except Exception as e:
        print(f"❌ An error occurred during PDF conversion: {e}")
        # Re-raise the exception to be handled by the calling interface
        raise

async def convert_pdf_bytes_with_settings(pdf_bytes: bytes, settings: dict) -> Tuple[str, str]:
    """
    A convenience wrapper that takes PDF content as bytes, saves it to a
    temporary file, and then calls the main conversion function.

    Args:
        pdf_bytes: The binary content of the PDF file.
        settings: A dictionary with configuration options for Marker.

    Returns:
        A tuple with the converted text and output format.
    """
    # Use a temporary file to handle the byte stream
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf_path = temp_pdf.name

    try:
        # Await the conversion of the temporary file
        converted_text, output_format = await convert_pdf_with_settings(temp_pdf_path, settings)
        return converted_text, output_format
    finally:
        # Ensure the temporary file is always cleaned up
        try:
            os.unlink(temp_pdf_path)
        except OSError:
            # File might already be deleted, ignore
            pass

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
    if MODELS is None:
        raise RuntimeError("Marker models are not available. Check initialization logs.")

    def blocking_conversion() -> str:
        """
        A synchronous wrapper for the marker conversion call.
        This function will be run in a separate thread.
        """
        try:
            # Create a converter with default settings
            # Set single-threaded mode for Windows compatibility
            converter = PdfConverter(artifact_dict=MODELS)
            # The converter takes a file path and returns a rendered object
            rendered_document = converter(pdf_path)
            # The text_from_rendered function extracts the markdown string
            text, _, _ = text_from_rendered(rendered_document)
            return str(text)
        except Exception as e:
            print(f"Error in blocking conversion: {e}")
            raise

    try:
        # Run the blocking function in a separate thread
        print(f"🔄 Starting PDF conversion for: {os.path.basename(pdf_path)}")
        markdown_text = await asyncio.to_thread(blocking_conversion)
        print("✅ PDF conversion completed successfully")
        return markdown_text
    except Exception as e:
        print(f"❌ An error occurred during PDF conversion: {e}")
        # Re-raise the exception to be handled by the calling interface
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
        try:
            os.unlink(temp_pdf_path)
        except OSError:
            # File might already be deleted, ignore
            pass

def get_converter_status() -> dict:
    """
    Returns the current status of the converter initialization.
    
    Returns:
        A dictionary containing status information.
    """
    return {
        "initialized": MODELS is not None,
        "status": "ready" if MODELS is not None else "failed",
        "message": "Models ready for PDF processing" if MODELS is not None else "Model initialization failed"
    }
