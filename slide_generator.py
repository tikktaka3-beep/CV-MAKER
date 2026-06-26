import requests
import urllib.parse
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- QUVNOQ VA OCHIQ RANGLAR PALITRASI (Har slayd uchun turlicha) ---
PASTEL_THEMES = [
    RGBColor(255, 235, 238), # Och pushti
    RGBColor(227, 242, 253), # Och havorang
    RGBColor(232, 245, 233), # Och yashil
    RGBColor(255, 243, 224), # Och shaftoli (peach)
    RGBColor(243, 229, 245), # Och binafsha (lavender)
    RGBColor(255, 248, 225), # Och sariq
    RGBColor(224, 242, 241), # Och yalpiz (mint)
]

DARK_TEXT = RGBColor(43, 43, 43)
ACCENT_COLOR = RGBColor(255, 107, 107) # Bullets va urg'ular uchun qizil-pushti

FONT_TITLE = "Trebuchet MS"
FONT_BODY = "Calibri"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MAX_BULLETS = 5

def fetch_image(prompt: str) -> BytesIO:
    """Sun'iy intellekt orqali bepul va quvnoq vektor rasm yuklab olish"""
    if not prompt:
        return None
    full_prompt = f"{prompt}, cute colorful flat vector art illustration, bright, minimal background"
    safe_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=800&height=800&nologo=true"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            return BytesIO(r.content)
    except Exception as e:
        print(f"Rasm yuklashda xatolik ({prompt}): {e}")
    return None

def _set_background(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def _add_text(slide, left, top, width, height, text, size, color,
               bold=False, italic=False, align=PP_ALIGN.LEFT, anchor=None,
               font=FONT_BODY, line_spacing=1.1):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
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

def _add_circle(slide, left, top, diameter, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, diameter, diameter)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape

def add_cover_slide(prs, title, subtitle, image_prompt, theme_color):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_background(slide, theme_color)
    
    # Katta dekorativ doira fon uchun
    _add_circle(slide, SLIDE_W - Inches(5), Inches(-2), Inches(8), RGBColor(255, 255, 255))
    
    # Chap tomonda matn
    _add_text(slide, Inches(1.0), Inches(2.5), Inches(6.5), Inches(2.0),
              title, 48, DARK_TEXT, bold=True, align=PP_ALIGN.LEFT, font=FONT_TITLE)
    if subtitle:
        _add_text(slide, Inches(1.0), Inches(4.5), Inches(6.0), Inches(1.0),
                  subtitle, 22, ACCENT_COLOR, bold=True, italic=True, align=PP_ALIGN.LEFT)
                  
    # O'ng tomonda AI rasm
    img_stream = fetch_image(image_prompt) if image_prompt else None
    if img_stream:
        try:
            slide.shapes.add_picture(img_stream, Inches(7.5), Inches(1.5), height=Inches(4.5))
        except:
            pass

def add_content_slide(prs, title, bullets, image_prompt, slide_no, total, theme_color):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_background(slide, theme_color)
    
    # Har safar rasm va matn joylashuvini o'zgartirish (dinamik dizayn)
    image_on_left = (slide_no % 2 == 0)
    
    # Sarlavha (Tepada o'rtada)
    _add_text(slide, Inches(0.5), Inches(0.4), SLIDE_W - Inches(1.0), Inches(1.0),
              title, 36, DARK_TEXT, bold=True, align=PP_ALIGN.CENTER, font=FONT_TITLE)

    # Joylashuv o'lchamlari
    text_left = Inches(5.5) if image_on_left else Inches(0.8)
    img_left = Inches(0.5) if image_on_left else Inches(7.8)
    
    # Rasm yuklash va qo'yish
    img_stream = fetch_image(image_prompt) if image_prompt else None
    if img_stream:
        try:
            slide.shapes.add_picture(img_stream, img_left, Inches(2.0), width=Inches(5.0), height=Inches(5.0))
        except:
            pass
            
    # Oq fonga ega quti matnlar uchun
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, text_left, Inches(1.8), Inches(7.0), Inches(5.0))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(255, 255, 255)
    shape.line.fill.background()
    
    bullets = [b for b in (bullets or []) if b][:MAX_BULLETS]
    n = max(len(bullets), 1)
    row_h = min(Inches(1.0), Inches(4.6) / n)
    top = Inches(2.0)
    
    for bullet in bullets:
        circle_d = Inches(0.2)
        circle_top = top + (row_h - circle_d) / 2 - Inches(0.15)
        _add_circle(slide, text_left + Inches(0.3), circle_top, circle_d, ACCENT_COLOR)
        _add_text(slide, text_left + Inches(0.7), top, Inches(6.0), row_h,
                  bullet, 20, DARK_TEXT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)
        top += row_h

    # Slayd raqami
    _add_text(slide, SLIDE_W - Inches(1.5), SLIDE_H - Inches(0.6), Inches(1.0), Inches(0.4),
              f"{slide_no}/{total}", 14, DARK_TEXT, align=PP_ALIGN.RIGHT, bold=True)

def create_presentation(slides_data: list, output_path: str):
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    total = len(slides_data)
    for i, item in enumerate(slides_data, start=1):
        title = (item.get("title") or "").strip()
        subtitle = (item.get("subtitle") or "").strip()
        bullets = item.get("bullets") or []
        image_prompt = item.get("image_prompt") or ""
        
        # Har bir slayd uchun turlicha rang tanlash
        theme_color = PASTEL_THEMES[i % len(PASTEL_THEMES)]

        if i == 1:
            add_cover_slide(prs, title, subtitle, image_prompt, theme_color)
        elif i == total and not bullets:
            add_cover_slide(prs, title, subtitle, image_prompt, theme_color)
        else:
            add_content_slide(prs, title, bullets, image_prompt, i, total, theme_color)

    prs.save(output_path)
    return output_path
    
