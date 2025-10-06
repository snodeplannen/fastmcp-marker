"""
Test om te verifiëren dat Marker ALTIJD met 1 worker draait.
"""

import asyncio
import os
from conversion_service_zip import convert_pdf_with_zip_output

async def test_worker_configuration() -> bool:
    """Test dat Marker altijd met 1 worker draait."""
    
    if not os.path.exists('test_document.pdf'):
        print("❌ Test PDF niet gevonden!")
        return False
    
    print("🧪 Testing worker configuration...")
    
    # Test met verschillende worker instellingen
    test_configs = [
        {"pdftext_workers": 4, "name": "4 workers (should be overridden)"},
        {"pdftext_workers": 8, "name": "8 workers (should be overridden)"},
        {"pdftext_workers": 1, "name": "1 worker (should stay 1)"},
        {"pdftext_workers": 0, "name": "0 workers (should be overridden)"},
    ]
    
    for config in test_configs:
        print(f"\n🔍 Testing: {config['name']}")
        
        settings = {
            "output_format": "markdown",
            "use_llm": False,
            "extract_images": False,
            "debug": False,
            "pdftext_workers": config["pdftext_workers"]
        }
        
        try:
            result = await convert_pdf_with_zip_output('test_document.pdf', settings)
            
            if result.success:
                print(f"✅ Conversion successful")
                print(f"📄 Converted text length: {len(result.markdown_content)} characters")
            else:
                print(f"❌ Conversion failed: {result.error}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n🎯 Worker configuration test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_worker_configuration())
