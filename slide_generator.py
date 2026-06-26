"""
slide_generator.py
Berilgan slayd ma'lumotlari (JSON/dict) asosida chiroyli, rangli .pptx fayl yaratadi.
Faqat 1 ta belgilangan dizayn shabloni ishlatiladi (foydalanuvchi tomonidan tanlanmaydi).
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------- Rang palitrasi ----------
NAVY = RGBColor(0x1E, 0x27, 0x61)      # asosiy qorongi rang (muqova/yopilish slaydlari)
ICE = RGBColor(0xCA, 0xDC, 0xFC)       # yengil ko'k - subtitle/matn
GOLD = RGBColor(0xF2, 0xA9, 0x3B)      # urg'u rangi (doiralar, raqamlar)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x2B, 0x2B, 0x2B)
MUTED = RGBColor(0x9A, 0x9A, 0x9A)

FONT = "Calibri"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

MAX_BULLETS_PER_SLIDE = 5


def _set_background(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_text(slide, left, top, width, height, text, size, color,
               bold=False, italic=False, align=PP_ALIGN.LEFT, anchor=None,
               font=FONT, line_spacing=1.08):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    if anchor is not None:
        tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    return box


def _add_circle(slide, left, top, diameter, color, line=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, diameter, diameter)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if not line:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _decorate_dark_slide(slide):
    """Qorongi fon slaydlari uchun burchaklardagi bezak doiralar (vizual motiv)."""
    _add_circle(slide, SLIDE_W - Inches(2.4), Inches(-1.0), Inches(3.2), GOLD)
    _add_circle(slide, Inches(-1.4), SLIDE_H - Inches(1.6), Inches(2.8), ICE)
    # fon ustidagi doiralarni biroz xira ko'rsatish imkoni yo'q (pptx cheklovi),
    # shu sababli ular kichik va burchaklarda joylashtirildi - matnga xalaqit bermaydi.


def add_cover_slide(prs: Presentation, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_background(slide, NAVY)
    _decorate_dark_slide(slide)
    _add_text(
        slide, Inches(1.2), Inches(2.9), SLIDE_W - Inches(2.4), Inches(1.6),
        title, 40, WHITE, bold=True, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    if subtitle:
        _add_text(
            slide, Inches(1.8), Inches(4.6), SLIDE_W - Inches(3.6), Inches(0.8),
            subtitle, 18, GOLD, italic=True, align=PP_ALIGN.CENTER,
        )
    return slide


def add_content_slide(prs: Presentation, title: str, bullets, slide_no: int, total: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_background(slide, WHITE)

    _add_text(
        slide, Inches(0.8), Inches(0.55), SLIDE_W - Inches(1.6), Inches(0.9),
        title, 30, NAVY, bold=True, align=PP_ALIGN.LEFT,
    )

    bullets = [b for b in (bullets or []) if b][:MAX_BULLETS_PER_SLIDE]
    n = max(len(bullets), 1)
    top_start = Inches(1.95)
    bottom_limit = SLIDE_H - Inches(0.9)
    available = bottom_limit - top_start
    row_h = min(Inches(1.05), available / n)
    block_h = row_h * n
    top = top_start + max(available - block_h, 0) / 2
    for bullet in bullets:
        circle_d = Inches(0.22)
        circle_top = top + (row_h - circle_d) / 2 - Inches(0.18)
        _add_circle(slide, Inches(0.85), circle_top, circle_d, GOLD)
        _add_text(
            slide, Inches(1.35), top, SLIDE_W - Inches(2.2), row_h,
            bullet, 16, DARK_TEXT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
        )
        top += row_h

    _add_text(
        slide, SLIDE_W - Inches(1.4), SLIDE_H - Inches(0.55), Inches(1.0), Inches(0.4),
        f"{slide_no}/{total}", 10, MUTED, align=PP_ALIGN.RIGHT,
    )
    return slide


def add_closing_slide(prs: Presentation, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_background(slide, NAVY)
    _decorate_dark_slide(slide)
    _add_text(
        slide, Inches(1.2), Inches(3.0), SLIDE_W - Inches(2.4), Inches(1.3),
        title, 36, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
    )
    if subtitle:
        _add_text(
            slide, Inches(1.8), Inches(4.35), SLIDE_W - Inches(3.6), Inches(0.8),
            subtitle, 16, ICE, italic=True, align=PP_ALIGN.CENTER,
        )
    return slide


def create_presentation(slides_data: list, output_path: str):
    """
    slides_data: [{"title": str, "subtitle": str, "bullets": [str, ...]}, ...]
    Birinchi element - muqova, oxirgisi (agar bullets bo'sh bo'lsa) - yopilish slaydi.
    """
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    total = len(slides_data)
    for i, item in enumerate(slides_data, start=1):
        title = (item.get("title") or "").strip()
        subtitle = (item.get("subtitle") or "").strip()
        bullets = item.get("bullets") or []

        if i == 1:
            add_cover_slide(prs, title, subtitle)
        elif i == total and not bullets:
            add_closing_slide(prs, title, subtitle)
        else:
            add_content_slide(prs, title, bullets, i, total)

    prs.save(output_path)
    return output_path
