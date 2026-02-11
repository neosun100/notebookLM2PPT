"""
FastAPI Server for PDF2PPT
Comprehensive API with detailed documentation
"""

# Disable PIL decompression bomb check for large PDF images
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from pdf2ppt import pdf2svg, svg2emf, emf2ppt, clean_tmp, parse_page_range
from pdf2ppt.watermark import remove_watermark
from pypdf import PdfReader

app = FastAPI(
    title="PDF2PPT API",
    description="""
## Convert PDF Slides to PowerPoint with Vector Graphics

This API provides multiple ways to convert PDF presentations to PowerPoint format while maintaining the highest resolution using vector graphics.

### Features
- 🎯 Vector graphics conversion (highest quality)
- 📄 Page selection support
- ⚡ Parallel processing for speed
- 📊 Real-time progress streaming
- 📦 Batch conversion support
- 🌐 Multi-language Web UI
- 🎨 Ultra glassmorphism design
- 🖼️ Large image support (no pixel limit)
- 🧹 NotebookLM watermark removal
    """,
    version="1.4.0",
    contact={"name": "Teddy van Jerry", "url": "https://github.com/neosun100/notebookLM2PPT"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
)

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

UPLOAD_DIR = Path("/tmp/pdf2ppt/uploads")
OUTPUT_DIR = Path("/tmp/pdf2ppt/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ConversionOptions(BaseModel):
    pages: Optional[str] = Field(None, description="Page range (e.g., '1-5,7,9-11')")
    parallel: int = Field(4, ge=1, le=16, description="Parallel workers (1-16)")
    force: bool = Field(True, description="Force overwrite")
    no_clean: bool = Field(False, description="Keep temp files")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    return {"status": "healthy", "version": "1.4.0"}


@app.post("/api/convert", tags=["Conversion"])
async def convert_pdf(
    file: UploadFile = File(..., description="PDF file to convert"),
    options: str = Form("{}", description="JSON conversion options")
):
    opts = json.loads(options)
    task_id = f"{Path(file.filename).stem}_{asyncio.get_event_loop().time()}"
    input_path = UPLOAD_DIR / f"{task_id}.pdf"
    with open(input_path, "wb") as f:
        f.write(await file.read())

    async def generate():
        try:
            yield f"data: {json.dumps({'progress': 5, 'message': 'Reading PDF...', 'status': 'processing'})}\n\n"

            # Optional watermark removal
            actual_input = input_path
            if opts.get('remove_watermark', False):
                yield f"data: {json.dumps({'progress': 10, 'message': 'Removing watermark...', 'status': 'processing'})}\n\n"
                cleaned_path = UPLOAD_DIR / f"{task_id}_nowm.pdf"
                try:
                    await asyncio.to_thread(remove_watermark, str(input_path), str(cleaned_path))
                    actual_input = cleaned_path
                except Exception:
                    pass  # fallback to original

            pdf_reader = await asyncio.to_thread(PdfReader, actual_input)
            total_pages = len(pdf_reader.pages)
            pages = parse_page_range(opts.get('pages'), total_pages) if opts.get('pages') else list(range(1, total_pages + 1))
            yield f"data: {json.dumps({'progress': 20, 'message': 'Converting to SVG...', 'status': 'processing'})}\n\n"
            success = await asyncio.to_thread(pdf2svg, actual_input, 'pdf2svg', False)
            if not success:
                raise Exception("PDF to SVG conversion failed")
            yield f"data: {json.dumps({'progress': 50, 'message': 'Converting to EMF...', 'status': 'processing'})}\n\n"
            success, filters = await asyncio.to_thread(svg2emf, pdf_reader, actual_input, 'inkscape', pages, False, True, opts.get('parallel', 4))
            if not success:
                raise Exception("SVG to EMF conversion failed")
            yield f"data: {json.dumps({'progress': 80, 'message': 'Creating PowerPoint...', 'status': 'processing'})}\n\n"
            output_filename = f"{Path(file.filename).stem}.pptx"
            output_path = OUTPUT_DIR / output_filename
            await asyncio.to_thread(emf2ppt, pdf_reader, actual_input, output_path, pages, False)
            if not opts.get('no_clean', False):
                await asyncio.to_thread(clean_tmp, actual_input, False)
            input_path.unlink(missing_ok=True)
            if actual_input != input_path:
                actual_input.unlink(missing_ok=True)
            yield f"data: {json.dumps({'progress': 100, 'status': 'completed', 'output_file': output_filename, 'download_url': f'/api/download/{output_filename}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'progress': 100, 'status': 'error', 'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/download/{filename}", tags=["Conversion"])
async def download(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, detail=f"File not found: {filename}")
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=filename)


@app.post("/api/batch-convert", tags=["Conversion"])
async def batch_convert(files: List[UploadFile] = File(..., description="Multiple PDF files")):
    task_ids = []
    for file in files:
        task_id = f"{Path(file.filename).stem}_{asyncio.get_event_loop().time()}"
        task_ids.append(task_id)
        input_path = UPLOAD_DIR / f"{task_id}.pdf"
        with open(input_path, "wb") as f:
            f.write(await file.read())
    return {"task_ids": task_ids, "message": f"Queued {len(files)} files for conversion"}


@app.get("/api/info", tags=["System"])
async def api_info():
    return {
        "name": "PDF2PPT API",
        "version": "1.4.0",
        "description": "Convert PDF Slides to PowerPoint with Vector Graphics",
        "features": ["Vector graphics", "Page selection", "Parallel processing", "Batch conversion", "Large image support", "NotebookLM watermark removal"],
        "endpoints": {"ui": "/", "health": "/health", "docs": "/docs", "convert": "/api/convert", "batch": "/api/batch-convert", "download": "/api/download/{filename}"},
        "links": {"github": "https://github.com/neosun100/notebookLM2PPT", "pypi": "https://pypi.org/project/pdfslides2ppt/", "docker": "https://hub.docker.com/r/neosun/pdf2ppt"}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
