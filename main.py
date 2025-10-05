"""
FastMCP Marker - Simple Demo

Een eenvoudige demo van de PDF naar Markdown conversie service.
Dit bestand toont de basis functionaliteit zonder de volledige interfaces.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import Windows fix first
#import windows_fix

def print_banner():
    """Print een mooie banner."""
    print("=" * 60)
    print("🚀 FastMCP Marker - PDF to Markdown Service")
    print("=" * 60)
    print("Een geavanceerde PDF-naar-Markdown conversie service")
    print("met dubbele interface: FastMCP voor AI agents en Gradio voor gebruikers")
    print("=" * 60)
    print()

async def demo_conversion_service() -> None:
    """Demo van de conversion service."""
    print("🧪 Testing Conversion Service...")
    
    try:
        import conversion_service
        
        # Check converter status
        status = conversion_service.get_converter_status()
        print(f"   Converter Status: {status['status']}")
        print(f"   Message: {status['message']}")
        
        if status['initialized']:
            print("   ✅ Conversion service is ready!")
        else:
            print("   ⚠️  Conversion service needs dependencies installed")
            print("   Run: uv sync")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Make sure all dependencies are installed with: uv sync")

def demo_mcp_server() -> None:
    """Demo van de MCP server."""
    print("\n🤖 Testing MCP Server...")
    
    try:
        import mcp_server
        
        server = mcp_server.mcp
        print(f"   Server Name: {server.name}")
        print("   ✅ MCP server can be instantiated")
        print("   Available tools:")
        print("     - convert_pdf_to_markdown")
        print("     - get_converter_status")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")

def demo_gradio_app() -> None:
    """Demo van de Gradio app."""
    print("\n🌐 Testing Gradio App...")
    
    try:
        import importlib.util
        spec = importlib.util.find_spec("gradio_app_advanced_full")
        
        if spec is not None:
            print("   ✅ Gradio app can be imported")
            print("   Features:")
            print("     - Drag & drop PDF upload")
            print("     - Real-time conversion progress")
            print("     - Markdown preview")
            print("     - Download functionality")
        else:
            print("   ❌ Gradio app module not found")
        
    except Exception as e:
        print(f"   ❌ Error checking Gradio app: {e}")

def show_usage_instructions():
    """Toon gebruiksinstructies."""
    print("\n📋 How to Use:")
    print("-" * 30)
    print("1. Install dependencies:")
    print("   uv sync")
    print()
    print("2. Start basic Gradio interface:")
    print("   uv run gradio_app.py")
    print("   Then open: http://localhost:7860")
    print()
    print("3. Start advanced Gradio interface:")
    print("   uv run gradio_app_advanced.py")
    print("   Features: OCR, LLM, multiple formats")
    print()
    print("4. Start FastMCP server:")
    print("   uv run mcp_server.py")
    print("   Server runs on: http://localhost:8000")
    print()
    print("5. Run tests:")
    print("   uv run test_system.py")
    print()
    print("6. Use interactive startup:")
    print("   uv run start_service.py")

async def main() -> None:
    """Hoofdfunctie."""
    print_banner()
    
    await demo_conversion_service()
    demo_mcp_server()
    demo_gradio_app()
    show_usage_instructions()
    
    print("\n🎉 Demo completed!")
    print("Check the README.md for detailed usage instructions.")

if __name__ == "__main__":
    asyncio.run(main())
