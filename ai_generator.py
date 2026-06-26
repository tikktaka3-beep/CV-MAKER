import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

LANGUAGE_NAMES = {
    "uz": "o'zbek",
    "ru": "rus",
    "en": "ingliz",
}

STYLE_DESCRIPTIONS = {
    "rasmiy": "rasmiy va professional uslubda, ishbilarmonlik tiliga mos",
    "quvnoq": "quvnoq, jonli, rang-barang va qiziqarli uslubda, oddiy odamlarga tushunarli ohangda",
    "simple": "juda sodda va tushunarli tilda, ortiqcha murakkab so'z va atamalarsiz",
}

def generate_slides_content(text: str, language: str, slide_count: int,
                             style: str, extra_notes: str = "") -> dict:
    lang_name = LANGUAGE_NAMES.get(language, "o'zbek")
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["quvnoq"])

    system_prompt = f"""Sen kreativ taqdimot (prezentatsiya) tarkibini tuzuvchi yordamchisan.

Foydalanuvchi bergan matn/mavzu asosida ANIQ {slide_count} ta slayddan iborat taqdimot tarkibini tuz.

Qoidalar:
- Taqdimot tili: {lang_name} tili. Barcha matn {lang_name} tilida yozilishi shart.
- Uslub: {style_desc}. Quruq faktlar emas, balki qiziqarli va sodda gaplardan foydalan.
- Birinchi slayd - muqova: qisqa sarlavha (title) va kichik subtitle, bullets bo'sh [].
- Oxirgi slayd - xulosa: qisqa rahmat yoki xulosa sarlavhasi, bullets bo'sh [].
- Qolgan slaydlar - mazmun: har birida qisqa sarlavha va 3-5 ta QISQA bullet point (1 qisqa gap).
- Muhim: Har bir slayd uchun mos keluvchi bitta qisqa INGLIZCHA rasm g'oyasini (image_prompt) yoz. Rasm g'oyasi 2-4 ta inglizcha so'zdan iborat bo'lsin (masalan: "happy student", "colorful rocket", "teamwork success"). Bu rasmlar keyinchalik slayd dizayni uchun ishlatiladi.

Javobni faqat quyidagi JSON sxemasiga mos holda qaytar:
{{"slides": [{{"title": "...", "subtitle": "...", "bullets": ["...", "..."], "image_prompt": "english keyword"}}, ...]}}
"""

    user_content = f"Mavzu/matn:\n{text}"
    if extra_notes:
        user_content += f"\n\nQo'shimcha izoh:\n{extra_notes}"

    response = client.models.generate_content(
        model=MODEL,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    data = json.loads(response.text)

    if "slides" not in data or not isinstance(data["slides"], list) or not data["slides"]:
        raise ValueError("AI javobida slaydlar topilmadi")

    return data
                                 
                                 
