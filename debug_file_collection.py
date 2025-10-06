"""
Debug script om te onderzoeken waarom bestandsverzameling niet werkt.
"""

import os
import tempfile
from conversion_service_zip import convert_pdf_with_zip_output

async def debug_file_collection():
    """Debug de bestandsverzameling."""
    
    if not os.path.exists('test_document.pdf'):
        print("❌ Test PDF niet gevonden!")
        return
    
    print("🔍 Debugging file collection...")
    
    settings = {
        "output_format": "markdown",
        "use_llm": False,
        "extract_images": True,
        "debug": True,
        "debug_layout_images": True,
        "debug_pdf_images": True,
        "debug_json": True,
        "debug_data_folder": "debug_data"
    }
    
    try:
        result = await convert_pdf_with_zip_output('test_document.pdf', settings)
        
        print(f"📄 PDF: {result.pdf_name}")
        print(f"✅ Success: {result.success}")
        print(f"📁 Output dir: {result.output_dir}")
        print(f"📄 Output files: {len(result.output_files)}")
        print(f"🐛 Debug files: {len(result.debug_files)}")
        print(f"🖼️ Image files: {len(result.image_files)}")
        
        if result.output_dir and os.path.exists(result.output_dir):
            print(f"\n📁 Contents of output directory '{result.output_dir}':")
            for root, dirs, files in os.walk(result.output_dir):
                level = root.replace(result.output_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        else:
            print("❌ Output directory does not exist!")
        
        # Toon de geconverteerde tekst
        print(f"\n📝 Converted text preview:")
        print(result.markdown_content[:500] + "..." if len(result.markdown_content) > 500 else result.markdown_content)
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_file_collection())
