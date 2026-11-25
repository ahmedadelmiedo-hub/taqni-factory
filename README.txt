# بوت قصص الأطفال 🧒📚

بوت بيكتب قصة أطفال بالعربي (Gemini)، يقراها بصوت (edge-tts)، يركب فيديو بخلفيات من Pexels، ويرفعه على يوتيوب **كمحتوى مخصص للأطفال** + Short مربوط بيه. كل 6 ساعات أوتوماتيك.

## 1) الريبو
1. اعمل ريبو جديد على GitHub وارفع كل الملفات دي (مع فولدر `.github`).
2. ملحوظة: الريبو الـprivate ليه حوالي 2000 دقيقة تشغيل مجانية في الشهر، والتشغيل كل 6 ساعات (حوالي 120 تشغيلة × 10-20 دقيقة) ممكن يخلصها. الريبو public تشغيله مجاني. لو private خليه كل 12 أو 24 ساعة.

## 2) الـSecrets
من Settings → Secrets and variables → Actions → New repository secret:
- `GEMINI_API_KEY` من aistudio.google.com/apikey
- `PEXELS_API_KEY` من pexels.com/api (مجاني)
- `YT_TOKEN_JSON` (الخطوة الجاية)

## 3) توكن يوتيوب (للقناة الجديدة)
1. في Google Cloud Console اعمل مشروع، فعّل **YouTube Data API v3**.
2. APIs & Services → Credentials → Create OAuth client ID → نوع **Desktop app**، نزّل ملف `client_secret.json`. من OAuth consent screen ضيف إيميلك Test user.
3. على جهازك شغل:
```
pip install google-auth-oauthlib
python get_token.py
```
واختار **القناة الجديدة** (Brand account) وقت تسجيل الدخول. هيطلعلك `token.json`.
4. انسخ محتوى `token.json` كله وحطه في secret اسمه `YT_TOKEN_JSON`.
5. تنبيه: المشروع لو في وضع Testing التوكن بيموت بعد 7 أيام. اعمل Publish للتطبيق (In production) من OAuth consent screen عشان يفضل شغال.
6. تنبيه: المشاريع الجديدة ممكن الفيديوهات تتقفل private لحد ما تعمل audit لـ API. لو حصل، قدّم طلب الـaudit من نموذج يوتيوب.

## 4) أول تشغيل
Actions → Kids Story Publisher → Run workflow → اختار `dry_run = true` تجرب بدون رفع، وحمّل الفيديو من Artifacts وشوفه. بعدها شغله عادي.

## 5) تغيير الإعدادات
- **الجدول:** عدّل سطر `cron` في `.github/workflows/kids-publisher.yml` (مثلا `0 */12 * * *` كل 12 ساعة).
- **الصوت:** Settings → Variables → `TTS_VOICE` مثلا `ar-SA-ZariyahNeural` أو `ar-EG-ShakirNeural`. `TTS_RATE` للسرعة (`-10%` أبطأ).
- **الخصوصية:** متغير `PRIVACY_STATUS` (`public` / `unlisted` / `private`).
- **القصص:** عدّل الـprompt وقوائم القيم والأبطال في `kids_story_generator.py`.

## ملاحظات مهمة
- كل فيديو بيتعلّم تلقائي "Made for kids" (`selfDeclaredMadeForKids`). ده إجباري ومتشالش.
- محتوى الأطفال على يوتيوب مالوش تعليقات ولا إشعارات، وده طبيعي.
- راجع أول كام فيديو بنفسك قبل ما تسيبه على الأوتوماتيك.
