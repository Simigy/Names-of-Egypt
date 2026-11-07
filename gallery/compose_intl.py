from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os
import arabic_reshaper
from bidi.algorithm import get_display

def ar(t):
    return get_display(arabic_reshaper.reshape(t))

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 769
NAVY_TOP = (10, 24, 42)
NAVY_BOT = (20, 46, 74)
GOLD = (216, 186, 118)
CREAM = (244, 236, 216)
MUT = (168, 184, 201)
DARK = (6, 14, 24)

F_HEAD = r"C:\Windows\Fonts\cambriab.ttf"
F_BODY = r"C:\Windows\Fonts\constan.ttf"
F_UI = r"C:\Windows\Fonts\segoeuib.ttf"
F_AR = r"C:\Windows\Fonts\trado.ttf"

def vgrad(size, top, bot):
    w, h = size
    grad = Image.new("RGB", (1, h))
    px = grad.load()
    for y in range(h):
        t = (y / (h - 1)) ** 1.25
        px[0, y] = tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return grad.resize(size, Image.BILINEAR).convert("RGBA")

def radial_glow(size, center, radius, color, strength):
    w, h = size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    steps = 46
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        a = int(255 * strength * (1 - t) ** 2)
        d.ellipse([center[0] - r, center[1] - r * 0.92, center[0] + r, center[1] + r * 0.92], fill=a)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.16))
    g = Image.new("RGBA", size, color + (0,))
    g.putalpha(layer)
    return g

def vignette(size):
    w, h = size
    v = Image.radial_gradient("L").resize((w, h), Image.BILINEAR)
    v = v.point(lambda x: int(max(0, x - 120) * 0.9))
    g = Image.new("RGBA", size, DARK + (0,))
    g.putalpha(v)
    return g

def fibers(size, seed=7):
    import random
    rnd = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(150):
        y = rnd.uniform(0, h)
        x0 = rnd.uniform(-100, w)
        ln = rnd.uniform(80, 420)
        a = rnd.randint(4, 12)
        c = (216, 186, 118, a) if rnd.random() < 0.55 else (255, 255, 255, max(2, a - 3))
        d.line([(x0, y), (x0 + ln, y + rnd.uniform(-3, 3))], fill=c, width=1)
    return layer.filter(ImageFilter.GaussianBlur(0.6))

def bg():
    base = vgrad((W, H), NAVY_TOP, NAVY_BOT)
    base.alpha_composite(radial_glow((W, H), (990, 360), 620, (46, 92, 140), 0.55))
    base.alpha_composite(radial_glow((W, H), (430, 120), 460, (58, 86, 120), 0.22))
    base.alpha_composite(fibers((W, H)))
    base.alpha_composite(vignette((W, H)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([26, 26, W - 26, H - 26], radius=4, outline=(216, 186, 118, 80), width=1)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=3, outline=(216, 186, 118, 34), width=1)
    return base

def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m

def paste_card(base, path, width, center, angle, radius=9, shadow=0.55):
    im = Image.open(path).convert("RGBA")
    h = round(width * im.height / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), rounded_mask(im.size, radius)))
    rot = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    a = rot.getchannel("A")
    sh = Image.new("RGBA", rot.size, (3, 9, 18, 0))
    sh.putalpha(a.point(lambda v: int(v * shadow)))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    base.alpha_composite(sh, (round(center[0] - sh.width / 2) + 4, round(center[1] - sh.height / 2) + 22))
    base.alpha_composite(rot, (round(center[0] - rot.width / 2), round(center[1] - rot.height / 2)))
    return rot.size

def font(p, s):
    return ImageFont.truetype(p, s)

def tracked(d, xy, text, f, color, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + spacing
    return x

def chip(d, xy, text, f, fg=CREAM, border=(216,186,118,110)):
    tw = d.textlength(text, font=f)
    w = tw + 34
    d.rounded_rectangle([xy[0], xy[1], xy[0]+w, xy[1]+34], radius=17, outline=border, width=1)
    d.text((xy[0]+17, xy[1]+9), text, font=f, fill=fg)
    return w

def wordmark(base, x=72, y=64):
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x, y+2, x+34, y+20], radius=9, outline=GOLD, width=2)
    d.line([x+26, y+3, x+26, y+19], fill=GOLD, width=1)
    tracked(d, (x+48, y+2), "NAMES OF EGYPT", font(F_UI, 15), GOLD, 2.6)

def kicker(d, x, y, text):
    tracked(d, (x, y), text, font(F_UI, 14), (216,186,118), 3.0)

def body_lines(d, x, y, lines, size=19, lh=31, color=MUT):
    f = font(F_BODY, size)
    for i, ln in enumerate(lines):
        d.text((x, y+i*lh), ln, font=f, fill=color)
    return y + len(lines)*lh

def fit(d, text, path, size, maxw, minsize=18):
    s = size
    while s > minsize:
        f = font(path, s)
        if d.textlength(text, font=f) <= maxw:
            return f
        s -= 2
    return font(path, minsize)

def compose_common(lang):
    base = bg()
    wordmark(base)
    d = ImageDraw.Draw(base)
    TXT = {
        "en": {
            "kicker": "PERSONALISED CARDS",
            "h1": "Your name,",
            "h2": "in hieroglyphs.",
            "body": ["See your name in hieroglyphs, Coptic,", "English and Arabic — a museum-style", "keepsake, made in minutes."],
            "chips": ["PNG · 300 DPI", "Any name", "Ready to print"],
            "sub1": "Designed in Egypt · Delivered as a high-resolution file",
            "sub2": "اسمك بالهيروغليفية والقبطية والعربية",
            "price": "From $10 · Print $20 · Family $35",
        },
        "fr": {
            "kicker": "CARTES PERSONNALISÉES",
            "h1": "Votre nom,",
            "h2": "en hiéroglyphes.",
            "body": ["Voyez votre nom en hiéroglyphes, copte,", "anglais et arabe — une pièce de", "collection style musée, en minutes."],
            "chips": ["PNG · 300 DPI", "Tous les noms", "Prêt à imprimer"],
            "sub1": "Conçu en Égypte · Livré en haute résolution",
            "sub2": "اسمك بالهيروغليفية والقبطية والعربية",
            "price": "À partir de 10 $ · Impression 20 $ · Famille 35 $",
        },
        "de": {
            "kicker": "PERSONALISIERTE KARTEN",
            "h1": "Dein Name,",
            "h2": "in Hieroglyphen.",
            "body": ["Sieh deinen Namen in Hieroglyphen, Koptisch,", "Englisch und Arabisch — ein", "Erinnerungsstück, in wenigen Minuten."],
            "chips": ["PNG · 300 DPI", "Jeder Name", "Druckfertig"],
            "sub1": "Gestaltet in Ägypten · Als hochauflösende Datei",
            "sub2": "اسمك بالهيروغليفية والقبطية والعربية",
            "price": "Ab 10 $ · Druck 20 $ · Familie 35 $",
        },
    }[lang]

    kicker(d, 72, 128, TXT["kicker"])
    f1 = fit(d, TXT["h1"], F_HEAD, 58, 470)
    f2 = fit(d, TXT["h2"], F_HEAD, 58, 470)
    d.text((72, 160), TXT["h1"], font=f1, fill=CREAM)
    d.text((72, 226), TXT["h2"], font=f2, fill=GOLD)
    body_lines(d, 72, 322, TXT["body"], 18, 31)
    fy = 448
    x = 72
    for t in TXT["chips"]:
        x += chip(d, (x, fy), t, font(F_UI, 14)) + 10
    d.line([72, 512, 116, 512], fill=(216,186,118,120), width=1)
    d.text((72, 530), TXT["sub1"], font=font(F_BODY, 17), fill=(150,168,187))
    d.text((72, 564), TXT["price"], font=font(F_UI, 16), fill=GOLD)
    # Arabic accent small
    d.text((72, 594), ar(TXT["sub2"]), font=font(F_AR, 20), fill=(198,172,112))

    # right card
    glow = radial_glow((W,H), (975,390), 430*0.85, (120,96,40), 0.30)
    base.alpha_composite(glow)
    paste_card(base, os.path.join(HERE, "cards", "mina-papyrus.png"), 380, (970, 378), -5)
    return base

if __name__ == "__main__":
    import sys
    for lang in ["en", "fr", "de"]:
        im = compose_common(lang).convert("RGB")
        out = os.path.join(HERE, f"fiverr-{lang}.png")
        im.save(out, "PNG", optimize=True)
        print(out, im.size, round(os.path.getsize(out)/1048576,2), "MB")
