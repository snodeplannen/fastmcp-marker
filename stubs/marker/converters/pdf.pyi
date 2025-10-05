import io
from typing import Any, Dict
from contextlib import contextmanager

class PdfConverter:
    """PDF converter class for converting PDFs to markdown."""
    
    def __init__(
        self,
        artifact_dict: Dict[str, Any],
        processor_list: list[str] | None = None,
        renderer: str | None = None,
        llm_service: str | None = None,
        config: Dict[str, Any] | None = None
    ) -> None:
        """Initialize PDF converter with configuration and models."""
        ...
    
    @contextmanager
    def filepath_to_str(self, file_input: str | io.BytesIO) -> Any:
        """Convert file input to string path."""
        ...
    
    def build_document(self, filepath: str) -> Any:
        """Build document from PDF file."""
        ...
    
    def __call__(self, filepath: str | io.BytesIO) -> Any:
        """Convert PDF file to rendered document."""
        ...
