"""
ai_generator.py — Groq (tez va kuchli)
"""

import os
import json
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"   # yoki "mixtral-8x7b-32768", "gemma2-9b-it"

LANGUAGE_NAMES = {
    "uz": "o'zbek",
    "ru": "rus",
    "en": "ingliz",
}

STYLE_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional uslubda",
    "quvnoq": "quvnoq, jonli va qiziqarli uslubda",
    "simple": "juda sodda va tushunarli tilda",
}

THEME_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional", "zamonaviy": "zamonaviy va minimalistik",
    "rangbarang": "rang-barang va quvnoq", "och": "engil va ochiq ranglarda",
    "toq": "chuqur va to'q ranglarda", "qadimiy": "qadimiy va klassik",
    "adabiy": "adabiy va ilhomlantiruvchi", "matematik": "ilmiy va aniq",
    "kimyoviy": "kimyoviy uslubda", "fizik": "fizika ruhida",
    "astronomik": "kosmos va yulduzlar mavzusida", "sport": "dinamik va motivatsion"
}


def generate_slides_content(text: str, language: str, slide_count: int, style: str, extra_notes: str = "") -> dict:
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["rasmiy"])
    theme_desc = THEME_DESCRIPTIONS.get(style, THEME_DESCRIPTIONS["rasmiy"])

    system_prompt = f"""Sen professional prezentatsiya yaratuvchisan.
Foydalanuvchi matni asosida aniq {slide_count} ta slayddan iborat mukammal taqdimot yarating.

Qoidalar:
- Til: {lang_name}
- Uslub: {style_desc}
- Theme: {theme_desc} — kontentni shunga moslashtir
- 1-slayd: Muqova
- Oxirgi slayd: Xulosa / Rahmat
- O'rtadagilar: 3-5 ta qisqa bullet
- Javob faqat JSON bo'lsin."""

    user_prompt = f"Mavzu: {text}\nQo'shimcha: {extra_notes}" if extra_notes else f"Mavzu: {text}"

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

    data = json.loads(response.choices[0].message.content)

    if "slides" not in data:
        raise ValueError("AI javobi noto'g'ri")

    # Slayd sonini to'g'rilash
    data["slides"] = data["slides"][:slide_count]
    while len(data["slides"]) < slide_count:
        data["slides"].append({"title": "Xulosa", "subtitle": "Rahmat!", "bullets": []})

    return data
                                 
