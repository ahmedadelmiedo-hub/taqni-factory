"""Flat vector scenes for the mascots (Lulu fox, Bibo elephant) and word pictures. Pure PIL, no network, no AI images."""
import math, random, os
from PIL import Image, ImageDraw, ImageFilter
OUT=(60,30,70)
def ell(d,cx,cy,rx,ry,fill,outline=None,w=0):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=fill,outline=outline,width=w)
def fox(S=1.0, scarf=True):
    """fox head+body on transparent 1000x1100 canvas"""
    im=Image.new("RGBA",(1000,1100),(0,0,0,0)); d=ImageDraw.Draw(im)
    O=(255,140,40); D=(215,95,20); Wt=(255,246,232)
    # tail behind
    ell(d,820,930,150,95,O); ell(d,915,900,62,45,Wt)
    # body
    ell(d,500,930,260,230,O); ell(d,500,960,150,170,Wt)
    # ears
    d.polygon([(220,330),(250,40),(450,230)],fill=O); d.polygon([(780,330),(750,40),(550,230)],fill=O)
    d.polygon([(265,280),(280,120),(390,235)],fill=(255,190,170)); d.polygon([(735,280),(720,120),(610,235)],fill=(255,190,170))
    # head
    ell(d,500,440,370,320,O)
    # cheeks white
    ell(d,330,540,190,140,Wt); ell(d,670,540,190,140,Wt); ell(d,500,580,150,110,Wt)
    # eyes
    for x in (360,640):
        ell(d,x,430,62,78,(40,25,40)); ell(d,x+18,405,22,26,(255,255,255)); ell(d,x-14,450,10,10,(255,255,255))
    # blush
    ell(d,255,520,45,28,(255,150,140)); ell(d,745,520,45,28,(255,150,140))
    # nose + mouth
    ell(d,500,520,48,36,(40,25,40))
    d.arc((410,520,500,620),20,160,fill=(40,25,40),width=10); d.arc((500,520,590,620),20,160,fill=(40,25,40),width=10)
    d.pieslice((440,570,560,680),0,180,fill=(200,60,70))
    if not scarf: return im
    # scarf
    d.rounded_rectangle((250,740,750,850),radius=55,fill=(40,130,230)); d.rounded_rectangle((250,740,750,780),radius=20,fill=(90,170,250))
    d.rounded_rectangle((590,800,700,1010),radius=40,fill=(40,130,230))
    return im
def ele(S=1.0):
    im=Image.new("RGBA",(1000,1100),(0,0,0,0)); d=ImageDraw.Draw(im)
    B=(120,190,245); L=(175,220,255); P=(255,170,190)
    ell(d,500,930,250,230,B); ell(d,500,960,150,170,L)
    # ears
    ell(d,200,420,170,220,B); ell(d,200,420,105,150,P); ell(d,800,420,170,220,B); ell(d,800,420,105,150,P)
    # head
    ell(d,500,420,300,300,B)
    # trunk
    d.rounded_rectangle((430,480,570,880),radius=70,fill=B); ell(d,500,880,95,60,B)
    for y in (560,640,720,800): d.arc((430,y-30,570,y+30),0,180,fill=(90,160,220),width=7)
    # eyes
    for x in (390,610):
        ell(d,x,380,48,62,(40,25,40)); ell(d,x+14,360,17,20,(255,255,255))
    ell(d,300,480,38,24,(255,150,160)); ell(d,700,480,38,24,(255,150,160))
    # tusk-free smile
    d.arc((400,520,600,640),15,165,fill=(40,25,40),width=9)
    # bow
    d.polygon([(500,140),(380,60),(380,200)],fill=(255,215,40)); d.polygon([(500,140),(620,60),(620,200)],fill=(255,215,40)); ell(d,500,140,34,34,(240,180,20))
    return im
def outline(im,color=(255,255,255),px=14):
    a=im.split()[3].filter(ImageFilter.MaxFilter(px*2+1))
    bg=Image.new("RGBA",im.size,color+(0,)); bg.putalpha(a)
    o=Image.new("RGBA",im.size,(0,0,0,0)); o.alpha_composite(bg); o.alpha_composite(im); return o

def outline(im, color=(255, 255, 255), px=14):
    a = im.split()[3].filter(ImageFilter.MaxFilter(px * 2 + 1))
    bg = Image.new("RGBA", im.size, color + (0,)); bg.putalpha(a)
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); o.alpha_composite(bg); o.alpha_composite(im); return o

def _canvas(): 
    im = Image.new("RGBA", (800, 800), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)
K = (40, 25, 40)
def _eye(d, x, y, r=26):
    ell(d, x, y, r, r * 1.2, K); ell(d, x + r * .3, y - r * .3, r * .38, r * .38, (255, 255, 255))

def o_rabbit():
    im, d = _canvas(); Wt = (250, 250, 255); P = (255, 175, 195)
    ell(d, 400, 600, 190, 160, Wt); ell(d, 560, 640, 45, 40, (255, 255, 255))
    ell(d, 300, 190, 60, 170, Wt); ell(d, 300, 200, 28, 130, P); ell(d, 500, 190, 60, 170, Wt); ell(d, 500, 200, 28, 130, P)
    ell(d, 400, 400, 190, 170, Wt)
    _eye(d, 335, 380); _eye(d, 465, 380)
    ell(d, 400, 440, 20, 15, (255, 120, 150)); d.arc((360, 440, 400, 490), 10, 150, fill=K, width=6); d.arc((400, 440, 440, 490), 30, 170, fill=K, width=6)
    ell(d, 285, 450, 28, 18, (255, 190, 200)); ell(d, 515, 450, 28, 18, (255, 190, 200))
    return im
def o_duck():
    im, d = _canvas(); Y = (255, 215, 50); Or = (255, 150, 40)
    ell(d, 400, 560, 250, 190, Y); ell(d, 330, 560, 120, 80, (255, 190, 30)); 
    ell(d, 470, 270, 150, 150, Y); d.polygon([(560, 300), (700, 330), (560, 380)], fill=Or)
    _eye(d, 490, 240, 22); ell(d, 440, 330, 28, 18, (255, 170, 120))
    d.polygon([(200, 560), (110, 480), (150, 600)], fill=Y)
    ell(d, 330, 760, 55, 22, Or); ell(d, 470, 760, 55, 22, Or)
    return im
def o_apple():
    im, d = _canvas(); R = (235, 45, 55)
    ell(d, 330, 450, 200, 220, R); ell(d, 470, 450, 200, 220, R); ell(d, 400, 560, 190, 170, R)
    ell(d, 330, 360, 40, 70, (255, 130, 140)); d.rectangle((388, 140, 412, 250), fill=(110, 70, 30))
    d.polygon([(412, 190), (520, 120), (540, 210), (430, 230)], fill=(90, 190, 70))
    return im
def o_banana():
    im, d = _canvas(); Y = (255, 225, 60)
    d.arc((100, 40, 700, 700), 20, 160, fill=Y, width=130); d.arc((100, 40, 700, 700), 20, 160, fill=(255, 205, 40), width=30)
    ell(d, 118, 420, 22, 22, (110, 70, 30)); ell(d, 640, 550, 22, 22, (110, 70, 30))
    return im
def o_star():
    im, d = _canvas(); pts = []
    for i in range(10):
        r = 330 if i % 2 == 0 else 150; a = -math.pi / 2 + i * math.pi / 5
        pts.append((400 + r * math.cos(a), 420 + r * math.sin(a)))
    d.polygon(pts, fill=(255, 215, 40)); _eye(d, 340, 420, 20); _eye(d, 460, 420, 20); d.arc((350, 450, 450, 530), 20, 160, fill=K, width=8)
    return im
def o_ball():
    im, d = _canvas(); ell(d, 400, 420, 300, 300, (255, 90, 90))
    d.pieslice((100, 120, 700, 720), 200, 260, fill=(255, 255, 255)); d.pieslice((100, 120, 700, 720), 20, 80, fill=(255, 255, 255))
    d.pieslice((100, 120, 700, 720), 290, 350, fill=(80, 170, 250)); d.pieslice((100, 120, 700, 720), 110, 170, fill=(80, 170, 250))
    return im
def o_flower():
    im, d = _canvas(); d.rectangle((388, 400, 412, 760), fill=(70, 170, 70)); ell(d, 470, 620, 80, 30, (90, 190, 80))
    for a in range(6): ell(d, 400 + 150 * math.cos(a * 1.047), 300 + 150 * math.sin(a * 1.047), 95, 95, (255, 120, 170))
    ell(d, 400, 300, 90, 90, (255, 215, 50)); _eye(d, 370, 290, 14); _eye(d, 430, 290, 14); d.arc((365, 310, 435, 350), 20, 160, fill=K, width=6)
    return im
def o_fish():
    im, d = _canvas(); B = (80, 170, 250)
    ell(d, 340, 400, 270, 190, B); d.polygon([(560, 400), (730, 250), (730, 550)], fill=(60, 140, 230)); ell(d, 300, 430, 120, 90, (140, 205, 255))
    _eye(d, 190, 360, 30); d.arc((120, 410, 220, 480), 20, 160, fill=K, width=8)
    return im
def o_cat():
    im, d = _canvas(); G = (150, 150, 170)
    d.polygon([(190, 300), (200, 80), (350, 220)], fill=G); d.polygon([(610, 300), (600, 80), (450, 220)], fill=G)
    ell(d, 400, 440, 250, 220, G); ell(d, 400, 520, 150, 110, (235, 235, 245))
    _eye(d, 315, 400); _eye(d, 485, 400); ell(d, 400, 470, 22, 16, (255, 130, 150))
    for y in (480, 510):
        d.line((250, y, 130, y - 20), fill=K, width=5); d.line((550, y, 670, y - 20), fill=K, width=5)
    d.arc((360, 480, 400, 530), 10, 150, fill=K, width=6); d.arc((400, 480, 440, 530), 30, 170, fill=K, width=6)
    return im
def o_tree():
    im, d = _canvas(); d.rectangle((350, 450, 450, 780), fill=(140, 90, 50))
    for (x, y, r) in [(400, 230, 190), (270, 360, 150), (530, 360, 150)]: ell(d, x, y, r, r, (70, 180, 80))
    return im
def o_sun():
    im, d = _canvas()
    for a in range(12): 
        x, y = 400 + 340 * math.cos(a * .5236), 400 + 340 * math.sin(a * .5236); ell(d, x, y, 28, 28, (255, 190, 40))
    ell(d, 400, 400, 230, 230, (255, 215, 50)); _eye(d, 330, 370, 22); _eye(d, 470, 370, 22); d.arc((330, 410, 470, 520), 20, 160, fill=K, width=9)
    return im
def o_house():
    im, d = _canvas(); d.rectangle((150, 360, 650, 740), fill=(255, 200, 120)); d.polygon([(100, 380), (400, 120), (700, 380)], fill=(220, 80, 70))
    d.rectangle((340, 520, 460, 740), fill=(120, 80, 50)); d.rectangle((190, 440, 290, 540), fill=(160, 215, 255)); d.rectangle((510, 440, 610, 540), fill=(160, 215, 255))
    return im
def o_heart():
    im, d = _canvas(); ell(d, 290, 300, 150, 150, (240, 70, 110)); ell(d, 510, 300, 150, 150, (240, 70, 110))
    d.polygon([(160, 370), (640, 370), (400, 700)], fill=(240, 70, 110)); _eye(d, 340, 400, 20); _eye(d, 460, 400, 20); d.arc((350, 430, 450, 500), 20, 160, fill=K, width=8)
    return im
def o_car():
    im, d = _canvas(); d.rounded_rectangle((70, 380, 730, 600), radius=60, fill=(235, 70, 70)); d.rounded_rectangle((200, 230, 600, 400), radius=70, fill=(235, 70, 70))
    d.rounded_rectangle((235, 260, 390, 385), radius=25, fill=(170, 220, 255)); d.rounded_rectangle((410, 260, 565, 385), radius=25, fill=(170, 220, 255))
    for x in (230, 570): ell(d, x, 610, 80, 80, K); ell(d, x, 610, 36, 36, (200, 200, 210))
    return im
def o_fox():
    im = fox(scarf=False); return im.resize((800, 880)).crop((0, 0, 800, 800)) if False else im.resize((730, 803))

OBJ = {"rabbit": o_rabbit, "duck": o_duck, "apple": o_apple, "banana": o_banana, "star": o_star, "ball": o_ball, "flower": o_flower, "fish": o_fish,
       "cat": o_cat, "tree": o_tree, "sun": o_sun, "house": o_house, "heart": o_heart, "car": o_car, "fox": o_fox}
# Arabic word -> object (checked first, so the picture always matches the printed word)
AR = {"أرنب": "rabbit", "ارنب": "rabbit", "بطة": "duck", "بط": "duck", "تفاح": "apple", "تفاحة": "apple", "ثعلب": "fox", "موز": "banana", "نجمة": "star",
      "كرة": "ball", "زهرة": "flower", "وردة": "flower", "سمكة": "fish", "قطة": "cat", "شجرة": "tree", "شمس": "sun", "بيت": "house", "قلب": "heart", "سيارة": "car"}
def pick_obj(on_screen, obj=None):
    for w, k in AR.items():
        if w in (on_screen or ""): return k
    return obj if obj in OBJ else "star"

def _bg(idx, W, H):
    S = 2; w, h = W * S, H * S
    pal = [((120, 190, 255), (210, 240, 255)), ((255, 200, 220), (255, 240, 235)), ((150, 220, 200), (235, 255, 240)), ((255, 225, 150), (255, 248, 220))][idx % 4]
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h; d.line((0, y, w, y), fill=tuple(int(pal[0][i] + (pal[1][i] - pal[0][i]) * t) for i in range(3)))
    im = im.convert("RGBA"); d = ImageDraw.Draw(im)
    ell(d, w * (.15 + .7 * ((idx * 37) % 10) / 10), h * .17, 110, 110, (255, 225, 90))
    for (x, y, s) in [(.2, .2, 1.0), (.62, .12, .8), (.88, .3, .7)]:
        for dx, dy, r in [(0, 0, 60), (70, -25, 80), (150, 0, 60), (80, 25, 70)]:
            ell(d, w * x + dx * s * S / 1.5, h * y + dy * s * S / 1.5, r * s, r * s * .75, (255, 255, 255, 235))
    g = [(110, 205, 100), (90, 190, 90), (130, 215, 110)]
    d.ellipse((-w * .2, h * .72, w * .7, h * 1.5), fill=g[0]); d.ellipse((w * .4, h * .78, w * 1.3, h * 1.6), fill=g[1]); d.ellipse((w * .1, h * .86, w * .9, h * 1.7), fill=g[2])
    r = random.Random(idx + 3)
    for _ in range(26):
        x = r.randint(0, w); y = r.randint(int(h * .86), int(h * .98))
        for a in range(5): ell(d, x + 12 * math.cos(a * 1.256), y + 12 * math.sin(a * 1.256), 8, 8, r.choice([(255, 120, 160), (255, 255, 255), (255, 210, 60)]))
        ell(d, x, y, 6, 6, (255, 200, 40))
    return im

def _fit(im, height):
    return im.resize((int(im.width * height / im.height), height), Image.LANCZOS)

def vector_scene(idx, on_screen, obj, count, path, W=1280, H=720, who=None, big=False):
    """Writes path (composite jpg), path+'.bg.png', path+'.fg.png' (mascot+object layer, same size as bg)."""
    S = 2; w, h = W * S, H * S
    bg = _bg(idx, W, H)
    fg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    key = pick_obj(on_screen, obj); n = max(1, min(int(count or 1), 5))
    who = who or ("fox" if idx % 2 == 0 else "ele")
    m = outline((fox() if who == "fox" else ele()), px=14)
    mh = int(h * (0.78 if big else 0.6)); m = _fit(m, mh)
    left = (idx % 3 != 1)
    mx = int(w * .03) if left else w - m.width - int(w * .03)
    fg.alpha_composite(m, (mx, h - mh - int(h * .12)))
    base = OBJ[key]()
    base = outline(base, px=12)
    oh = int(h * (0.6 if n == 1 else 0.36)); o = _fit(base, oh)
    area_x0 = mx + m.width + int(w * .03) if left else int(w * .04)
    area_x1 = w - int(w * .04) if left else mx - int(w * .03)
    step = (area_x1 - area_x0) / n if n > 1 else (area_x1 - area_x0)
    for i in range(n):
        cx = area_x0 + step * (i + .5)
        fg.alpha_composite(o, (int(cx - o.width / 2), int(h * (.62 if n == 1 else .6)) - o.height // 2))
    # keep everything inside the central 80% (the parallax camera zooms 1.25x) and above the caption bar
    inner = fg.resize((int(w * .76), int(h * .76)), Image.LANCZOS); fg = Image.new("RGBA", (w, h), (0, 0, 0, 0)); fg.alpha_composite(inner, (int(w * .12), int(h * .07)))
    comp = bg.copy(); comp.alpha_composite(fg)
    bgS = bg.resize((W, H), Image.LANCZOS); fgS = fg.resize((W, H), Image.LANCZOS); cS = comp.resize((W, H), Image.LANCZOS)
    cS.convert("RGB").save(path, quality=93); bgS.convert("RGB").save(path + ".bg.png"); fgS.save(path + ".fg.png")
    return path
