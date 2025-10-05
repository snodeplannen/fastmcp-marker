#!/usr/bin/env python3
"""
Startup script voor FastMCP Marker service.

Dit script biedt een eenvoudige manier om beide interfaces te starten:
- Gradio web interface voor gebruikers
- FastMCP server voor AI agents
"""

import asyncio
import subprocess
import sys
import time
import signal
from pathlib import Path

# Import Windows fix first
import windows_fix

def print_banner():
    """Print een mooie banner."""
    print("=" * 60)
    print("🚀 FastMCP Marker - PDF to Markdown Service")
    print("=" * 60)
    print()

def print_menu():
    """Print het hoofdmenu."""
    print("📋 Kies een optie:")
    print("1. 🌐 Start Gradio Web Interface (basis)")
    print("2. 🚀 Start Geavanceerde Gradio Interface")
    print("3. 🤖 Start FastMCP Server (voor AI agents)")
    print("4. 🧪 Run Test Suite")
    print("5. 📊 Check System Status")
    print("6. ❌ Exit")
    print()

def run_gradio():
    """Start de basis Gradio web interface."""
    print("🌐 Starting basic Gradio web interface...")
    print("   URL: http://localhost:7860")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "uv", "run", "gradio_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Gradio interface stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Gradio: {e}")

def run_advanced_gradio():
    """Start de geavanceerde Gradio web interface."""
    print("🚀 Starting advanced Gradio web interface...")
    print("   URL: http://localhost:7860")
    print("   Features: OCR settings, LLM enhancement, multiple formats")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "uv", "run", "gradio_app_advanced.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Advanced Gradio interface stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Advanced Gradio: {e}")

def run_mcp_server():
    """Start de FastMCP server."""
    print("🤖 Starting FastMCP server...")
    print("   URL: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "uv", "run", "mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 MCP server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting MCP server: {e}")

def run_tests():
    """Run de test suite."""
    print("🧪 Running test suite...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "-m", "uv", "run", "test_system.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        print("Output:", e.stdout)
        print("Errors:", e.stderr)

def check_status():
    """Check system status."""
    print("📊 Checking system status...")
    print()
    
    # Check if required files exist
    required_files = [
        "conversion_service.py",
        "mcp_server.py", 
        "gradio_app.py",
        "test_system.py",
        "pyproject.toml"
    ]
    
    print("📁 Required files:")
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    print()
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if uv is available
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        print(f"📦 uv version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv not found - please install uv package manager")
    
    print()

def main():
    """Hoofdfunctie."""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                run_gradio()
            elif choice == "2":
                run_advanced_gradio()
            elif choice == "3":
                run_mcp_server()
            elif choice == "4":
                run_tests()
            elif choice == "5":
                check_status()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
            
            print("\n" + "-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
