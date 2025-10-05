"""
Test script voor de subprocess conversie functie.
"""

import asyncio
import tempfile
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import Windows fix first
import windows_fix
import conversion_service_subprocess as conversion_service

async def test_subprocess_conversion():
    """Test de subprocess conversie functie."""
    print("🧪 Testing subprocess conversion...")
    
    # Create a simple test PDF content (this would normally be a real PDF)
    # For testing purposes, we'll create a dummy PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    # Write test PDF to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(test_pdf_content)
        temp_pdf_path = temp_pdf.name
    
    try:
        print(f"📄 Test PDF created at: {temp_pdf_path}")
        
        # Test the conversion
        settings = {"output_format": "markdown"}
        print(f"🔧 Settings: {settings}")
        
        converted_text, output_format = await conversion_service.convert_pdf_with_subprocess(
            temp_pdf_path, settings
        )
        
        print(f"✅ Conversion successful!")
        print(f"📝 Output format: {output_format}")
        print(f"📄 Converted text length: {len(converted_text)} characters")
        print(f"📄 First 200 characters: {converted_text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_pdf_path)
        except OSError:
            pass

async def main():
    """Hoofdfunctie."""
    print("🚀 Starting subprocess conversion test...")
    print("=" * 50)
    
    success = await test_subprocess_conversion()
    
    print("=" * 50)
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("❌ Test failed!")

if __name__ == "__main__":
    asyncio.run(main())

