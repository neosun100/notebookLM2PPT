"""Comprehensive test suite for notebookLM2PPT.

Tests cover:
- Watermark removal module
- Page range parsing
- Dependency checking
- CLI argument parsing
- Web API endpoints
- MCP server tools

Run: pytest tests/test_all.py -v
"""

import io
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import fitz
from PIL import Image

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pdf2ppt import parse_page_range, check_dependency, __version__
from pdf2ppt.watermark import remove_watermark


# ── Helpers ──────────────────────────────────────────────────────────

def create_test_pdf(path: str, pages: int = 3, width: float = 612, height: float = 792):
    """Create a minimal test PDF with coloured pages."""
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=width, height=height)
        # Draw a background colour
        page.draw_rect(page.rect, color=(0.2, 0.3, 0.8), fill=(0.9, 0.9, 0.95))
        # Simulate a NotebookLM watermark in bottom-right
        wm_rect = fitz.Rect(width - 115, height - 30, width - 5, height - 5)
        page.draw_rect(wm_rect, color=(0.5, 0.5, 0.5), fill=(0.5, 0.5, 0.5))
        page.insert_text((50, 100), f"Test Page {i + 1}", fontsize=24)
    doc.save(path)
    doc.close()


# ── Version ──────────────────────────────────────────────────────────

class TestVersion:
    def test_version_format(self):
        parts = __version__.split('.')
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ── Page Range Parsing ───────────────────────────────────────────────

class TestParsePageRange:
    def test_empty_returns_all(self):
        assert parse_page_range('', 10) == list(range(1, 11))

    def test_none_returns_all(self):
        assert parse_page_range(None, 5) == list(range(1, 6))

    def test_single_page(self):
        assert parse_page_range('3', 10) == [3]

    def test_range(self):
        assert parse_page_range('2-5', 10) == [2, 3, 4, 5]

    def test_mixed(self):
        assert parse_page_range('1-3,7,9-10', 10) == [1, 2, 3, 7, 9, 10]

    def test_out_of_range_clamped(self):
        result = parse_page_range('1-100', 5)
        assert result == [1, 2, 3, 4, 5]

    def test_zero_ignored(self):
        result = parse_page_range('0,1,2', 5)
        assert 0 not in result
        assert 1 in result

    def test_duplicates_removed(self):
        result = parse_page_range('1,1,2,2', 5)
        assert result == [1, 2]

    def test_reverse_range(self):
        # '5-3' should produce nothing since start > end
        result = parse_page_range('5-3', 10)
        assert result == []


# ── Watermark Removal ────────────────────────────────────────────────

class TestWatermarkRemoval:
    def test_basic_removal(self, tmp_path):
        input_pdf = str(tmp_path / 'input.pdf')
        output_pdf = str(tmp_path / 'output.pdf')
        create_test_pdf(input_pdf, pages=2)

        result = remove_watermark(input_pdf, output_pdf)

        assert result['pages_processed'] == 2
        assert os.path.exists(output_pdf)
        # Output should be a valid PDF
        doc = fitz.open(output_pdf)
        assert len(doc) == 2
        doc.close()

    def test_single_page(self, tmp_path):
        input_pdf = str(tmp_path / 'single.pdf')
        output_pdf = str(tmp_path / 'single_out.pdf')
        create_test_pdf(input_pdf, pages=1)

        result = remove_watermark(input_pdf, output_pdf)
        assert result['pages_processed'] == 1

    def test_many_pages(self, tmp_path):
        input_pdf = str(tmp_path / 'many.pdf')
        output_pdf = str(tmp_path / 'many_out.pdf')
        create_test_pdf(input_pdf, pages=10)

        result = remove_watermark(input_pdf, output_pdf)
        assert result['pages_processed'] == 10

    def test_output_file_size(self, tmp_path):
        input_pdf = str(tmp_path / 'size.pdf')
        output_pdf = str(tmp_path / 'size_out.pdf')
        create_test_pdf(input_pdf, pages=3)

        remove_watermark(input_pdf, output_pdf)

        # Output should exist and have reasonable size
        assert os.path.getsize(output_pdf) > 0

    def test_watermark_region_covered(self, tmp_path):
        """Verify the watermark region pixels changed after removal."""
        input_pdf = str(tmp_path / 'verify.pdf')
        output_pdf = str(tmp_path / 'verify_out.pdf')
        create_test_pdf(input_pdf, pages=1)

        # Sample watermark region before
        doc_before = fitz.open(input_pdf)
        page = doc_before[0]
        rect = page.rect
        wm_rect = fitz.Rect(rect.width - 115, rect.height - 30, rect.width - 5, rect.height - 5)
        pix_before = page.get_pixmap(clip=wm_rect)
        before_bytes = pix_before.tobytes()
        doc_before.close()

        remove_watermark(input_pdf, output_pdf)

        # Sample watermark region after
        doc_after = fitz.open(output_pdf)
        page = doc_after[0]
        pix_after = page.get_pixmap(clip=wm_rect)
        after_bytes = pix_after.tobytes()
        doc_after.close()

        # Pixels should be different (watermark was covered)
        assert before_bytes != after_bytes

    def test_nonexistent_input_raises(self, tmp_path):
        with pytest.raises(Exception):
            remove_watermark(str(tmp_path / 'nonexistent.pdf'), str(tmp_path / 'out.pdf'))

    def test_different_page_sizes(self, tmp_path):
        """Test with landscape and different dimensions."""
        input_pdf = str(tmp_path / 'landscape.pdf')
        output_pdf = str(tmp_path / 'landscape_out.pdf')
        create_test_pdf(input_pdf, pages=2, width=842, height=595)  # A4 landscape

        result = remove_watermark(input_pdf, output_pdf)
        assert result['pages_processed'] == 2


# ── Dependency Checking ──────────────────────────────────────────────

class TestDependencyCheck:
    def test_existing_command(self):
        # 'python' should always exist
        assert check_dependency('python3', 'python3') is True

    def test_nonexistent_command(self):
        assert check_dependency('nonexistent_tool_xyz', 'test') is False

    def test_pdf2svg_check(self):
        # Should not crash regardless of whether pdf2svg is installed
        result = check_dependency('pdf2svg', 'pdf2svg')
        assert isinstance(result, bool)

    def test_inkscape_check(self):
        result = check_dependency('inkscape', 'inkscape')
        assert isinstance(result, bool)


# ── CLI Argument Parsing ─────────────────────────────────────────────

class TestCLI:
    def test_version_flag(self):
        """--version should print version and exit."""
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['pdf2ppt', '--version']):
                from pdf2ppt import main
                main()
        assert exc_info.value.code == 0

    def test_missing_input_exits(self):
        """Missing input file should exit with error."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['pdf2ppt', '/nonexistent/file.pdf']):
                from pdf2ppt import main
                main()


# ── Web API (unit-level) ─────────────────────────────────────────────

class TestWebAPI:
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from web.app import app
            from starlette.testclient import TestClient
            return TestClient(app)
        except ImportError:
            pytest.skip('FastAPI/starlette not installed (install with: pip install -e ".[server]")')

    def test_health_endpoint(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_api_info(self, client):
        resp = client.get('/api/info')
        assert resp.status_code == 200
        data = resp.json()
        assert 'NotebookLM watermark removal' in data['features']

    def test_index_page(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert 'PDF2PPT' in resp.text

    def test_download_404(self, client):
        resp = client.get('/api/download/nonexistent.pptx')
        assert resp.status_code == 404


# ── Integration: Watermark + PDF validity ────────────────────────────

class TestIntegration:
    def test_watermark_preserves_page_count(self, tmp_path):
        input_pdf = str(tmp_path / 'int.pdf')
        output_pdf = str(tmp_path / 'int_out.pdf')
        create_test_pdf(input_pdf, pages=5)

        remove_watermark(input_pdf, output_pdf)

        doc = fitz.open(output_pdf)
        assert len(doc) == 5
        doc.close()

    def test_watermark_preserves_page_dimensions(self, tmp_path):
        input_pdf = str(tmp_path / 'dim.pdf')
        output_pdf = str(tmp_path / 'dim_out.pdf')
        create_test_pdf(input_pdf, pages=1, width=800, height=600)

        remove_watermark(input_pdf, output_pdf)

        doc = fitz.open(output_pdf)
        page = doc[0]
        assert abs(page.rect.width - 800) < 1
        assert abs(page.rect.height - 600) < 1
        doc.close()

    def test_watermark_output_is_valid_pdf(self, tmp_path):
        input_pdf = str(tmp_path / 'valid.pdf')
        output_pdf = str(tmp_path / 'valid_out.pdf')
        create_test_pdf(input_pdf, pages=3)

        remove_watermark(input_pdf, output_pdf)

        # Should be readable by pypdf too
        from pypdf import PdfReader
        reader = PdfReader(output_pdf)
        assert len(reader.pages) == 3
