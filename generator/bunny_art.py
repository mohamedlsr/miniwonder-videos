"""White Bunny universe: original characters and places (flat storybook style)."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import art
from art import Pen, hexc, rot_ell, bezier, W, H
from engine import vgrad, radial, to_img, hills

OL = "#3a2e2a"


# ------------------------------------------------------------------ faces
def face(p, cx, cy, s, mouth="smile", blink=False, mood="happy", nose="#ff8fab", lashes=False):
    """Big cute eyes, nose, mouth. s = head radius scale (1 = r 115)."""
    ex, ey, er = 42 * s, -8 * s, 22 * s
    for side in (-1, 1):
        x = cx + side * ex
        if blink:
            p.arc(x, cy + ey, er, er * 0.8, 20, 160, OL, er * 0.3)
        else:
            p.ell(x, cy + ey, er * 0.82, er, "#1f1f2e")
            p.circ(x - er * 0.3, cy + ey - er * 0.4, er * 0.36, "#ffffff")
            p.circ(x + er * 0.28, cy + ey + er * 0.35, er * 0.15, "#ffffff")
            if lashes:
                for k in (-1, 0):
                    a = math.radians(-120 + k * 25) if side < 0 else math.radians(-60 - k * 25)
                    p.line([(x + er * 0.8 * math.cos(a), cy + ey + er * math.sin(a)),
                            (x + er * 1.3 * math.cos(a), cy + ey + er * 1.4 * math.sin(a))], OL, 4 * s)
        if mood == "sad":
            p.line([(x - side * er * 0.9, cy + ey - er * 1.5), (x + side * er * 0.6, cy + ey - er * 1.25)], OL, 6 * s)
        if mood == "surprised":
            p.arc(x, cy + ey - er * 1.5, er * 0.8, er * 0.4, 200, 340, OL, 5 * s)
        art.cheek(p, cx + side * 72 * s, cy + 32 * s, 17 * s)
    # nose
    ny = cy + 30 * s
    p.ell(cx, ny, 13 * s, 9 * s, nose, OL, 2.5 * s)
    my = ny + 16 * s
    if mouth == "open":
        p.d.chord([(cx - 20 * s) * p.k, (my - 8 * s) * p.k, (cx + 20 * s) * p.k, (my + 26 * s) * p.k], 0, 180, fill=hexc("#7a2e3e"))
        p.ell(cx, my + 12 * s, 10 * s, 6 * s, "#ff8fa3")
    elif mood == "sad":
        p.arc(cx, my + 18 * s, 18 * s, 12 * s, 200, 340, OL, 4 * s)
    elif mood == "surprised" or mouth == "o":
        p.ell(cx, my + 8 * s, 9 * s, 12 * s, "#7a2e3e")
    else:
        p.arc(cx - 11 * s, my - 2 * s, 11 * s, 10 * s, 10, 170, OL, 4 * s)
        p.arc(cx + 11 * s, my - 2 * s, 11 * s, 10 * s, 10, 170, OL, 4 * s)


# ------------------------------------------------------------------ rabbits
RABBITS = {
    # fur, inner ear, outfit kind, outfit colour, accessory
    "bunny": ("#ffffff", "#ffb3c6", "scarf", "#4dabf7", None),
    "maman": ("#fff6ec", "#ffb3c6", "dress", "#ff8fab", "flower"),
    "papa": ("#d8c3a5", "#f0b8a8", "sweater", "#51a46a", "glasses"),
    "noisette": ("#e7c39b", "#ffb3c6", "dress", "#ffd43b", "bow"),
    "mamie": ("#f1f1f1", "#ffc9d6", "shawl", "#b197fc", "glasses"),
}


@lru_cache(None)
def rabbit(who="bunny", mouth="smile", blink=False, mood="happy"):
    fur, inner, outfit, ocol, acc = RABBITS[who]
    p = Pen(420, 640)
    shade = "#e9eef5" if fur == "#ffffff" else None
    # ears
    tilt = {"bunny": (-12, 14), "maman": (-8, 18), "papa": (-6, 8), "noisette": (-16, 30), "mamie": (-10, 25)}[who]
    if mood == "sad":
        tilt = (tilt[0] - 25, tilt[1] + 25)
    for (cx, cy, ang) in ((160, 125, tilt[0]), (262, 125, tilt[1])):
        p.poly(rot_ell(cx, cy, 40, 115, ang, 50), fur, OL, 5)
        p.poly(rot_ell(cx, cy + 10, 20, 82, ang, 40), inner)
    # feet + body
    for x in (148, 272):
        p.ell(x, 600, 55, 26, fur, OL, 5)
    p.ell(210, 470, 112, 130, fur, OL, 5)
    if shade:
        p.ell(210, 500, 70, 80, shade)
    if outfit == "dress":
        p.poly([(130, 400), (290, 400), (330, 575), (90, 575)], ocol, OL, 5)
        for i in range(9):
            p.circ(120 + (i % 3) * 80 + (i // 3) * 20, 440 + (i // 3) * 45, 8, (255, 255, 255, 200))
    elif outfit == "sweater":
        p.ell(210, 470, 112, 130, ocol, OL, 5)
        for y in (420, 470, 520):
            p.line([(130, y), (290, y)], (255, 255, 255, 90), 6)
    elif outfit == "shawl":
        p.poly([(110, 380), (310, 380), (250, 470), (210, 500), (170, 470)], ocol, OL, 5)
    # arms
    for side in (-1, 1):
        p.poly(rot_ell(210 + side * 108, 450, 26, 62, side * 25, 30), fur if outfit not in ("sweater",) else ocol, OL, 5)
        p.circ(210 + side * 128, 500, 22, fur, OL, 4)
    if outfit == "scarf":
        p.rect(118, 352, 302, 392, 20, ocol, OL, 5)
        p.poly([(250, 380), (292, 380), (300, 460), (262, 455)], ocol, OL, 5)
        for x in (268, 282):
            p.line([(x, 458), (x, 474)], ocol, 6)
    # head
    p.circ(210, 265, 122, fur, OL, 5)
    face(p, 210, 270, 1.0, mouth, blink, mood, lashes=who in ("maman", "noisette", "mamie"))
    for side in (-1, 1):
        for k in (-1, 1):
            p.line([(210 + side * 40, 302 + k * 6), (210 + side * 95, 296 + k * 14)], (90, 80, 80, 160), 3)
    if acc == "glasses":
        for side in (-1, 1):
            p.circ(210 + side * 42, 262, 34, None, "#5c4033", 6)
        p.line([(198, 258), (222, 258)], "#5c4033", 5)
    elif acc == "flower":
        for i in range(6):
            a = 2 * math.pi * i / 6
            p.circ(285 + 22 * math.cos(a), 150 + 22 * math.sin(a), 16, "#ff8fab", OL, 3)
        p.circ(285, 150, 13, "#ffd43b", OL, 3)
    elif acc == "bow":
        p.poly([(250, 150), (300, 120), (300, 182)], "#ff6b81", OL, 4)
        p.poly([(250, 150), (205, 120), (205, 182)], "#ff6b81", OL, 4)
        p.circ(252, 150, 14, "#ff4d6d", OL, 4)
    return p.done()


# ------------------------------------------------------------------ friends
@lru_cache(None)
def pipo(mouth="smile", blink=False, mood="happy"):
    """Pipo the squirrel: orange, giant fluffy tail, red cap."""
    p = Pen(460, 600)
    o, od, cream = "#f08c3a", "#d9732a", "#ffe3c2"
    tail = bezier((300, 520), (460, 480), (470, 200), (330, 140), 50)
    p.stroke(tail, od, 120, 70, OL, 5)
    p.stroke(tail, o, 95, 50)
    for x in (165, 255):
        p.ell(x, 575, 42, 22, od, OL, 4)
    p.ell(210, 455, 95, 115, o, OL, 5)
    p.ell(210, 475, 58, 80, cream)
    for side in (-1, 1):
        p.poly(rot_ell(210 + side * 92, 440, 22, 52, side * 25, 30), o, OL, 4)
        p.circ(210 + side * 108, 482, 18, o, OL, 4)
    for side in (-1, 1):
        p.poly([(210 + side * 50, 175), (210 + side * 95, 90), (210 + side * 105, 185)], o, OL, 5)
        p.poly([(210 + side * 62, 168), (210 + side * 92, 112), (210 + side * 96, 172)], "#ffb3c6")
    p.circ(210, 265, 112, o, OL, 5)
    p.ell(210, 300, 80, 62, cream)
    face(p, 210, 268, 0.95, mouth, blink, mood, nose="#5c3a21")
    # cap
    p.d.chord([(210 - 100) * p.k, (110) * p.k, (210 + 100) * p.k, (290) * p.k], 180, 360, fill=hexc("#e03131"))
    p.arc(210, 200, 100, 90, 180, 360, OL, 5)
    p.rect(200, 186, 330, 206, 10, "#c92a2a", OL, 4)
    p.circ(210, 112, 10, "#ffffff", OL, 3)
    return p.done()


@lru_cache(None)
def lila(mouth="smile", blink=False, mood="happy"):
    """Lila the turtle: green, domed shell, purple scarf. Wide and low."""
    p = Pen(560, 460)
    g, gd = "#8fd18a", "#5fae5a"
    for x in (150, 380):
        p.ell(x, 352, 52, 34, g, OL, 5)
    p.d.chord([60 * p.k, 140 * p.k, 470 * p.k, 520 * p.k], 180, 360, fill=hexc("#a0703c"))
    p.arc(265, 330, 205, 190, 180, 360, OL, 6)
    p.line([(60, 330), (470, 330)], OL, 6)
    for cx, cy in ((170, 270), (265, 230), (360, 270), (215, 305), (315, 305)):
        p.poly(rot_ell(cx, cy, 42, 30, 0, 6), "#c4904f", "#7a5228", 4)
    p.rect(70, 320, 460, 350, 14, "#d9b06b", OL, 4)
    # head on the right
    p.poly(rot_ell(470, 290, 40, 60, 20, 30), g, OL, 5)
    p.circ(470, 210, 82, g, OL, 5)
    p.rect(410, 268, 535, 298, 14, "#9775fa", OL, 4)
    face(p, 470, 212, 0.68, mouth, blink, mood, nose=gd, lashes=True)
    return p.done()


def char_sprite(who, mouth="smile", blink=False, mood="happy"):
    if who in RABBITS:
        return rabbit(who, mouth, blink, mood)
    if who == "pipo":
        return pipo(mouth, blink, mood)
    if who == "lila":
        return lila(mouth, blink, mood)
    raise KeyError(who)


# base display scale for each character (so families have consistent sizes)
SIZES = {"bunny": 0.72, "maman": 0.82, "papa": 0.86, "noisette": 0.56, "mamie": 0.78, "pipo": 0.66, "lila": 0.62}


# ------------------------------------------------------------------ props
@lru_cache(None)
def carrot(size=120):
    p = Pen(80, 160)
    p.poly([(20, 40), (60, 40), (42, 155), (38, 155)], "#ff922b", OL, 4)
    for y in (70, 95, 120):
        p.line([(32, y), (48, y + 4)], "#e8590c", 3)
    for dx in (-14, 0, 14):
        p.poly(rot_ell(40 + dx, 22, 9, 24, dx * 1.5, 16), "#51cf66", OL, 3)
    return p.done().resize((int(size * 0.5), size), Image.LANCZOS)


@lru_cache(None)
def basket(size=200):
    p = Pen(240, 180)
    p.arc(120, 90, 80, 80, 180, 360, "#a0703c", 12)
    p.poly([(20, 80), (220, 80), (195, 170), (45, 170)], "#d9a066", OL, 5)
    for y in (105, 135):
        p.line([(35, y), (205, y)], "#a0703c", 5)
    for x in range(55, 200, 30):
        p.line([(x, 82), (x - 5, 168)], "#b9844f", 4)
    return p.done().resize((size, int(size * 0.75)), Image.LANCZOS)


@lru_cache(None)
def blanket(size=700):
    p = Pen(700, 160)
    p.poly([(60, 0), (640, 0), (700, 160), (0, 160)], "#ff6b6b", OL, 5)
    for i in range(1, 6):
        x = i * 110
        p.line([(x + 10, 0), (x - 10 + (x - 350) * 0.18, 160)], (255, 255, 255, 200), 14)
    p.line([(30, 80), (670, 80)], (255, 255, 255, 200), 14)
    return p.done().resize((size, int(size * 160 / 700)), Image.LANCZOS)


@lru_cache(None)
def nut(size=50):
    p = Pen(60, 70)
    p.ell(30, 42, 24, 26, "#b5651d", OL, 3)
    p.ell(30, 22, 26, 12, "#7a4a1c", OL, 3)
    p.line([(30, 10), (32, 2)], OL, 4)
    return p.done().resize((size, int(size * 70 / 60)), Image.LANCZOS)


@lru_cache(None)
def heart(size=80, col="#ff6b81"):
    p = Pen(100, 100)
    p.circ(32, 38, 24, col)
    p.circ(68, 38, 24, col)
    p.poly([(10, 46), (90, 46), (50, 92)], col)
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def zzz(size=70):
    p = Pen(100, 100)
    p.text((50, 52), "z", "Fredoka-Bold.ttf", 80, "#ffffff", stroke=5, sfill="#5c7cfa")
    return p.done().resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ places
def _sky(top="#8fd3ff", bottom="#e3f6ff"):
    return to_img(vgrad(top, bottom))


@lru_cache(None)
def bg_meadow(variant=0):
    """Le Pré des Trèfles: the family burrow-house in a green hill, flowers."""
    img = _sky("#7fcfff", "#e8f8ff") if variant != 2 else _sky("#ff9a76", "#ffd8a8")
    p = Pen(W, H, 2)
    hills(p, 560, 30, "#b7e4a0", 21, 0.6)
    hills(p, 640, 25, "#94d47c", 22, 0.9)
    # burrow hill
    p.ell(470, 760, 420, 330, "#7cc35a")
    p.circ(470, 690, 110, "#7a4b2a", OL, 6)
    p.circ(470, 690, 95, "#c98d54")
    p.rect(461, 600, 479, 785, 4, "#a8703a")
    p.circ(530, 700, 10, "#ffd43b", OL, 3)
    p.circ(300, 600, 50, "#fff3bf", OL, 6)
    p.line([(300, 552), (300, 648)], OL, 5)
    p.line([(252, 600), (348, 600)], OL, 5)
    p.rect(610, 380, 660, 470, 6, "#a35d3a", OL, 5)
    hills(p, 820, 18, "#69b84e", 23, 1.3)
    rnd = random.Random(4 + variant)
    cols = ["#ff8fab", "#ffd43b", "#ffffff", "#b197fc"]
    for _ in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(850, H)
        c = rnd.choice(cols)
        for i in range(5):
            a = 2 * math.pi * i / 5
            p.circ(x + 7 * math.cos(a), y + 7 * math.sin(a), 6, c)
        p.circ(x, y, 4, "#f59f00")
    for _ in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(830, H)
        for dx in (-8, 0, 8):
            p.circ(x + dx, y - abs(dx) * 0.6, 7, "#4f9e3a")
    img.alpha_composite(p.done())
    # big tree on the right
    t = Pen(600, 700, 2)
    t.rect(260, 300, 340, 700, 20, "#8b5a2b", OL, 5)
    for cx, cy, r, c in ((300, 230, 200, "#4f9e3a"), (170, 300, 120, "#5cb247"), (430, 300, 120, "#5cb247"), (300, 140, 140, "#69c055")):
        t.circ(cx, cy, r, c)
    for i in range(6):
        t.circ(200 + i * 40, 250 + (i % 2) * 60, 14, "#ff6b6b")
    img.alpha_composite(t.done(), (1420, 160))
    return img.convert("RGB")


@lru_cache(None)
def bg_kitchen():
    img = to_img(vgrad("#ffe8cc", "#ffd8a8"))
    p = Pen(W, H, 2)
    for x in range(0, W, 120):
        p.rect(x + 50, 0, x + 70, 700, 6, (255, 255, 255, 110))
    p.rect(0, 700, W, H, 0, "#d9a066")
    for x in range(0, W, 160):
        p.line([(x, 700), (x - 120, H)], "#c48a52", 4)
    # window
    p.rect(760, 120, 1160, 440, 30, "#a5d8ff", OL, 8)
    p.line([(960, 120), (960, 440)], OL, 8)
    p.line([(760, 280), (1160, 280)], OL, 8)
    p.circ(1060, 200, 40, "#fff3bf")
    p.rect(730, 430, 1190, 460, 10, "#f08c00", OL, 5)
    # shelf with jars and carrots
    p.rect(120, 260, 560, 290, 8, "#a0703c", OL, 5)
    for i, c in enumerate(("#ff8787", "#ffd43b", "#69db7c")):
        p.rect(150 + i * 130, 170, 240 + i * 130, 260, 18, c, OL, 5)
        p.rect(160 + i * 130, 150, 230 + i * 130, 175, 8, "#868e96", OL, 4)
    # table
    p.ell(1500, 760, 330, 70, "#c98d54", OL, 6)
    p.rect(1380, 770, 1420, 1000, 10, "#a8703a", OL, 5)
    p.rect(1580, 770, 1620, 1000, 10, "#a8703a", OL, 5)
    p.ell(1500, 742, 120, 30, "#ffffff", OL, 4)
    img.alpha_composite(p.done())
    for i in range(4):
        img.alpha_composite(carrot(90), (1420 + i * 45, 670))
    return img.convert("RGB")


@lru_cache(None)
def bg_bedroom():
    img = to_img(vgrad("#3b3f8f", "#5c5fb8"))
    p = Pen(W, H, 2)
    rnd = random.Random(2)
    for _ in range(40):
        p.circ(rnd.uniform(0, W), rnd.uniform(0, 650), rnd.uniform(3, 7), (255, 255, 255, 60))
    p.rect(0, 720, W, H, 0, "#7c5cbf")
    p.rect(1150, 130, 1550, 470, 40, "#1c1f4a", OL, 8)
    p.circ(1430, 230, 60, "#fff3bf")
    p.circ(1455, 210, 55, "#1c1f4a")
    for _ in range(12):
        p.circ(rnd.uniform(1180, 1520), rnd.uniform(160, 440), 4, "#ffffff")
    # bed
    p.rect(150, 560, 900, 820, 40, "#ffa8a8", OL, 6)
    p.rect(120, 470, 190, 900, 20, "#a0703c", OL, 6)
    p.rect(860, 600, 930, 900, 20, "#a0703c", OL, 6)
    p.ell(300, 560, 110, 50, "#ffffff", OL, 5)
    # lamp
    p.rect(1010, 640, 1110, 760, 10, "#a0703c", OL, 5)
    p.rect(1050, 520, 1070, 640, 6, "#868e96", OL, 4)
    p.poly([(990, 530), (1130, 530), (1095, 440), (1025, 440)], "#ffd43b", OL, 5)
    img.alpha_composite(p.done())
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([860, 330, 1260, 730], fill=(255, 230, 140, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    return img.convert("RGB")


@lru_cache(None)
def bg_picnic():
    img = _sky("#86d0ff", "#eaf9ff")
    p = Pen(W, H, 2)
    hills(p, 600, 40, "#a9dd8e", 31, 0.7)
    # pond
    p.ell(1500, 690, 360, 70, "#4dabf7", "#1c7ed6", 6)
    for x, y in ((1400, 680), (1580, 700)):
        p.ell(x, y, 40, 14, "#51cf66", OL, 3)
    hills(p, 760, 15, "#86cc6c", 32, 1.2)
    rnd = random.Random(8)
    for _ in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(800, H)
        c = rnd.choice(["#ff8fab", "#ffd43b", "#ffffff"])
        for i in range(5):
            a = 2 * math.pi * i / 5
            p.circ(x + 6 * math.cos(a), y + 6 * math.sin(a), 5, c)
    img.alpha_composite(p.done())
    for x in (80, 380):
        img.alpha_composite(_round_tree(), (x, 250))
    return img.convert("RGB")


@lru_cache(None)
def _round_tree():
    t = Pen(320, 480, 2)
    t.rect(130, 230, 190, 480, 16, "#8b5a2b", OL, 5)
    t.circ(160, 170, 150, "#5cb247")
    t.circ(90, 220, 80, "#69c055")
    t.circ(230, 220, 80, "#69c055")
    return t.done()


@lru_cache(None)
def logo_card(size=1.0):
    """'White Bunny' logo: bunny head + rounded title."""
    p = Pen(1200, 420, 2)
    p.rect(20, 40, 1180, 400, 180, (255, 255, 255, 235), "#ff8fab", 10)
    img = p.done()
    head = rabbit("bunny").crop((60, 0, 360, 400))
    head = head.resize((int(head.width * 0.78), int(head.height * 0.78)), Image.LANCZOS)
    img.alpha_composite(head, (40, 40))
    t = Pen(1200, 420, 2)
    t.text((735, 168), "White", "Fredoka-Bold.ttf", 140, "#4dabf7", stroke=10, sfill="#ffffff")
    t.text((735, 310), "Bunny", "Fredoka-Bold.ttf", 150, "#ff8fab", stroke=10, sfill="#ffffff")
    img.alpha_composite(t.done())
    if size != 1.0:
        img = img.resize((int(1200 * size), int(420 * size)), Image.LANCZOS)
    return img
