from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 2480, 3508  # A4 @ 300 DPI

NAVY_TOP = (10, 24, 42)
NAVY_BOT = (20, 46, 74)
GOLD = (216, 186, 118)
CREAM = (244, 236, 216)
MUT = (170, 186, 202)
DARK = (6, 14, 24)

F_HEAD = r"C:\Windows\Fonts\cambriab.ttf"
F_BODY = r"C:\Windows\Fonts\constan.ttf"
F_UI = r"C:\Windows\Fonts\segoeuib.ttf"
F_UI_R = r"C:\Windows\Fonts\segoeui.ttf"


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


def fibers(size, seed=11):
    import random
    rnd = random.Random(seed)
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(260):
        y = rnd.uniform(0, h)
        x0 = rnd.uniform(-200, w)
        ln = rnd.uniform(150, 700)
        a = rnd.randint(4, 12)
        c = (216, 186, 118, a) if rnd.random() < 0.55 else (255, 255, 255, max(2, a - 3))
        d.line([(x0, y), (x0 + ln, y + rnd.uniform(-4, 4))], fill=c, width=2)
    return layer.filter(ImageFilter.GaussianBlur(0.8))


def bg(seed):
    base = vgrad((PW, PH), NAVY_TOP, NAVY_BOT)
    base.alpha_composite(radial_glow((PW, PH), (1900, 900), 1200, (46, 92, 140), 0.55))
    base.alpha_composite(radial_glow((PW, PH), (450, 350), 900, (58, 86, 120), 0.22))
    base.alpha_composite(fibers((PW, PH), seed))
    base.alpha_composite(vignette((PW, PH)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([90, 90, PW - 90, PH - 90], radius=8, outline=(216, 186, 118, 85), width=3)
    d.rounded_rectangle([112, 112, PW - 112, PH - 112], radius=6, outline=(216, 186, 118, 36), width=2)
    return base


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, xy, text, f, color, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=color)
        x += draw.textlength(ch, font=f) + spacing
    return x


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m


def paste_card(base, path, width, center, angle, radius=14, shadow=0.55):
    im = Image.open(path).convert("RGBA")
    h = round(width * im.height / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), rounded_mask(im.size, radius)))
    rot = im.rotate(angle, expand=True, resample=Image.BICUBIC)

    a = rot.getchannel("A")
    sh = Image.new("RGBA", rot.size, (3, 9, 18, 0))
    sh.putalpha(a.point(lambda v: int(v * shadow)))
    sh = sh.filter(ImageFilter.GaussianBlur(38))
    base.alpha_composite(sh, (round(center[0] - sh.width / 2) + 8,
                              round(center[1] - sh.height / 2) + 46))
    base.alpha_composite(rot, (round(center[0] - rot.width / 2),
                               round(center[1] - rot.height / 2)))
    return rot.size


def wordmark(base, x=190, y=196, scale=1.0):
    d = ImageDraw.Draw(base)
    w, h = round(88 * scale), round(46 * scale)
    d.rounded_rectangle([x, y + 4, x + w, y + h], radius=round(22 * scale),
                        outline=GOLD, width=3)
    d.line([x + round(w * 0.76), y + 6, x + round(w * 0.76), y + h - 4], fill=GOLD, width=2)
    f = font(F_UI, round(38 * scale))
    tracked(d, (x + round(120 * scale), y + 2), "NAMES OF EGYPT", f, GOLD, 7 * scale)


def kicker(d, x, y, text, size=36, color=GOLD, spacing=8):
    tracked(d, (x, y), text, font(F_UI, size), color, spacing)


def rule(d, x, y, w, color=(216, 186, 118, 90), width=2):
    d.line([x, y, x + w, y], fill=color, width=width)


def page_one():
    base = bg(11)
    d = ImageDraw.Draw(base)
    wordmark(base)

    kicker(d, 190, 322, "SAMPLE CARDS")
    d.text((190, 372), "Your name,", font=font(F_HEAD, 168), fill=CREAM)
    d.text((190, 570), "in four scripts.", font=font(F_HEAD, 168), fill=GOLD)
    d.text((190, 806), "Hieroglyphs · Coptic · English · Arabic",
           font=font(F_BODY, 58), fill=MUT)

    cards = [
        ("mina-papyrus.png", "Mina", "Papyrus", -2.4),
        ("mariam-gold.png", "Mariam", "Gold", 0.0),
        ("bishoy-lapis.png", "Bishoy", "Lapis lazuli", 2.4),
    ]
    xs = [520, 1240, 1960]
    for (fn, name, tone, ang), cx in zip(cards, xs):
        paste_card(base, os.path.join(HERE, "cards", fn), 655, (cx, 1470), ang)

    d = ImageDraw.Draw(base)
    for (fn, name, tone, ang), cx in zip(cards, xs):
        f = font(F_UI, 34)
        tracked(d, (cx - 190, 2072), name.upper(), f, CREAM, 5)
        d.text((cx - 190, 2123), tone, font=font(F_BODY, 38), fill=MUT)

    rule(d, 190, 2280, 2100)
    feats = [
        ("FOUR SCRIPTS", "Hieroglyphs, Coptic,\nEnglish and Arabic"),
        ("FOUR BACKGROUNDS", "Papyrus, gold, silver\nand lapis lazuli"),
        ("PRINT READY", "Portrait, square and\nA4 at 300 DPI"),
    ]
    for i, (head, body) in enumerate(feats):
        x = 190 + i * 720
        tracked(d, (x, 2360), head, font(F_UI, 30), GOLD, 5)
        for j, ln in enumerate(body.split("\n")):
            d.text((x, 2416 + j * 56), ln, font=font(F_BODY, 40), fill=CREAM)

    rule(d, 940, 2640, 600, color=(216, 186, 118, 70))
    d.text((PW / 2, 2690), "Send a name. Receive a card you can print, frame or share.",
           font=font(F_BODY, 56), fill=CREAM, anchor="ma")
    d.text((PW / 2, 2800), "Personal, church and educational use  ·  Physical prints not included",
           font=font(F_BODY, 36), fill=(150, 168, 187), anchor="ma")

    d.text((190, 3320), "Sample sheet · Names of Egypt", font=font(F_BODY, 34), fill=(140, 158, 178))
    d.text((PW - 190 - d.textlength("1 / 2", font=font(F_BODY, 34)), 3320), "1 / 2",
           font=font(F_BODY, 34), fill=(140, 158, 178))
    return base


def page_two():
    base = bg(13)
    d = ImageDraw.Draw(base)
    wordmark(base)

    kicker(d, 190, 322, "DETAILS & DELIVERY")
    d.text((190, 372), "What you receive", font=font(F_HEAD, 132), fill=CREAM)
    d.text((190, 530), "A finished file, built from your name — not a template.",
           font=font(F_BODY, 50), fill=MUT)
    rule(d, 190, 640, 2100)

    # right: large detail crop
    card = Image.open(os.path.join(HERE, "cards", "mina-papyrus.png")).convert("RGB")
    crop = card.crop((40, 30, 729, 800)).resize((900, 940), Image.LANCZOS)
    cx, cy = 2290 - 900, 700
    d.rounded_rectangle([cx - 10, cy - 10, cx + 910, cy + 950], radius=6,
                        outline=(216, 186, 118, 110), width=2)
    base.paste(crop, (cx, cy))
    d.text((cx, cy + 984), "Detail — three of the four scripts, close up",
           font=font(F_BODY, 34), fill=MUT)

    # left column
    x = 190
    tracked(d, (x, 700), "FORMATS & SIZES", font(F_UI, 30), GOLD, 5)
    rows = [
        ("Portrait", "1080 × 1350 px  ·  PNG"),
        ("Square", "1080 × 1080 px  ·  PNG"),
        ("Print", "A4  ·  2480 × 3508 px  ·  300 DPI PDF"),
    ]
    for i, (a, b) in enumerate(rows):
        yy = 766 + i * 92
        d.text((x, yy), a, font=font(F_UI, 40), fill=CREAM)
        d.text((x + 250, yy + 6), b, font=font(F_BODY, 38), fill=MUT)

    tracked(d, (x, 1070), "BACKGROUNDS", font(F_UI, 30), GOLD, 5)
    swatches = [("Papyrus", (236, 217, 166)), ("Gold", (246, 220, 130)),
                ("Silver", (244, 246, 248)), ("Lapis", (28, 63, 135))]
    for i, (label, col) in enumerate(swatches):
        sx = x + i * 190
        d.ellipse([sx, 1130, sx + 96, 1226], fill=col, outline=(216, 186, 118, 140), width=2)
        d.text((sx, 1246), label, font=font(F_BODY, 32), fill=MUT)

    tracked(d, (x, 1350), "OPTIONS", font(F_UI, 30), GOLD, 5)
    opts = [
        "Hieroglyphic or Coptic border",
        "Cartouche around the Coptic name",
        "Two names on one card",
        "Custom background colour",
    ]
    for i, o in enumerate(opts):
        yy = 1414 + i * 64
        d.line([x, yy + 22, x + 26, yy + 22], fill=GOLD, width=2)
        d.text((x + 46, yy), o, font=font(F_BODY, 38), fill=CREAM)

    tracked(d, (x, 1745), "LICENSING", font(F_UI, 30), GOLD, 5)
    lic = [
        "Personal, church and educational use.",
        "The hieroglyphic form is an artistic transliteration",
        "based on published Coptic spellings — a keepsake,",
        "not an academic or church-certified reference.",
    ]
    for i, ln in enumerate(lic):
        d.text((x, 1806 + i * 52), ln, font=font(F_BODY, 35), fill=MUT)

    # bottom process panel
    py = 2180
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        [190, py, PW - 190, py + 640], radius=10,
        fill=(255, 255, 255, 10), outline=(216, 186, 118, 60), width=2)
    base.alpha_composite(panel)
    d = ImageDraw.Draw(base)
    tracked(d, (250, py + 58), "HOW IT WORKS", font(F_UI, 30), GOLD, 5)
    steps = [
        ("01", "Send the name", "Arabic, plus any spelling\nyou want me to follow."),
        ("02", "Approve a preview", "A watermarked proof comes\nback for your check."),
        ("03", "Receive the files", "Final PNG and PDF, clean,\nready to print or share."),
    ]
    for i, (num, head, body) in enumerate(steps):
        sx = 250 + i * 690
        d.text((sx, py + 140), num, font=font(F_HEAD, 84), fill=GOLD)
        d.text((sx, py + 262), head, font=font(F_UI, 42), fill=CREAM)
        for j, ln in enumerate(body.split("\n")):
            d.text((sx, py + 330 + j * 52), ln, font=font(F_BODY, 36), fill=MUT)
        if i < 2:
            d.line([sx + 610, py + 150, sx + 610, py + 540], fill=(216, 186, 118, 60), width=2)

    d.text((PW / 2, 2960), "Every card is prepared individually and checked before delivery.",
           font=font(F_BODY, 36), fill=(150, 168, 187), anchor="ma")

    d.text((190, 3320), "Sample sheet · Names of Egypt", font=font(F_BODY, 34), fill=(140, 158, 178))
    d.text((PW - 190 - d.textlength("2 / 2", font=font(F_BODY, 34)), 3320), "2 / 2",
           font=font(F_BODY, 34), fill=(140, 158, 178))
    return base


if __name__ == "__main__":
    p1 = page_one().convert("RGB")
    p2 = page_two().convert("RGB")
    out = os.path.join(HERE, "Names-of-Egypt-sample-cards.pdf")
    p1.save(out, "PDF", resolution=300.0, save_all=True, append_images=[p2], quality=92)
    print(out, round(os.path.getsize(out) / 1048576, 2), "MB")
    p1.save(os.path.join(HERE, "sample-page-1.png"), "PNG", optimize=True)
    p2.save(os.path.join(HERE, "sample-page-2.png"), "PNG", optimize=True)
