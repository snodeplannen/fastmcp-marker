"""
Alternative conversion service that avoids multiprocessing issues on Windows.

This module provides a workaround for Windows multiprocessing problems
by using a different approach to PDF conversion.
"""

import asyncio
import tempfile
import os
import subprocess
import sys
from typing import Optional, Tuple

# Import Windows fix first
#import windows_fix

async def convert_pdf_with_subprocess(pdf_path: str, settings: dict) -> Tuple[str, str]:
    """
    Convert PDF using subprocess to avoid multiprocessing issues.
    
    This approach runs the conversion in a separate Python process
    to completely avoid multiprocessing threading issues.
    """
    output_format = settings.get("output_format", "markdown")
    
    # Create a temporary script for conversion
    script_content = f'''
import sys
import os
sys.path.append(r"{os.getcwd()}")

# Set environment variables
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMBA_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    
    # Initialize models
    models = create_model_dict()
    converter = PdfConverter(artifact_dict=models)
    
    # Convert PDF
    rendered_document = converter(r"{pdf_path}")
    text, _, _ = text_from_rendered(rendered_document)
    
    print("SUCCESS:", text)
    
except Exception as e:
    print("ERROR:", str(e))
    sys.exit(1)
'''
    
    # Write script to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
        script_file.write(script_content)
        script_path = script_file.name
    
    try:
        # Run the script in a subprocess
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            # Extract the converted text
            output_lines = result.stdout.strip().split('\n')
            if output_lines and output_lines[0].startswith('SUCCESS: '):
                converted_text = '\n'.join(output_lines[0].split('SUCCESS: ')[1:])
                return converted_text, output_format
            else:
                raise Exception("Unexpected output format from subprocess")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise Exception(f"Conversion failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        raise Exception("PDF conversion timed out after 10 minutes")
    except Exception as e:
        raise Exception(f"Subprocess conversion failed: {e}")
    finally:
        # Clean up temporary script
        try:
            os.unlink(script_path)
        except OSError:
            pass

async def convert_pdf_bytes_with_subprocess(pdf_bytes: bytes, settings: dict) -> Tuple[str, str]:
    """
    Convert PDF bytes using subprocess approach.
    """
    # Use a temporary file to handle the byte stream
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf_path = temp_pdf.name

    try:
        # Await the conversion of the temporary file
        converted_text, output_format = await convert_pdf_with_subprocess(temp_pdf_path, settings)
        return converted_text, output_format
    finally:
        # Ensure the temporary file is always cleaned up
        try:
            os.unlink(temp_pdf_path)
        except OSError:
            pass
