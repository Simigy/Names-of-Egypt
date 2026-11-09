"""Gig gallery v2 for Fiverr (1280x769 x3):
  fiverr-cover.png    - lapis cover, one large gold sample name (real crops from Bishoy card)
  fiverr-styles.png   - the same name (MINA) in papyrus / gold / silver / lapis, labeled
  fiverr-packages.png - package comparison: 1 name x 1 style / 1 name x 4 styles / up to 4 names x 1 style

The "same name in four styles" panels are duotone re-tints of the real MINA card
(the delivered card comes from the generator with these styles); Bishoy/Mary cards
are used untouched.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import compose as C  # shared helpers/fonts/palette

W, H = 1280, 769
GOLD = C.GOLD
CREAM = C.CREAM
MUT = C.MUT
DARK = C.DARK

CARD_MINA = os.path.join(HERE, "cards", "mina-papyrus.png")
CARD_MARY = os.path.join(HERE, "cards", "mariam-gold.png")
CARD_BISHOY = os.path.join(HERE, "cards", "bishoy-lapis.png")

LAPIS_TOP = (14, 36, 70)
LAPIS_BOT = (24, 56, 102)
GOLD_LT = (242, 208, 132)
GOLD_HL = (226, 186, 106)


def font(p, s):
    return ImageFont.truetype(p, s)


def center_en(d, cx, y, text, f, color, spacing=0):
    if spacing > 0:
        total = 0
        for ch in text:
            total += d.textlength(ch, font=f) + spacing
        total -= spacing
        C.tracked(d, (cx - total / 2, y), text, f, color, spacing)
    else:
        tw = d.textlength(text, font=f)
        d.text((cx - tw / 2, y), text, font=f, fill=color)


def recolor(path, ink, mid, paper):
    """Duotone re-tint of a real card render (style flip)."""
    im = Image.open(path).convert("RGB")
    g = im.convert("L")
    return ImageOps.colorize(g, black=ink, white=paper, mid=mid)


def mina_styles():
    papyrus = Image.open(CARD_MINA).convert("RGB")
    gold = recolor(CARD_MINA, (66, 42, 12), (190, 138, 50), (226, 176, 78))
    silver = recolor(CARD_MINA, (38, 42, 48), (132, 137, 145), (234, 236, 240))
    lapis = recolor(CARD_MINA, (246, 238, 206), (28, 62, 112), (16, 42, 84))  # inverted: bg->navy, ink->cream
    return [("Papyrus", papyrus), ("Gold", gold), ("Silver", silver), ("Lapis", lapis)]


def extract_gold(src, box, out_h):
    """Crop bright strokes out of a lapis card region and return a gold RGBA image."""
    crop = src.crop(box).convert("RGB")
    g = crop.convert("L")
    mask = g.point(lambda v: max(0, min(255, int((v - 116) * 255 / 66))))
    mask = mask.filter(ImageFilter.GaussianBlur(0.7))
    out = ImageOps.colorize(g, black=(96, 66, 24), white=GOLD_LT, mid=GOLD_HL)
    out.putalpha(mask)
    w = round(out_h * out.width / out.height)
    return out.resize((w, out_h), Image.LANCZOS)


def lapis_bg():
    base = C.vgrad((W, H), LAPIS_TOP, LAPIS_BOT)
    base.alpha_composite(C.radial_glow((W, H), (640, 330), 640, (56, 104, 156), 0.5))
    base.alpha_composite(C.radial_glow((W, H), (640, 620), 480, (30, 62, 108), 0.35))
    base.alpha_composite(C.paper_fibers((W, H), seed=11))
    base.alpha_composite(C.vignette((W, H)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([26, 26, W - 26, H - 26], radius=4, outline=(216, 186, 118, 90), width=1)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=3, outline=(216, 186, 118, 38), width=1)
    return base


def gold_text_layer(src, box, out_h, tint="gold"):
    crop = src.crop(box).convert("RGB")
    g = crop.convert("L")
    mask = g.point(lambda v: max(0, min(255, int((v - 112) * 255 / 70))))
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))
    if tint == "gold":
        out = ImageOps.colorize(g, black=(120, 84, 30), white=(250, 220, 148), mid=(230, 189, 110))
    else:
        out = crop.convert("RGBA")
    out.putalpha(mask)
    w = round(out_h * out.width / out.height)
    return out.resize((w, out_h), Image.LANCZOS)


def paste_rune(base, art, cx, cy, shadow=True):
    if shadow:
        sh = Image.new("RGBA", art.size, (3, 9, 18, 0))
        sh.putalpha(art.getchannel("A").point(lambda v: int(v * 0.5)))
        sh = sh.filter(ImageFilter.GaussianBlur(16))
        base.alpha_composite(sh, (round(cx - art.width / 2) + 2, round(cy - art.height / 2) + 12))
    base.alpha_composite(art, (round(cx - art.width / 2), round(cy - art.height / 2)))


def brand_row(base, cx, y=52):
    d = ImageDraw.Draw(base)
    # mini cartouche mark
    x = cx - 118
    d.rounded_rectangle([x, y + 2, x + 34, y + 20], radius=9, outline=GOLD, width=2)
    d.line([x + 26, y + 3, x + 26, y + 19], fill=GOLD, width=1)
    C.tracked(d, (x + 48, y + 2), "NAMES OF EGYPT", font(C.F_UI, 15), GOLD, 2.6)


def compose_cover():
    base = lapis_bg()
    bishoy = Image.open(CARD_BISHOY).convert("RGB")
    dst = ImageDraw.Draw(base)

    brand_row(base, W // 2)

    # real hieroglyph cartouche, recoloured gold
    cart = gold_text_layer(bishoy, (66, 104, 706, 300), 158)
    paste_rune(base, cart, W // 2, 200)

    # giant readable sample name
    f = font(C.F_HEAD, 172)
    name = "BISHOY"
    tw = dst.textlength(name, font=f)
    ny = 300
    dst.text((W // 2 - tw / 2 + 4, ny + 6), name, font=f, fill=(8, 20, 38))
    dst.text((W // 2 - tw / 2, ny), name, font=f, fill=GOLD_LT)

    # real Coptic + Arabic strokes, gold
    cpt = gold_text_layer(bishoy, (150, 372, 620, 532), 104)
    paste_rune(base, cpt, W // 2, 528)
    arb = gold_text_layer(bishoy, (196, 940, 578, 1120), 104)
    paste_rune(base, arb, W // 2, 656)

    f_t = font(C.F_UI, 15)
    center_en(dst, W // 2, 722, "YOUR NAME  ·  HIEROGLYPHS  ·  COPTIC  ·  ENGLISH  ·  ARABIC", f_t, CREAM, 2)

    return base


def compose_styles():
    base = C.bg()
    C.wordmark(base)
    d = ImageDraw.Draw(base)
    C.kicker(d, 72, 128, "ONE NAME · FOUR STYLES")
    d.text((72, 156), "Pick your style.", font=font(C.F_HEAD, 54), fill=CREAM)
    d.text((72, 224), "Same card, four finishes.", font=font(C.F_BODY, 20), fill=GOLD)

    styles = mina_styles()
    slot_w = 250
    margins = 96
    gap = (W - 2 * margins - 4 * slot_w) / 3
    cy = 476
    card_h = round(slot_w * 1280 / 769)
    order = [s[1] for s in styles]
    for i, im in enumerate(order):
        cx = margins + slot_w / 2 + i * (slot_w + gap)
        tmp_path = os.path.join(HERE, "_style_tmp.png")
        im.save(tmp_path)
        C.paste_card(base, tmp_path, slot_w, (cx, cy), [4, -3, -5, 5][i] * 0.9, radius=10)
        os.remove(tmp_path)

    lbl = font(C.F_UI, 17)
    names = [s[0].upper() for s in styles]
    for i, nm in enumerate(names):
        cx = margins + slot_w / 2 + i * (slot_w + gap)
        center_en(d, cx, cy + card_h / 2 + 26, nm, lbl, GOLD, 2)
    return base


def compose_packages():
    base = C.bg()
    C.wordmark(base)
    d = ImageDraw.Draw(base)
    C.kicker(d, 72, 128, "PACKAGES")

    styles = mina_styles()
    panels = [
        ("BASIC", "$10", "1 name  ·  1 style", 0),
        ("STANDARD", "$20", "1 name  ·  4 styles", 1),
        ("PREMIUM", "$35", "Up to 4 names  ·  1 style each", 2),
    ]

    margin, gap_pan = 46, 26
    pw = (W - 2 * margin - 2 * gap_pan) / 3
    top, ph = 168, 520

    for i, (nm, price, desc, kind) in enumerate(panels):
        x = margin + i * (pw + gap_pan)
        cx = x + pw / 2

        sh = Image.new("RGBA", (round(pw) + 30, ph + 30), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([15, 15, 15 + pw, 15 + ph], radius=16, fill=(0, 0, 0, 110))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (round(x) - 15, top + 6))

        panel = Image.new("RGBA", (round(pw), ph), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=16,
                                                fill=(255, 255, 255, 12), outline=(216, 186, 118, 110), width=2)
        base.alpha_composite(panel, (round(x), top))
        d = ImageDraw.Draw(base)

        center_en(d, cx, top + 22, nm, font(C.F_UI, 16), GOLD, 4)
        center_en(d, cx, top + 46, price, font(C.F_HEAD, 46), GOLD_LT)
        center_en(d, cx, top + 104, desc, font(C.F_BODY, 19), CREAM)

        mid_y = top + 118  # header block height
        vy = top + 176
        vh = 300

        if kind == 0:
            tmp = os.path.join(HERE, "_p_tmp.png")
            styles[0][1].save(tmp)
            C.paste_card(base, tmp, 168, (cx, vy + vh / 2 + 10), -3, radius=10)
            os.remove(tmp)
        elif kind == 1:
            gx, gapm = 88, 16
            gh = round(gx * 1280 / 769)
            for j in range(4):
                r, c2 = divmod(j, 2)
                px2 = cx - gx / 2 - gapm / 2 + c2 * (gx + gapm)
                py2 = vy + gh / 2 + r * (gh + 12)
                tmp = os.path.join(HERE, "_p_tmp.png")
                styles[j][1].save(tmp)
                C.paste_card(base, tmp, gx, (px2, py2), [-2, 2, -2, 2][j], radius=7)
                os.remove(tmp)
            center_en(d, cx, vy + 2 * gh + 38, "Papyrus · Gold · Silver · Lapis", font(C.F_UI, 13), MUT, 1)
        else:
            trio = [
                (CARD_MINA, -9, cx - 84, 112, 34),
                (CARD_MARY, 2, cx, 124, 10),
                (CARD_BISHOY, 10, cx + 84, 112, 34),
            ]
            for j, (p, ang, px3, wdt, dy) in enumerate(trio):
                C.paste_card(base, p, wdt, (px3, vy + vh / 2 + dy), ang, radius=9)
            center_en(d, cx, vy + 300, "Portrait · Square · A4 print", font(C.F_UI, 13), MUT, 1)

    center_en(d, W // 2, 722, "WATERMARKED PREVIEW BEFORE PAYMENT  ·  FINAL FILES AFTER", font(C.F_UI, 14), GOLD, 2)
    return base


def main():
    outs = {
        "fiverr-cover.png": compose_cover,
        "fiverr-styles.png": compose_styles,
        "fiverr-packages.png": compose_packages,
    }
    for name, fn in outs.items():
        im = fn().convert("RGB")
        out = os.path.join(HERE, name)
        im.save(out, "PNG", optimize=True)
        print(out, im.size, round(os.path.getsize(out) / 1048576, 2), "MB")


if __name__ == "__main__":
    main()
