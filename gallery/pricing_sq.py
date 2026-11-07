from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
import arabic_reshaper
from bidi.algorithm import get_display

def ar(t):
    return get_display(arabic_reshaper.reshape(t))

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1080
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

INSTA = "01273546616"
VF = "01003677386"

def vgrad(size, top, bot):
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = (y / (h - 1)) ** 1.25
        px[0, y] = tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return g.resize(size, Image.BILINEAR).convert("RGBA")

def radial_glow(size, center, radius, color, strength):
    w, h = size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    steps = 40
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
    for _ in range(160):
        y = rnd.uniform(0, h)
        x0 = rnd.uniform(-100, w)
        ln = rnd.uniform(90, 450)
        a = rnd.randint(4, 12)
        c = (216, 186, 118, a) if rnd.random() < 0.55 else (255, 255, 255, max(2, a - 3))
        d.line([(x0, y), (x0 + ln, y + rnd.uniform(-3, 3))], fill=c, width=1)
    return layer.filter(ImageFilter.GaussianBlur(0.6))

def bg():
    base = vgrad((W, H), NAVY_TOP, NAVY_BOT)
    base.alpha_composite(radial_glow((W, H), (540, 560), 720, (46, 92, 140), 0.45))
    base.alpha_composite(fibers((W, H)))
    base.alpha_composite(vignette((W, H)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([26, 26, W - 26, H - 26], radius=4, outline=(216, 186, 118, 80), width=1)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=3, outline=(216, 186, 118, 34), width=1)
    return base

def font(p, s):
    return ImageFont.truetype(p, s)

def tracked(d, xy, text, f, color, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + spacing
    return x

def center_ar(d, cx, y, text, f, color):
    t = ar(text)
    w = d.textlength(t, font=f)
    d.text((cx - w / 2, y), t, font=f, fill=color)
    return w

def center_en(d, cx, y, text, f, color, spacing=0):
    if spacing > 0:
        total = 0
        for ch in text:
            total += d.textlength(ch, font=f) + spacing
        total -= spacing
        x = cx - total / 2
        tracked(d, (x, y), text, f, color, spacing)
    else:
        w = d.textlength(text, font=f)
        d.text((cx - w / 2, y), text, font=f, fill=color)

def main():
    base = bg()
    d = ImageDraw.Draw(base)

    d.rounded_rectangle([54, 40, 54 + 34, 40 + 20], radius=9, outline=GOLD, width=2)
    d.line([54 + 26, 41, 54 + 26, 58], fill=GOLD, width=1)
    tracked(d, (54 + 48, 42), "NAMES OF EGYPT", font(F_UI, 15), GOLD, 2.6)

    center_en(d, 540, 78, "PRICE LIST · EGYPT", font(F_UI, 13), GOLD, 3)
    center_ar(d, 540, 100, "أسعار البطاقات في مصر", font(F_AR, 40), CREAM)

    # launch ribbon
    def pill(cx, y, text, f, fg=None, w_pad=18, h_pad=8):
        t = ar(text) if text.isascii() is False else text
        # measure
        w = d.textlength(t, font=f) + w_pad*2
        h = f.size + h_pad*2
        d.rounded_rectangle([cx-w/2, y, cx+w/2, y+h], radius=h//2, fill=(200,64,47,255))
        d.text((cx-w/2 + w_pad, y+h_pad-2), t, font=f, fill=(255,255,255,255))
        return h
    pill(540, 148, "عرض افتتاحي - أول عشرة أوردرات", font(F_AR, 18))

    cards = [
        {
            "title": "بطاقة واحدة",
            "en": "BASIC",
            "price": "59",
            "old": "79",
            "currency": "جنيه",
            "feats": ["اسم واحد", "خلفية واحدة", "صورة للطباعة والمشاركة", "تعديل مرتين", "تسليم يومين"],
            "hot": False
        },
        {
            "title": "جاهزة للطباعة",
            "en": "POPULAR",
            "price": "119",
            "old": "149",
            "currency": "جنيه",
            "feats": ["اسم واحد", "ثلاث خلفيات", "ثلاثة مقاسات مع ملف للطباعة", "تعديل ثلاث مرات", "تسليم ثلاثة أيام"],
            "hot": True
        },
        {
            "title": "باقة العائلة",
            "en": "FAMILY",
            "price": "199",
            "old": "249",
            "currency": "جنيه",
            "feats": ["حتى أربعة أسماء", "كل الخلفيات", "كل المقاسات مع ملف للطباعة", "تعديل أربع مرات", "تسليم أربعة أيام"],
            "hot": False
        },
    ]

    card_w, card_h = 308, 420
    gap = 22
    total_w = card_w * 3 + gap * 2
    start_x = (W - total_w) // 2
    top_y = 212

    for i, c in enumerate(cards):
        x = start_x + i * (card_w + gap)
        y = top_y + (-14 if c["hot"] else 0)
        h = card_h + (28 if c["hot"] else 0)

        shadow = Image.new("RGBA", (card_w + 30, h + 30), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([15, 15, card_w + 15, h + 15], radius=18, fill=(0, 0, 0, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        base.alpha_composite(shadow, (x - 15, y + 6))

        card = Image.new("RGBA", (card_w, h), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(card)
        if c["hot"]:
            d2.rounded_rectangle([0, 0, card_w - 1, h - 1], radius=18, fill=(24, 52, 82, 255), outline=(216, 186, 118, 255), width=3)
        else:
            d2.rounded_rectangle([0, 0, card_w - 1, h - 1], radius=18, fill=(255, 255, 255, 14), outline=(216, 186, 118, 80), width=1)
        base.alpha_composite(card, (x, y))
        d = ImageDraw.Draw(base)

        cx = x + card_w // 2
        if c["hot"]:
            pill_w, pill_h = 150, 28
            d.rounded_rectangle([cx - pill_w // 2, y - 14, cx + pill_w // 2, y + 14], radius=14, fill=(216, 186, 118, 255))
            center_en(d, cx, y - 7, "MOST POPULAR", font(F_UI, 12), (10, 24, 42), 2)

        center_ar(d, cx, y + 28, c["title"], font(F_AR, 24), CREAM)
        center_en(d, cx, y + 60, c["en"], font(F_UI, 12), GOLD, 3)

        f_price = font(F_HEAD, 52)
        f_cur = font(F_AR, 20)
        cur_ar = ar(c["currency"])
        f_old = font(F_UI, 18)
        w_old = d.textlength(c["old"], font=f_old)
        old_top = y + 78
        d.text((cx - w_old/2, old_top), c["old"], font=f_old, fill=MUT)
        d.line([cx - w_old/2 - 4, old_top+8, cx + w_old/2 + 4, old_top+8], fill=(200,64,47,255), width=2)

        w_price = d.textlength(c["price"], font=f_price)
        w_cur = d.textlength(cur_ar, font=f_cur)
        total_price_w = w_price + 8 + w_cur
        sx = cx - total_price_w / 2
        d.text((sx, y + 102), c["price"], font=f_price, fill=GOLD)
        d.text((sx + w_price + 8, y + 132), cur_ar, font=f_cur, fill=MUT)

        d.line([x + 32, y + 168, x + card_w - 32, y + 168], fill=(216, 186, 118, 60), width=1)

        fy = y + 184
        for ft in c["feats"]:
            f_ft = font(F_AR, 18)
            t_ar = ar(ft)
            w_ft = d.textlength(t_ar, font=f_ft)
            text_x = cx + 92 - w_ft
            d.ellipse([cx + 98, fy + 8, cx + 104, fy + 14], fill=GOLD)
            d.text((text_x, fy), t_ar, font=f_ft, fill=CREAM)
            fy += 32

    # payment panel
    py = 656
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        [54, py, W - 54, py + 200], radius=14,
        fill=(255, 255, 255, 10), outline=(216, 186, 118, 70), width=1)
    base.alpha_composite(panel)
    d = ImageDraw.Draw(base)

    center_ar(d, 540, py + 22, "الدفع مقدم", font(F_AR, 24), GOLD)
    # two columns: InstaPay | Vodafone Cash  (numbers LTR)
    col_cx = [300, 780]
    # left: Insta
    labels_en = ["InstaPay", "Vodafone Cash"]
    numbers = [INSTA, VF]
    for j, (cx, lab, num) in enumerate(zip(col_cx, labels_en, numbers)):
        # label EN
        center_en(d, cx, py + 66, lab, font(F_UI, 16), MUT, 2)
        # number centered
        f_num = font(F_UI, 34)
        w_num = d.textlength(num, font=f_num)
        d.text((cx - w_num / 2, py + 92), num, font=f_num, fill=CREAM)
        # underline gold
        d.line([cx - 70, py + 140, cx + 70, py + 140], fill=(216, 186, 118, 80), width=1)
    # divider
    d.line([540, py + 60, 540, py + 155], fill=(216, 186, 118, 50), width=1)

    center_ar(d, 540, py + 158 - 16, "الطلب والتسليم واتساب فقط", font(F_AR, 19), GOLD)

    center_ar(d, 540, 872, "للاستخدام الشخصي والكنسي والتعليمي", font(F_AR, 18), MUT)
    center_ar(d, 540, 906, "كل بطاقة تُجهز على اسمك وتُراجع قبل التسليم", font(F_AR, 17), (150, 168, 187))
    center_en(d, 540, 958, "SEND YOUR NAME ON WHATSAPP  ·  RECEIVE YOUR CARD", font(F_UI, 12), GOLD, 2)

    out = HERE + "/prices-egypt-square-launch.png"
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(out, base.size, round(os.path.getsize(out) / 1048576, 2), "MB")

if __name__ == "__main__":
    main()
