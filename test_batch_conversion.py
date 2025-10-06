#!/usr/bin/env python3
"""
Test script voor batch PDF conversie functionaliteit.
"""

import asyncio
import tempfile
import os
from pathlib import Path

# Import de conversion service
import conversion_service_original as conversion_service

async def test_single_file_conversion():
    """Test enkele bestand conversie."""
    print("🧪 Testing single file conversion...")
    
    # Maak een dummy PDF bestand voor testing
    # In een echte test zou je een echte PDF gebruiken
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(test_pdf_content)
        temp_pdf_path = temp_file.name
    
    try:
        settings = {
            "output_format": "markdown",
            "use_llm": False,  # Disable LLM for faster testing
            "force_ocr": False
        }
        
        result = await conversion_service.convert_pdf_with_settings(temp_pdf_path, settings)
        print(f"✅ Single file conversion successful: {len(result)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Single file conversion failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(temp_pdf_path)
        except:
            pass

async def test_batch_conversion():
    """Test batch conversie met meerdere bestanden."""
    print("🧪 Testing batch conversion...")
    
    # Maak meerdere dummy PDF bestanden
    test_files = []
    for i in range(3):
        test_pdf_content = f"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 50\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF {i+1}) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n303\n%%EOF".encode()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_test_{i+1}.pdf") as temp_file:
            temp_file.write(test_pdf_content)
            test_files.append(temp_file.name)
    
    try:
        settings = {
            "output_format": "markdown",
            "use_llm": False,  # Disable LLM for faster testing
            "force_ocr": False
        }
        
        successful_conversions = 0
        failed_conversions = 0
        
        for i, pdf_path in enumerate(test_files):
            try:
                result = await conversion_service.convert_pdf_with_settings(pdf_path, settings)
                print(f"✅ File {i+1} conversion successful: {len(result)} characters")
                successful_conversions += 1
            except Exception as e:
                print(f"❌ File {i+1} conversion failed: {e}")
                failed_conversions += 1
        
        print(f"📊 Batch conversion results: {successful_conversions} successful, {failed_conversions} failed")
        return successful_conversions > 0
        
    except Exception as e:
        print(f"❌ Batch conversion test failed: {e}")
        return False
    finally:
        # Cleanup
        for pdf_path in test_files:
            try:
                os.unlink(pdf_path)
            except:
                pass

async def main():
    """Run all tests."""
    print("🚀 Starting batch conversion tests...\n")
    
    # Test single file conversion
    single_success = await test_single_file_conversion()
    print()
    
    # Test batch conversion
    batch_success = await test_batch_conversion()
    print()
    
    # Summary
    print("📋 Test Summary:")
    print(f"   Single file conversion: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"   Batch conversion: {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    if single_success and batch_success:
        print("\n🎉 All tests passed! Batch conversion functionality is working.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())

