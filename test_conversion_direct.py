"""
Direct test van de conversion service om de debug output te zien.
"""

import asyncio
import os
from conversion_service_zip import convert_multiple_pdfs_with_zip

class MockUploadedFile:
    def __init__(self, path: str):
        self.name = path
        self.path = path

async def test_conversion_direct() -> bool:
    """Test de conversion service direct."""
    
    print("🧪 Testing conversion service directly...")
    
    # Maak een mock uploaded file
    test_pdf_path = "test_document.pdf"
    if not os.path.exists(test_pdf_path):
        print("❌ Test PDF not found!")
        return False
    
    mock_file = MockUploadedFile(test_pdf_path)
    
    # Test settings
    settings = {
        "output_format": "markdown",
        "use_llm": False,
        "extract_images": True,
        "debug": True,
        "include_images_in_zip": True,
        "include_debug_in_zip": False,
        "pdftext_workers": 1,
        "force_ocr": False,
        "strip_existing_ocr": False,
        "disable_ocr": False,
        "languages": "",
        "ocr_space_threshold": 0.7,
        "ocr_newline_threshold": 0.6,
        "ocr_alphanum_threshold": 0.3,
        "lowres_image_dpi": 96,
        "highres_image_dpi": 192,
        "layout_coverage_threshold": 0.1,
        "document_ocr_threshold": 0.8,
        "detect_boxes": False,
        "max_table_rows": 175,
        "row_split_threshold": 0.5,
        "column_gap_ratio": 0.02,
        "recognition_batch_size": 0,
        "detection_batch_size": 0,
        "paginate_output": False,
        "page_separator": "------------------------------------------------",
        "disable_links": False,
        "debug_layout_images": False,
        "debug_pdf_images": False,
        "debug_json": False,
        "debug_data_folder": "debug_data",
        "llm_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model_name": "llama3.2:latest",
        "max_retries": 3,
        "max_concurrency": 3,
        "timeout": 60,
        "temperature": 0.1,
        "max_tokens": 4096,
        "llm_layout_builder": False,
        "llm_table_processor": False,
        "llm_equation_processor": False,
        "llm_handwriting_processor": False,
        "llm_complex_region_processor": False,
        "llm_form_processor": False,
        "llm_image_description": False,
        "llm_table_merge": False,
        "llm_text_processor": False
    }
    
    try:
        zip_path, combined_content = await convert_multiple_pdfs_with_zip(
            [mock_file], 
            settings,
            include_debug=False,
            include_images=True
        )
        
        print("✅ Conversion successful!")
        print(f"📦 ZIP path: {zip_path}")
        print(f"📝 Content length: {len(combined_content)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_conversion_direct())
