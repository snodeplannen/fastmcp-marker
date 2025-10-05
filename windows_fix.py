"""
Windows-specific wrapper to fix multiprocessing issues with Marker library.

This module provides a workaround for Windows multiprocessing problems
by setting appropriate environment variables and using spawn method.
"""

import os
import sys
import multiprocessing

def setup_windows_multiprocessing() -> None:
    """Setup Windows-compatible multiprocessing settings."""
    if sys.platform == "win32":
        # Set environment variables to prevent threading issues
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
        os.environ['NUMBA_NUM_THREADS'] = '1'
        
        # Additional environment variables for Marker library
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        # Disable multiprocessing completely
        os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU mode
        
        # Set multiprocessing start method to spawn for Windows
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # Already set, ignore
            pass
        
        print("🔧 Windows multiprocessing settings configured")

# Auto-setup when imported
setup_windows_multiprocessing()
