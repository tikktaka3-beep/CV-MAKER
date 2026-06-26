import requests, urllib.parse
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

STYLE_CONFIGS = {
    "rasmiy": {"bg": RGBColor(240, 240, 240), "text": RGBColor(0, 0, 0), "accent": RGBColor(0, 50, 100), "font": "Arial"},
    "zamonaviy": {"bg": RGBColor(30, 30, 30), "text": RGBColor(255, 255, 255), "accent": RGBColor(0, 255, 255), "font": "Segoe UI"},
    "rangbarang": {"bg": RGBColor(255, 250, 240), "text": RGBColor(40, 40, 40), "accent": RGBColor(255, 100, 100), "font": "Verdana"},
    "och_ranglar": {"bg": RGBColor(245, 245, 255), "text": RGBColor(80, 80, 80), "accent": RGBColor(150, 150, 255), "font": "Calibri"},
    "toq_ranglar": {"bg": RGBColor(20, 20, 40), "text": RGBColor(220, 220, 220), "accent": RGBColor(200, 100, 200), "font": "Georgia"},
    "qadimiy": {"bg": RGBColor(230, 210, 180), "text": RGBColor(60, 40, 20), "accent": RGBColor(100, 60, 20), "font": "Times New Roman"},
    "adabiy": {"bg": RGBColor(255, 255, 240), "text": RGBColor(40, 40, 40), "accent": RGBColor(180, 80, 80), "font": "Cambria"},
    "matematik": {"bg": RGBColor(255, 255, 255), "text": RGBColor(0, 0, 0), "accent": RGBColor(0, 100, 200), "font": "Courier New"},
    "kimyoviy": {"bg": RGBColor(230, 240, 250), "text": RGBColor(0, 0, 50), "accent": RGBColor(0, 150, 100), "font": "Arial"},
    "fizik": {"bg": RGBColor(240, 240, 240), "text": RGBColor(20, 20, 20), "accent": RGBColor(255, 150, 0), "font": "Helvetica"},
    "astronomik": {"bg": RGBColor(5, 5, 20), "text": RGBColor(200, 200, 255), "accent": RGBColor(255, 255, 0), "font": "Arial"},
    "sport": {"bg": RGBColor(0, 0, 0), "text": RGBColor(255, 255, 255), "accent": RGBColor(255, 0, 0), "font": "Impact"},
}

def create_presentation(slides_data, output_path, style="rasmiy"):
    prs = Presentation()
    config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["rasmiy"])
    
    for i, item in enumerate(slides_data):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = config["bg"]
        
        # Sarlavha
        title = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        p = title.text_frame.paragraphs[0]
        p.text = item.get("title", "")
        p.font.color.rgb = config["text"]
        p.font.bold = True
        p.font.size = Pt(40)
        p.font.name = config["font"]
        
        # Matn va rasm qutisi
        top = Inches(2)
        bullets = item.get("bullets", [])
        
        # Rasm
        if item.get("image_prompt"):
            try:
                img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(item['image_prompt'] + ' ' + style)}?nologo=true"
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    slide.shapes.add_picture(BytesIO(response.content), Inches(8), Inches(1.5), width=Inches(4.5))
            except: pass
            
        # Bullets
        for bullet in bullets[:7]: # 7 tagacha ko'paytirdik
            box = slide.shapes.add_textbox(Inches(0.5), top, Inches(7.5), Inches(0.8))
            tf = box.text_frame
            p = tf.paragraphs[0]
            p.text = f"• {bullet}"
            p.font.color.rgb = config["text"]
            p.font.size = Pt(18)
            p.font.name = config["font"]
            top += Inches(0.6)
            
    prs.save(output_path)
    return output_path
    
    
