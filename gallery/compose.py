from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps
import math, os
import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    return get_display(arabic_reshaper.reshape(text))

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 769
NAVY_TOP = (10, 24, 42)
NAVY_BOT = (20, 46, 74)
GOLD = (216, 186, 118)
CREAM = (244, 236, 216)
MUT = (168, 184, 201)
DARK = (6, 14, 24)

F_HEAD = os.path.join("C:\\Windows\\Fonts", "cambriab.ttf")
F_BODY = os.path.join("C:\\Windows\\Fonts", "constan.ttf")
F_UI = os.path.join("C:\\Windows\\Fonts", "segoeuib.ttf")
F_AR = os.path.join("C:\\Windows\\Fonts", "trado.ttf")


def vgrad(size, top, bot):
    w, h = size
    grad = Image.new("RGB", (1, h))
    px = grad.load()
    for y in range(h):
        t = y / (h - 1)
        t = t ** 1.25
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


def paper_fibers(size, seed=7):
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
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return layer


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
    base.alpha_composite(sh, (round(center[0] - sh.width / 2) + 4,
                              round(center[1] - sh.height / 2) + 22))
    base.alpha_composite(rot, (round(center[0] - rot.width / 2),
                               round(center[1] - rot.height / 2)))
    return rot.size


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, maxw, minsize=18):
    s = size
    while s > minsize:
        f = font(path, s)
        if draw.textlength(text, font=f) <= maxw:
            return f
        s -= 2
    return font(path, minsize)


def tracked(draw, xy, text, f, color, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=color)
        x += draw.textlength(ch, font=f) + spacing
    return x


def chip(draw, xy, text, f, fg=CREAM, border=(216, 186, 118, 110)):
    tw = draw.textlength(text, font=f)
    w = tw + 34
    h = 34
    draw.rounded_rectangle([xy[0], xy[1], xy[0] + w, xy[1] + h], radius=17,
                           outline=border, width=1)
    draw.text((xy[0] + 17, xy[1] + 9), text, font=f, fill=fg)
    return w


def bg():
    base = vgrad((W, H), NAVY_TOP, NAVY_BOT)
    base.alpha_composite(radial_glow((W, H), (990, 360), 620, (46, 92, 140), 0.55))
    base.alpha_composite(radial_glow((W, H), (430, 120), 460, (58, 86, 120), 0.22))
    base.alpha_composite(paper_fibers((W, H)))
    base.alpha_composite(vignette((W, H)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([26, 26, W - 26, H - 26], radius=4, outline=(216, 186, 118, 80), width=1)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=3, outline=(216, 186, 118, 34), width=1)
    return base


def wordmark(base, x=72, y=64):
    d = ImageDraw.Draw(base)
    # tiny cartouche glyph
    d.rounded_rectangle([x, y + 2, x + 34, y + 20], radius=9, outline=GOLD, width=2)
    d.line([x + 26, y + 3, x + 26, y + 19], fill=GOLD, width=1)
    f = font(F_UI, 15)
    tracked(d, (x + 48, y + 2), "NAMES OF EGYPT", f, GOLD, 2.6)


def kicker(d, x, y, text):
    f = font(F_UI, 14)
    tracked(d, (x, y), text, f, (216, 186, 118), 3.0)


def body_lines(d, x, y, lines, size=19, lh=31, color=MUT):
    f = font(F_BODY, size)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=color)
    return y + len(lines) * lh


def card_shadow_floor(base, cx, cy, w):
    # soft warm pool of light under the arrangement
    glow = radial_glow((W, H), (cx, cy), w * 0.85, (120, 96, 40), 0.30)
    base.alpha_composite(glow)


def compose_one():
    base = bg()
    wordmark(base)
    d = ImageDraw.Draw(base)
    kicker(d, 72, 128, "PERSONALISED CARDS")
    f1 = fit(d, "Your name,", F_HEAD, 58, 470)
    f2 = fit(d, "in hieroglyphs.", F_HEAD, 58, 470)
    d.text((72, 160), "Your name,", font=f1, fill=CREAM)
    d.text((72, 226), "in hieroglyphs.", font=f2, fill=GOLD)
    body_lines(d, 72, 322, [
        "See your name in hieroglyphs, Coptic,",
        "English and Arabic — a museum-style",
        "keepsake, made in minutes.",
    ], 19, 31)
    fy = 448
    x = 72
    for t in ["PNG · 300 DPI", "Any name", "Ready to print"]:
        x += chip(d, (x, fy), t, font(F_UI, 14)) + 10
    d.line([72, 522, 116, 522], fill=(216, 186, 118, 120), width=1)
    d.text((72, 540), "Designed in Egypt · Delivered as a high-resolution file",
           font=font(F_BODY, 17), fill=(150, 168, 187))
    d.text((72, 578), ar("اسمك بالهيروغليفية والقبطية والعربية"),
           font=font(F_AR, 22), fill=(198, 172, 112))

    card_shadow_floor(base, 975, 390, 430)
    paste_card(base, os.path.join(HERE, "cards", "mina-papyrus.png"), 380, (970, 378), -5)
    return base


def compose_two():
    base = bg()
    wordmark(base)
    d = ImageDraw.Draw(base)
    kicker(d, 72, 128, "FOUR SCRIPTS, ONE NAME")
    f1 = fit(d, "One name.", F_HEAD, 58, 470)
    f2 = fit(d, "Four ways to write it.", F_HEAD, 56, 470)
    d.text((72, 160), "One name.", font=f1, fill=CREAM)
    d.text((72, 226), "Four ways to write it.", font=f2, fill=GOLD)
    y = body_lines(d, 72, 322, [
        "Every card carries the hieroglyphic",
        "spelling, the Coptic letters, the English",
        "form and the Arabic name — side by side.",
    ], 19, 31)
    labels = [("Hieroglyphs", "\u2c98\u2c9b\u2ca0"), ("Coptic", "\u2c8e\u2c93\u2ca1"),
              ("English", "MARY"), ("Arabic", "\u0645\u0631\u064a\u0645")]
    yy = 470
    d.text((72, yy), "SHOWN ON EACH CARD", font=font(F_UI, 12), fill=(150, 168, 187))
    d.text((72, yy + 26), "Hieroglyphs · Coptic · English · Arabic",
           font=font(F_BODY, 19), fill=CREAM)
    d.text((72, 545), "Curated spellings · Portrait & landscape · Print or share",
           font=font(F_BODY, 17), fill=(150, 168, 187))

    card_shadow_floor(base, 950, 400, 470)
    paste_card(base, os.path.join(HERE, "cards", "bishoy-lapis.png"), 305, (780, 392), 7)
    paste_card(base, os.path.join(HERE, "cards", "mariam-gold.png"), 285, (1075, 372), -6)
    return base


def compose_three():
    base = bg()
    wordmark(base)
    d = ImageDraw.Draw(base)
    kicker(d, 72, 128, "FOR CHURCH & FAMILY")
    f1 = fit(d, "A gift that", F_HEAD, 58, 470)
    f2 = fit(d, "carries a name.", F_HEAD, 58, 470)
    d.text((72, 160), "A gift that", font=f1, fill=CREAM)
    d.text((72, 226), "carries a name.", font=f2, fill=GOLD)
    body_lines(d, 72, 322, [
        "Baptisms, ordinations, name days and",
        "church feasts — a personal keepsake",
        "rooted in Egypt's oldest script.",
    ], 19, 31)

    f = font(F_BODY, 18)
    items = ["Baptism & confirmation", "Ordination & monastic vows", "Name days & church feasts"]
    for i, it in enumerate(items):
        yy = 452 + i * 34
        d.line([72, yy + 9, 86, yy + 9], fill=GOLD, width=1)
        d.text((96, yy), it, font=f, fill=CREAM)

    badge_f = font(F_UI, 14)
    bw = d.textlength("PERSONAL & CHURCH USE", font=badge_f) + 40
    d.rounded_rectangle([72, 566, 72 + bw, 602], radius=18,
                        outline=(216, 186, 118, 130), width=1)
    d.text((92, 576), "PERSONAL & CHURCH USE", font=badge_f, fill=GOLD)

    card_shadow_floor(base, 975, 400, 470)
    paste_card(base, os.path.join(HERE, "cards", "mina-papyrus.png"), 290, (760, 402), -7)
    paste_card(base, os.path.join(HERE, "cards", "mariam-gold.png"), 310, (1060, 388), 6)
    return base


if __name__ == "__main__":
    for i, fn in enumerate([compose_one, compose_two, compose_three], 1):
        im = fn().convert("RGB")
        out = os.path.join(HERE, "fiverr-%d.png" % i)
        im.save(out, "PNG", optimize=True)
        print(out, im.size, round(os.path.getsize(out) / 1048576, 2), "MB")
