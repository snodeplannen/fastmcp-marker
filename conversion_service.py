"""
Unified PDF to Markdown conversion service.
Supports both simple conversion and ZIP output with full file collection.
No Windows-specific fixes needed - works on all platforms.
"""

import asyncio
import tempfile
import os
import zipfile
import shutil
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Initialize the converter and models once when the module is loaded.
CONVERTER: Optional[PdfConverter] = None

try:
    models = create_model_dict()
    CONVERTER = PdfConverter(artifact_dict=models)
    print("✅ Marker PDF Converter initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing Marker PDF Converter: {e}")
    CONVERTER = None

class ConversionResult:
    """Result of a PDF conversion with all generated files."""
    
    def __init__(self, pdf_name: str):
        self.pdf_name = pdf_name
        self.markdown_content = ""
        self.html_content = ""
        self.json_content = ""
        self.output_files: List[str] = []  # All generated files
        self.debug_files: List[str] = []  # Debug files
        self.image_files: List[str] = []   # Extracted images
        self.success = False
        self.error: str = ""
        self.output_dir: Optional[str] = None

async def convert_pdf_to_markdown(pdf_path: str, settings: Optional[dict] = None) -> str:
    """
    Convert a PDF file to Markdown string.
    
    Args:
        pdf_path: Path to the PDF file
        settings: Optional conversion settings
        
    Returns:
        Converted Markdown text
    """
    if CONVERTER is None:
        raise RuntimeError("Marker PDF Converter is not available. Check initialization logs.")
    
    # Set default settings if None
    if settings is None:
        settings = {}
    
    def blocking_conversion() -> str:
        """Synchronous wrapper for the marker conversion call."""
        try:
            # Create converter with settings if provided
            if settings:
                converter = PdfConverter(artifact_dict=models, config=settings)
            else:
                converter = CONVERTER
            
            # Convert PDF
            rendered_document = converter(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            return str(text)
            
        except Exception as e:
            print(f"Error in blocking conversion: {e}")
            raise
    
    try:
        print(f"🔄 Converting PDF: {os.path.basename(pdf_path)}")
        markdown_text = await asyncio.to_thread(blocking_conversion)
        print("✅ PDF conversion completed successfully")
        return markdown_text
    except Exception as e:
        print(f"❌ PDF conversion failed: {e}")
        raise

async def convert_pdf_bytes_to_markdown(pdf_bytes: bytes, settings: Optional[dict] = None) -> str:
    """
    Convert PDF bytes to Markdown string.
    
    Args:
        pdf_bytes: PDF file content as bytes
        settings: Optional conversion settings
        
    Returns:
        Converted Markdown text
    """
    # Use a temporary file to handle the byte stream
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf_path = temp_pdf.name

    try:
        # Convert the temporary file
        markdown_result = await convert_pdf_to_markdown(temp_pdf_path, settings)
        return markdown_result
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_pdf_path)
        except OSError:
            pass

async def convert_pdf_with_zip_output(pdf_path: str, settings: dict) -> ConversionResult:
    """
    Convert a PDF and collect all generated files for ZIP output.
    
    Args:
        pdf_path: Path to the PDF file
        settings: Dictionary with Marker configuration options
        
    Returns:
        ConversionResult object with all generated files
    """
    if CONVERTER is None:
        raise RuntimeError("Marker PDF Converter is not available. Check initialization logs.")

    result = ConversionResult(os.path.basename(pdf_path))
    
    def blocking_conversion() -> ConversionResult:
        """Synchronous wrapper for marker conversion with full output collection."""
        try:
            # Create temporary output directory for this conversion
            temp_output_dir = tempfile.mkdtemp(prefix=f"marker_output_{os.path.splitext(result.pdf_name)[0]}_")
            result.output_dir = temp_output_dir
            
            # Filter None values from settings
            filtered_settings = {k: v for k, v in settings.items() if v is not None}
            
            # Create config dict with output directory
            direct_config: dict[str, Any] = {
                "output_dir": temp_output_dir,
                "debug_data_folder": os.path.join(temp_output_dir, "debug_data"),
            }
            
            # Add all settings to config, but protect debug_data_folder from boolean values
            for key, value in filtered_settings.items():
                if key == "debug_data_folder" and isinstance(value, bool):
                    # Skip boolean debug_data_folder values - use the correct path instead
                    continue
                direct_config[key] = value
            
            print(f"🔍 Converting {result.pdf_name} with output directory: {temp_output_dir}")
            
            # Create converter with settings
            converter = PdfConverter(
                config=direct_config,
                artifact_dict=models
            )
            
            # Perform conversion
            rendered_document = converter(pdf_path)
            text, _, _ = text_from_rendered(rendered_document)
            
            # Save main text
            result.markdown_content = str(text)
            
            # Collect all generated files
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
        print(f"❌ Error during PDF conversion: {e}")
        result.error = str(e)
        result.success = False
        return result

def collect_output_files(output_dir: str) -> List[str]:
    """Collect all output files from the output directory."""
    files: List[str] = []
    if not os.path.exists(output_dir):
        return files
    
    for root, dirs, filenames in os.walk(output_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Skip temporary files
            if not filename.startswith('.') and not filename.endswith('.tmp'):
                files.append(file_path)
    
    return files

def collect_debug_files(output_dir: str) -> List[str]:
    """Collect debug files (images, JSON, etc.)."""
    debug_files: List[str] = []
    if not os.path.exists(output_dir):
        return debug_files
    
    # Look for debug directories within the output directory
    debug_dirs = ['debug_data', 'debug_images', 'layout_images', 'pdf_images']
    
    for debug_dir in debug_dirs:
        debug_path = os.path.join(output_dir, debug_dir)
        if os.path.exists(debug_path):
            for root, dirs, filenames in os.walk(debug_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    debug_files.append(file_path)
    
    # Also search in current directory for backward compatibility
    current_debug_path = os.path.join(os.getcwd(), 'debug_data')
    if os.path.exists(current_debug_path):
        for root, dirs, filenames in os.walk(current_debug_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                debug_files.append(file_path)
    
    return debug_files

def collect_image_files(output_dir: str) -> List[str]:
    """Collect extracted images."""
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
    Create a zip file from all conversion results.
    
    Args:
        results: List of ConversionResult objects
        include_debug: Whether to include debug files
        include_images: Whether to include images
        
    Returns:
        Path to the created zip file
    """
    # Create temporary zip file
    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_path = zip_file.name
    zip_file.close()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add each result
        for i, result in enumerate(results):
            if not result.success:
                continue
                
            # Create directory for this PDF file
            pdf_base_name = os.path.splitext(result.pdf_name)[0]
            pdf_dir = f"{i+1:02d}_{pdf_base_name}"
            
            # Add main text
            if result.markdown_content:
                zipf.writestr(f"{pdf_dir}/converted_text.md", result.markdown_content)
            
            # Add all output files
            for file_path in result.output_files:
                if os.path.exists(file_path):
                    # Determine relative name within zip
                    rel_path = os.path.relpath(file_path, result.output_dir)
                    zip_path_in_zip = f"{pdf_dir}/output/{rel_path}"
                    zipf.write(file_path, zip_path_in_zip)
            
            # Add debug files (optional)
            if include_debug and result.debug_files:
                for file_path in result.debug_files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, result.output_dir)
                        zip_path_in_zip = f"{pdf_dir}/debug/{rel_path}"
                        zipf.write(file_path, zip_path_in_zip)
            
            # Add images (optional)
            if include_images and result.image_files:
                for file_path in result.image_files:
                    if os.path.exists(file_path):
                        rel_path = os.path.relpath(file_path, result.output_dir)
                        zip_path_in_zip = f"{pdf_dir}/images/{rel_path}"
                        zipf.write(file_path, zip_path_in_zip)
        
        # Add overview
        overview_content = create_overview_content(results)
        zipf.writestr("00_OVERVIEW.md", overview_content)
    
    return zip_path

def create_overview_content(results: List[ConversionResult]) -> str:
    """Create overview of all conversions."""
    content = "# PDF Conversion Overview\n\n"
    content += f"**Total files:** {len(results)}\n"
    content += f"**Successful:** {sum(1 for r in results if r.success)}\n"
    content += f"**Failed:** {sum(1 for r in results if not r.success)}\n\n"
    
    for i, result in enumerate(results, 1):
        content += f"## {i}. {result.pdf_name}\n\n"
        if result.success:
            content += f"✅ **Status:** Successfully converted\n"
            content += f"📄 **Output files:** {len(result.output_files)}\n"
            content += f"🐛 **Debug files:** {len(result.debug_files)}\n"
            content += f"🖼️ **Images:** {len(result.image_files)}\n"
        else:
            content += f"❌ **Status:** Failed\n"
            content += f"**Error:** {result.error}\n"
        content += "\n"
    
    return content

async def convert_multiple_pdfs_with_zip(uploaded_files: List[Any], settings: dict, 
                                       include_debug: bool = True, include_images: bool = True) -> Tuple[str, str]:
    """
    Convert multiple PDFs and create a zip file.
    
    Args:
        uploaded_files: List of uploaded files
        settings: Conversion settings
        include_debug: Whether to include debug files
        include_images: Whether to include images
        
    Returns:
        Tuple of (zip_file_path, combined_markdown_content)
    """
    results = []
    
    # Convert each file
    for uploaded_file in uploaded_files:
        # Get the file path from the uploaded file
        if hasattr(uploaded_file, 'name'):
            file_path = uploaded_file.name
        elif hasattr(uploaded_file, 'path'):
            file_path = uploaded_file.path
        else:
            file_path = str(uploaded_file)
        
        result = await convert_pdf_with_zip_output(file_path, settings)
        results.append(result)
    
    # Create zip file
    zip_path = create_zip_from_results(results, include_debug, include_images)
    
    # Create combined markdown content
    combined_content = create_overview_content(results)
    combined_content += "\n\n# Converted Texts\n\n"
    
    for i, result in enumerate(results, 1):
        if result.success:
            combined_content += f"## {i}. {result.pdf_name}\n\n"
            combined_content += result.markdown_content + "\n\n"
            combined_content += "---\n\n"
    
    return zip_path, combined_content

def cleanup_temp_directories(results: List[ConversionResult]) -> None:
    """Clean up temporary directories."""
    for result in results:
        if result.output_dir and os.path.exists(result.output_dir):
            try:
                shutil.rmtree(result.output_dir)
                print(f"🧹 Cleaned up temporary directory: {result.output_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean up {result.output_dir}: {e}")

def get_converter_status() -> dict:
    """
    Returns the current status of the converter initialization.
    
    Returns:
        A dictionary containing status information.
    """
    return {
        "initialized": CONVERTER is not None,
        "status": "ready" if CONVERTER is not None else "failed",
        "message": "Converter ready for PDF processing" if CONVERTER is not None else "Converter initialization failed"
    }
