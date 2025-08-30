"""
Takes Chinese text, converts it into Hanzi, Pinyin, and ruby-annotated
representations, and compiles them into a formatted PDF using XeLaTeX.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from config import BASE_DIR, CJK_MAIN_FONT
from text_formatter import hanzi_only, hanzi_with_ruby, parse_paragraphs, pinyin_only


def generate_pdf(
    text: str,
    title: str = "Chinese Text",
    filename: str | Path = "output.pdf",
    cleanup: bool = True,
) -> None:
    """
    Generate a PDF from Chinese text using LaTeX (via XeLaTeX).

    Produces a professionally typeset document containing:
      - Hanzi-only view
      - Pinyin-only view
      - Hanzi with ruby Pinyin annotations

    Parameters
    ----------
    text : str
        Input Chinese text (UTF-8).
    title : str, optional
        Title for the PDF (default: "Chinese Text").
    filename : str | Path, optional
        Output PDF filename (default: "output.pdf").
    cleanup : bool, optional
        If True (default), intermediate .aux/.log/.tex files are deleted.
        If False, they are copied alongside the final PDF.
    """
    filename = Path(filename).resolve()
    out_dir = filename.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load LaTeX template and inject content
    template_path = BASE_DIR / "latex_template.tex"
    filled = (
        template_path.read_text(encoding="utf-8")
        .replace("<<FONT>>", CJK_MAIN_FONT)
        .replace("<<TITLE>>", title)
        .replace("<<HANZI>>", hanzi_only(parse_paragraphs(text)))
        .replace("<<PINYIN>>", pinyin_only(parse_paragraphs(text)))
        .replace("<<RUBY>>", hanzi_with_ruby(parse_paragraphs(text)))
    )

    jobname = filename.stem

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        tex_file = tmpdir / f"{jobname}.tex"
        tex_file.write_text(filled, encoding="utf-8")

        # Run XeLaTeX
        subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                f"-jobname={jobname}",
                f"-output-directory={tmpdir}",
                str(tex_file),
            ],
            check=True,
        )

        # Move the final PDF into the requested location
        produced_pdf = tmpdir / f"{jobname}.pdf"
        shutil.move(produced_pdf, filename)

        if not cleanup:
            # Preserve aux/log/tex files alongside the PDF
            for ext in (".aux", ".log", ".tex"):
                produced_file = tmpdir / f"{jobname}{ext}"
                if produced_file.exists():
                    shutil.copy(produced_file, out_dir / produced_file.name)
