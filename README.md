# Chinese2PDF

Generate beautifully formatted PDFs from Chinese text with **Hanzi**, **Pinyin (tone-marked & colorized)**, **ruby annotations**, and **HSK-aware tooltips & tables** using LaTeX. Perfect for learners, teachers, and anyone studying Chinese.

## Features

-   Convert plain Chinese text into structured PDFs
-   Views: **Hanzi only**, **Pinyin only**, and **Hanzi + Pinyin (ruby)**
-   **HSK annotations**:
    -   Color highlights by HSK level
    -   Hover **tooltips** per token (HSK level, Pinyin, POS, English)
    -   **Vocabulary tables** grouped by HSK level, with audio links
-   Tone colors and diacritics for easier pronunciation
-   Automatic word segmentation (via `jieba`)
-   Built with LaTeX for professional-quality output
-   Fully configurable fonts, colors, tone styles, and HSK colors
-   Correct line wrapping without inserting visible spaces

## Requirements

-   **Python 3.8+**
-   **LaTeX distribution** (e.g. [TeX Live](https://www.tug.org/texlive/))
-   LaTeX packages used by generated documents:
    -   `xcolor`, `pdfcomment` (for `\pdftooltip`)
    -   `ruby` (for Hanzi + Pinyin section)
    -   `longtable` (for multipage vocabulary tables)
    -   `fontawesome5` (for audio/play icons)

> Ensure these packages are available in your TeX installation. The project’s template/preamble can include them automatically; if you use your own preamble, add them as needed.

## Installation

You can install dependencies with either `conda` or `pip`.

### Using conda

```bash
conda create -n chinese2pdf python jieba pypinyin -c conda-forge
conda activate chinese2pdf
```

### Using pip

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install jieba pypinyin
```

_(Install a LaTeX distribution such as TeX Live to compile PDFs.)_

## Usage

Basic usage:

```bash
python chinese2pdf/main.py <input.txt> -o <output.pdf> -t "My Chinese Story"
```

Advanced usage:

```bash
python chinese2pdf/main.py <input.txt> -o <output.pdf> -t "My Chinese Story" --hsk-csv ./scripts/hsk_words.csv --annotate-hsk 1 2 3 --no-cleanup
```

### Command-line options

-   `input` (positional) → Path to the input text file (UTF-8).
-   `-o / --output` → Output PDF filename (default: `output.pdf`).
-   `-t / --title` → PDF title (default: `ChineseToPDF`).
-   `--no-cleanup` → Keep intermediate LaTeX files (`.aux`, `.log`, `.tex`) for debugging.
-   `--hsk-csv` → Path to HSK CSV dataset to use for annotations
-   `--annotate-hsk` → Levels to annotate with HSK tooltips (default: `1 2 3 4 5 6`)

## HSK Annotations

When HSK data is provided, tokens are:

-   **Highlighted** by HSK level color (configurable via `HSK_LEVEL_COLORS`)
-   Wrapped with **`\pdftooltip{...}{...}`** containing:

    -   `level_display` (e.g., “HSK 3”)
    -   `pinyin` (tone-colored syllables)
    -   `pos` (part of speech)
    -   `english` (gloss/translation)

### Vocabulary Tables

The PDF includes an **HSK Vocabulary** section with one table per HSK level:

-   Columns: **Hanzi**, **Pinyin**, **POS**, **Audio**, **English**
-   **Audio links**: If a token includes a `tts_url`, the table renders a clickable audio icon using `\href{...}{\faVolumeUp}` (requires `fontawesome5`).

## Providing HSK Data

You have two options:

### Option A — Build the CSV with the script from this repository (recommended)

Run the builder:

```bash
python ./scripts/build_hsk_dataset.py --out ./scripts/hsk_words.csv
```

This produces a normalized CSV compatible with the project.

### Option B — Download the dataset from Hugging Face

Download **willfliaw/hsk-dataset** directly from Hugging Face and use it as your HSK source. Ensure the file you use (or export) matches the expected schema below.

Dataset page: [https://huggingface.co/datasets/willfliaw/hsk-dataset](https://huggingface.co/datasets/willfliaw/hsk-dataset)

### Expected CSV Columns

-   `hanzi` — Token string (single character or multi-character word)
-   `pinyin_tone` — Tone-marked pinyin (used when `TONE_STYLE = Style.TONE`)
-   `pinyin_num` — Numeric pinyin (used when `TONE_STYLE = Style.TONE3`)
-   `english` — Gloss
-   `pos` — Part of speech tag
-   `level` — HSK level (1–6+)
-   `tts_url` — (optional) URL to an audio pronunciation

> If no HSK data is provided, the document still builds without annotations.

## Examples

Generate a PDF:

```bash
python chinese2pdf/main.py examples/story.txt -o examples/story.pdf
```

The repository includes [`examples/story.txt`](examples/story.txt) (input) and a pre-generated [`examples/story.pdf`](examples/story.pdf).

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

### HSK level colors

```python
HSK_LEVEL_COLORS = {
    1: "green!20",
    2: "cyan!20",
    3: "blue!20",
    4: "orange!20",
    5: "red!20",
    6: "purple!20",
}
```

### Pinyin style

```python
from pypinyin import Style
TONE_STYLE = Style.TONE     # diacritics (mǎ)
# TONE_STYLE = Style.TONE3  # numbers (ma3)
```

### Punctuation handling

Custom regex patterns decide how punctuation binds to words:

```python
PUNCT_OPEN_PATTERN   # opening punctuation (binds forward)
PUNCT_CLOSE_PATTERN  # closing punctuation (binds backward)
```

## Motivation & Future Directions

This project was created to support **Mandarin Chinese** learners, such as myself, with readable, annotated texts. The approach could be extended to:

-   **Japanese** (furigana)
-   **Korean** (romanization/spacing aids)
-   Other languages with ruby/phonetic systems

Contributions and ideas are welcome, specially if you have expertise in these areas!

## License

MIT License. See [LICENSE](LICENSE) for details.
