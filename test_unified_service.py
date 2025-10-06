"""
Test script voor de nieuwe geünificeerde conversion service.
Test zowel simpele conversie als ZIP output functionaliteit.
"""

import asyncio
import os
import tempfile
import shutil
from conversion_service import (
    convert_pdf_to_markdown,
    convert_pdf_bytes_to_markdown,
    convert_pdf_with_zip_output,
    convert_multiple_pdfs_with_zip,
    get_converter_status,
    ConversionResult
)

async def test_simple_conversion() -> bool:
    """Test simpele PDF conversie."""
    print("🧪 Testing simple PDF conversion...")
    
    if not os.path.exists('test_document.pdf'):
        print("❌ test_document.pdf not found!")
        return False
    
    try:
        # Test simpele conversie
        markdown_text = await convert_pdf_to_markdown('test_document.pdf')
        
        if markdown_text and len(markdown_text) > 0:
            print(f"✅ Simple conversion successful! Text length: {len(markdown_text)} characters")
            return True
        else:
            print("❌ Simple conversion returned empty text")
            return False
            
    except Exception as e:
        print(f"❌ Simple conversion failed: {e}")
        return False

async def test_bytes_conversion() -> bool:
    """Test PDF bytes conversie."""
    print("\n🧪 Testing PDF bytes conversion...")
    
    if not os.path.exists('test_document.pdf'):
        print("❌ test_document.pdf not found!")
        return False
    
    try:
        # Read PDF as bytes
        with open('test_document.pdf', 'rb') as f:
            pdf_bytes = f.read()
        
        # Test bytes conversie
        markdown_text = await convert_pdf_bytes_to_markdown(pdf_bytes)
        
        if markdown_text and len(markdown_text) > 0:
            print(f"✅ Bytes conversion successful! Text length: {len(markdown_text)} characters")
            return True
        else:
            print("❌ Bytes conversion returned empty text")
            return False
            
    except Exception as e:
        print(f"❌ Bytes conversion failed: {e}")
        return False

async def test_zip_output() -> bool:
    """Test ZIP output functionaliteit."""
    print("\n🧪 Testing ZIP output functionality...")
    
    if not os.path.exists('test_document.pdf'):
        print("❌ test_document.pdf not found!")
        return False
    
    try:
        # Test settings voor ZIP output
        settings = {
            "output_format": "markdown",
            "extract_images": True,
            "debug_layout_images": True,
            "debug_pdf_images": True,
            "debug_json": True,
        }
        
        # Test ZIP conversie
        result = await convert_pdf_with_zip_output('test_document.pdf', settings)
        
        if result.success:
            print(f"✅ ZIP conversion successful!")
            print(f"   📄 Output files: {len(result.output_files)}")
            print(f"   🐛 Debug files: {len(result.debug_files)}")
            print(f"   🖼️ Image files: {len(result.image_files)}")
            print(f"   📝 Text length: {len(result.markdown_content)} characters")
            return True
        else:
            print(f"❌ ZIP conversion failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ ZIP conversion failed: {e}")
        return False

async def test_multiple_pdfs() -> bool:
    """Test meerdere PDF's conversie."""
    print("\n🧪 Testing multiple PDFs conversion...")
    
    # Check if we have multiple test PDFs
    test_files = []
    if os.path.exists('test_document.pdf'):
        test_files.append('test_document.pdf')
    if os.path.exists('testdocument2.pdf'):
        test_files.append('testdocument2.pdf')
    
    if len(test_files) < 1:
        print("❌ No test PDFs found!")
        return False
    
    try:
        # Create mock uploaded files
        class MockFile:
            def __init__(self, path: str) -> None:
                self.name = path
        
        uploaded_files = [MockFile(f) for f in test_files]
        
        # Test settings
        settings = {
            "output_format": "markdown",
            "extract_images": False,
            "debug_layout_images": False,
        }
        
        # Test multiple PDFs conversie
        zip_path, combined_content = await convert_multiple_pdfs_with_zip(
            uploaded_files, settings, include_debug=False, include_images=False
        )
        
        if zip_path and os.path.exists(zip_path):
            print(f"✅ Multiple PDFs conversion successful!")
            print(f"   📦 ZIP file: {zip_path}")
            print(f"   📝 Combined content length: {len(combined_content)} characters")
            
            # Clean up
            os.unlink(zip_path)
            return True
        else:
            print("❌ Multiple PDFs conversion failed - no ZIP file created")
            return False
            
    except Exception as e:
        print(f"❌ Multiple PDFs conversion failed: {e}")
        return False

def test_converter_status() -> bool:
    """Test converter status."""
    print("\n🧪 Testing converter status...")
    
    try:
        status = get_converter_status()
        
        print(f"   Initialized: {status['initialized']}")
        print(f"   Status: {status['status']}")
        print(f"   Message: {status['message']}")
        
        if status['initialized']:
            print("✅ Converter status check successful!")
            return True
        else:
            print("❌ Converter not initialized!")
            return False
            
    except Exception as e:
        print(f"❌ Converter status check failed: {e}")
        return False

async def main() -> None:
    """Hoofdfunctie om alle tests uit te voeren."""
    print("🚀 Unified Conversion Service Test Suite")
    print("=" * 50)
    
    # Test converter status
    status_ok = test_converter_status()
    if not status_ok:
        print("❌ Converter not ready, aborting tests")
        return
    
    # Run all tests
    tests = [
        ("Simple Conversion", test_simple_conversion),
        ("Bytes Conversion", test_bytes_conversion),
        ("ZIP Output", test_zip_output),
        ("Multiple PDFs", test_multiple_pdfs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Unified conversion service is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
