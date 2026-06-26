"""
ai_generator.py
Google Gemini API (BEPUL tarif) orqali foydalanuvchi matni asosida
slaydlar tarkibini (JSON) generatsiya qiladi.
"""

import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Bepul tarifda ishlaydigan tezkor model. Agar limitga tez-tez tegib qolsangiz,
# "gemini-2.5-flash-lite" ga o'zgartirib ko'ring (kuniga ko'proq so'rov beradi).
MODEL = "gemini-2.5-flash"

LANGUAGE_NAMES = {
    "uz": "o'zbek",
    "ru": "rus",
    "en": "ingliz",
}

STYLE_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional uslubda, ishbilarmonlik tiliga mos",
    "quvnoq": "quvnoq, jonli va qiziqarli uslubda, o'quvchini qiziqtiradigan ohangda",
    "simple": "juda sodda va tushunarli tilda, ortiqcha murakkab so'z va atamalarsiz",
}


def generate_slides_content(text: str, language: str, slide_count: int,
                             style: str, extra_notes: str = "") -> dict:
    """
    Qaytaradi: {"slides": [{"title": str, "subtitle": str, "bullets": [str, ...]}, ...]}
    Birinchi element - muqova slayd (bullets bo'sh), oxirgisi - yopilish slaydi (bullets bo'sh).
    """
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["rasmiy"])

    system_prompt = f"""Sen professional taqdimot (prezentatsiya) tarkibini tuzuvchi yordamchisan.

Foydalanuvchi bergan matn/mavzu asosida ANIQ {slide_count} ta slayddan iborat taqdimot tarkibini tuz.

Qoidalar:
- Taqdimot tili: {lang_name} tili. Barcha matn (sarlavha, subtitle, bullet'lar) {lang_name} tilida yozilishi shart.
- Uslub: {style_desc}.
- Birinchi slayd - muqova (cover) slayd: faqat qisqa va ta'sirli sarlavha (title) va kichik subtitle bo'lsin, "bullets" bo'sh array [] bo'lsin.
- Oxirgi slayd - yopilish/xulosa slaydi: qisqa rahmat yoki xulosa sarlavhasi va subtitle, "bullets" bo'sh array [] bo'lsin.
- Orada qolgan slaydlar - mazmunli slaydlar: har birida qisqa sarlavha va 3-5 ta QISQA bullet point (har biri 1 qisqa gap, 12 so'zdan oshmasin).
- Umumiy slayd soni aniq {slide_count} ta bo'lishi kerak (muqova va yopilish ham shu songa kiradi).
- Takrorlanishlardan saqlan, har slayd alohida fikr bersin.

Javobni faqat quyidagi JSON sxemasiga mos holda qaytar:
{{"slides": [{{"title": "...", "subtitle": "...", "bullets": ["...", "..."]}}, ...]}}
"""

    user_content = f"Mavzu/matn:\n{text}"
    if extra_notes:
        user_content += f"\n\nQo'shimcha izoh/talab:\n{extra_notes}"

    response = client.models.generate_content(
        model=MODEL,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.7,
            max_output_tokens=4096,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    if not response.text:
        raise ValueError("AI hech qanday javob qaytarmadi (bo'sh javob)")

    data = json.loads(response.text)

    if "slides" not in data or not isinstance(data["slides"], list) or not data["slides"]:
        raise ValueError("AI javobida slaydlar topilmadi")

    return data
                                 
