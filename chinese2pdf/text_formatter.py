"""
Text formatting utilities for converting Chinese text into LaTeX-friendly
Hanzi, Pinyin, and ruby-annotated representations.
"""

from typing import Iterable, List

import jieba
from config import (
    DIACRITIC_TO_TONE,
    PUNCT_CLOSE_PATTERN,
    PUNCT_OPEN_PATTERN,
    TONE_COLORS,
    TONE_STYLE,
)
from pypinyin import pinyin


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
# Rendering Functions
# ---------------------------------------------------------------------
def hanzi_only(paragraphs: Iterable[str]) -> str:
    """
    Render paragraphs as Hanzi-only LaTeX strings.

    - Preserves word segmentation with `jieba`.
    - Opening punctuation binds forward, closing punctuation backward.
    """
    out: List[str] = []
    for para in paragraphs:
        tokens = list(jieba.cut(para, cut_all=False))
        pieces, pending_open = [], ""

        for tok in tokens:
            if is_hanzi_word(tok):
                word = f"\\mbox{{{tok}}}"
                if pending_open:
                    word = pending_open + word
                    pending_open = ""
                pieces.append(word)

            elif PUNCT_OPEN_PATTERN.match(tok):
                pending_open += tok

            elif PUNCT_CLOSE_PATTERN.match(tok):
                if pieces:
                    pieces[-1] += tok
                else:  # edge case: paragraph starts with closer
                    pieces.append(tok)

            else:  # Latin/number/etc.
                word = pending_open + tok if pending_open else tok
                pending_open = ""
                pieces.append(word)

        if pending_open:
            pieces.append(pending_open)

        out.append(" ".join(pieces))
    return "\n\n".join(out)


def hanzi_with_ruby(paragraphs: Iterable[str]) -> str:
    """
    Render paragraphs with ruby annotations (Hanzi + Pinyin).

    - Pinyin syllables are colorized by tone.
    - Opening punctuation binds forward, closing backward.
    """
    out: List[str] = []
    for para in paragraphs:
        tokens = list(jieba.cut(para, cut_all=False))
        pieces, pending_open = [], ""

        for tok in tokens:
            if is_hanzi_word(tok):
                pys = pinyin(tok, style=TONE_STYLE, strict=False, errors="ignore")
                syls = "".join(colorize_pinyin(s[0]) for s in pys)
                word = f"\\ruby{{{tok}}}{{{syls}}}"
                if pending_open:
                    word = pending_open + word
                    pending_open = ""
                pieces.append(word)

            elif PUNCT_OPEN_PATTERN.match(tok):
                pending_open += tok

            elif PUNCT_CLOSE_PATTERN.match(tok):
                if pieces:
                    pieces[-1] += tok
                else:
                    pieces.append(tok)

            else:
                word = pending_open + tok if pending_open else tok
                pending_open = ""
                pieces.append(word)

        if pending_open:
            pieces.append(pending_open)

        out.append(" ".join(pieces))
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
        tokens = list(jieba.cut(para, cut_all=False))
        n_tokens = len(tokens)
        pieces, pending_open = [], ""

        for i, tok in enumerate(tokens):
            if is_hanzi_word(tok):
                pys = pinyin(tok, style=TONE_STYLE, strict=False, errors="ignore")
                word = "".join(colorize_pinyin(s[0]) for s in pys)
                if pending_open:
                    word = pending_open + word
                    pending_open = ""
                pieces.append(word)
                if not (next_is_punct(i, tokens, n_tokens) or i == n_tokens - 1):
                    pieces.append("\\pywordsep")

            elif PUNCT_OPEN_PATTERN.match(tok):
                # opening punct attaches to next token
                pending_open += f"\\pypunct{{{tok}}}"

            elif PUNCT_CLOSE_PATTERN.match(tok):
                # closing punct attaches to previous token
                if pieces:
                    pieces[-1] += f"\\pypunct{{{tok}}}"
                else:
                    pieces.append(f"\\pypunct{{{tok}}}")
                # no \pywordsep if the next token is punctuation
                if i != n_tokens - 1 and not next_is_punct(i, tokens, n_tokens):
                    pieces.append("\\pywordsep")

            else:  # Latin/number/etc.
                word = pending_open + tok if pending_open else tok
                pending_open = ""
                pieces.append(word)
                if not (next_is_punct(i, tokens, n_tokens) or i == n_tokens - 1):
                    pieces.append("\\pywordsep")

        if pending_open:
            pieces.append(pending_open)

        out.append("".join(pieces))
    return "\n\n".join(out)
