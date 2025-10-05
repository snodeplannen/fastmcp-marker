from typing import Any, Dict

class ConfigParser:
    """Configuration parser for Marker settings."""
    
    def __init__(self, cli_options: Dict[str, Any]) -> None:
        """Initialize config parser with settings dictionary."""
        ...
    
    @staticmethod
    def common_options(fn: Any) -> Any:
        """Common options decorator."""
        ...
    
    def generate_config_dict(self) -> Dict[str, Any]:
        """Generate configuration dictionary."""
        ...
    
    def get_llm_service(self) -> Any:
        """Get LLM service configuration."""
        ...
    
    def get_renderer(self) -> Any:
        """Get renderer configuration."""
        ...
    
    def get_processors(self) -> Any:
        """Get processors configuration."""
        ...
    
    def get_converter_cls(self) -> Any:
        """Get converter class."""
        ...
    
    def get_output_folder(self, filepath: str) -> str:
        """Get output folder path."""
        ...
    
    def get_base_filename(self, filepath: str) -> str:
        """Get base filename."""
        ...