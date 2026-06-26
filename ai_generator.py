"""
ai_generator.py — Groq (tuzatilgan, mustahkam versiya)
"""

import os
import json
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"  # yoki "mixtral-8x7b-32768"

LANGUAGE_NAMES = {
    "uz": "o'zbek",
    "ru": "rus",
    "en": "ingliz",
}

STYLE_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional uslubda",
    "quvnoq": "quvnoq va jonli uslubda",
    "simple": "oddiy va tushunarli tilda",
}

THEME_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional", 
    "zamonaviy": "zamonaviy va minimalistik",
    "rangbarang": "rang-barang va quvnoq", 
    "och": "engil va ochiq ranglarda",
    "toq": "chuqur va to'q ranglarda", 
    "qadimiy": "qadimiy va klassik",
    "adabiy": "adabiy va ilhomlantiruvchi", 
    "matematik": "ilmiy va aniq",
    "kimyoviy": "kimyoviy uslubda", 
    "fizik": "fizika ruhida",
    "astronomik": "kosmos va yulduzlar mavzusida", 
    "sport": "dinamik va motivatsion"
}


def generate_slides_content(text: str, language: str, slide_count: int, style: str, extra_notes: str = "") -> dict:
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["rasmiy"])
    theme_desc = THEME_DESCRIPTIONS.get(style, THEME_DESCRIPTIONS["rasmiy"])

    system_prompt = f"""Sen professional prezentatsiya yaratuvchisan. 
Foydalanuvchi bergan mavzu asosida aniq {slide_count} ta slayddan iborat taqdimot tayyorla.

QAT'IY TALABLAR:
- Barcha matn {lang_name} tilida bo'lsin.
- Uslub: {style_desc}
- Dizayn mavzusi: {theme_desc}
- 1-slayd: Muqova (title + subtitle, bullets: [])
- Oxirgi slayd: Xulosa yoki rahmat (bullets: [])
- O'rtadagi slaydlar: Har birida 3-5 ta qisqa bullet
- Javobni faqat toza JSON formatida qaytar. Boshqa hech narsa yozma.

JSON sxemasi:
{{
  "slides": [
    {{"title": "Sarlavha", "subtitle": "Qo'shimcha matn", "bullets": ["bullet 1", "bullet 2"]}},
    ...
  ]
}}"""

    user_prompt = f"Mavzu: {text}"
    if extra_notes:
        user_prompt += f"\n\nQo'shimcha talab: {extra_notes}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)

        if "slides" not in data or not isinstance(data["slides"], list):
            raise ValueError("JSON da 'slides' topilmadi")

        # Slayd sonini to'g'rilash
        slides = data["slides"][:slide_count]
        while len(slides) < slide_count:
            slides.append({
                "title": "Xulosa",
                "subtitle": "Rahmat! Savollaringiz bo'lsa so'rang.",
                "bullets": []
            })
        
        return {"slides": slides}

    except Exception as e:
        print("Groq xatosi:", str(e))
        # Fallback oddiy struktura
        return {
            "slides": [
                {"title": "Muqova", "subtitle": text[:100], "bullets": []},
                {"title": "Asosiy ma'lumot", "subtitle": "", "bullets": ["Ma'lumot yetarli emas"]},
                {"title": "Xulosa", "subtitle": "Rahmat!", "bullets": []}
            ][:slide_count]
        }
                                 
