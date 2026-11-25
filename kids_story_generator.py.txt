"""Generate an Arabic kids story with Gemini. Returns dict: title, story, description, tags, visual_keywords."""
import json, os, re, random, requests

HISTORY_FILE = os.getenv("HISTORY_FILE", "kids_history.json")
MODELS = [m.strip() for m in os.getenv("GEMINI_MODEL", "gemini-2.5-flash,gemini-2.0-flash").split(",") if m.strip()]
THEMES = ["الصدق", "الكرم والمشاركة", "مساعدة الآخرين", "الشجاعة", "الصبر", "احترام الوالدين",
          "النظافة", "الصداقة", "الاعتذار", "عدم التنمر", "التعاون", "الشكر والامتنان", "حب الحيوانات", "الاجتهاد"]
HEROES = ["أرنب صغير", "قطة", "فيل", "عصفورة", "سلحفاة", "طفل اسمه يوسف", "طفلة اسمها ليلى", "دب", "نحلة", "زرافة"]


def load_history():
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(h):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h[-200:], f, ensure_ascii=False, indent=1)


def _call(model, prompt, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r = requests.post(url, params={"key": key}, timeout=120, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"}})
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def generate_story():
    key = os.environ["GEMINI_API_KEY"]
    hist = load_history()
    used = [h["title"] for h in hist[-30:]]
    theme, hero = random.choice(THEMES), random.choice(HEROES)
    prompt = f"""اكتب قصة أطفال بالعربية الفصحى المبسطة (يفهمها طفل من 4 إلى 8 سنين).
الفكرة/القيمة: {theme}. البطل: {hero}.
الشروط: من 600 إلى 900 كلمة، جمل قصيرة وواضحة، أسلوب دافئ ومرح، حوار بسيط، نهاية سعيدة فيها عبرة.
ممنوع تماما: العنف، الرعب، الألفاظ السيئة، السياسة، الدين الخلافي، أي محتوى غير مناسب للأطفال.
لا تكرر هذه القصص: {used}
رجّع JSON فقط بهذه المفاتيح:
title (عنوان قصير جذاب بالعربية), story (نص القصة فقط بدون عناوين أو رموز),
description (وصف يوتيوب من سطرين بالعربية), tags (قائمة 8 كلمات مفتاحية),
visual_keywords (قائمة 6 كلمات إنجليزية بسيطة للبحث عن فيديوهات خلفية مناسبة مثل: forest, rabbit, garden, sunshine)."""
    last = None
    for model in MODELS:
        for _ in range(2):
            try:
                txt = _call(model, prompt, key)
                data = json.loads(re.sub(r"^```json|```$", "", txt.strip()).strip())
                if len(data["story"].split()) < 250:
                    raise ValueError("story too short")
                hist.append({"title": data["title"], "theme": theme})
                save_history(hist)
                return data
            except Exception as e:
                last = e
                print(f"[gemini:{model}] {e}")
    raise RuntimeError(f"Story generation failed: {last}")


if __name__ == "__main__":
    print(json.dumps(generate_story(), ensure_ascii=False, indent=2))
