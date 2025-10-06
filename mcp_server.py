"""
FastMCP server implementation for PDF to Markdown conversion.

This module implements the machine-facing interface using FastMCP framework.
It exposes the PDF conversion functionality as a discoverable MCP tool that
AI agents can use to convert PDF documents to Markdown format.
"""

from fastmcp import FastMCP


import conversion_service

# Instantiate the FastMCP server with a descriptive name
mcp = FastMCP(name="PDF to Markdown Conversion Service")

@mcp.tool
async def convert_pdf_to_markdown(pdf_file_content: bytes) -> str:
    """
    Converts the binary content of a PDF file to well-formatted Markdown text.

    This tool processes a given PDF document and returns its content as a
    single Markdown string, preserving tables, code blocks, and equations.
    It is suitable for use by AI agents that need to process PDF documents.

    The conversion uses the advanced Marker library which provides high-fidelity
    document intelligence, accurately parsing complex elements like tables,
    mathematical equations (converted to LaTeX), and multi-column layouts.

    Args:
        pdf_file_content: The raw binary content of the PDF file to be converted.

    Returns:
        A string containing the converted Markdown text.

    Raises:
        RuntimeError: If the Marker converter is not available.
        Exception: If the PDF conversion fails for any reason.
    """
    try:
        # Delegate the conversion to the core service module
        markdown_text = await conversion_service.convert_pdf_bytes_to_markdown(pdf_file_content, {"output_format": "markdown"})
        return markdown_text
    except Exception as e:
        # FastMCP will automatically catch this exception and return a
        # standard MCP Error message to the client.
        print(f"❌ Error in MCP tool execution: {e}")
        raise

@mcp.tool
async def convert_multiple_pdfs_to_markdown(pdf_files: list[dict]) -> dict:
    """
    Converts multiple PDF files to Markdown text in batch.

    This tool processes multiple PDF documents and returns their content as
    individual Markdown strings, preserving tables, code blocks, and equations.
    It is suitable for batch processing of PDF documents by AI agents.

    The conversion uses the advanced Marker library which provides high-fidelity
    document intelligence, accurately parsing complex elements like tables,
    mathematical equations (converted to LaTeX), and multi-column layouts.

    Args:
        pdf_files: A list of dictionaries, each containing:
            - filename: The name of the PDF file
            - content: The raw binary content of the PDF file

    Returns:
        A dictionary containing:
            - results: List of conversion results, each containing:
                - filename: Original filename
                - success: Boolean indicating if conversion succeeded
                - content: Markdown text (if successful)
                - error: Error message (if failed)
            - summary: Summary statistics (total, successful, failed)

    Raises:
        RuntimeError: If the Marker converter is not available.
        Exception: If batch processing fails for any reason.
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                filename = pdf_file.get('filename', 'unknown.pdf')
                content = pdf_file.get('content', b'')
                
                if not content:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'content': None,
                        'error': 'No content provided'
                    })
                    failed += 1
                    continue
                
                # Convert single PDF
                markdown_text = await conversion_service.convert_pdf_bytes_to_markdown(
                    content, {"output_format": "markdown"}
                )
                
                results.append({
                    'filename': filename,
                    'success': True,
                    'content': markdown_text,
                    'error': None
                })
                successful += 1
                
            except Exception as e:
                filename = pdf_file.get('filename', 'unknown.pdf')
                results.append({
                    'filename': filename,
                    'success': False,
                    'content': None,
                    'error': str(e)
                })
                failed += 1
        
        return {
            'results': results,
            'summary': {
                'total': len(pdf_files),
                'successful': successful,
                'failed': failed
            }
        }
        
    except Exception as e:
        print(f"❌ Error in batch MCP tool execution: {e}")
        raise

@mcp.tool
async def get_converter_status() -> dict:
    """
    Returns the current status of the PDF converter service.

    This tool allows AI agents to check if the converter is properly
    initialized and ready to process PDF files before attempting conversion.

    Returns:
        A dictionary containing status information including:
        - initialized: Boolean indicating if converter is ready
        - status: String status ("ready" or "failed")
        - message: Human-readable status message
    """
    return {"initialized": True, "status": "ready", "message": "Subprocess converter ready"}

# This block allows the server to be run directly from the command line
if __name__ == "__main__":
    # The run() method starts the server, defaulting to the STDIO transport
    # for local tool use. It can also be run with HTTP transport.
    print("🚀 Starting FastMCP PDF to Markdown server...")
    print("📋 Available tools:")
    print("   - convert_pdf_to_markdown: Convert single PDF bytes to Markdown text")
    print("   - convert_multiple_pdfs_to_markdown: Convert multiple PDFs to Markdown text (batch)")
    print("   - get_converter_status: Check converter initialization status")
    print()
    
    # Run with HTTP transport for easier testing
    mcp.run(transport="http", port=8000)
