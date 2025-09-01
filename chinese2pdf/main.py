"""
Command-line interface for Chinese → PDF generator.
"""

import argparse
from pathlib import Path

import pandas as pd
from pdf_generator import generate_pdf


def parse_args() -> argparse.Namespace:
    """
    Define and parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing:
        - input : Path to the input text file (UTF-8).
        - output : Path to the output PDF file.
        - title : Title string for the PDF.
        - cleanup : Whether to remove intermediate LaTeX files.
    """
    parser = argparse.ArgumentParser(
        prog="chinese2pdf",
        description="Generate a Chinese PDF with Hanzi, Pinyin, and ruby annotations via LaTeX.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input text file (UTF-8).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output.pdf"),
        help="Output PDF filename (default: output.pdf).",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="ChineseToPDF",
        help="PDF title (default: ChineseToPDF).",
    )
    parser.add_argument(
        "--cleanup",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove intermediate LaTeX files (default: True). Use --no-cleanup to keep them.",
    )
    parser.add_argument(
        "--hsk-csv", type=Path, help="Path to HSK CSV dataset to use for annotations."
    )
    parser.add_argument(
        "--annotate-hsk",
        nargs="*",
        type=int,
        help=(
            "Levels to annotate with HSK tooltips.\n"
            "Usage:\n"
            "  --annotate-hsk        (all levels)\n"
            "  --annotate-hsk 1 2 3  (only specific levels)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """
    Entry point for the command-line tool.

    - Reads the input Chinese text file.
    - Generates a PDF with Hanzi, Pinyin, and ruby annotations.
    - Saves the result to the specified output path.
    """
    args = parse_args()
    text = args.input.read_text(encoding="utf-8")

    hsk_df = pd.DataFrame()
    if args.hsk_csv:
        hsk_df = pd.read_csv(args.hsk_csv)
        if args.annotate_hsk:
            hsk_df = hsk_df[hsk_df["level"].isin(args.annotate_hsk)]

    generate_pdf(
        text=text,
        title=args.title,
        filename=args.output,
        cleanup=args.cleanup,
        hsk_df=hsk_df,
    )


if __name__ == "__main__":
    main()
