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
F_AR_UI = r"C:\Windows\Fonts\segoeuib.ttf"  # fallback

def vgrad(size, top, bot):
    w, h = size
    g = Image.new("RGB", (1,h))
    px = g.load()
    for y in range(h):
        t = (y/(h-1))**1.25
        px[0,y] = tuple(round(top[i]+(bot[i]-top[i])*t) for i in range(3))
    return g.resize(size, Image.BILINEAR).convert("RGBA")

def radial_glow(size, center, radius, color, strength):
    w,h=size
    layer=Image.new("L",(w,h),0)
    d=ImageDraw.Draw(layer)
    steps=40
    for i in range(steps,0,-1):
        t=i/steps
        r=radius*t
        a=int(255*strength*(1-t)**2)
        d.ellipse([center[0]-r,center[1]-r*0.92,center[0]+r,center[1]+r*0.92],fill=a)
    layer=layer.filter(ImageFilter.GaussianBlur(radius*0.16))
    g=Image.new("RGBA",size,color+(0,))
    g.putalpha(layer)
    return g

def vignette(size):
    w,h=size
    v=Image.radial_gradient("L").resize((w,h), Image.BILINEAR)
    v=v.point(lambda x: int(max(0,x-120)*0.9))
    g=Image.new("RGBA",size,DARK+(0,))
    g.putalpha(v)
    return g

def fibers(size, seed=7):
    import random
    rnd=random.Random(seed)
    w,h=size
    layer=Image.new("RGBA",size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    for _ in range(140):
        y=rnd.uniform(0,h)
        x0=rnd.uniform(-100,w)
        ln=rnd.uniform(80,400)
        a=rnd.randint(4,12)
        c=(216,186,118,a) if rnd.random()<0.55 else (255,255,255,max(2,a-3))
        d.line([(x0,y),(x0+ln,y+rnd.uniform(-3,3))],fill=c,width=1)
    return layer.filter(ImageFilter.GaussianBlur(0.6))

def bg():
    base=vgrad((W,H),NAVY_TOP,NAVY_BOT)
    base.alpha_composite(radial_glow((W,H),(640,350),700,(46,92,140),0.45))
    base.alpha_composite(fibers((W,H)))
    base.alpha_composite(vignette((W,H)))
    d=ImageDraw.Draw(base)
    d.rounded_rectangle([26,26,W-26,H-26],radius=4,outline=(216,186,118,80),width=1)
    d.rounded_rectangle([34,34,W-34,H-34],radius=3,outline=(216,186,118,34),width=1)
    return base

def font(p,s):
    return ImageFont.truetype(p,s)

def tracked(d,xy,text,f,color,spacing):
    x,y=xy
    for ch in text:
        d.text((x,y),ch,font=f,fill=color)
        x+=d.textlength(ch,font=f)+spacing
    return x

def center_ar(d, cx, y, text, f, color):
    t=ar(text)
    w=d.textlength(t,font=f)
    d.text((cx-w/2,y),t,font=f,fill=color)
    return w

def center_en(d,cx,y,text,f,color,spacing=0):
    if spacing>0:
        # measure
        total=0
        for ch in text:
            total+=d.textlength(ch,font=f)+spacing
        total-=spacing
        x=cx-total/2
        tracked(d,(x,y),text,f,color,spacing)
    else:
        w=d.textlength(text,font=f)
        d.text((cx-w/2,y),text,font=f,fill=color)

def main():
    base=bg()
    d=ImageDraw.Draw(base)

    # wordmark
    d.rounded_rectangle([72,42,72+34,42+20],radius=9,outline=GOLD,width=2)
    d.line([72+26,43,72+26,60],fill=GOLD,width=1)
    tracked(d,(72+48,44),"NAMES OF EGYPT",font(F_UI,15),GOLD,2.6)

    # title
    center_en(d,640,82,"PRICE LIST  ·  EGYPT",font(F_UI,13),(216,186,118),3)
    center_ar(d,640,106,"أسعار البطاقات في مصر",font(F_AR,38),CREAM)

    # cards
    cards=[
        {
            "title":"بطاقة واحدة",
            "en":"BASIC",
            "price":"79",
            "currency":"جنيه",
            "feats":["اسم واحد","خلفية واحدة","صورة للطباعة والمشاركة","تعديل مرتين","تسليم يومين"],
            "hot":False
        },
        {
            "title":"جاهزة للطباعة",
            "en":"POPULAR",
            "price":"149",
            "currency":"جنيه",
            "feats":["اسم واحد","ثلاث خلفيات","ثلاثة مقاسات مع ملف للطباعة","تعديل ثلاث مرات","تسليم ثلاثة أيام"],
            "hot":True
        },
        {
            "title":"باقة العائلة",
            "en":"FAMILY",
            "price":"249",
            "currency":"جنيه",
            "feats":["حتى أربعة أسماء","كل الخلفيات","كل المقاسات مع ملف للطباعة","تعديل أربع مرات","تسليم أربعة أيام"],
            "hot":False
        },
    ]

    card_w, card_h = 330, 380
    gap=32
    total_w = card_w*3 + gap*2
    start_x = (W-total_w)//2
    top_y = 180

    for i,c in enumerate(cards):
        x = start_x + i*(card_w+gap)
        y = top_y + ( -14 if c["hot"] else 0)
        h = card_h + (28 if c["hot"] else 0)

        # shadow
        shadow = Image.new("RGBA",(card_w+30,h+30),(0,0,0,0))
        ImageDraw.Draw(shadow).rounded_rectangle([15,15,card_w+15,h+15],radius=18,fill=(0,0,0,120))
        shadow=shadow.filter(ImageFilter.GaussianBlur(12))
        base.alpha_composite(shadow,(x-15,y+6))

        # card bg
        if c["hot"]:
            card = Image.new("RGBA",(card_w,h),(24,52,82,255))
            d2=ImageDraw.Draw(card)
            d2.rounded_rectangle([0,0,card_w-1,h-1],radius=18,fill=(24,52,82,255),outline=(216,186,118,255),width=3)
            # gold top strip
            d2.rounded_rectangle([0,0,card_w-1,10],radius=5,fill=(216,186,118,255))
        else:
            card = Image.new("RGBA",(card_w,h),(255,255,255,12))
            d2=ImageDraw.Draw(card)
            d2.rounded_rectangle([0,0,card_w-1,h-1],radius=18,fill=(255,255,255,14),outline=(216,186,118,80),width=1)
        base.alpha_composite(card,(x,y))
        d=ImageDraw.Draw(base)

        cx = x+card_w//2
        # badge
        if c["hot"]:
            # pill
            pill_w=150
            pill_h=28
            d.rounded_rectangle([cx-pill_w//2,y-14,cx+pill_w//2,y+14],radius=14,fill=(216,186,118,255))
            center_en(d,cx,y-7,"MOST POPULAR",font(F_UI,12),(10,24,42),2)

        # title arabic
        center_ar(d,cx,y+34,c["title"],font(F_AR,26),CREAM)
        center_en(d,cx,y+76,c["en"],font(F_UI,12),GOLD,3)

        # price
        # 79 جنيه
        price_text = f"{c['price']}"
        f_price = font(F_HEAD, 66)
        f_cur = font(F_AR, 22)
        cur_ar = ar(c["currency"])
        w_price = d.textlength(price_text, font=f_price)
        w_cur = d.textlength(cur_ar, font=f_cur)
        total_price_w = w_price + 8 + w_cur
        sx = cx - total_price_w/2
        d.text((sx, y+96), price_text, font=f_price, fill=GOLD)
        d.text((sx+w_price+8, y+132), cur_ar, font=f_cur, fill=MUT)

        d.line([x+36, y+178, x+card_w-36, y+178], fill=(216,186,118,60), width=1)

        # features
        fy = y+194
        for ft in c["feats"]:
            f_ft = font(F_AR,19)
            t_ar = ar(ft)
            w_ft = d.textlength(t_ar, font=f_ft)
            # right-aligned block for RTL
            text_x = cx + 92 - w_ft
            d.ellipse([cx+98, fy+8, cx+104, fy+14], fill=GOLD)
            d.text((text_x, fy), t_ar, font=f_ft, fill=CREAM)
            fy+=32

    # extras line
    center_ar(d,640,592,"أسماء ومقاسات إضافية متاحة عند الطلب",font(F_AR,18),MUT)
    # payment line
    center_ar(d,640,624,"الطلب والتسليم واتساب فقط · دفع مقدم انستاباي / فودافون كاش",font(F_AR,19),GOLD)
    center_ar(d,640,654,"للاستخدام الشخصي والكنسي والتعليمي",font(F_AR,16),(150,168,187))

    out=os.path.join(HERE,"prices-egypt.png")
    base.convert("RGB").save(out,"PNG",optimize=True)
    print(out, base.size, round(os.path.getsize(out)/1048576,2),"MB")

if __name__=="__main__":
    main()
