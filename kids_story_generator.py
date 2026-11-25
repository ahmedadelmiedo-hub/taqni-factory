"""Generate an Arabic kids story with Gemini, split into illustrated scenes.
Returns dict: title, story, description, tags, character, scenes[{narration,image_prompt,search}], thumbnail_prompt."""
import json, os, re, random, requests

HISTORY_FILE = os.getenv("HISTORY_FILE", "kids_history.json")
MODELS = [m.strip() for m in os.getenv("GEMINI_MODEL", "gemini-2.5-flash,gemini-2.0-flash").split(",") if m.strip()]
N_SCENES = int(os.getenv("N_SCENES", "12"))
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
    r = requests.post(url, params={"key": key}, timeout=180, json={
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
الشروط: من 600 إلى 900 كلمة، جمل قصيرة وواضحة، أسلوب دافئ ومرح، حوار بسيط، تكرار لطيف لجملة أو صوت مرح يحبه الأطفال، نهاية سعيدة فيها عبرة.
ممنوع تماما: العنف، الرعب، الألفاظ السيئة، السياسة، الدين الخلافي، أي محتوى غير مناسب للأطفال.
لا تكرر هذه القصص: {used}

قسّم القصة إلى {N_SCENES} مشهدا متتاليا، كل مشهد حوالي 40 إلى 65 كلمة، ودمج المشاهد بالترتيب يعطي القصة كاملة.
لكل مشهد اكتب image_prompt بالإنجليزية: وصف بصري محدد لما يحدث في هذا المشهد بالذات (المكان، ماذا يفعل البطل، المشاعر، الإضاءة)،
وابدأه دائما باسم/وصف الشخصية الرئيسية كما في character. بدون أي نص مكتوب داخل الصورة.

رجّع JSON فقط بهذه المفاتيح:
title (عنوان قصير جذاب بالعربية), description (وصف يوتيوب من سطرين بالعربية), tags (قائمة 8 كلمات مفتاحية),
character (بالإنجليزية: وصف ثابت ومفصل للشخصية الرئيسية: النوع واللون والملابس والملامح، مثل: a small cute gray baby elephant with big ears, a red scarf and big friendly eyes),
scenes (قائمة من {N_SCENES} كائنا، كل كائن فيه: narration (نص المشهد بالعربية فقط بدون رموز), image_prompt (بالإنجليزية), search (كلمتان إنجليزيتان بسيطتان لصورة احتياطية)),
thumbnail_prompt (بالإنجليزية: لقطة قريبة مبهجة جدا للشخصية الرئيسية بوجه سعيد معبر وألوان زاهية وخلفية بسيطة، مع ترك مساحة فارغة في الأسفل),
thumbnail_text (من كلمتين إلى 4 كلمات بالعربية جذابة للغلاف)."""
    last = None
    for model in MODELS:
        for _ in range(2):
            try:
                txt = _call(model, prompt, key)
                data = json.loads(re.sub(r"^```json|```$", "", txt.strip()).strip())
                scenes = [s for s in data["scenes"] if s.get("narration", "").strip()]
                if len(scenes) < 8:
                    raise ValueError("too few scenes")
                data["scenes"] = scenes
                data["story"] = " ".join(s["narration"].strip() for s in scenes)
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
