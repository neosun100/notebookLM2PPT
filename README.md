[English](README.md) | [简体中文](README_CN.md)

# 📝 notebookLM2PPT

[![Python](https://img.shields.io/badge/Python-3.9+-green?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com)

> Convert NotebookLM PDF exports to PowerPoint with **watermark removal** and **vector graphics** (highest resolution).

## ✨ Features

- 🧹 **Watermark Removal** - Auto-remove NotebookLM bottom-right watermark (gradient-aware)
- 🎯 **Vector Graphics** - Maintains highest resolution in generated PPT
- 📝 **Metadata Conversion** - Preserves title, author and other metadata
- 📐 **Auto Detection** - Automatically detects slide size and aspect ratio
- 📄 **Page Selection** - Convert specific pages with `--pages` option
- ⚡ **Parallel Processing** - Speed up conversion with `--parallel` option
- 🎨 **Web UI** - Modern glassmorphism web interface with drag-and-drop
- 📡 **REST API** - FastAPI server with async processing
- 🔧 **MCP Support** - Model Context Protocol for AI integration
- 🐳 **Docker Ready** - All-in-one Docker image
- 🌍 **18 Languages** - Full internationalization support

## 🚀 Quick Start

### Option 1: Command Line (pip)

```bash
# Install
pip install -e .

# Convert with watermark removal
pdf2ppt input.pdf output.pptx --remove-watermark

# Short form
pdf2ppt input.pdf --rw --force
```

### Option 2: Docker

```bash
docker run -d -p 8100:8100 neosun/notebooklm2ppt:latest
```

Access at: http://localhost:8100

### Option 3: API Server

```bash
pip install -e ".[server]"
python -m uvicorn web.app:app --host 0.0.0.0 --port 8100
```

## 📦 Installation

### Prerequisites

- **Python >= 3.9**
- [**pdf2svg**](https://github.com/dawbarton/pdf2svg) - PDF to SVG conversion
- [**Inkscape**](https://inkscape.org/) - SVG to EMF conversion

```bash
# macOS
brew install pdf2svg inkscape

# Ubuntu/Debian
sudo apt-get install pdf2svg inkscape
```

### Install

```bash
git clone https://github.com/neosun100/notebookLM2PPT.git
cd notebookLM2PPT
pip install -e .
```

## 📖 Usage

### Basic

```bash
pdf2ppt input.pdf                          # Auto output: input.pptx
pdf2ppt input.pdf output.pptx              # Specify output
pdf2ppt input.pdf --rw                     # Remove watermark
pdf2ppt input.pdf --rw -f                  # Remove watermark + force overwrite
```

### Advanced

```bash
pdf2ppt input.pdf -p 1-5,7,9-11           # Specific pages
pdf2ppt input.pdf -j 4 --rw               # Parallel + watermark removal
pdf2ppt input.pdf --verbose --no-clean     # Debug mode
```

### CLI Options

```
positional arguments:
  input                    Input PDF file
  output                   Output PPTX file (default: input.pptx)

options:
  -v, --version            Show version
  --remove-watermark, --rw Remove NotebookLM watermark
  --pages, -p PAGES        Page range (e.g., "1-5,7,9-11")
  --parallel, -j N         Parallel workers (default: 1)
  --force, -f              Overwrite output file
  --verbose                Verbose output
  --no-clean               Keep temporary files
```

## 🔧 How It Works

```
PDF → [Remove Watermark] → PDF → SVG → EMF → PPTX
       (optional)          pdf2svg  inkscape  python-pptx
```

1. **Watermark Removal** (optional): PyMuPDF samples background colors column-by-column above the watermark region, then draws matching rectangles to cover it. Supports gradient backgrounds.
2. **PDF → SVG**: `pdf2svg` converts each page to vector SVG
3. **SVG → EMF**: `inkscape` converts SVG to EMF (required by python-pptx)
4. **EMF → PPTX**: `python-pptx` assembles the final presentation

## 🧪 Testing

```bash
pip install -e ".[test]"
pytest tests/ -v
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| PDF Processing | pypdf, PyMuPDF |
| PPT Generation | python-pptx |
| PDF to SVG | pdf2svg |
| SVG to EMF | Inkscape |
| CLI Output | rich |
| Web Server | FastAPI |
| AI Integration | FastMCP |

## 🏗️ Project Structure

```
notebookLM2PPT/
├── src/pdf2ppt/
│   ├── __init__.py        # Core conversion engine + CLI
│   └── watermark.py       # Watermark removal module
├── web/
│   ├── app.py             # FastAPI server
│   ├── templates/         # HTML templates
│   └── static/            # CSS + JS (18 languages)
├── mcp/
│   └── mcp_server.py      # MCP tool server
├── tests/
│   └── test_all.py        # Comprehensive test suite
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/notebookLM2PPT&type=Date)](https://star-history.com/#neosun100/notebookLM2PPT)
