# Chinese2PDF

Generate beautifully formatted PDFs from Chinese text with **Hanzi**, **Pinyin (tone-marked & colorized)**, and **ruby annotations** using LaTeX. Perfect for learners, teachers, and anyone studying Chinese.

---

## Features

* Convert plain Chinese text into structured PDFs
* Includes **Hanzi only**, **Pinyin only**, and **Hanzi + Pinyin (ruby)** views
* Tone colors and diacritics for easier pronunciation
* Automatic word segmentation (via `jieba`)
* Built with LaTeX for professional-quality output
* Fully configurable fonts, colors, and tone styles

---

## Requirements

* **Python 3.8+**
* **LaTeX distribution** (e.g. [TeX Live](https://www.tug.org/texlive/), required for PDF generation)

---

## Installation

You can install dependencies with either `conda` (recommended if using Miniconda/Anaconda) or `pip`.

### Using conda

```bash
conda create -n chinese2pdf python jieba pypinyin -c conda-forge
conda activate chinese2pdf
```

### Using pip

```bash
python -m venv venv
source venv/bin/activate  # on Linux/macOS
venv\Scripts\activate     # on Windows

pip install jieba pypinyin
```

*(Make sure you also install a LaTeX distribution such as TeX Live to compile PDFs.)*

---

## Usage

Basic usage:

```bash
python chinese2pdf/main.py <input.txt> -o <output.pdf> -t "My Chinese Story"
```

### Command-line options

* `input` (positional) → Path to the input text file (UTF-8).
* `-o / --output` → Output PDF filename (default: `output.pdf`).
* `-t / --title` → PDF title (default: `ChineseToPDF`).
* `--no-cleanup` → Keep intermediate LaTeX files (`.aux`, `.log`, `.tex`) for debugging.

---

## Examples

Generate a PDF:

```bash
python chinese2pdf/main.py examples/story.txt -o examples/story.pdf
```

The repository includes [`examples/story.txt`](examples/story.txt) (input) and a pre-generated [`examples/story.pdf`](examples/story.pdf) (output) so you can compare results immediately.

---

## Configuration

All configuration lives in [`config.py`](chinese2pdf/config.py). You can customize:

### Fonts

```python
CJK_MAIN_FONT = "田英章硬笔楷书简体.ttf"  # default
```

By default, the project uses **田英章硬笔楷书简体**, a beautiful handwritten-style font by the famous calligrapher **田英章**. The font was installed from [zitijia.com](https://www.zitijia.com/i/261836868063087673.html). You can replace this with any system-installed font or your own `.ttf`/`.otf` file, for example:

```python
CJK_MAIN_FONT = "KaiTi"     # 楷体
CJK_MAIN_FONT = "SimHei"    # 黑体
CJK_MAIN_FONT = "SimSun"    # 宋体
CJK_MAIN_FONT = "Fangsong"  # 仿宋
```

### Tone colors

```python
TONE_COLORS = {
    "1": "red",
    "2": "green!50!black",
    "3": "blue",
    "4": "orange",
    "5": "gray",  # neutral tone
}
```

### Pinyin style

```python
from pypinyin import Style
TONE_STYLE = Style.TONE   # Use diacritics (mǎ)
# TONE_STYLE = Style.TONE3  # Use numbers (ma3)
```

### Punctuation handling

Custom regex patterns decide how punctuation binds to words:

```python
PUNCT_OPEN_PATTERN  # opening punctuation (binds forward)
PUNCT_CLOSE_PATTERN # closing punctuation (binds backward)
```

---

## Motivation & Future Directions

This project was created because I am a **Mandarin Chinese learner**, and I wanted a tool that makes it easier to read and study texts with side-by-side Pinyin support.

While the current version is focused on **Chinese (Mandarin)**, the same approach could be extended to:

* **Japanese** → Furigana annotations above Kanji
* **Korean** → Hangul with romanization or spacing aids
* Other languages with **ruby annotation or phonetic systems**

Contributions and ideas are welcome if you have expertise in these areas!

---

## License

MIT License. See [LICENSE](LICENSE) for details.
