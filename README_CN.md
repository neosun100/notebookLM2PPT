[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# pdf2ppt

[![PyPI version](https://badge.fury.io/py/pdfslides2ppt.svg)](https://badge.fury.io/py/pdfslides2ppt)
[![Python](https://img.shields.io/pypi/pyversions/pdfslides2ppt.svg)](https://pypi.org/project/pdfslides2ppt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/neosun100/pdf2ppt.svg)](https://github.com/neosun100/pdf2ppt/stargazers)

将 PDF 幻灯片转换为 PowerPoint 演示文稿，使用**矢量图形**保持最高分辨率。

![notebookLM2PPT Web UI](docs/screenshot_web_ui.png?v=1.4.0)

## ✨ 功能特性

- 🎯 **矢量图形** - 生成的 PPT 保持最高分辨率
- 📝 **元数据转换** - 保留标题、作者等元数据
- 📐 **自动检测** - 自动检测幻灯片尺寸和宽高比
- 🚀 **简单易用** - 简洁的命令行界面，美观的输出
- 📄 **页面选择** - 使用 `--pages` 选项转换指定页面
- ⚡ **并行处理** - 使用 `--parallel` 选项加速转换
- 🔍 **依赖检查** - 自动检查所需工具是否已安装

## 🎯 使用场景

- **LaTeX** 用户可以轻松将 [`beamer`](https://ctan.org/pkg/beamer) 幻灯片从 PDF 转换为 PPT
- **Typst** 用户可以轻松将 [`touying`](https://typst.app/universe/package/touying/) 幻灯片从 PDF 转换为 PPT

## 🚀 快速开始

### 方式一：命令行工具 (pipx)

```bash
# 使用 pipx 安装（推荐）
pipx install pdfslides2ppt

# 转换 PDF 到 PPT
pdf2ppt input.pdf output.pptx
```

### 方式二：Web 界面 (Docker)

**x86_64 / AMD64 架构（Linux 服务器、Intel Mac）：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:1.2.0-amd64
```

**ARM64 架构（Apple Silicon Mac、ARM 服务器）：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:1.2.0-arm64
```

**自动检测架构：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:latest
```

**访问地址：** http://localhost:8100

### 方式三：API 服务器

```bash
# 安装服务器依赖
pip install "pdfslides2ppt[server]"

# 启动服务器
python -m uvicorn web.app:app --host 0.0.0.0 --port 8100
```

**API 文档：** http://localhost:8100/docs

## 📦 安装

### 前置条件

- **Python >= 3.9**
- [**pdf2svg**](https://github.com/dawbarton/pdf2svg) - 用于 PDF 转 SVG
- [**Inkscape**](https://inkscape.org/) - 用于 SVG 转 EMF

### 安装依赖

**macOS:**
```bash
brew install pdf2svg inkscape
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pdf2svg inkscape
```

**Windows:**
- 下载并安装 [pdf2svg](https://github.com/dawbarton/pdf2svg) 和 [Inkscape](https://inkscape.org/)
- 将它们添加到系统 PATH

### 安装 pdf2ppt

```bash
# 推荐：使用 pipx 安装（隔离环境）
pipx install pdfslides2ppt

# 或使用 pip 安装
pip install pdfslides2ppt
```

## 📖 使用方法

### 基本用法

```bash
# 指定输出文件
pdf2ppt input.pdf output.pptx

# 自动生成输出文件名（input.pptx）
pdf2ppt input.pdf

# 详细模式
pdf2ppt input.pdf --verbose
```

### 高级用法

```bash
# 转换指定页面
pdf2ppt input.pdf -p 1-5,7,9-11

# 并行处理（4个工作线程）
pdf2ppt input.pdf -j 4

# 强制覆盖已存在的文件
pdf2ppt input.pdf output.pptx --force

# 保留临时文件（用于调试）
pdf2ppt input.pdf --no-clean
```

### 命令行选项

```
用法: pdf2ppt [-h] [-v] [--verbose] [--no-clean] [--no-check] [--force]
              [--pages PAGES] [--parallel PARALLEL]
              [--pdf2svg-path PATH] [--inkscape-path PATH]
              input [output]

位置参数:
  input                 输入的 PDF 文件
  output                输出的 PPT 文件（默认：input.pptx）

选项:
  -h, --help            显示帮助信息
  -v, --version         显示版本号
  --verbose             详细模式
  --no-clean            保留临时文件
  --no-check            跳过 SVG 滤镜检查
  --force, -f           强制覆盖已存在的文件
  --pages, -p PAGES     页面范围（如 "1-5,7,9-11"）
  --parallel, -j N      并行工作线程数（默认：1）
  --pdf2svg-path PATH   pdf2svg 可执行文件路径
  --inkscape-path PATH  inkscape 可执行文件路径
```

## 🔧 技术实现

1. 使用 `pdf2svg` 将 PDF 转换为 SVG
2. 使用 `inkscape` 将 SVG 转换为 EMF（由于 python-pptx 的限制）
3. 使用 `python-pptx` 将 EMF 插入 PPT

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.9+ |
| PDF 处理 | pypdf |
| PPT 生成 | python-pptx |
| PDF 转 SVG | pdf2svg |
| SVG 转 EMF | Inkscape |
| CLI 输出 | rich |

## ⚠️ 已知问题

### 透明背景

由于依赖库的限制，带有透明度的元素可能无法完全支持。检测到此类问题时会收到警告。您可以手动复制生成的 SVG 来修复问题。

详见 [#1](https://github.com/neosun100/pdf2ppt/issues/1)。

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

版权所有 © 2023-2024 Teddy van Jerry ([Wuqiong Zhao](https://wqzhao.org))

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/pdf2ppt&type=Date)](https://star-history.com/#neosun100/pdf2ppt)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
