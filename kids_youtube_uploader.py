"""Kids story bot: story -> edge-tts voice -> Pexels visuals -> moviepy video -> YouTube (made for kids) + linked Short."""
import asyncio, json, os, random, sys, requests
import edge_tts
from moviepy.editor import (VideoFileClip, AudioFileClip, ColorClip, concatenate_videoclips)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from kids_story_generator import generate_story

VOICE = os.getenv("TTS_VOICE", "ar-EG-SalmaNeural")   # or ar-SA-ZariyahNeural, ar-EG-ShakirNeural
RATE = os.getenv("TTS_RATE", "-10%")                  # slower = better for kids
PRIVACY = os.getenv("PRIVACY_STATUS", "public")       # public / unlisted / private
MAKE_SHORT = os.getenv("MAKE_SHORT", "true").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"  # build video, skip upload
PEXELS = os.environ["PEXELS_API_KEY"]
OUT = "out"
os.makedirs(OUT, exist_ok=True)


async def _tts(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)


def fetch_clips(keywords, n=8):
    paths = []
    for kw in (keywords * 2)[:n]:
        try:
            r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": PEXELS},
                             params={"query": kw, "per_page": 5, "orientation": "landscape"}, timeout=30)
            vids = r.json().get("videos", [])
            if not vids:
                continue
            v = random.choice(vids)
            files = sorted([f for f in v["video_files"] if f.get("width") and f["width"] <= 1920],
                           key=lambda f: -f["width"])
            f = next((x for x in files if x["width"] <= 1280), files[0])
            p = f"{OUT}/clip{len(paths)}.mp4"
            with open(p, "wb") as fh:
                fh.write(requests.get(f["link"], timeout=120).content)
            paths.append(p)
        except Exception as e:
            print("pexels:", kw, e)
    return paths


def cover(clip, w, h):
    clip = clip.resize(height=h) if clip.w / clip.h < w / h else clip.resize(width=w)
    return clip.crop(x_center=clip.w / 2, y_center=clip.h / 2, width=w, height=h)


def build_video(audio_path, clip_paths, w, h, out, max_dur=None):
    audio = AudioFileClip(audio_path)
    dur = min(audio.duration, max_dur) if max_dur else audio.duration
    audio = audio.subclip(0, dur)
    parts, total, i = [], 0, 0
    while total < dur:
        if clip_paths:
            c = VideoFileClip(clip_paths[i % len(clip_paths)]).without_audio()
            c = cover(c.subclip(0, min(c.duration, 8)), w, h)
        else:
            c = ColorClip((w, h), color=(255, 200, 80), duration=8)
        parts.append(c); total += c.duration; i += 1
    v = concatenate_videoclips(parts).subclip(0, dur).set_audio(audio)
    v.write_videofile(out, fps=24, codec="libx264", audio_codec="aac", preset="veryfast", logger=None)
    return dur


def youtube():
    creds = Credentials.from_authorized_user_info(json.loads(os.environ["YT_TOKEN_JSON"]))
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def upload(yt, path, title, desc, tags):
    body = {"snippet": {"title": title[:100], "description": desc, "tags": tags, "categoryId": "27",
                        "defaultLanguage": "ar", "defaultAudioLanguage": "ar"},
            # selfDeclaredMadeForKids is the writable field (madeForKids is read-only and derived from it).
            "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": True}}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(path, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


def main():
    d = generate_story()
    title, story = d["title"], d["story"]
    tags = [t for t in d.get("tags", [])][:12] + ["قصص أطفال", "kids stories"]
    print("Story:", title)
    asyncio.run(_tts(story, f"{OUT}/voice.mp3"))
    clips = fetch_clips(d.get("visual_keywords") or ["nature", "garden", "animals"])
    build_video(f"{OUT}/voice.mp3", clips, 1280, 720, f"{OUT}/story.mp4")
    if MAKE_SHORT:
        build_video(f"{OUT}/voice.mp3", clips, 720, 1280, f"{OUT}/short.mp4", max_dur=55)
    if DRY_RUN:
        print("DRY_RUN: skipping upload"); return
    yt = youtube()
    vid = upload(yt, f"{OUT}/story.mp4", title, d["description"] + "\n\nاشترك في القناة لقصص جديدة كل يوم 🌟", tags)
    url = f"https://www.youtube.com/watch?v={vid}"
    print("Uploaded:", url)
    if MAKE_SHORT:
        sid = upload(yt, f"{OUT}/short.mp4", f"{title} #Shorts",
                     f"{d['description']}\n\nالقصة كاملة: {url}\n#Shorts #قصص_أطفال", tags + ["Shorts"])
        print("Short:", f"https://www.youtube.com/shorts/{sid}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", e); sys.exit(1)
