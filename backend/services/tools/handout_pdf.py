from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Iterable

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
HANDOUT_DIR = BACKEND_ROOT / "generated_handouts"
HANDOUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß_-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "handout"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def register_unicode_fonts() -> tuple[str, str]:
    """
    Register Unicode-capable fonts for ReportLab.

    Helvetica is not enough for German umlauts, arrows, math symbols, etc.
    DejaVuSans is commonly available on Linux systems.
    """
    font_candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/local/share/fonts/DejaVuSans.ttf",
            "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
        ),
        (
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),
    ]

    for regular_path, bold_path in font_candidates:
        regular = Path(regular_path)
        bold = Path(bold_path)

        if regular.exists():
            pdfmetrics.registerFont(TTFont("HandoutRegular", str(regular)))

            if bold.exists():
                pdfmetrics.registerFont(TTFont("HandoutBold", str(bold)))
                return "HandoutRegular", "HandoutBold"

            return "HandoutRegular", "HandoutRegular"

    # Fallback. This works, but Unicode support is worse.
    return "Helvetica", "Helvetica-Bold"


REGULAR_FONT, BOLD_FONT = register_unicode_fonts()


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "HandoutTitle",
            parent=base["Title"],
            fontName=BOLD_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "HandoutSubtitle",
            parent=base["Normal"],
            fontName=REGULAR_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "HandoutH1",
            parent=base["Heading1"],
            fontName=BOLD_FONT,
            fontSize=14,
            leading=18,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "HandoutH2",
            parent=base["Heading2"],
            fontName=BOLD_FONT,
            fontSize=12,
            leading=15,
            spaceBefore=7,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "HandoutH3",
            parent=base["Heading3"],
            fontName=BOLD_FONT,
            fontSize=10.5,
            leading=13,
            spaceBefore=5,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "HandoutBody",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "HandoutBullet",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=9,
            leading=12,
            leftIndent=12,
            firstLineIndent=0,
            spaceAfter=2,
        ),
        "code": ParagraphStyle(
            "HandoutCode",
            parent=base["Code"],
            fontName=REGULAR_FONT,
            fontSize=7.5,
            leading=9,
            leftIndent=8,
            rightIndent=8,
            backColor=colors.HexColor("#F3F4F6"),
            borderColor=colors.HexColor("#E5E7EB"),
            borderWidth=0.5,
            borderPadding=4,
            spaceBefore=4,
            spaceAfter=5,
        ),
    }

    return styles


STYLES = build_styles()


def markdown_inline_to_reportlab(node) -> str:
    """
    Convert inline HTML/Markdown nodes into ReportLab Paragraph markup.

    ReportLab Paragraph does not understand Markdown directly.
    It understands a small XML-like subset such as <b>, <i>, <br/>.
    """
    if isinstance(node, NavigableString):
        return html.escape(str(node))

    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()

    inner = "".join(markdown_inline_to_reportlab(child) for child in node.children)

    if name in {"strong", "b"}:
        return f"<b>{inner}</b>"

    if name in {"em", "i"}:
        return f"<i>{inner}</i>"

    if name == "code":
        return f"<font name='{REGULAR_FONT}' backColor='#F3F4F6'>{inner}</font>"

    if name == "br":
        return "<br/>"

    if name == "a":
        href = html.escape(node.get("href", ""))
        if href:
            return f'<a href="{href}" color="blue">{inner}</a>'
        return inner

    return inner


def tag_text_as_reportlab_markup(tag: Tag) -> str:
    return "".join(markdown_inline_to_reportlab(child) for child in tag.children).strip()


def html_to_flowables(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    flowables = []

    def add_paragraph(tag: Tag, style_name: str = "body"):
        content = tag_text_as_reportlab_markup(tag)
        if content:
            flowables.append(Paragraph(content, STYLES[style_name]))

    for element in soup.children:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                flowables.append(Paragraph(html.escape(text), STYLES["body"]))
            continue

        if not isinstance(element, Tag):
            continue

        name = element.name.lower()

        if name == "h1":
            add_paragraph(element, "h1")

        elif name == "h2":
            add_paragraph(element, "h2")

        elif name == "h3":
            add_paragraph(element, "h3")

        elif name in {"h4", "h5", "h6"}:
            add_paragraph(element, "h3")

        elif name == "p":
            add_paragraph(element, "body")

        elif name in {"ul", "ol"}:
            items = []

            for li in element.find_all("li", recursive=False):
                li_content = tag_text_as_reportlab_markup(li)
                if li_content:
                    bullet = Paragraph(li_content, STYLES["bullet"])
                    items.append(ListItem(bullet, leftIndent=8))

            if items:
                flowables.append(
                    ListFlowable(
                        items,
                        bulletType="bullet" if name == "ul" else "1",
                        leftIndent=14,
                    )
                )
                flowables.append(Spacer(1, 3))

        elif name == "pre":
            code_text = element.get_text()
            flowables.append(Preformatted(code_text, STYLES["code"]))

        elif name == "blockquote":
            content = tag_text_as_reportlab_markup(element)
            if content:
                quote_style = ParagraphStyle(
                    "HandoutQuote",
                    parent=STYLES["body"],
                    leftIndent=12,
                    textColor=colors.HexColor("#555555"),
                    borderColor=colors.HexColor("#D1D5DB"),
                    borderWidth=0,
                    spaceBefore=4,
                    spaceAfter=4,
                )
                flowables.append(Paragraph(content, quote_style))

        elif name == "hr":
            flowables.append(Spacer(1, 6))

        else:
            text = tag_text_as_reportlab_markup(element)
            if text:
                flowables.append(Paragraph(text, STYLES["body"]))

    return flowables


def markdown_to_flowables(markdown_text: str):
    html_text = markdown.markdown(
        markdown_text,
        extensions=[
            "extra",
            "sane_lists",
            "nl2br",
        ],
        output_format="html5",
    )

    return html_to_flowables(html_text)


def create_one_page_handout_pdf(
    title: str,
    handout_text: str,
    output_path: Path,
) -> Path:
    """
    Creates a Markdown-aware PDF handout.

    Important:
    - Uses a Unicode-capable TTF font if available.
    - Supports Markdown headings, bold, italic, bullet lists, numbered lists,
      inline code, code blocks and links.
    - Does not use canvas.drawString for body text anymore.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"Handout - {title}",
        author="MyWikiGPT",
    )

    story = [
        Paragraph("Lern-Handout", STYLES["title"]),
        Paragraph(html.escape(title), STYLES["subtitle"]),
    ]

    normalized = normalize_text(handout_text)
    story.extend(markdown_to_flowables(normalized))

    doc.build(story)

    return output_path


def build_handout_filename(session_id: str, article_title: str) -> Path:
    filename = f"{safe_filename(article_title)}_{session_id[:8]}_handout.pdf"
    return HANDOUT_DIR / filename