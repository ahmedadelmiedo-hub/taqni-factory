"""Taqni (تقني): Arabic tech shorts factory.
Gemini writes a hook-first script -> edge-tts voice (word timings) -> animated tech visuals
-> big word-by-word captions -> 9:16 mp4 -> optional YouTube upload.
Free tooling only. Env: GEMINI_API_KEY (required), PEXELS_API_KEY (optional), YT_TOKEN_JSON (upload),
DRY_RUN=1 (default for manual runs), PRIVACY_STATUS, TTS_VOICE, TTS_RATE, TOPIC (override)."""
import asyncio, json, os, random, re, subprocess, sys, time
import requests
import edge_tts
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
HISTORY = os.path.join(HERE, "history.json")
W, H = 1080, 1920
VOICE = os.getenv("TTS_VOICE", "ar-EG-ShakirNeural")
RATE = os.getenv("TTS_RATE", "+5%")
MODELS = [m.strip() for m in os.getenv("GEMINI_MODEL", "gemini-3.8-flash,gemini-3.5-flash,gemini-flash-latest,gemini-3.5-flash-lite").split(",") if m.strip()]
FONT = os.path.join(HERE, "fonts", "NotoSansArabic-Black.ttf")
FONT_URL = "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSansArabic/hinted/ttf/NotoSansArabic-Black.ttf"

PILLARS = {
    "phone": "الموبايل والنت: حاجات في جيب الناس (بطارية، تخزين، إعدادات، نت بطيء، واتساب)",
    "ai": "الذكاء الاصطناعي بالبلدي: أدوات وحيل بتوفر وقت وفلوس لواحد عادي",
    "security": "أمان وخصوصية: نصب، تجسس، حماية الحسابات، علامات خطر",
    "stories": "خفايا الشركات والتقنية: قصص حقيقية مشهورة ومؤكدة (جوجل، نوكيا، تطبيقات)",
    "money": "فلوس من التقنية: شغل أونلاين، اشتراكات بتتسحب، أدوات مجانية بدل المدفوعة",
}
SERIES = ["خرافة تقنية", "ثانية ثانية AI", "إعداد لازم تقفله", "قصة شركة في دقيقة", "نصبة اتكشفت"]


def ensure_font():
    for p in (FONT, "/usr/share/fonts/truetype/noto/NotoSansArabic-Black.ttf"):
        if os.path.exists(p):
            return p
    os.makedirs(os.path.dirname(FONT), exist_ok=True)
    r = requests.get(FONT_URL, timeout=60); r.raise_for_status()
    open(FONT, "wb").write(r.content)
    return FONT


def ar(s):
    s = re.sub(r'[\u064B-\u0652\u0670]', '', s)
    return get_display(arabic_reshaper.reshape(s))


def load_hist():
    try:
        return json.load(open(HISTORY, encoding="utf-8"))
    except Exception:
        return []


def save_hist(h):
    json.dump(h[-300:], open(HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- script
def gemini(prompt):
    key = os.environ["GEMINI_API_KEY"]
    last = None
    for model in MODELS:
        for t in range(3):
            try:
                r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                  params={"key": key}, timeout=90,
                                  json={"contents": [{"parts": [{"text": prompt}]}],
                                        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"}})
                if r.status_code in (400, 404):
                    print(f"[gemini:{model}] HTTP {r.status_code}, skipping model"); break
                r.raise_for_status()
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```json|```$", "", txt.strip()).strip())
            except Exception as e:
                last = e; print(f"[gemini:{model}] {type(e).__name__}"); time.sleep(8 * (t + 1))
    raise RuntimeError(f"gemini failed: {last}")


def make_script():
    hist = load_hist()
    used = [h["title"] for h in hist[-60:]]
    counts = {}
    for h in hist[-20:]:
        counts[h.get("pillar")] = counts.get(h.get("pillar"), 0) + 1
    pillar = min(PILLARS, key=lambda k: counts.get(k, 0) + random.random())
    topic = os.getenv("TOPIC", "")
    series = random.choice(SERIES)
    prompt = f"""أنت كاتب محتوى تقني مصري لقناة شورتس اسمها "تقني". اكتب سكريبت فيديو عمودي مدته 40 إلى 55 ثانية بالعامية المصرية البسيطة (مفهومة لأي حد، من غير مصطلحات معقدة).
المحور: {PILLARS[pillar]}. السلسلة (اختياري تستخدمها): {series}. {('الموضوع المطلوب: ' + topic) if topic else 'اختار موضوع محدد وجذاب وغير مكرر.'}
قواعد صارمة:
- المعلومة لازم تكون صحيحة ومؤكدة ومعروفة. ممنوع تأليف أرقام أو أسعار أو أخبار أو أسماء. لو مش متأكد من رقم، متكتبوش. ممنوع ذكر أسعار أو إصدارات متغيرة.
- المشهد الأول هوك صادم أو سؤال فضول في أقل من 12 كلمة، يتكلم عن فايدة أو خطر يخص المشاهد نفسه. بدون "أهلا" وبدون مقدمات.
- بعدها 4 إلى 6 مشاهد: كل مشهد جملة أو جملتين قصار (10 إلى 22 كلمة)، فيها معلومة واحدة واضحة وخطوة عملية لو ينفع.
- المشهد الأخير: خلاصة + دعوة للمتابعة قصيرة، وآخر جملة ترجع للهوك عشان الفيديو يتعاد (لوب).
- ممنوع كلام سياسي أو ديني أو طبي، وممنوع تعليم نصب أو اختراق (الأمان للدفاع بس).
- لا تكرر هذه العناوين: {used}
رجّع JSON فقط بالمفاتيح:
title (عنوان يوتيوب أقل من 60 حرف، فجوة فضول + فايدة، بالمصري),
description (سطرين + كلمة هاشتاج #Shorts #تقني),
tags (8 كلمات),
hook_text (2 إلى 4 كلمات كبيرة تظهر على الشاشة في أول ثانيتين),
scenes (قائمة، كل عنصر: narration بالمصري بدون رموز وبالتشكيل الخفيف لو لازم, on_screen (كلمة إلى 3 كلمات كبار تظهر مع المشهد), keyword (كلمتين إنجليزي لبحث لقطة فيديو تقنية مناسبة مثل: smartphone battery, hacker laptop, artificial intelligence))."""
    data = gemini(prompt)
    scenes = [s for s in data["scenes"] if s.get("narration", "").strip()]
    if len(scenes) < 4:
        raise ValueError("too few scenes")
    data["scenes"] = scenes
    data["_pillar"] = pillar
    return data


Gemini writes a hook-first script -> edge-tts voice (word timings) -> animated tech visuals
-> big word-by-word captions -> 9:16 mp4 -> optional YouTube upload.
Free tooling only. Env: GEMINI_API_KEY (required), PEXELS_API_KEY (optional), YT_TOKEN_JSON (upload),
DRY_RUN=1 (default for manual runs), PRIVACY_STATUS, TTS_VOICE, TTS_RATE, TOPIC (override)."""
import asyncio, json, os, random, re, subprocess, sys, time
import requests
import edge_tts
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
HISTORY = os.path.join(HERE, "history.json")
W, H = 1080, 1920
VOICE = os.getenv("TTS_VOICE", "ar-EG-ShakirNeural")
RATE = os.getenv("TTS_RATE", "+5%")
MODELS = [m.strip() for m in os.getenv("GEMINI_MODEL", "gemini-3.5-flash,gemini-3.5-flash-lite,gemini-flash-latest").split(",") if m.strip()]
FONT = os.path.join(HERE, "fonts", "NotoSansArabic-Black.ttf")
FONT_URL = "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSansArabic/hinted/ttf/NotoSansArabic-Black.ttf"

PILLARS = {
    "explain": "ليه موبايلك بيعمل كده: بطارية، سخونة، بطء",
    "tricks": "إعدادات وحيل مخفية في الأندرويد والواتساب",
    "save": "توفير شحن ونت وتخزين",
    "gear": "أكسسوارات تستاهل (شواحن، اكسسوارات عربية) = فيديو عمولة",
    "news": "أخبار وتقنيات جديدة ببساطة، من غير تعقيد",
}
import datetime
WEEK_PLAN = {5: "tricks", 6: "gear", 0: "explain", 1: "save", 2: "tricks", 3: "explain", 4: "news"}
CAIRO = datetime.timezone(datetime.timedelta(hours=2))


def pick_pillar():
    day = int(os.getenv("FORCE_DAY", datetime.datetime.now(CAIRO).weekday()))
    return WEEK_PLAN[day]


AFF = os.getenv("AFFILIATE_LINKS", "")  # JForce links, comma separated, from the catalog file
SERIES = ["خرافة تقنية", "ثانية ثانية AI", "إعداد لازم تقفله", "قصة شركة في دقيقة", "نصبة اتكشفت"]


def ensure_font():
    for p in (FONT, "/usr/share/fonts/truetype/noto/NotoSansArabic-Black.ttf"):
        if os.path.exists(p):
            return p
    os.makedirs(os.path.dirname(FONT), exist_ok=True)
    r = requests.get(FONT_URL, timeout=60); r.raise_for_status()
    open(FONT, "wb").write(r.content)
    return FONT


def ar(s):
    s = re.sub(r'[\u064B-\u0652\u0670]', '', s)
    return get_display(arabic_reshaper.reshape(s))


def load_hist():
    try:
        return json.load(open(HISTORY, encoding="utf-8"))
    except Exception:
        return []


def save_hist(h):
    json.dump(h[-300:], open(HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- script
def gemini(prompt):
    key = os.environ["GEMINI_API_KEY"]
    last = None
    for model in MODELS:
        for t in range(3):
            try:
                r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                  params={"key": key}, timeout=90,
                                  json={"contents": [{"parts": [{"text": prompt}]}],
                                        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"}})
                if r.status_code in (400, 404, 429):
                    print(f"[gemini:{model}] HTTP {r.status_code}, skipping model"); break
                r.raise_for_status()
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```json|```$", "", txt.strip()).strip())
            except Exception as e:
                last = e; print(f"[gemini:{model}] {type(e).__name__}"); time.sleep(8 * (t + 1))
    raise RuntimeError(f"gemini failed: {last}")


def make_script():
    hist = load_hist()
    used = [h["title"] for h in hist[-60:]]
    counts = {}
    for h in hist[-20:]:
        counts[h.get("pillar")] = counts.get(h.get("pillar"), 0) + 1
    pillar = pick_pillar()
    topic = os.getenv("TOPIC", "")
    series = random.choice(SERIES)
    prompt = f"""أنت كاتب محتوى تقني مصري لقناة شورتس اسمها "تقني". اكتب سكريبت فيديو عمودي مدته 40 إلى 55 ثانية بالعامية المصرية البسيطة (مفهومة لأي حد، من غير مصطلحات معقدة).
المحور: {PILLARS[pillar]}. السلسلة (اختياري تستخدمها): {series}. {('الموضوع المطلوب: ' + topic) if topic else 'اختار موضوع محدد وجذاب وغير مكرر.'}
قواعد صارمة:
- المعلومة لازم تكون صحيحة ومؤكدة ومعروفة. ممنوع تأليف أرقام أو أسعار أو أخبار أو أسماء. لو مش متأكد من رقم، متكتبوش. ممنوع ذكر أسعار أو إصدارات متغيرة.
- المشهد الأول هوك صادم أو سؤال فضول في أقل من 12 كلمة، يتكلم عن فايدة أو خطر يخص المشاهد نفسه. بدون "أهلا" وبدون مقدمات.
- بعدها 4 إلى 6 مشاهد: كل مشهد جملة أو جملتين قصار (10 إلى 22 كلمة)، فيها معلومة واحدة واضحة وخطوة عملية لو ينفع.
- المشهد الأخير: خلاصة + دعوة للمتابعة قصيرة، وآخر جملة ترجع للهوك عشان الفيديو يتعاد (لوب).
- ممنوع كلام سياسي أو ديني أو طبي، وممنوع تعليم نصب أو اختراق (الأمان للدفاع بس).
- لا تكرر هذه العناوين: {used}
رجّع JSON فقط بالمفاتيح:
title (عنوان يوتيوب أقل من 60 حرف، فجوة فضول + فايدة، بالمصري),
description (سطرين + كلمة هاشتاج #Shorts #تقني),
tags (8 كلمات),
hook_text (2 إلى 4 كلمات كبيرة تظهر على الشاشة في أول ثانيتين),
scenes (قائمة، كل عنصر: narration بالمصري بدون رموز وبالتشكيل الخفيف لو لازم, on_screen (كلمة إلى 3 كلمات كبار تظهر مع المشهد), keyword (لازم تختار واحدة بالظبط من القائمة دي حسب معنى الجملة: {', '.join(lib_topics()) or 'smartphone'}))."""
    data = gemini(prompt)
    scenes = [s for s in data["scenes"] if s.get("narration", "").strip()]
    if len(scenes) < 4:
        raise ValueError("too few scenes")
    data["scenes"] = scenes
    data["_pillar"] = pillar
    return data


# ---------------------------------------------------------------- voice
async def _tts(text, path):
    for attempt in range(4):
        com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
        words = []
        try:
            with open(path, "wb") as f:
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append((ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7))
            return words
        except Exception as e:
            print(f"[tts retry {attempt + 1}] {type(e).__name__}")
            await asyncio.sleep(5 * (attempt + 1))
    raise RuntimeError("tts failed: " + text[:40])


def dur(path):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(o.strip())


# ---------------------------------------------------------------- visuals
PALETTES = [((8, 12, 40), (0, 120, 255)), ((20, 8, 40), (170, 60, 255)), ((6, 30, 30), (0, 220, 170)),
            ((35, 10, 20), (255, 70, 90)), ((10, 20, 45), (255, 180, 0))]


def bg_image(i, path):
    top, acc = PALETTES[i % len(PALETTES)]
    img = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[k] * (1 - t * .6) + acc[k] * t * .35) for k in range(3)))
    rnd = random.Random(i * 7 + 3)
    for gx in range(0, W + 1, 90):
        d.line([(gx, 0), (gx, H)], fill=tuple(min(255, c + 18) for c in top), width=2)
    for gy in range(0, H + 1, 90):
        d.line([(0, gy), (W, gy)], fill=tuple(min(255, c + 18) for c in top), width=2)
    for _ in range(26):  # circuit nodes
        x, y = rnd.randrange(60, W - 60, 90), rnd.randrange(60, H - 60, 90)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=acc)
        d.line([(x, y), (x + rnd.choice([-1, 1]) * 90 * rnd.randint(1, 3), y)], fill=acc, width=4)
    img.save(path)


CLIPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clips")


def lib():
    p = os.path.join(CLIPDIR, "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def lib_topics():
    return list(lib().keys())


def footage_bg(keyword, d, path, tmp, i):
    """Fast-cut real-footage background of length d from the stock library. Returns True on success."""
    m = lib()
    if not m:
        return False
    kw = (keyword or "").lower().strip()
    topic = kw if kw in m else next((t for t in m if kw and (kw in t or t in kw)), random.choice(list(m)))
    pool = list(m[topic])
    others = [f for t, fs in m.items() if t != topic for f in fs]
    random.shuffle(pool); random.shuffle(others)
    pool += others[:3]
    segs, t, k = [], 0.0, 0
    while t < d - 0.05:
        L = min(random.uniform(1.4, 2.3), d - t)
        if d - t - L < 0.7:
            L = d - t
        f = os.path.join(CLIPDIR, pool[k % len(pool)])
        k += 1
        total = max(dur(f), L + 0.1)
        ss = random.uniform(0, max(0, total - L - 0.05))
        sp = os.path.join(tmp, f"seg{i}_{k}.mp4")
        zoom = random.choice(["1.0", "1.08"])
        vf = (f"scale={W*1.12:.0f}:{H*1.12:.0f}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"eq=brightness=-0.05:contrast=1.08:saturation=1.15,setsar=1,fps=30")
        subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.2f}", "-t", f"{L:.2f}", "-i", f,
                               "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                               "-pix_fmt", "yuv420p", sp])
        segs.append(sp)
        t += L
    lst = os.path.join(tmp, f"segs{i}.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", path])
    return True


def text_png(text, path, size_max=150, y_center=H // 2 - 80, color=(255, 255, 255), stroke=(0, 0, 0)):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    words = text.split()
    size = size_max
    while True:
        f = ImageFont.truetype(ensure_font(), size, layout_engine=ImageFont.Layout.BASIC)
        lines, cur = [], []
        for w in words:
            trial = " ".join(cur + [w])
            if d.textlength(ar(trial), font=f) <= W * 0.86 or not cur:
                cur.append(w)
            else:
                lines.append(" ".join(cur)); cur = [w]
        if cur:
            lines.append(" ".join(cur))
        if (len(lines) <= 3 and max(d.textlength(ar(l), font=f) for l in lines) <= W * 0.9) or size < 56:
            break
        size -= 8
    lh = int(size * 1.55)
    y = y_center - lh * len(lines) // 2
    for l in lines:
        t = ar(l); tw = d.textlength(t, font=f)
        d.text(((W - tw) / 2, y), t, font=f, fill=color, stroke_width=max(6, size // 10), stroke_fill=stroke)
        y += lh
    img.save(path)


def render_scene(i, sc, words, audio_path, d, tmp):
    """Returns path of scene mp4 (video+audio), length d seconds."""
    base = os.path.join(tmp, f"bg{i}")
    clip = base + ".mp4"
    vf_in = []
    if footage_bg(sc.get("keyword", ""), d, clip, tmp, i):
        vf_in = ["-i", clip]
        bgf = "[0:v]setsar=1[bg]"
    else:
        bg_image(i, base + ".png")
        vf_in = ["-loop", "1", "-i", base + ".png"]
        z = "zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=30" % (W, H)
        bgf = f"[0:v]{z},setsar=1[bg]"
    inputs = vf_in
    # on-screen keyword card (top) and caption chunks (center-low)
    overlays = []
    if sc.get("on_screen"):
        p = os.path.join(tmp, f"os{i}.png")
        text_png(sc["on_screen"], p, size_max=120, y_center=330, color=(255, 214, 10), stroke=(20, 20, 20))
        overlays.append((p, 0.0, d))
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[0].endswith(("،", ".", "؟", "!")):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    for k, ch in enumerate(chunks):
        start = ch[0][1]
        end = chunks[k + 1][0][1] if k + 1 < len(chunks) else d
        p = os.path.join(tmp, f"cap{i}_{k}.png")
        text_png(" ".join(w[0] for w in ch), p, size_max=130, y_center=H * 3 // 5 + 90)
        overlays.append((p, start, end))
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs
    for p, _, _ in overlays:
        cmd += ["-i", p]
    cmd += ["-i", audio_path]
    fc = [bgf]
    last = "bg"
    for n, (p, s, e) in enumerate(overlays):
        fc.append(f"[{last}][{n + 1}:v]overlay=0:0:enable='between(t,{s:.2f},{e:.2f})'[o{n}]")
        last = f"o{n}"
    out = os.path.join(tmp, f"scene{i}.mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", f"{len(overlays) + 1}:a",
            "-t", f"{d:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", out]
    subprocess.check_call(cmd)
    return out


def build(data, tmp):
    os.makedirs(tmp, exist_ok=True)
    scenes = data["scenes"][:int(os.getenv("MAXSCENES", "99"))]
    parts = []
    for i, sc in enumerate(scenes):
        if os.getenv('RESUME') and os.path.exists(os.path.join(tmp, f'scene{i}.mp4')):
            parts.append(os.path.join(tmp, f'scene{i}.mp4')); continue
        ap = os.path.join(tmp, f"a{i}.mp3")
        words = asyncio.run(_tts(sc["narration"], ap))
        d = dur(ap) + 0.25
        parts.append(render_scene(i, sc, words, ap, d, tmp))
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = os.path.join(OUT, "short.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    return out


# ---------------------------------------------------------------- upload
def build_description(data):
    d = data.get("description", "").strip()
    if AFF:
        d += "\n\nالروابط في أول تعليق (لينك أفلييت)."
    return d + "\n\n#Shorts #تقني"


def upload(path, data):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaFileUpload
    creds = Credentials.from_authorized_user_info(json.loads(os.environ["YT_TOKEN_JSON"]))
    yt = gbuild("youtube", "v3", credentials=creds)
    title = data["title"][:95]
    desc = build_description(data)
    body = {"snippet": {"title": title, "description": desc, "tags": data.get("tags", [])[:15], "categoryId": "28",
                        "defaultLanguage": "ar", "defaultAudioLanguage": "ar"},
            "status": {"privacyStatus": os.getenv("PRIVACY_STATUS", "public"), "selfDeclaredMadeForKids": False}}
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(path, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    print("uploaded", resp["id"])
    vid = resp["id"]
    if AFF:
        try:
            links = "\n".join(x.strip() for x in AFF.split(",") if x.strip())
            yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid,
                "topLevelComment": {"snippet": {"textOriginal": links + "\nلينك أفلييت"}}}}).execute()
        except Exception as e:  # needs youtube.force-ssl scope; pin by hand in Studio (API cannot pin)
            print("first comment failed:", e)
    return vid


def main():
    tmp = os.path.join(HERE, "tmp")
    os.makedirs(tmp, exist_ok=True)
    cache = os.path.join(tmp, "data.json")
    if os.getenv("RESUME") and os.path.exists(cache):
        data = json.load(open(cache, encoding="utf-8"))
    else:
        data = make_script()
        json.dump(data, open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(data, ensure_ascii=False, indent=1))
    path = build(data, tmp)
    print("video:", path, round(dur(path), 1), "s")
    if os.getenv("DRY_RUN", "1").strip().lower() in ("1", "true"):
        print("dry run: no upload"); return
    today = datetime.datetime.now(CAIRO).date().isoformat()
    if any(h.get("date") == today and h.get("id") for h in load_hist()):
        sys.exit("فيديو النهاردة اترفع بالفعل — قاعدة فيديو واحد في اليوم")
    vid = upload(path, data)
    h = load_hist(); h.append({"date": today, "title": data["title"], "pillar": data.get("_pillar"), "id": vid}); save_hist(h)


if __name__ == "__main__":
    main()
