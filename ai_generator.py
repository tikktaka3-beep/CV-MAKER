"""
ai_generator.py
Google Gemini API orqali foydalanuvchi matni asosida slaydlar tarkibini (JSON) generatsiya qiladi.
Yangi ko'p theme (dizayn) qo'llab-quvvatlanadi.
"""

import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Bepul tarifda ishlaydigan tezkor model
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


def generate_slides_content(text: str, language: str, slide_count: int,
                             style: str, extra_notes: str = "") -> dict:
    """
    Qaytaradi: {"slides": [{"title": str, "subtitle": str, "bullets": [str, ...]}, ...]}
    Birinchi element - muqova slayd, oxirgisi - yopilish slaydi.
    """
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["rasmiy"])
    theme_desc = THEME_DESCRIPTIONS.get(style, THEME_DESCRIPTIONS["rasmiy"])

    system_prompt = f"""Sen professional taqdimot (prezentatsiya) tarkibini tuzuvchi yordamchisan.

Foydalanuvchi bergan matn/mavzu asosida ANIQ {slide_count} ta slayddan iborat taqdimot tarkibini tuz.

Qoidalar:
- Taqdimot tili: {lang_name} tili. Barcha matn (sarlavha, subtitle, bullet'lar) {lang_name} tilida yozilishi shart.
- Matn uslubi: {style_desc}.
- Visual theme: {theme_desc}. Kontentni shu mavzuga mos ravishda jonlantiring (masalan, matematik mavzuda formulalar, astronomikda kosmos haqida, sportda harakat va motivatsiya elementlari).
- Birinchi slayd - muqova (cover) slayd: faqat qisqa va ta'sirli sarlavha (title) va kichik subtitle bo'lsin, "bullets" bo'sh array [] bo'lsin.
- Oxirgi slayd - yopilish/xulosa slaydi: qisqa rahmat yoki xulosa sarlavhasi va subtitle, "bullets" bo'sh array [] bo'lsin.
- Orada qolgan slaydlar - mazmunli slaydlar: har birida qisqa sarlavha va 3-5 ta QISQA bullet point (har biri 1 qisqa gap, 12-15 so'zdan oshmasin).
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
        ),
    )

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError("AI javobi JSON formatida emas")

    if "slides" not in data or not isinstance(data["slides"], list) or not data["slides"]:
        raise ValueError("AI javobida slaydlar topilmadi")

    # Slayd sonini tekshirish
    if len(data["slides"]) != slide_count:
        # Agar kerakli son bo'lmasa, qisqartiramiz yoki to'ldiramiz (oddiy yechim)
        data["slides"] = data["slides"][:slide_count]
        while len(data["slides"]) < slide_count:
            data["slides"].append({"title": "Xulosa", "subtitle": "", "bullets": []})

    return data
                                 
                                 
