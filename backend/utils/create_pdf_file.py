import io
import os
from typing import Dict, List

from django.http import FileResponse
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

FONTS_ROOT = os.path.dirname(os.path.abspath(__file__))


def add_title(doc: List, title: str, size: int, space: int, ta: int):
    doc.append(Spacer(1, 20))
    doc.append(
        Paragraph(
            title,
            ParagraphStyle(
                name='name',
                fontName='timesnewromanpsmt',
                fontSize=size,
                alignment=ta,
            ),
        )
    )
    doc.append(Spacer(1, space))
    return doc


def add_paragraphs(doc: List, text: str, size: int):
    for line in text:
        doc.append(
            Paragraph(
                line,
                ParagraphStyle(
                    name='line',
                    fontName='timesnewromanpsmt',
                    fontSize=size,
                    alignment=TA_LEFT,
                ),
            )
        )
        doc.append(Spacer(1, 12))
    return doc


def create_pdf(obj: Dict[str, str]):
    buffer = io.BytesIO()

    font_fullpath = os.path.join(
        FONTS_ROOT, 'fonts/', 'timesnewromanpsmt.ttf'
    )
    pdfmetrics.registerFont(TTFont('timesnewromanpsmt', font_fullpath))

    doc = add_title([], obj['title'], 18, 12, TA_CENTER)
    doc = add_title(doc, obj['user'], 12, 12, TA_LEFT)
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12,
        leftMargin=12,
        topMargin=12,
        bottomMargin=12,
    )
    pdf.build(add_paragraphs(doc, obj['text'], 12))
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=obj['file_name'])
