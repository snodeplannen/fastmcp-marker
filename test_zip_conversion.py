"""
Test script voor de nieuwe ZIP conversion functionaliteit.
"""

import asyncio
import tempfile
import os
from conversion_service_zip import convert_multiple_pdfs_with_zip, ConversionResult, create_zip_from_results

async def test_zip_conversion():
    """Test de nieuwe ZIP conversion functionaliteit."""
    
    # Maak een test PDF bestand (dummy content)
    test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
    
    # Maak tijdelijke PDF bestanden
    test_files = []
    for i in range(2):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(test_pdf_content)
            test_files.append(temp_pdf.name)
    
    try:
        # Test instellingen
        settings = {
            "output_format": "markdown",
            "use_llm": False,  # Disable LLM voor snellere test
            "extract_images": True,
            "debug": False,
            "include_images_in_zip": True,
            "include_debug_in_zip": False
        }
        
        print("🧪 Testing ZIP conversion functionality...")
        
        # Simuleer uploaded files (zoals in Gradio)
        class MockUploadedFile:
            def __init__(self, path: str):
                self.name = os.path.basename(path)
                self.path = path
        
        uploaded_files = [MockUploadedFile(path) for path in test_files]
        
        # Test de conversie
        zip_path, combined_content = await convert_multiple_pdfs_with_zip(
            uploaded_files, 
            settings,
            include_debug=False,
            include_images=True
        )
        
        print(f"✅ ZIP conversion completed!")
        print(f"📦 ZIP file created: {zip_path}")
        print(f"📄 Combined content length: {len(combined_content)} characters")
        
        # Controleer of het ZIP bestand bestaat
        if os.path.exists(zip_path):
            print(f"✅ ZIP file exists and is {os.path.getsize(zip_path)} bytes")
        else:
            print("❌ ZIP file was not created")
        
        # Toon een deel van de gecombineerde content
        print(f"\n📝 Preview of combined content:")
        print(combined_content[:500] + "..." if len(combined_content) > 500 else combined_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup test files
        for file_path in test_files:
            try:
                os.unlink(file_path)
                print(f"🧹 Cleaned up test file: {file_path}")
            except OSError:
                pass

async def test_conversion_result():
    """Test de ConversionResult class."""
    
    print("\n🧪 Testing ConversionResult class...")
    
    result = ConversionResult("test.pdf")
    
    # Test properties
    assert result.pdf_name == "test.pdf"
    assert result.success == False
    assert result.error == ""
    assert result.output_dir is None
    assert len(result.output_files) == 0
    assert len(result.debug_files) == 0
    assert len(result.image_files) == 0
    
    # Test content setting
    result.markdown_content = "Test content"
    result.success = True
    
    assert result.markdown_content == "Test content"
    assert result.success == True
    
    print("✅ ConversionResult class test passed!")

if __name__ == "__main__":
    async def main():
        print("🚀 Starting ZIP conversion tests...")
        
        # Test ConversionResult class
        await test_conversion_result()
        
        # Test ZIP conversion
        success = await test_zip_conversion()
        
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    
    asyncio.run(main())
