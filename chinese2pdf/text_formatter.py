"""
Text formatting utilities for converting Chinese text into LaTeX-friendly
Hanzi, Pinyin, and ruby-annotated representations.
"""

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Set

import jieba
import pandas as pd
from config import (
    DIACRITIC_TO_TONE,
    HANZI_RUN,
    HSK_LEVEL_COLORS,
    PUNCT_CLOSE_PATTERN,
    PUNCT_OPEN_PATTERN,
    TONE_COLORS,
    TONE_STYLE,
)
from pypinyin import Style, pinyin


# ---------------------------------------------------------------------
# Paragraph & Token Helpers
# ---------------------------------------------------------------------
def parse_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs, preserving line breaks.

    Consecutive non-empty lines are joined into a paragraph.
    Blank lines mark paragraph boundaries.
    """
    paragraphs, buffer = [], []
    for line in text.splitlines():
        clean = line.strip()
        if clean:
            buffer.append(clean)
        elif buffer:
            paragraphs.append(" ".join(buffer))
            buffer = []
    if buffer:
        paragraphs.append(" ".join(buffer))
    return paragraphs


def is_hanzi(ch: str) -> bool:
    """Return True if the character is a CJK Unified Ideograph (U+4E00–U+9FFF)."""
    return "\u4e00" <= ch <= "\u9fff"


def is_hanzi_word(token: str) -> bool:
    """Return True if the entire token consists of Hanzi."""
    return all(is_hanzi(c) for c in token)


def cut_mixed(s: str) -> List[str]:
    """Segment a mixed Chinese/Latin string into tokens.
    - Hanzi runs -> jieba.lcut (HMM=False)
    - Latin/digits/etc. -> grouped
    - Punctuation -> separate tokens
    """
    tokens: List[str] = []
    i = 0
    n = len(s)

    while i < n:
        # Case 1: Hanzi run
        m = HANZI_RUN.match(s, i)
        if m:
            han = m.group(0)
            tokens.extend(jieba.lcut(han, HMM=False))
            i = m.end()
            continue

        # Case 2: Non-Hanzi segment; split out open/close punctuation as single tokens
        j = i
        buf_start = j
        while j < n and not HANZI_RUN.match(s, j):
            ch = s[j]
            if PUNCT_OPEN_PATTERN.match(ch) or PUNCT_CLOSE_PATTERN.match(ch):
                # flush any buffered non-punct chars before this punctuation
                if j > buf_start:
                    tokens.append(s[buf_start:j])
                # add the punctuation itself as a separate token
                tokens.append(ch)
                j += 1
                buf_start = j
            else:
                j += 1

        # flush remaining non-punct chars in this non-Hanzi span
        if j > buf_start:
            tokens.append(s[buf_start:j])

        i = j

    return tokens


# ---------------------------------------------------------------------
# Tone Helpers
# ---------------------------------------------------------------------
def detect_tone(syl: str) -> str:
    """
    Return tone number (1 - 5) from a Pinyin syllable.

    - Handles numeric style (TONE3, e.g. "ma3").
    - Handles diacritic style (TONE, e.g. "mǎ").
    - Defaults to neutral tone (5).
    """
    if syl and syl[-1].isdigit():
        return syl[-1]
    for ch in syl:
        if ch in DIACRITIC_TO_TONE:
            return DIACRITIC_TO_TONE[ch]
    return "5"


def colorize_pinyin(syl: str) -> str:
    """Return LaTeX macro with syllable colored according to its tone."""
    tone = detect_tone(syl)
    color = TONE_COLORS.get(tone, "black")
    return f"\\pysyl{{{color}}}{{{syl}}}"


# ---------------------------------------------------------------------
# HSK Helpers
# ---------------------------------------------------------------------
def build_hsk_map(hsk_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Build an index from Hanzi → HSK metadata.
    """
    if hsk_df.empty:
        return {}

    pinyin_column = "pinyin_tone" if TONE_STYLE == Style.TONE else "pinyin_num"

    df = hsk_df.dropna(subset=["hanzi"]).copy()

    hsk_map: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        if not row["hanzi"]:
            continue

        # Pinyin
        pinyin_raw = row[pinyin_column]
        syllables = pinyin_raw.split()
        pinyin_display = "".join(syllables)
        pinyin_display_colorized = "".join(colorize_pinyin(s) for s in syllables)

        # Other fields
        english_display = row["english"].capitalize()
        pos_display = row["pos"]
        level_display = f"HSK {row['level']}" if row["level"] else ""
        audio_display = (
            f"\\href{{{row["tts_url"]}}}{{\\faVolumeUp}}" if row["tts_url"] else ""
        )

        # Toolttip
        tip: List[str] = ",\t ".join(
            str(x)
            for x in (level_display, pinyin_display, pos_display, english_display)
            if x
        )

        # Store
        # TODO: Better handle duplicates
        hsk_map[row["hanzi"]] = {
            "level": row["level"],
            "level_display": level_display,
            "pinyin": pinyin_display_colorized,
            "pos": pos_display,
            "english": english_display,
            "audio": audio_display,
            "tip": tip,
        }

    return hsk_map


def highlight(word: str, color: str) -> str:
    """Return Hanzi wrapped in a colorbox with strut for consistent height."""
    return (
        r"\begingroup"
        r"\setlength{\fboxsep}{0pt}"  # no padding
        rf"\colorbox{{{color}}}{{{word}}}"
        r"\endgroup"
    )


def tooltip(visible: str, tip: str) -> str:
    """Return LaTeX \\pdftooltip wrapper."""
    return f"\\pdftooltip{{{visible}}}{{{tip}}}"


# ---------------------------------------------------------------------
# Rendering Functions
# ---------------------------------------------------------------------
def render_hanzi(
    paragraphs: Iterable[str],
    hsk_df: pd.DataFrame = pd.DataFrame(),
    with_ruby: bool = False,
) -> str:
    """
    Render paragraphs as LaTeX with HSK tooltips and optional ruby Pinyin.

    - Whole-word annotation when available; otherwise per-character.
    - Opening punctuation binds forward; closing punctuation binds backward.
    - Inserts zero-width glue after each Hanzi chunk to allow wrapping without
      inserting visible characters.
    """
    hsk_map = build_hsk_map(hsk_df)

    def annotate_token(token: str) -> str:
        # Whole word if known; else character-by-character.
        if token in hsk_map:
            level = hsk_map[token]["level"]
            color = HSK_LEVEL_COLORS[level]
            visible = highlight(token, color)
            tip = hsk_map[token]["tip"]
            return tooltip(visible, tip)
        chars: List[str] = []
        for ch in token:
            if ch in hsk_map:
                level = hsk_map[ch]["level"]
                color = HSK_LEVEL_COLORS[level]
                vis = highlight(ch, color)
                tip = hsk_map[ch]["tip"]
                chars.append(tooltip(vis, tip))
            else:
                chars.append(ch)

        return "".join(chars)

    out: List[str] = []
    for para in paragraphs:
        pieces: List[str] = []

        for token in cut_mixed(para):
            if is_hanzi_word(token):
                word = annotate_token(token)

                if with_ruby:
                    # Compute tone-colored Pinyin only when needed.
                    pys = pinyin(token, style=TONE_STYLE, strict=False, errors="ignore")
                    syls = "".join(colorize_pinyin(s[0]) for s in pys)
                    word = f"\\ruby{{{word}}}{{{syls}}}"
                else:
                    # Avoids breaking word
                    word = f"\\ruby{{{word}}}{{}}"

                pieces.append(word)

            else:
                # Latin/number/punctuation/etc.
                if PUNCT_OPEN_PATTERN.match(token) or PUNCT_CLOSE_PATTERN.match(token):
                    pieces.append(token)
                else:
                    pieces.append(f"\\ruby{{{token}}}{{}}")

        out.append("".join(pieces))

    return "\n\n".join(out)


def pinyin_only(paragraphs: Iterable[str]) -> str:
    """
    Render paragraphs as colorized Pinyin LaTeX strings.

    - Hanzi → converted with pypinyin + `colorize_pinyin`.
    - Opening punctuation binds forward, closing punctuation backward.
    - Non-Hanzi (Latin, numbers, etc.) kept as-is.
    - Words separated by ``\\pywordsep``, except before punctuation or end of line.
    """

    def next_is_punct(i: int, tokens: List[str], n_tokens: int) -> bool:
        """Return True if the token after index `i` is any punctuation (open or close)."""
        return i + 1 < n_tokens and (
            PUNCT_CLOSE_PATTERN.match(tokens[i + 1])
            or PUNCT_OPEN_PATTERN.match(tokens[i + 1])
        )

    out: List[str] = []
    for para in paragraphs:
        tokens = cut_mixed(para)
        n_tokens = len(tokens)
        pieces: List[str] = []
        pending_open = ""

        for i, token in enumerate(tokens):
            if is_hanzi_word(token):
                pys = pinyin(token, style=TONE_STYLE, strict=False, errors="ignore")
                word = "".join(colorize_pinyin(s[0]) for s in pys)
                if pending_open:
                    word = pending_open + word
                    pending_open = ""
                pieces.append(word)
                if not (next_is_punct(i, tokens, n_tokens) or i == n_tokens - 1):
                    pieces.append("\\pywordsep{}")

            elif PUNCT_OPEN_PATTERN.match(token):
                # opening punct attaches to next token
                pending_open += token

            elif PUNCT_CLOSE_PATTERN.match(token):
                # closing punct attaches to previous token
                if pieces:
                    pieces[-1] += token
                else:
                    pieces.append(token)
                # no \pywordsep if the next token is punctuation
                if i != n_tokens - 1 and not next_is_punct(i, tokens, n_tokens):
                    pieces.append("\\pywordsep{}")

            else:  # Latin/number/etc.
                word = pending_open + token if pending_open else token
                pending_open = ""
                pieces.append(word)
                if not (next_is_punct(i, tokens, n_tokens) or i == n_tokens - 1):
                    pieces.append("\\pywordsep{}")

        if pending_open:
            pieces.append(pending_open)

        out.append("".join(pieces))
    return "\n\n".join(out)


def vocabulary(text: str, hsk_df: pd.DataFrame = pd.DataFrame()) -> str:
    """
    Build a LaTeX Vocabulary section from the given Chinese text,
    using HSK data to annotate known words.
    """
    if hsk_df.empty:
        return ""

    hsk_map = build_hsk_map(hsk_df)

    vocabulary_hanzi: Dict[str, Set[str]] = defaultdict(set)
    for token in cut_mixed(text):
        if not is_hanzi_word(token):
            continue
        if token in hsk_map:
            vocabulary_hanzi[str(hsk_map[token]["level"])].add(token)
        else:
            for ch in token:
                if ch in hsk_map:
                    vocabulary_hanzi[str(hsk_map[ch]["level"])].add(ch)

    if not vocabulary_hanzi:
        return ""

    parts = []
    english_col_width = "0.5\\linewidth"
    colspec = "cccc p{" + english_col_width + "}"

    for level in sorted(vocabulary_hanzi.keys()):
        # Pick a sample to get level_display
        level_display = None
        for sample in vocabulary_hanzi[level]:
            level_display = hsk_map[sample]["level_display"]
            break
        title = level_display if level_display else f"HSK {level}"

        parts.append(f"\\subsection*{{{title}}}")
        parts.append(f"\\begin{{longtable}}{{{colspec}}}")
        # --- header for first page
        parts.append("\\hline")
        parts.append(
            "\\textbf{Hanzi} & \\textbf{Pinyin} & \\textbf{POS}"
            " & \\textbf{Audio} & \\textbf{English}\\\\"
        )
        parts.append("\\hline")
        parts.append("\\endfirsthead")
        # --- header for continuation pages
        parts.append("\\hline")
        parts.append(
            "\\textbf{Hanzi} & \\textbf{Pinyin} & \\textbf{POS}"
            " & \\textbf{Audio} & \\textbf{English}\\\\"
        )
        parts.append("\\hline")
        parts.append("\\endhead")
        # --- footer on non-final pages
        parts.append("\\hline")
        parts.append("\\multicolumn{5}{r}{\\footnotesize Continued on next page}\\\\")
        parts.append("\\endfoot")
        # --- footer on last page
        parts.append("\\hline")
        parts.append("\\endlastfoot")

        for hanzi in sorted(vocabulary_hanzi[level]):
            entry = hsk_map[hanzi]
            parts.append(
                f"{hanzi} & {entry['pinyin']} & {entry['pos']}"
                f" & {entry["audio"]} & {entry['english']}\\\\"
            )

        parts.append("\\end{longtable}")
        parts.append("")  # blank line between subsections

    return "\n".join(parts)
