"""
MCP Tool Server for PDF2PPT
Model Context Protocol integration for AI assistants

This server provides three main tools for PDF to PPT conversion:
1. convert_pdf_to_ppt - Convert single PDF file
2. batch_convert_pdfs - Batch convert directory of PDFs
3. check_dependencies - Verify required tools are installed

Usage:
    python mcp/mcp_server.py

Configuration (for Claude Desktop or other MCP clients):
    {
      "mcpServers": {
        "pdf2ppt": {
          "command": "python",
          "args": ["/path/to/pdf2ppt/mcp/mcp_server.py"]
        }
      }
    }
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fastmcp import FastMCP
from pdf2ppt import pdf2svg, svg2emf, emf2ppt, clean_tmp, parse_page_range
from pdf2ppt.watermark import remove_watermark as _remove_watermark
from pypdf import PdfReader

mcp = FastMCP("pdf2ppt")


@mcp.tool()
def convert_pdf_to_ppt(
    input_pdf: str,
    output_ppt: Optional[str] = None,
    pages: Optional[str] = None,
    parallel: int = 4,
    force: bool = True,
    no_clean: bool = False,
    remove_watermark: bool = False
) -> Dict[str, Any]:
    """
    Convert a PDF file to PowerPoint presentation with vector graphics.
    
    This tool maintains the highest resolution by using vector graphics (SVG → EMF → PPT).
    Perfect for converting LaTeX Beamer or Typst Touying slides.
    
    Args:
        input_pdf: Path to the input PDF file (required)
                  Example: "/path/to/slides.pdf" or "lecture.pdf"
        
        output_ppt: Path to the output PPTX file (optional)
                   If not specified, uses input filename with .pptx extension
                   Example: "/path/to/output.pptx" or "lecture.pptx"
        
        pages: Page range to convert (optional)
              Format: "start-end,single,start-end"
              Examples:
                - "1-5" → pages 1 to 5
                - "1,3,5" → pages 1, 3, and 5
                - "1-5,7,9-11" → pages 1-5, 7, and 9-11
              Leave empty to convert all pages
        
        parallel: Number of parallel workers (default: 4)
                 Range: 1-16
                 Higher values = faster conversion (if you have multiple CPU cores)
                 Recommended: 4-8 for most systems
        
        force: Force overwrite if output file exists (default: True)
              Set to False to prevent accidental overwrites
        
        no_clean: Keep temporary files for debugging (default: False)
                 Temporary files are stored in {input_dir}/_pdf2ppt.tmp/
        
        remove_watermark: Remove NotebookLM watermark before conversion (default: False)
                         Automatically detects and removes the bottom-right watermark
                         from NotebookLM exported PDFs. Supports gradient backgrounds.
    
    Returns:
        Dictionary with conversion results:
        {
            "status": "success" or "error",
            "output": "/path/to/output.pptx",
            "pages_converted": 10,
            "total_pages": 20,
            "watermark_removed": true (if remove_watermark was enabled),
            "warning": "Pages [3, 5] may have transparency issues" (if applicable)
        }
    
    Examples:
        # Convert entire PDF
        >>> convert_pdf_to_ppt("lecture.pdf")
        {'status': 'success', 'output': 'lecture.pptx', 'pages_converted': 20, 'total_pages': 20}
        
        # Convert specific pages with parallel processing
        >>> convert_pdf_to_ppt("slides.pdf", pages="1-10", parallel=8)
        {'status': 'success', 'output': 'slides.pptx', 'pages_converted': 10, 'total_pages': 50}
        
        # Convert with custom output path
        >>> convert_pdf_to_ppt("input.pdf", output_ppt="/output/result.pptx")
        {'status': 'success', 'output': '/output/result.pptx', 'pages_converted': 15, 'total_pages': 15}
    
    Common Errors:
        - "Input file not found" → Check if the file path is correct
        - "Failed to convert PDF to SVG" → Install pdf2svg (brew install pdf2svg)
        - "Failed to convert SVG to EMF" → Install inkscape (brew install inkscape)
        - "Output file exists" → Use force=True or delete the existing file
    """
    try:
        input_path = Path(input_pdf)
        
        if not input_path.exists():
            return {
                'status': 'error',
                'error': f'Input file not found: {input_pdf}'
            }
        
        # Determine output path
        if output_ppt:
            output_path = Path(output_ppt)
        else:
            output_path = input_path.with_suffix('.pptx')
        
        # Check if output exists
        if output_path.exists() and not force:
            return {
                'status': 'error',
                'error': f'Output file exists: {output_path}. Use force=True to overwrite.'
            }
        
        # Read PDF
        pdf_reader = PdfReader(input_path)
        total_pages = len(pdf_reader.pages)
        
        # Optional watermark removal
        actual_input = input_path
        watermark_removed = False
        if remove_watermark:
            try:
                cleaned = input_path.parent / f'{input_path.stem}_nowm.pdf'
                _remove_watermark(str(input_path), str(cleaned))
                actual_input = cleaned
                pdf_reader = PdfReader(actual_input)
                watermark_removed = True
            except Exception:
                pass  # fallback to original
        
        # Parse page range
        pages_to_convert = parse_page_range(pages, total_pages) if pages else list(range(1, total_pages + 1))
        
        # Step 1: PDF to SVG
        if not pdf2svg(actual_input, 'pdf2svg', False):
            return {
                'status': 'error',
                'error': 'Failed to convert PDF to SVG. Is pdf2svg installed? (brew install pdf2svg)'
            }
        
        # Step 2: SVG to EMF
        success, filters = svg2emf(
            pdf_reader, actual_input, 'inkscape',
            pages_to_convert, False, False, parallel
        )
        
        if not success:
            return {
                'status': 'error',
                'error': 'Failed to convert SVG to EMF. Is inkscape installed? (brew install inkscape)'
            }
        
        # Step 3: EMF to PPT
        emf2ppt(pdf_reader, actual_input, output_path, pages_to_convert, False)
        
        # Cleanup
        if not no_clean:
            clean_tmp(actual_input, False)
        if watermark_removed and actual_input != input_path:
            actual_input.unlink(missing_ok=True)
        
        result = {
            'status': 'success',
            'output': str(output_path),
            'pages_converted': len(pages_to_convert),
            'total_pages': total_pages,
            'watermark_removed': watermark_removed
        }
        
        if filters:
            result['warning'] = f'Pages {filters} may have transparency issues. See: https://github.com/neosun100/notebookLM2PPT/issues/1'
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Unexpected error: {str(e)}'
        }


@mcp.tool()
def batch_convert_pdfs(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.pdf",
    parallel: int = 4
) -> Dict[str, Any]:
    """
    Batch convert multiple PDF files in a directory.
    
    This tool automatically finds all PDF files matching the pattern and converts them.
    Perfect for processing multiple lecture slides or presentation files at once.
    
    Args:
        input_dir: Directory containing PDF files (required)
                  Example: "./lectures" or "/path/to/slides"
        
        output_dir: Output directory for PPTX files (optional)
                   If not specified, PPTX files are created in the same directory as PDFs
                   Example: "./output" or "/path/to/pptx"
        
        pattern: File pattern to match (default: "*.pdf")
                Examples:
                  - "*.pdf" → all PDF files
                  - "lecture*.pdf" → files starting with "lecture"
                  - "2024-*.pdf" → files starting with "2024-"
        
        parallel: Number of parallel workers per file (default: 4)
                 Higher values = faster conversion per file
    
    Returns:
        Dictionary with batch conversion results:
        {
            "status": "success",
            "converted": 5,
            "failed": 0,
            "total": 5,
            "files": [
                {"file": "lecture1.pdf", "status": "success", "output": "lecture1.pptx"},
                {"file": "lecture2.pdf", "status": "success", "output": "lecture2.pptx"},
                ...
            ]
        }
    
    Examples:
        # Convert all PDFs in a directory
        >>> batch_convert_pdfs("./lectures")
        {'status': 'success', 'converted': 10, 'failed': 0, 'total': 10, 'files': [...]}
        
        # Convert specific pattern with custom output directory
        >>> batch_convert_pdfs("./slides", output_dir="./pptx", pattern="2024-*.pdf")
        {'status': 'success', 'converted': 5, 'failed': 0, 'total': 5, 'files': [...]}
        
        # High-performance batch conversion
        >>> batch_convert_pdfs("./lectures", parallel=8)
        {'status': 'success', 'converted': 20, 'failed': 0, 'total': 20, 'files': [...]}
    
    Common Errors:
        - "Input directory not found" → Check if the directory path is correct
        - "No PDF files found" → Check the pattern or directory contents
        - Individual file errors are reported in the 'files' array
    """
    try:
        input_path = Path(input_dir)
        
        if not input_path.exists() or not input_path.is_dir():
            return {
                'status': 'error',
                'error': f'Input directory not found: {input_dir}'
            }
        
        output_path = Path(output_dir) if output_dir else input_path
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find PDF files
        pdf_files = list(input_path.glob(pattern))
        
        if not pdf_files:
            return {
                'status': 'error',
                'error': f'No PDF files found matching pattern: {pattern} in {input_dir}'
            }
        
        results = []
        success_count = 0
        fail_count = 0
        
        for pdf_file in pdf_files:
            output_file = output_path / pdf_file.with_suffix('.pptx').name
            
            result = convert_pdf_to_ppt(
                str(pdf_file),
                str(output_file),
                parallel=parallel,
                force=True
            )
            
            results.append({
                'file': pdf_file.name,
                'status': result['status'],
                'output': result.get('output'),
                'error': result.get('error')
            })
            
            if result['status'] == 'success':
                success_count += 1
            else:
                fail_count += 1
        
        return {
            'status': 'success',
            'converted': success_count,
            'failed': fail_count,
            'total': len(pdf_files),
            'files': results
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Batch conversion error: {str(e)}'
        }


@mcp.tool()
def check_dependencies() -> Dict[str, Any]:
    """
    Check if required dependencies (pdf2svg, inkscape) are installed.
    
    This tool verifies that all external dependencies needed for PDF to PPT conversion
    are properly installed and accessible on your system.
    
    Returns:
        Dictionary with dependency status:
        {
            "pdf2svg": true/false,
            "inkscape": true/false,
            "all_installed": true/false,
            "install_instructions": {
                "macos": "brew install pdf2svg inkscape",
                "ubuntu": "sudo apt-get install pdf2svg inkscape",
                "windows": "Download from official websites"
            }
        }
    
    Examples:
        # Check dependencies before conversion
        >>> deps = check_dependencies()
        >>> if not deps['all_installed']:
        ...     print(f"Missing dependencies. Install with: {deps['install_instructions']['macos']}")
        ... else:
        ...     print("All dependencies installed!")
        
        # Conditional conversion based on dependencies
        >>> deps = check_dependencies()
        >>> if deps['all_installed']:
        ...     result = convert_pdf_to_ppt("slides.pdf")
        ... else:
        ...     print("Please install dependencies first")
    
    Dependency Details:
        - pdf2svg: Converts PDF pages to SVG format
          Install: brew install pdf2svg (macOS) or sudo apt install pdf2svg (Ubuntu)
        
        - inkscape: Converts SVG to EMF format (required by python-pptx)
          Install: brew install inkscape (macOS) or sudo apt install inkscape (Ubuntu)
    
    Troubleshooting:
        - If pdf2svg shows as not installed but you installed it:
          → Check if it's in your PATH: which pdf2svg
          → Try specifying full path in conversion
        
        - If inkscape shows as not installed:
          → Verify installation: inkscape --version
          → On macOS, ensure Homebrew is in PATH
    """
    import subprocess
    
    def check_command(cmd):
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
            return True
        except:
            # pdf2svg doesn't have --version, try without it
            try:
                subprocess.run([cmd], capture_output=True, timeout=5)
                return True
            except:
                return False
    
    pdf2svg_installed = check_command('pdf2svg')
    inkscape_installed = check_command('inkscape')
    
    result = {
        'pdf2svg': pdf2svg_installed,
        'inkscape': inkscape_installed,
        'all_installed': pdf2svg_installed and inkscape_installed
    }
    
    if not result['all_installed']:
        result['install_instructions'] = {
            'macos': 'brew install pdf2svg inkscape',
            'ubuntu': 'sudo apt-get install pdf2svg inkscape',
            'windows': 'Download from https://github.com/dawbarton/pdf2svg and https://inkscape.org/'
        }
        result['missing'] = []
        if not pdf2svg_installed:
            result['missing'].append('pdf2svg')
        if not inkscape_installed:
            result['missing'].append('inkscape')
    
    return result


if __name__ == "__main__":
    mcp.run()
