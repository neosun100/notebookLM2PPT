"""Watermark removal for NotebookLM exported PDFs.

Uses PyMuPDF to detect and cover the bottom-right watermark with
column-by-column sampled background colors (supports gradients).
"""

import io
from pathlib import Path

import fitz
from PIL import Image


def remove_watermark(input_path: str, output_path: str) -> dict:
    """Remove NotebookLM watermark from every page of a PDF.

    Args:
        input_path: Source PDF file path.
        output_path: Destination PDF file path.

    Returns:
        dict with ``pages_processed`` count.
    """
    doc = fitz.open(input_path)
    pages_processed = 0

    for page in doc:
        rect = page.rect

        # Watermark region \u2013 fixed bottom-right position used by NotebookLM
        wm_x1 = rect.width - 115
        wm_y1 = rect.height - 30
        wm_x2 = rect.width - 5
        wm_y2 = rect.height - 5

        # Sample a thin strip just above the watermark for background colours
        sample_rect = fitz.Rect(wm_x1, wm_y1 - 10, wm_x2, wm_y1 - 2)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=sample_rect)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        pixels = img.load()

        # Draw column-by-column to preserve gradient backgrounds
        col_width = (wm_x2 - wm_x1) / img.width
        for x in range(img.width):
            r, g, b = (c / 255 for c in pixels[x, img.height // 2][:3])
            col_rect = fitz.Rect(
                wm_x1 + x * col_width, wm_y1,
                wm_x1 + (x + 1) * col_width, wm_y2,
            )
            page.draw_rect(col_rect, color=(r, g, b), fill=(r, g, b))

        pages_processed += 1

    doc.save(output_path)
    doc.close()
    return {"pages_processed": pages_processed}
