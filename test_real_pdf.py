"""
Echte test van de ZIP functionaliteit met een echt PDF bestand.
"""

import asyncio
import os
from conversion_service_zip import convert_multiple_pdfs_with_zip

async def test_real_pdf():
    """Test met een echt PDF bestand."""
    
    if not os.path.exists('test_document.pdf'):
        print("❌ Test PDF niet gevonden!")
        return False
    
    print("🧪 Testing with real PDF document...")
    
    # Simuleer uploaded file
    class MockUploadedFile:
        def __init__(self, path: str):
            self.name = path
            self.path = path
    
    uploaded_files = [MockUploadedFile('test_document.pdf')]
    
    # Test instellingen
    settings = {
        "output_format": "markdown",
        "use_llm": False,  # Disable LLM voor snellere test
        "extract_images": True,
        "debug": True,  # Enable debug om meer bestanden te genereren
        "include_images_in_zip": True,
        "include_debug_in_zip": True
    }
    
    try:
        # Test de conversie
        zip_path, combined_content = await convert_multiple_pdfs_with_zip(
            uploaded_files, 
            settings,
            include_debug=True,
            include_images=True
        )
        
        print(f"✅ Real PDF conversion completed!")
        print(f"📦 ZIP file created: {zip_path}")
        print(f"📄 Combined content length: {len(combined_content)} characters")
        
        # Controleer ZIP inhoud
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
            print(f"\n📁 ZIP contains {len(files)} files:")
            for file in files:
                print(f"  {file}")
        
        # Toon een deel van de content
        print(f"\n📝 Preview of converted content:")
        print(combined_content[:1000] + "..." if len(combined_content) > 1000 else combined_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Real PDF test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_real_pdf())
