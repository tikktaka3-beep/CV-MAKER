"""
ai_generator.py — Mukammal AI prompt bilan
"""

import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

LANGUAGE_NAMES = {"uz": "o'zbek", "ru": "rus", "en": "ingliz"}

STYLE_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional uslubda",
    "quvnoq": "quvnoq, jonli va qiziqarli uslubda",
    "simple": "juda sodda va tushunarli tilda",
}

THEME_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional",
    "zamonaviy": "zamonaviy, minimalistik va texnologik",
    "rangbarang": "rang-barang, quvnoq va yorqin",
    "och": "engil, ochiq va havo ranglarda",
    "toq": "chuqur, kuchli va to'q ranglarda",
    "qadimiy": "qadimiy, klassik va tarixiy ruhda",
    "adabiy": "adabiy, she'riy va ilhomlantiruvchi",
    "matematik": "ilmiy, aniq va formula/usulga asoslangan",
    "kimyoviy": "kimyoviy elementlar va reaktsiyalar uslubida",
    "fizik": "fizika tajribalari va energiya ruhida",
    "astronomik": "kosmos, yulduzlar va galaktika mavzusida",
    "sport": "dinamik, harakatli va motivatsion"
}


def generate_slides_content(text: str, language: str, slide_count: int, style: str, extra_notes: str = "") -> dict:
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["rasmiy"])
    theme_desc = THEME_DESCRIPTIONS.get(style, THEME_DESCRIPTIONS["rasmiy"])

    system_prompt = f"""Sen yuqori darajadagi professional prezentatsiya dizayneri va kontent muallifisan.

Foydalanuvchi matni asosida aniq {slide_count} ta slayddan iborat mukammal taqdimot yarating.

QAT'IY QOIDALAR:
- Til: {lang_name} tili. Barcha matnlar toza {lang_name} tilida bo'lsin.
- Matn uslubi: {style_desc}.
- Visual Theme: {theme_desc}. Kontentni shu mavzuga to'liq moslashtiring (masalan: matematikada formulalar, astronomiyada kosmos tasvirlari, sportda dinamika va g'alaba ruhini qo'shing).
- Birinchi slayd: Kuchli muqova (title + subtitle).
- Oxirgi slayd: Yopilish / Rahmat / Savollar slaydi.
- O'rtadagi slaydlar: Har birida 3-5 ta qisqa, ta'sirli bullet (har biri 10-15 so'zdan oshmasin).
- Har bir slayd alohida, mantiqiy ketma-ketlikda bo'lsin.
- Takrorlanish bo'lmasin.

Javobni faqat quyidagi JSON formatida qaytar:
{{"slides": [{{"title": "...", "subtitle": "...", "bullets": ["...", "..."]}}, ...]}}
"""

    user_content = f"Mavzu:\n{text}"
    if extra_notes:
        user_content += f"\n\nQo'shimcha talablar:\n{extra_notes}"

    response = client.models.generate_content(
        model=MODEL,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.75,
            top_p=0.85,
        ),
    )

    data = json.loads(response.text)

    if "slides" not in data or len(data["slides"]) < 2:
        raise ValueError("AI javobi noto'g'ri")

    # Slayd sonini to'g'rilash
    data["slides"] = data["slides"][:slide_count]
    while len(data["slides"]) < slide_count:
        data["slides"].append({"title": "Xulosa", "subtitle": "Rahmat!", "bullets": []})

    return data
                                 
