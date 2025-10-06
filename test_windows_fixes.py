"""
Test script om te controleren of Windows multiprocessing fixes nog nodig zijn.
Test beide scenario's: met en zonder threading fixes.
"""

import asyncio
import os
import sys
import tempfile
import traceback
from typing import Dict, Any

def test_without_fixes() -> Dict[str, Any]:
    """Test Marker conversie zonder Windows fixes."""
    print("🧪 Testing WITHOUT Windows fixes...")
    
    # Clear all threading environment variables
    threading_vars = [
        'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
        'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMBA_NUM_THREADS',
        'TOKENIZERS_PARALLELISM', 'MKL_DYNAMIC', 'OMP_DYNAMIC',
        'GRPC_VERBOSITY', 'GLOG_minloglevel', 'PYTORCH_ENABLE_MPS_FALLBACK',
        'IN_STREAMLIT'
    ]
    
    # Backup current values
    backup_values = {}
    for var in threading_vars:
        backup_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    print("🔧 Cleared threading environment variables")
    
    try:
        # Import Marker without fixes
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        
        # Initialize models
        print("📦 Initializing Marker models...")
        models = create_model_dict()
        
        # Create converter with default settings (no threading fixes)
        print("🔧 Creating converter WITHOUT threading fixes...")
        converter = PdfConverter(artifact_dict=models)
        
        # Test with a simple PDF
        test_pdf_path = "test_document.pdf"
        if not os.path.exists(test_pdf_path):
            return {
                "success": False,
                "error": "Test PDF not found",
                "traceback": None
            }
        
        print(f"📄 Converting {test_pdf_path}...")
        rendered_document = converter(test_pdf_path)
        text, _, _ = text_from_rendered(rendered_document)
        
        print("✅ Conversion successful WITHOUT fixes!")
        return {
            "success": True,
            "error": None,
            "traceback": None,
            "text_length": len(str(text))
        }
        
    except Exception as e:
        print(f"❌ Conversion failed WITHOUT fixes: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        # Restore environment variables
        for var, value in backup_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

def test_with_fixes() -> Dict[str, Any]:
    """Test Marker conversie met Windows fixes."""
    print("\n🧪 Testing WITH Windows fixes...")
    
    # Apply Windows fixes
    os.environ["MKL_DYNAMIC"] = "FALSE"
    os.environ["OMP_DYNAMIC"] = "FALSE"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMBA_NUM_THREADS"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    os.environ["IN_STREAMLIT"] = "true"
    
    print("🔧 Applied Windows threading fixes")
    
    try:
        # Import Marker with fixes
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        
        # Initialize models
        print("📦 Initializing Marker models...")
        models = create_model_dict()
        
        # Create converter with threading fixes
        print("🔧 Creating converter WITH threading fixes...")
        config_dict = {
            "pdftext_workers": 1,
            "disable_multiprocessing": True,
        }
        converter = PdfConverter(artifact_dict=models, config=config_dict)
        
        # Test with a simple PDF
        test_pdf_path = "test_document.pdf"
        if not os.path.exists(test_pdf_path):
            return {
                "success": False,
                "error": "Test PDF not found",
                "traceback": None
            }
        
        print(f"📄 Converting {test_pdf_path}...")
        rendered_document = converter(test_pdf_path)
        text, _, _ = text_from_rendered(rendered_document)
        
        print("✅ Conversion successful WITH fixes!")
        return {
            "success": True,
            "error": None,
            "traceback": None,
            "text_length": len(str(text))
        }
        
    except Exception as e:
        print(f"❌ Conversion failed WITH fixes: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def test_multiprocessing_methods() -> Dict[str, Any]:
    """Test verschillende multiprocessing methoden."""
    print("\n🧪 Testing multiprocessing methods...")
    
    import multiprocessing
    
    results = {}
    
    # Test spawn method (Windows default)
    try:
        multiprocessing.set_start_method('spawn', force=True)
        print("✅ Spawn method set successfully")
        results['spawn'] = True
    except Exception as e:
        print(f"❌ Spawn method failed: {e}")
        results['spawn'] = False
    
    # Test fork method (Unix default)
    try:
        multiprocessing.set_start_method('fork', force=True)
        print("✅ Fork method set successfully")
        results['fork'] = True
    except Exception as e:
        print(f"❌ Fork method failed: {e}")
        results['fork'] = False
    
    # Test forkserver method
    try:
        multiprocessing.set_start_method('forkserver', force=True)
        print("✅ Forkserver method set successfully")
        results['forkserver'] = True
    except Exception as e:
        print(f"❌ Forkserver method failed: {e}")
        results['forkserver'] = False
    
    return results

def main():
    """Hoofdfunctie om alle tests uit te voeren."""
    print("🚀 Windows Fixes Test Suite")
    print("=" * 50)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print()
    
    # Check if test PDF exists
    if not os.path.exists("test_document.pdf"):
        print("❌ test_document.pdf not found!")
        print("Please ensure test_document.pdf is in the current directory.")
        return
    
    # Test 1: Without fixes
    result_without = test_without_fixes()
    
    # Test 2: With fixes
    result_with = test_with_fixes()
    
    # Test 3: Multiprocessing methods
    mp_results = test_multiprocessing_methods()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    print(f"\n🔧 WITHOUT Windows fixes:")
    print(f"   Success: {result_without['success']}")
    if not result_without['success']:
        print(f"   Error: {result_without['error']}")
    else:
        print(f"   Text length: {result_without['text_length']} characters")
    
    print(f"\n✅ WITH Windows fixes:")
    print(f"   Success: {result_with['success']}")
    if not result_with['success']:
        print(f"   Error: {result_with['error']}")
    else:
        print(f"   Text length: {result_with['text_length']} characters")
    
    print(f"\n🔄 Multiprocessing methods:")
    for method, success in mp_results.items():
        status = "✅" if success else "❌"
        print(f"   {method}: {status}")
    
    # Conclusion
    print(f"\n🎯 CONCLUSION:")
    if result_without['success'] and result_with['success']:
        print("   Both tests passed - Windows fixes may NOT be necessary!")
        print("   Consider removing threading fixes for better performance.")
    elif not result_without['success'] and result_with['success']:
        print("   Only test WITH fixes passed - Windows fixes ARE necessary!")
        print("   Keep the threading fixes in place.")
    elif result_without['success'] and not result_with['success']:
        print("   Only test WITHOUT fixes passed - This is unexpected!")
        print("   Investigate why fixes are causing issues.")
    else:
        print("   Both tests failed - There may be other issues!")
        print("   Check Marker installation and dependencies.")
    
    # Detailed error reporting
    if not result_without['success'] and result_without['traceback']:
        print(f"\n🔍 DETAILED ERROR (without fixes):")
        print(result_without['traceback'])
    
    if not result_with['success'] and result_with['traceback']:
        print(f"\n🔍 DETAILED ERROR (with fixes):")
        print(result_with['traceback'])

if __name__ == "__main__":
    main()
