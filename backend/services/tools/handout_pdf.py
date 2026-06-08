from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


HANDOUT_DIR = Path("generated_handouts")
HANDOUT_DIR.mkdir(exist_ok=True)


def safe_filename(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß_-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "handout"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def create_one_page_handout_pdf(
    title: str,
    handout_text: str,
    output_path: Path,
) -> Path:
    """
    Creates a simple one-page PDF handout.

    The function intentionally keeps the layout simple because this PDF is meant
    to be downloaded by the UI, not edited manually. Text that does not fit on
    the first page is shortened instead of spilling onto a second page.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = A4
    margin_x = 48
    margin_y = 48
    title_font_size = 18
    body_font_size = 10
    line_height = 13

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Handout - {title}")

    # Header
    y = page_height - margin_y
    pdf.setFont("Helvetica-Bold", title_font_size)
    pdf.drawString(margin_x, y, "Lern-Handout")

    y -= 24
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin_x, y, title[:95])

    y -= 16
    pdf.line(margin_x, y, page_width - margin_x, y)
    y -= 22

    # Body
    pdf.setFont("Helvetica", body_font_size)

    normalized = normalize_text(handout_text)
    max_chars_per_line = 95
    min_y = margin_y + 24
    shortened = False

    for paragraph in normalized.split("\n"):
        paragraph = paragraph.strip()

        if not paragraph:
            y -= line_height // 2
            continue

        # Preserve simple Markdown-like bullet points a little bit.
        bullet_prefix = ""
        wrapped_text = paragraph
        if paragraph.startswith(("- ", "* ")):
            bullet_prefix = "- "
            wrapped_text = paragraph[2:].strip()

        lines = textwrap.wrap(
            wrapped_text,
            width=max_chars_per_line,
            replace_whitespace=False,
            drop_whitespace=True,
        ) or [""]

        for index, line in enumerate(lines):
            if y < min_y:
                shortened = True
                break

            if bullet_prefix and index == 0:
                pdf.drawString(margin_x, y, bullet_prefix + line)
            elif bullet_prefix:
                pdf.drawString(margin_x + 12, y, line)
            else:
                pdf.drawString(margin_x, y, line)

            y -= line_height

        if shortened:
            break

    if shortened and y >= min_y:
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.drawString(margin_x, y, "Hinweis: Das Handout wurde gekuerzt, damit es auf eine Seite passt.")

    # Footer
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_width - margin_x, margin_y - 12, "AI Learning Coach")

    pdf.showPage()
    pdf.save()
    return output_path


def build_handout_filename(session_id: str, article_title: str) -> Path:
    filename = f"{safe_filename(article_title)}_{session_id[:8]}_handout.pdf"
    return HANDOUT_DIR / filename
