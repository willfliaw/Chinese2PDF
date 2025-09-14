"""
Configuration for Hanzi → Pinyin → LaTeX conversion.
"""

import re
from pathlib import Path

from pypinyin import Style

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
# Base directory of this package (used for locating LaTeX templates)
BASE_DIR: Path = Path(__file__).resolve().parent

# ---------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------

# Main CJK font (can be a system font name or a path to a .ttf/.otf file)
CJK_MAIN_FONT: str = "田英章硬笔楷书简体.ttf"  # Custom font path

# Alternative examples
# CJK_MAIN_FONT = "KaiTi"     # 楷体
# CJK_MAIN_FONT = "SimHei"    # 黑体
# CJK_MAIN_FONT = "SimSun"    # 宋体
# CJK_MAIN_FONT = "Fangsong"  # 仿宋


# ---------------------------------------------------------------------
# Pinyin & Tones
# ---------------------------------------------------------------------
# Tone colors for LaTeX rendering
TONE_COLORS: dict[str, str] = {
    "1": "red",
    "2": "green!50!black",
    "3": "blue",
    "4": "orange",
    "5": "gray",  # neutral tone
}

# Pinyin style (TONE = diacritics, TONE3 = numeric)
TONE_STYLE: Style = Style.TONE
# TONE_STYLE: Style = Style.TONE3

# Map diacritic characters to tone numbers
DIACRITIC_TO_TONE: dict[str, str] = {
    **dict.fromkeys("āēīōūǖ", "1"),
    **dict.fromkeys("áéíóúǘ", "2"),
    **dict.fromkeys("ǎěǐǒǔǚ", "3"),
    **dict.fromkeys("àèìòùǜ", "4"),
}


# ---------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------
# Regex for opening punctuation (binds forward)
PUNCT_OPEN_PATTERN = re.compile(r"^[“‘（《〈【『「〖〔［｛]+$")

# Regex for closing punctuation (binds backward)
PUNCT_CLOSE_PATTERN = re.compile(r"^[，。？！：；、”’）》〉】』」〗〕］｝…—]+$")

# ---------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------
# Regex for Hanzi characters
HANZI_RUN = re.compile(r"[\u3400-\u9FFF]+")

# ---------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------
# Colors for HSK levels (1-6)
HSK_LEVEL_COLORS = {
    1: "green!20",
    2: "cyan!20",
    3: "blue!20",
    4: "orange!20",
    5: "red!20",
    6: "purple!20",
}
