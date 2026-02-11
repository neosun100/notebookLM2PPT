[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# pdf2ppt

[![PyPI version](https://badge.fury.io/py/pdfslides2ppt.svg)](https://badge.fury.io/py/pdfslides2ppt)
[![Python](https://img.shields.io/pypi/pyversions/pdfslides2ppt.svg)](https://pypi.org/project/pdfslides2ppt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/neosun100/pdf2ppt.svg)](https://github.com/neosun100/pdf2ppt/stargazers)

PDFスライドを**ベクターグラフィックス**（最高解像度）でPowerPointプレゼンテーションに変換します。

![notebookLM2PPT Web UI](docs/screenshot_web_ui.png?v=1.4.0)

## ✨ 機能

- 🎯 **ベクターグラフィックス** - 生成されたPPTで最高解像度を維持
- 📝 **メタデータ変換** - タイトル、作成者などのメタデータを保持
- 📐 **自動検出** - スライドサイズとアスペクト比を自動検出
- 🚀 **簡単操作** - シンプルなコマンドラインインターフェース、美しい出力
- 📄 **ページ選択** - `--pages` オプションで特定のページを変換
- ⚡ **並列処理** - `--parallel` オプションで変換を高速化
- 🔍 **依存関係チェック** - 必要なツールが自動的にチェックされます

## 🎯 ユースケース

- **LaTeX** ユーザーは [`beamer`](https://ctan.org/pkg/beamer) スライドをPDFからPPTに簡単に変換できます
- **Typst** ユーザーは [`touying`](https://typst.app/universe/package/touying/) スライドをPDFからPPTに簡単に変換できます

## 🚀 クイックスタート

### 方法1：コマンドラインツール (pipx)

```bash
# pipxでインストール（推奨）
pipx install pdfslides2ppt

# PDFをPPTに変換
pdf2ppt input.pdf output.pptx
```

### 方法2：Web UI (Docker)

**x86_64 / AMD64 アーキテクチャ（Linuxサーバー、Intel Mac）：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:1.2.0-amd64
```

**ARM64 アーキテクチャ（Apple Silicon Mac、ARMサーバー）：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:1.2.0-arm64
```

**アーキテクチャ自動検出：**
```bash
docker run -d -p 8100:8100 neosun/pdf2ppt:latest
```

**アクセス：** http://localhost:8100

### 方法3：APIサーバー

```bash
# サーバー依存関係をインストール
pip install "pdfslides2ppt[server]"

# サーバー起動
python -m uvicorn web.app:app --host 0.0.0.0 --port 8100
```

**APIドキュメント：** http://localhost:8100/docs

## 📦 インストール

### 前提条件

- **Python >= 3.9**
- [**pdf2svg**](https://github.com/dawbarton/pdf2svg) - PDFからSVGへの変換用
- [**Inkscape**](https://inkscape.org/) - SVGからEMFへの変換用

### 依存関係のインストール

**macOS:**
```bash
brew install pdf2svg inkscape
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pdf2svg inkscape
```

**Windows:**
- [pdf2svg](https://github.com/dawbarton/pdf2svg) と [Inkscape](https://inkscape.org/) をダウンロードしてインストール
- システムPATHに追加

### pdf2pptのインストール

```bash
# 推奨：pipxでインストール（隔離環境）
pipx install pdfslides2ppt

# またはpipでインストール
pip install pdfslides2ppt
```

## 📖 使用方法

### 基本的な使い方

```bash
# 出力ファイルを指定
pdf2ppt input.pdf output.pptx

# 出力ファイル名を自動生成（input.pptx）
pdf2ppt input.pdf

# 詳細モード
pdf2ppt input.pdf --verbose
```

### 高度な使い方

```bash
# 特定のページを変換
pdf2ppt input.pdf -p 1-5,7,9-11

# 並列処理（4ワーカー）
pdf2ppt input.pdf -j 4

# 既存ファイルを強制上書き
pdf2ppt input.pdf output.pptx --force

# 一時ファイルを保持（デバッグ用）
pdf2ppt input.pdf --no-clean
```

### コマンドラインオプション

```
使用法: pdf2ppt [-h] [-v] [--verbose] [--no-clean] [--no-check] [--force]
                [--pages PAGES] [--parallel PARALLEL]
                [--pdf2svg-path PATH] [--inkscape-path PATH]
                input [output]

位置引数:
  input                 入力PDFファイル
  output                出力PPTファイル（デフォルト：input.pptx）

オプション:
  -h, --help            ヘルプを表示
  -v, --version         バージョンを表示
  --verbose             詳細モード
  --no-clean            一時ファイルを保持
  --no-check            SVGフィルターチェックをスキップ
  --force, -f           既存ファイルを強制上書き
  --pages, -p PAGES     ページ範囲（例："1-5,7,9-11"）
  --parallel, -j N      並列ワーカー数（デフォルト：1）
  --pdf2svg-path PATH   pdf2svg実行ファイルのパス
  --inkscape-path PATH  inkscape実行ファイルのパス
```

## 🔧 技術的実装

1. `pdf2svg` を使用してPDFをSVGに変換
2. `inkscape` を使用してSVGをEMFに変換（python-pptxの制限のため）
3. `python-pptx` を使用してEMFをPPTに挿入

## 🛠️ 技術スタック

| コンポーネント | 技術 |
|---------------|------|
| 言語 | Python 3.9+ |
| PDF処理 | pypdf |
| PPT生成 | python-pptx |
| PDF→SVG | pdf2svg |
| SVG→EMF | Inkscape |
| CLI出力 | rich |

## ⚠️ 既知の問題

### 透明背景

依存ライブラリの制限により、透明度を持つ要素は完全にサポートされていません。このような問題が検出されると警告が表示されます。生成されたSVGを手動でコピーして問題を修正できます。

詳細は [#1](https://github.com/neosun100/pdf2ppt/issues/1) を参照してください。

## 🤝 コントリビューション

コントリビューションを歓迎します！お気軽にPull Requestを提出してください。

1. リポジトリをFork
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Requestを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

Copyright © 2023-2024 Teddy van Jerry ([Wuqiong Zhao](https://wqzhao.org))

## ⭐ Star履歴

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/pdf2ppt&type=Date)](https://star-history.com/#neosun100/pdf2ppt)

## 📱 フォローする

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
