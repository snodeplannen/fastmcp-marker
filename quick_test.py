"""
Snelle test van de ZIP functionaliteit zonder debug mode.
"""

import asyncio
import os
from conversion_service_zip import convert_multiple_pdfs_with_zip

async def quick_test():
    """Snelle test zonder debug mode."""
    
    if not os.path.exists('test_document.pdf'):
        print("❌ Test PDF niet gevonden!")
        return False
    
    print("🧪 Quick test without debug mode...")
    
    # Simuleer uploaded file
    class MockUploadedFile:
        def __init__(self, path: str):
            self.name = path
            self.path = path
    
    uploaded_files = [MockUploadedFile('test_document.pdf')]
    
    # Minimale instellingen
    settings = {
        "output_format": "markdown",
        "use_llm": False,
        "extract_images": False,  # Disable images voor snellere test
        "debug": False,  # Disable debug voor snellere test
        "include_images_in_zip": False,
        "include_debug_in_zip": False
    }
    
    try:
        zip_path, combined_content = await convert_multiple_pdfs_with_zip(
            uploaded_files, 
            settings,
            include_debug=False,
            include_images=False
        )
        
        print(f"✅ Quick test completed!")
        print(f"📦 ZIP file: {zip_path}")
        print(f"📄 Content length: {len(combined_content)} characters")
        
        # Controleer ZIP inhoud
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
            print(f"📁 ZIP contains {len(files)} files:")
            for file in files:
                print(f"  {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(quick_test())
