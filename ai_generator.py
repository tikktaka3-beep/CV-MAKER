import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

def generate_slides_content(text: str, language: str, slide_count: int,
                             style: str, extra_notes: str = "") -> dict:
    
    style_prompts = {
        "rasmiy": "Korporativ, professional, ishbilarmonlik tili. Aniq faktlar va grafik ma'lumotlar.",
        "zamonaviy": "Minimalist, qisqa va lo'nda, trenddagi dizayn.",
        "rangbarang": "Yorqin, hissiyotli, pozitiv va kreativ yondashuv.",
        "och_ranglar": "Tinchlantiruvchi, havodor, yengil va estetik.",
        "toq_ranglar": "Dramatik, jiddiy, chuqur va kontrastli uslub.",
        "qadimiy": "Tarixiy, adabiy, klassik va nafis so'z boyligi.",
        "adabiy": "Badiiy, tasviriy, chuqur ma'noli va poetik.",
        "matematik": "Mantiqiy, formulalar va ketma-ketlikka asoslangan, aniq.",
        "kimyoviy": "Strukturaviy, jarayonlarga asoslangan, ilmiy atamalar.",
        "fizik": "Fundamental qonunlar, hodisalar va sabab-oqibat tahlili.",
        "astronomik": "Buyuk miqyosli, kosmik, kelajak va koinot haqida.",
        "sport": "Dinamik, motivatsion, tezkor va energiya bilan to'la."
    }

    system_prompt = f"""Sen professional prezentatsiya ustasisan.
    Mavzu: {text}
    Uslub: {style}. {style_prompts.get(style, 'Professional')}
    
    Qoidalar:
    - {slide_count} ta slayd tayyorla.
    - Slayd mazmunini tanlangan uslubga moslab boyit (ma'lumotlarni ko'paytir).
    - Har bir slayd uchun uslubga mos inglizcha rasm prompti (image_prompt) yoz.
    
    Javobni JSON formatida qaytar:
    {{"slides": [{{"title": "...", "subtitle": "...", "bullets": ["...", "..."], "image_prompt": "..."}}, ...]}}
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=f"Mavzu: {text}\nIzoh: {extra_notes}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )
    return json.loads(response.text)
                                 
                                 
                                 
