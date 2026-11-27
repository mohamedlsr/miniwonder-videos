"""Épisode 2 (aventure) : Le voyage de Plic, la goutte d'eau (le cycle de l'eau)."""
import math, random
from functools import lru_cache
from kit2 import *
import art
from art import Pen, eye, cheek

OL = "#3a2e2a"


# ================================================================ helpers
def line_at(S, t):
    i = -1
    for k, c in enumerate(S.cues):
        if c <= t + 0.05:
            i = k
    return i


def companion(sc, idxs):
    """Lines in idxs are spoken by the companion: Mini keeps her mouth closed, companion talks."""
    idxs = set(idxs)
    base = Scene.talking

    sc.talking = lambda t: base(sc, t) and line_at(sc, t) not in idxs
    sc.comp_talk = lambda t: base(sc, t) and line_at(sc, t) in idxs
    return sc


def comp_talk(S, t):
    f = getattr(S, "comp_talk", None)
    return bool(f and f(t))


def bob(S, t, amp=0.6, off=0.0):
    sx, sy, rot, hop = dance_params(S, t, amp, off)
    return sx, sy, rot, hop


def plic(F, S, t, x, y, size=170, alpha=1.0, rot=0.0, dance=True, sc=1.0):
    """Plic the drop, centred at (x, y). Opens her mouth on her own lines."""
    mouth = "open" if comp_talk(S, t) else "smile"
    eyes = "closed" if blinking(t, 1) else "open"
    sp = art.drop(size, mouth, eyes)
    if dance:
        sx, sy, r, hop = bob(S, t, 0.7, 0.4)
        F.put(sp, x, y - hop, sc, alpha=alpha, rot=rot + r, sx=sx, sy=sy)
    else:
        F.put(sp, x, y, sc, alpha=alpha, rot=rot)


def plic_fn(blink=False):
    return art.drop(170, "smile", "closed" if blink else "open")


# ================================================================ new characters
@lru_cache(None)
def bulle(blink=False, mouth="smile"):
    """Bulle, a little round orange fish (faces right)."""
    p = Pen(300, 220)
    p.poly([(70, 110), (8, 50), (22, 110), (8, 170)], "#e8590c")
    p.poly([(66, 110), (20, 62), (32, 110), (20, 158)], "#ff922b")
    p.poly([(120, 48), (175, 10), (200, 52)], "#e8590c")
    p.ell(165, 112, 108, 82, "#e8590c")
    p.ell(165, 110, 100, 75, "#ffa94d")
    p.ell(175, 140, 70, 38, "#ffd8a8")
    for xx in (120, 150):
        p.arc(xx, 110, 22, 70, 300, 60, (255, 255, 255, 150), 8)
    p.poly([(150, 150), (115, 185), (170, 168)], "#e8590c")
    eye(p, 222, 92, 17, look=(3, 0), closed=blink)
    cheek(p, 240, 128, 12)
    if mouth == "open":
        p.ell(262, 128, 9, 11, "#7a2e0c")
    else:
        p.arc(255, 124, 12, 9, 20, 150, "#7a2e0c", 4)
    return p.done()


def bulle_fn(blink=False):
    return bulle(blink)


@lru_cache(None)
def cumulo(blink=False, mouth="smile", grey=False, size=440):
    """Cumulo, a big soft cloud with a face and tiny arms."""
    p = Pen(440, 290)
    body = "#e3e9f2" if grey else "#ffffff"
    shade = "#9fb0c8" if grey else "#c9d6f5"
    p.ell(28, 190, 26, 18, shade)
    p.ell(412, 190, 26, 18, shade)
    blobs = [(110, 170, 80), (200, 110, 100), (300, 140, 85), (370, 185, 55), (60, 200, 50), (220, 195, 85)]
    for x, y, r in blobs:
        p.circ(x, y + 8, r, shade)
    for x, y, r in blobs:
        p.circ(x, y, r - 5, body)
    p.rect(60, 180, 390, 255, 36, body)
    p.ell(170, 80, 40, 18, (255, 255, 255, 200))
    eye(p, 185, 165, 16, closed=blink)
    eye(p, 260, 165, 16, closed=blink)
    cheek(p, 155, 200, 15)
    cheek(p, 290, 200, 15)
    if mouth == "open":
        p.ell(222, 208, 13, 15, "#55606e")
    else:
        p.arc(222, 196, 20, 13, 20, 160, "#55606e", 5)
    img = p.done()
    return img.resize((size, int(size * 290 / 440)), Image.LANCZOS) if size != 440 else img


def cumulo_fn(blink=False):
    return cumulo(blink, size=300)


@lru_cache(None)
def glacon(blink=False):
    """Plic frozen into an ice cube."""
    p = Pen(220, 220)
    p.rect(14, 22, 206, 212, 34, "#6cc6ea")
    p.rect(20, 18, 200, 200, 30, "#c5f1ff", "#6cc6ea", 6)
    p.poly([(40, 40), (80, 40), (44, 120)], (255, 255, 255, 190))
    p.circ(170, 46, 8, (255, 255, 255, 220))
    eye(p, 85, 110, 15, closed=blink)
    eye(p, 140, 110, 15, closed=blink)
    cheek(p, 66, 140, 12)
    cheek(p, 160, 140, 12)
    p.arc(112, 140, 16, 11, 20, 160, "#1c5d80", 5)
    return p.done()


@lru_cache(None)
def vapeur(blink=False):
    """Plic as water vapour: a pale swirly puff."""
    p = Pen(240, 240)
    for x, y, r in ((80, 150, 55), (125, 110, 70), (170, 150, 52), (120, 165, 60)):
        p.circ(x, y, r, (255, 255, 255, 140))
    for i in range(3):
        pts = [(70 + i * 50 + 12 * math.sin(k / 5 + i), 80 - k * 2.4) for k in range(25)]
        p.stroke(pts, (255, 255, 255, 150), 10, 4)
    eye(p, 100, 140, 13, closed=blink)
    eye(p, 148, 140, 13, closed=blink)
    cheek(p, 84, 166, 10)
    cheek(p, 164, 166, 10)
    p.arc(124, 164, 14, 9, 20, 160, "#4a6a8a", 4)
    return p.done()


@lru_cache(None)
def flocon(blink=False, size=260):
    """Plic as a six-branched snowflake."""
    p = Pen(260, 260)
    c = 130
    for pass_, (col, w) in enumerate((("#7cc4ef", 22), ("#f4fbff", 13))):
        for i in range(6):
            a = math.pi / 2 + i * math.pi / 3
            ex, ey = c + 118 * math.cos(a), c + 118 * math.sin(a)
            p.line([(c, c), (ex, ey)], col, w)
            for d, L in ((70, 30), (98, 20)):
                bx, by = c + d * math.cos(a), c + d * math.sin(a)
                for s in (-1, 1):
                    aa = a + s * 0.8
                    p.line([(bx, by), (bx + L * math.cos(aa), by + L * math.sin(aa))], col, w * 0.8)
    p.circ(c, c, 52, "#f4fbff", "#7cc4ef", 6)
    eye(p, c - 18, c - 4, 11, closed=blink)
    eye(p, c + 18, c - 4, 11, closed=blink)
    cheek(p, c - 32, c + 18, 9)
    cheek(p, c + 32, c + 18, 9)
    p.arc(c, c + 16, 12, 8, 20, 160, "#2f6f9e", 4)
    img = p.done()
    return img.resize((size, size), Image.LANCZOS) if size != 260 else img


def flocon_fn(blink=False):
    return flocon(blink, 200)


@lru_cache(None)
def pousse(blink=False, mouth="smile"):
    """Pousse, a young sprout with a round leafy face."""
    p = Pen(240, 320)
    p.stroke([(120, 310), (118, 230), (122, 160)], "#3f8f2e", 18, 14)
    p.poly(art.rot_ell(70, 225, 48, 22, -25, 30), "#5dbb63")
    p.poly(art.rot_ell(172, 205, 50, 22, 25, 30), "#5dbb63")
    p.line([(40, 238), (100, 214)], "#3f8f2e", 4)
    p.line([(140, 196), (205, 192)], "#3f8f2e", 4)
    p.circ(120, 96, 78, "#3f8f2e")
    p.circ(120, 92, 72, "#8fd16a")
    p.poly(art.rot_ell(120, 18, 16, 30, 0, 20), "#5dbb63")
    eye(p, 96, 90, 14, closed=blink)
    eye(p, 144, 90, 14, closed=blink)
    cheek(p, 78, 120, 12)
    cheek(p, 162, 120, 12)
    if mouth == "open":
        p.ell(120, 125, 11, 13, "#2b5d1f")
    else:
        p.arc(120, 116, 18, 12, 20, 160, "#2b5d1f", 5)
    return p.done()


def pousse_fn(blink=False):
    return pousse(blink)


@lru_cache(None)
def house(col="#ff8787", roof="#c2255c", s=1.0):
    p = Pen(130, 130)
    p.rect(15, 55, 115, 128, 6, col)
    p.poly([(5, 60), (65, 8), (125, 60)], roof)
    p.rect(52, 85, 78, 128, 4, "#7a4b2a")
    p.rect(24, 70, 44, 90, 3, "#fff3bf")
    p.rect(86, 70, 106, 90, 3, "#fff3bf")
    img = p.done()
    return img.resize((int(130 * s), int(130 * s)), Image.LANCZOS)


@lru_cache(None)
def faucet():
    p = Pen(420, 300, 2)
    p.rect(0, 60, 260, 130, 30, "#b0bec5", "#607d8b", 6)
    p.rect(200, 60, 300, 210, 34, "#b0bec5", "#607d8b", 6)
    p.rect(110, 20, 170, 70, 12, "#90a4ae", "#607d8b", 5)
    p.rect(60, 4, 220, 34, 14, "#4dabf7", "#1c7ed6", 5)
    p.rect(214, 200, 286, 230, 10, "#90a4ae", "#607d8b", 5)
    return p.done()


@lru_cache(None)
def toothbrush():
    p = Pen(320, 80)
    p.rect(10, 34, 230, 56, 11, "#ff6b81", "#c2255c", 4)
    p.rect(220, 28, 300, 50, 8, "#ffffff", "#adb5bd", 3)
    for x in range(228, 296, 10):
        p.line([(x, 28), (x, 8)], "#74c0fc", 5)
    return p.done()


@lru_cache(None)
def grid_img(blue):
    p = Pen(560, 240, 2)
    for i in range(10):
        x, y = 20 + (i % 5) * 106, 20 + (i // 5) * 106
        col = "#2d8fe0" if i < blue else "#4caf50"
        p.rect(x, y, x + 92, y + 92, 18, col, "#ffffff", 5)
    return p.done()


@lru_cache(None)
def bubble(size=30):
    p = Pen(40, 40)
    p.circ(20, 20, 16, (255, 255, 255, 70), (255, 255, 255, 220), 3)
    p.circ(14, 14, 4, (255, 255, 255, 230))
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def round_drop(size=40, flat=0.0):
    """A real raindrop: round (flat=0) or bun-shaped (flat=1)."""
    p = Pen(80, 80)
    ry = 30 * (1 - 0.35 * flat)
    p.ell(40, 46, 30, ry, "#3da7ec")
    if flat > 0:
        p.rect(10, 46, 70, 46 + ry * 0.55, 6, "#3da7ec")
    p.ell(30, 40, 7, 9, (255, 255, 255, 190))
    return p.done().resize((size, size), Image.LANCZOS)


# ================================================================ backgrounds
@lru_cache(None)
def bg_space():
    img = to_img(radial("#2b3f8f", "#0b1236", r=1300))
    p = Pen(W, H, 2)
    rnd = random.Random(12)
    for _ in range(170):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.5, 4.5)
        p.circ(x, y, r, (255, 255, 255, int(rnd.uniform(90, 230))))
    p.circ(1100, 150, 70, "#c9c3b5")
    p.circ(1078, 135, 14, "#aea796")
    p.circ(1125, 172, 10, "#aea796")
    img.alpha_composite(p.done())
    return img.convert("RGB")


SEA_Y = 520


@lru_cache(None)
def bg_sea(v=0):
    img = to_img(vgrad("#8ad4ff", "#e3f6ff"))
    sea = to_img(vgrad("#43b0f7", "#0b4f9c", h=H - SEA_Y))
    img.paste(sea, (0, SEA_Y))
    p = Pen(W, H, 2)
    rnd = random.Random(30 + v)
    if v == 1:
        p.ell(260, SEA_Y + 4, 210, 40, "#f2d28b")
        p.circ(240, SEA_Y - 40, 10, "#7a4b2a")
        p.rect(236, SEA_Y - 130, 246, SEA_Y - 10, 4, "#8d5a32")
        for a in (-60, -20, 20, 60, 100):
            r = math.radians(a - 90)
            p.stroke([(241, SEA_Y - 130), (241 + 80 * math.cos(r), SEA_Y - 130 + 40 * math.sin(r) + 20)], "#51cf66", 14, 4)
    for i in range(4):
        x0, y0 = rnd.uniform(0, W), SEA_Y
        p.poly([(x0, y0), (x0 + 120, y0), (x0 + 320, H), (x0 + 120, H)], (255, 255, 255, 22))
    hills(p, 1000, 22, "#e9c98a", 31 + v, 0.8)
    for _ in range(9):
        x = rnd.uniform(0, W)
        hgt = rnd.uniform(90, 200)
        pts = [(x + 14 * math.sin(k / 4), 1040 - k * hgt / 30) for k in range(31)]
        p.stroke(pts, "#2f9e44", 16, 6)
    for _ in range(8):
        p.ell(rnd.uniform(0, W), rnd.uniform(1010, 1070), rnd.uniform(20, 45), rnd.uniform(12, 22), "#adb5bd")
    for x in range(0, W + 60, 60):
        p.arc(x + 30, SEA_Y, 30, 10, 200, 340, "#ffffff", 5)
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_room(v=0):
    if v == 0:
        img = to_img(vgrad("#fff3d6", "#ffe0b0"))
    else:
        img = to_img(vgrad("#e3f4ff", "#c3e6ff"))
    p = Pen(W, H, 2)
    if v == 0:
        p.rect(140, 150, 560, 560, 20, "#ffffff", "#c98f4f", 12)
        p.rect(152, 162, 548, 548, 12, "#9fdcff")
        p.circ(300, 300, 50, "#ffe066")
        p.ell(450, 420, 80, 30, "#ffffff")
        p.line([(350, 162), (350, 548)], "#c98f4f", 10)
        p.line([(152, 355), (548, 355)], "#c98f4f", 10)
        p.rect(700, 330, 1100, 350, 6, "#c98f4f")
        for i, col in enumerate(("#ff8787", "#74c0fc", "#69db7c", "#ffd43b")):
            p.rect(720 + i * 55, 250, 760 + i * 55, 330, 6, col)
    else:
        for x in range(0, W, 120):
            p.line([(x, 0), (x, 820)], (255, 255, 255, 160), 4)
        for y in range(0, 820, 120):
            p.line([(0, y), (W, y)], (255, 255, 255, 160), 4)
        p.rect(130, 140, 470, 420, 30, "#d0ebff", "#ffffff", 10)
    p.rect(-10, 820, W + 10, H + 10, 0, "#c98f4f" if v == 0 else "#f1f3f5")
    p.rect(-10, 820, W + 10, 850, 0, "#a86f35" if v == 0 else "#ced4da")
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_highsky(v=0):
    img = to_img(vgrad("#3d7fd9", "#c6e9ff"))
    p = Pen(W, H, 2)
    rnd = random.Random(50 + v)
    for _ in range(6):
        x, y = rnd.uniform(0, W), rnd.uniform(120, 700)
        for k in range(4):
            p.circ(x + k * 50, y + (k % 2) * 12, 40, (255, 255, 255, 55))
    p.poly([(300, 1040), (520, 900), (740, 1040)], "#a9c4dc")
    p.poly([(1200, 1040), (1450, 880), (1700, 1040)], "#a9c4dc")
    hills(p, 1020, 14, "#9fd18a", 52 + v, 0.6)
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_rain():
    img = to_img(vgrad("#8aa4bf", "#dde7f0"))
    p = Pen(W, H, 2)
    hills(p, 760, 40, "#8cc976", 61, 0.7)
    hills(p, 850, 30, "#74b85f", 62, 1.1)
    img.alpha_composite(p.done())
    for x, y, col, roof, s in ((1050, 790, "#ff8787", "#c2255c", 0.9), (1180, 800, "#ffd43b", "#e8590c", 0.8),
                               (1320, 810, "#74c0fc", "#1c7ed6", 0.9), (1460, 820, "#b197fc", "#6741d9", 0.75)):
        hs = house(col, roof, s)
        img.alpha_composite(hs, (int(x), int(y - hs.height + 20)))
    p = Pen(W, H, 2)
    for x, y in ((300, 980), (800, 1010), (1500, 1000)):
        p.ell(x, y, 120, 22, "#6aa7d8")
        p.ell(x - 30, y - 6, 40, 6, (255, 255, 255, 120))
    img.alpha_composite(p.done())
    return img.convert("RGB")


STREAM = art.bezier((690, 390), (560, 620), (900, 760), (1180, 1000), 80)


@lru_cache(None)
def bg_mountain(winter=True):
    img = to_img(vgrad("#a9d6f5", "#eef8ff") if winter else vgrad("#7cc8f5", "#e6f7ff"))
    p = Pen(W, H, 2)
    p.poly([(900, 1000), (1350, 420), (1800, 1000)], "#9aabbf")
    p.poly([(120, 1000), (700, 240), (1300, 1000)], "#8394ab")
    if winter:
        p.poly([(1350, 420), (1100, 740), (1600, 740)], "#ffffff")
        p.poly([(700, 240), (330, 720), (1070, 720)], "#ffffff")
        hills(p, 760, 30, "#ffffff", 71, 0.7)
        hills(p, 860, 25, "#eef6ff", 72, 1.0)
    else:
        p.poly([(1350, 420), (1270, 520), (1310, 505), (1350, 530), (1390, 505), (1430, 520)], "#ffffff")
        p.poly([(700, 240), (590, 385), (640, 370), (690, 400), (740, 368), (800, 385)], "#ffffff")
        hills(p, 800, 30, "#7cc35a", 71, 0.7)
        hills(p, 900, 22, "#69b34c", 72, 1.0)
        p.stroke(STREAM, "#3da7ec", 18, 70)
        rnd = random.Random(73)
        for _ in range(30):
            x, y = rnd.uniform(0, W), rnd.uniform(900, 1060)
            p.circ(x, y, 9, rnd.choice(["#ff6fa5", "#ffd43b", "#ffffff"]))
    img.alpha_composite(p.done())
    if winter:
        p = Pen(W, H, 2)
        for x in (150, 1650, 1780):
            p.poly([(x, 760), (x - 50, 880), (x + 50, 880)], "#2f9e44")
            p.poly([(x, 790), (x - 42, 880), (x + 42, 880)], "#ffffff" if x != 1650 else "#2f9e44")
            p.rect(x - 8, 880, x + 8, 910, 3, "#7a4b2a")
        img.alpha_composite(p.done())
    return img.convert("RGB")


GROUND_Y = 430


@lru_cache(None)
def bg_ground():
    img = to_img(vgrad("#8fd3ff", "#e8f7ff"))
    soil = to_img(vgrad("#a0682e", "#5e3a1a", h=H - GROUND_Y))
    img.paste(soil, (0, GROUND_Y))
    p = Pen(W, H, 2)
    hills(p, 380, 20, "#a5d68a", 81, 0.8)
    p.rect(-10, GROUND_Y - 10, W + 10, GROUND_Y + 22, 0, "#6abf4b")
    rnd = random.Random(82)
    for x in range(0, W, 14):
        p.line([(x, GROUND_Y), (x + rnd.uniform(-5, 5), GROUND_Y - rnd.uniform(10, 26))], "#5aad3e", 4)
    for _ in range(160):
        p.ell(rnd.uniform(0, W), rnd.uniform(GROUND_Y + 40, 820), rnd.uniform(4, 12), rnd.uniform(3, 8), "#7d4f26")
    p.rect(-10, 860, W + 10, 1010, 40, "#4aa3e8")
    for _ in range(60):
        p.circ(rnd.uniform(0, W), rnd.uniform(870, 1000), rnd.uniform(10, 22), "#8c9aa6", "#6c7a86", 3)
    for _ in range(25):
        p.ell(rnd.uniform(0, W), rnd.uniform(880, 990), 14, 6, (255, 255, 255, 120))
    img.alpha_composite(p.done())
    return img.convert("RGB")


# ================================================================ sky extras
def sky_light(F, S, t):
    sun2(F, S, t, 1640, 170, 210)
    drift_clouds(F, t, 2, 150, seed=3 + S.idx, scale=0.6)


def sea_sky(F, S, t):
    sun2(F, S, t, 1620, 160, 220)
    birds(F, S, t, 210)
    rnd = random.Random(S.idx)
    for i in range(10):
        x = rnd.uniform(0, W)
        y = H - ((t * rnd.uniform(40, 80) + rnd.uniform(0, 500)) % (H - SEA_Y - 40))
        F.put(bubble(rnd.choice((22, 30, 38))), x + 10 * math.sin(t * 2 + i), y)


def rain_fx(F, S, t, x0, x1, y0, y1, n=40, k=1.0, seed=0):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1)
        ph = (t * rnd.uniform(1.2, 1.8) + rnd.uniform(0, 1)) % 1
        F.put(art.raindrop(24), x, y0 + ph * (y1 - y0), alpha=k)


def snow_fx(F, t, n=40, seed=0, x0=0, x1=W, y0=0, y1=H, k=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1)
        ph = (t * rnd.uniform(0.08, 0.16) + rnd.uniform(0, 1)) % 1
        F.put(art.snowflake(rnd.choice((26, 34, 42))), x + 30 * math.sin(t + i), y0 + ph * (y1 - y0),
              rot=(t * 40 + i * 30) % 360, alpha=k)


# ================================================================ 0. intro
def intro_extras(F, S, t):
    for i in range(14):
        x = (i * 173 + 60) % W
        y = H + 80 - ((t * (50 + i * 6) + i * 140) % (H + 200))
        F.put(bubble(36 + (i % 3) * 10), x + 30 * math.sin(t + i), y)
    t0 = S.cue(2) + 0.3
    if t > t0:
        k = back_out(prog(t, t0, 0.7), 2.2)
        plic(F, S, t, 1240, 880 + (1 - k) * 500, 200)
        sparkle_burst(F, 1240, 860, t, t0 + 0.4, 12, 200, seed=4)


s_intro = companion(intro2("Le voyage de la goutte d'eau", [
    "Coucou les petits curieux ! C'est Mini, l'étoile de MiniWonder !",
    "Sais-tu d'où vient l'eau de la pluie ? À la fin de cette vidéo, tu connaîtras son grand secret !",
    "Je te présente mon amie Plic, une petite goutte d'eau. Aujourd'hui, nous partons avec elle pour un très grand voyage !",
    "Plic s'écrie : Youpi ! En route pour l'aventure !",
], bg_intro, extras=intro_extras, title_ol="#1c7ed6"), [3])
_i = s_intro.sfx_fn
s_intro.sfx_fn = lambda S: _i(S) + [("boing", S.cue(2) + 0.4), ("sparkle", S.cue(2) + 0.6)]


# ================================================================ 1. la planète bleue
def earth_actor(F, S, t, shift):
    k = back_out(prog(t, 0.4, 0.9))
    ex = 520 - shift * 120
    F.put(art.earth(400), ex, 480 + math.sin(t * 1.5) * 10, sc=max(0.01, k), rot=math.sin(t * 0.8) * 5)
    plic(F, S, t, ex + 230, 310, 90, alpha=clamp(t - 1.0))
    t1 = S.cue(1) + 2.2
    if t > t1:
        n = min(10, int((t - t1) / 0.2) + 1)
        kk = back_out(prog(t, t1, 0.5))
        out = ease_in_out(prog(t, S.cue(4) - 0.5, 0.4))
        F.put(grid_img(min(7, n)), 520, 860 + out * 500, sc=max(0.01, kk * 0.85))


s_planet = topic2("LA PLANÈTE BLEUE", [
    "Notre voyage commence très haut, dans l'espace. Regarde la Terre : elle est presque toute bleue !",
    "C'est parce que l'eau recouvre environ sept dixièmes de sa surface. Sur dix carrés, sept sont bleus !",
    "Presque toute cette eau est salée : c'est l'eau des mers et des océans.",
    "L'eau douce, celle des rivières et des lacs, est beaucoup plus rare.",
    "Le savais-tu ? La plus grande partie de l'eau douce de la Terre est gelée, dans la glace des pôles et des glaciers !",
], bg_space, earth_actor,
    chip_items=[(1, "7 sur 10 = de l'eau", "#1c7ed6"), (2, "Les mers : eau salée", "#4dabf7"), (3, "L'eau douce est rare", "#51cf66")],
    fact=(4, "La plus grande partie de l'eau douce de la Terre est gelée, dans la glace des pôles et des glaciers !"),
    lab_bg="#1c7ed6", fact_cx=1300)


# ================================================================ 2. l'océan
def ocean_actor(F, S, t, shift):
    plic(F, S, t, 700 - shift * 300, SEA_Y + 10, 160)
    t0 = S.cue(1) - 0.2
    if t > t0:
        k = ease_out(prog(t, t0, 1.6))
        x = -200 + k * (520 - shift * 200 + 200)
        y = 820 + math.sin(t * 2.2) * 25
        F.put(bulle(blinking(t, 2), "open" if comp_talk(S, t) else "smile"), x, y, 0.95,
              rot=math.sin(t * 3) * 5)
    if t > S.cue(4) - 0.2:
        k = ease_out(prog(t, S.cue(4) - 0.2, 2.5))
        F.put(art.sun_rays(260), 1620, 160 + 0 * k, sc=1 + 0.15 * k, rot=(t * 30) % 360, alpha=0.6 * k)


s_ocean = companion(topic2("DANS L'OCÉAN", [
    "Zoom ! Nous voici dans l'océan. C'est ici que vit Plic, avec des milliards et des milliards d'autres gouttes.",
    "Plic s'exclame : Je te présente mon voisin, Bulle, le petit poisson !",
    "L'eau de mer est très salée. Si tu en as déjà bu une gorgée à la plage, tu t'en souviens sûrement !",
    "Le savais-tu ? Sur cent gouttes d'eau de la Terre, environ quatre-vingt-dix-sept se trouvent dans les océans !",
    "Mais aujourd'hui, Plic a envie de voir le monde. Et justement, le soleil brille très fort...",
], lambda: bg_sea(0), ocean_actor, extras=sea_sky,
    chip_items=[(2, "L'eau de mer est salée", "#1c7ed6")],
    fact=(3, "Sur 100 gouttes d'eau de la Terre, environ 97 se trouvent dans les océans !"),
    lab_bg="#0b7285", fact_cx=1250), [1])


# ================================================================ 3. évaporation
def evap_actor(F, S, t, shift):
    t1 = S.cue(1) + 1.2
    if t < t1:
        plic(F, S, t, 760, SEA_Y + 10, 160)
    else:
        k = ease_in_out(prog(t, t1, 5.0))
        x = 760 - 100 * k + 40 * math.sin(t * 2) - shift * 200
        y = SEA_Y + 10 - 230 * k
        a = 1 - k
        if a > 0.02:
            plic(F, S, t, x, y, 160, alpha=a)
        if k > 0.02:
            sx, sy, r, hop = bob(S, t, 0.6)
            F.put(vapeur(blinking(t, 4)), x, y - hop, 0.9, alpha=min(1, k * 1.4), rot=r)
        sparkle_burst(F, 760, SEA_Y, t, t1, 12, 220, seed=8)
    if t > S.cue(0):
        for i in range(9):
            ph = (t * 0.4 + i / 9) % 1
            x = 250 + i * 110 + 20 * math.sin(t + i)
            F.put(art.steam(55), x, SEA_Y - ph * 360, alpha=math.sin(ph * math.pi) * 0.8 * clamp(t - S.cue(0)))


s_evap = companion(topic2("L'ÉVAPORATION", [
    "Le soleil chauffe la surface de la mer. L'eau devient toute tiède...",
    "Plic se sent de plus en plus légère... Pouf ! Elle se transforme en vapeur d'eau, un gaz invisible !",
    "Plic s'envole tout doucement vers le ciel. Ce changement s'appelle l'évaporation.",
    "Plic rigole : Hi hi ! On ne me voit plus, mais je suis toujours là !",
    "Le savais-tu ? C'est grâce à l'évaporation que le linge mouillé sèche au soleil, et que les flaques disparaissent !",
], lambda: bg_sea(1), evap_actor, extras=sea_sky,
    chip_items=[(1, "L'eau devient vapeur", "#ff922b"), (2, "= l'évaporation", "#e8590c")],
    fact=(4, "C'est grâce à l'évaporation que le linge mouillé sèche au soleil, et que les flaques disparaissent !"),
    lab_bg="#ff922b"), [3])
_e = s_evap.sfx_fn
s_evap.sfx_fn = lambda S: _e(S) + [("whoosh", S.cue(1) + 1.1), ("sparkle", S.cue(1) + 1.2)]


# ================================================================ 4. les trois états
def states_actor(F, S, t, shift):
    xs = (290, 620, 950)
    fns = (glacon, plic_fn, vapeur)
    for i in range(3):
        t0 = S.cue(i + 1) - 0.1
        if t > t0:
            k = back_out(prog(t, t0, 0.5), 2.4)
            sx, sy, r, hop = bob(S, t, 0.8, i * 0.3)
            F.put(fns[i](blinking(t, i)), xs[i], 840 - hop, sc=max(0.05, k * 0.95), rot=r, anchor="b", sx=sx, sy=sy)
            sparkle_burst(F, xs[i], 700, t, t0, 10, 160, seed=i + 20)
            if i == 2:
                for j in range(3):
                    ph = (t * 0.6 + j / 3) % 1
                    F.put(art.steam(40), xs[i] - 50 + j * 50, 600 - ph * 160, alpha=math.sin(ph * math.pi) * 0.8)
    if t > S.cue(4):
        k = ease_out(prog(t, S.cue(4), 0.6))
        for i in range(2):
            x = (xs[i] + xs[i + 1]) / 2
            F.put(_arrow(), x, 740, sc=max(0.05, k))


@lru_cache(None)
def _arrow():
    p = Pen(110, 70)
    p.rect(5, 26, 70, 44, 9, "#ffffff", "#3a2e2a", 4)
    p.poly([(62, 8), (105, 35), (62, 62)], "#ffffff", "#3a2e2a", 4)
    return p.done()


s_states = topic2("LES 3 ÉTATS DE L'EAU", [
    "Attends, Plic ! Avant de monter, explique-nous ce qui t'arrive. L'eau sait changer de forme !",
    "Quand il fait très froid, l'eau devient dure et solide : c'est la glace.",
    "D'habitude, elle est liquide : elle coule, comme l'eau du robinet.",
    "Et quand on la chauffe, elle devient un gaz : la vapeur d'eau.",
    "Solide, liquide, gaz : ce sont les trois états de l'eau. Et c'est toujours la même eau !",
], lambda: bg_room(0), states_actor,
    chip_items=[(1, "Solide : la glace", "#4dabf7"), (2, "Liquide : l'eau", "#1c7ed6"), (3, "Gaz : la vapeur", "#845ef7")],
    lab_bg="#20c997")
_s = s_states.sfx_fn
s_states.sfx_fn = lambda S: _s(S) + [("boing", S.cue(i + 1)) for i in range(3)]


# ================================================================ 5. condensation
def cond_actor(F, S, t, shift):
    cx, cy = 640 - shift * 170, 420
    t1 = S.cue(1) + 0.6
    k_drop = ease_out(prog(t, t1, 1.0))
    # Plic: vapour rising, then a droplet again
    y_p = 900 - 380 * ease_out(prog(t, 0.3, 4.0))
    if k_drop < 1:
        sx, sy, r, hop = bob(S, t, 0.6)
        F.put(vapeur(blinking(t, 4)), cx + 220, y_p, 0.8, alpha=1 - k_drop)
    if k_drop > 0:
        plic(F, S, t, cx + 220, y_p, 120, alpha=k_drop)
    # droplets gathering into a cloud
    t2 = S.cue(2)
    kc = ease_out(prog(t, t2 + 1.0, 2.0))
    if t > t2 - 0.5:
        rnd = random.Random(3)
        for i in range(30):
            a = rnd.uniform(0, 2 * math.pi)
            r0 = rnd.uniform(260, 560)
            g = ease_in_out(prog(t, t2 - 0.5 + rnd.uniform(0, 1.2), 2.0))
            r = r0 * (1 - g) + 30 * g
            F.put(round_drop(26), cx + r * math.cos(a), cy + 0.55 * r * math.sin(a), alpha=1 - kc)
    if kc > 0:
        F.put(cumulo(blinking(t, 5), size=420), cx - 120, cy, sc=max(0.05, 0.3 + 0.7 * kc))
    # thermometer
    kt = back_out(prog(t, S.cue(0) + 1.5, 0.5))
    out = ease_in_out(prog(t, S.cue(2) - 0.4, 0.3))
    if kt > 0 and out < 1:
        F.put(art.icon("heat", 150), 180, 330, sc=max(0.05, kt * (1 - out)))
        snow_fx(F, t, 6, 9, 100, 300, 250, 480, 1 - out)


s_cond = topic2("LA CONDENSATION", [
    "Plic monte, monte, toujours plus haut. Brrr ! Plus on monte, plus l'air est froid.",
    "Avec le froid, la vapeur redevient de minuscules gouttelettes d'eau. Plic retrouve sa forme !",
    "Des milliards de gouttelettes se serrent les unes contre les autres, et forment... un nuage !",
    "Ce changement s'appelle la condensation.",
    "Le savais-tu ? Tu peux voir la condensation chez toi : souffle sur une vitre froide, et elle se couvre de buée !",
], lambda: bg_highsky(0), cond_actor,
    chip_items=[(0, "En haut, il fait froid", "#4dabf7"), (3, "= la condensation", "#845ef7")],
    fact=(4, "Souffle sur une vitre froide : elle se couvre de buée. C'est de la condensation !"),
    lab_bg="#845ef7")


# ================================================================ 6. Cumulo
def cumulo_actor(F, S, t, shift):
    cx = 560 - shift * 120
    cy = 480
    sx, sy, r, hop = bob(S, t, 0.5)
    talk = comp_talk(S, t) and line_at(S, t) == 1
    F.put(cumulo(blinking(t, 5), "open" if talk else "smile", size=520), cx, cy - hop * 0.5, rot=r * 0.5, sx=sx, sy=sy)
    # Plic peeks out of the cloud
    k = back_out(prog(t, S.cue(0) - 0.3, 0.6))
    if k > 0:
        F.put(art.drop(110, "open" if (comp_talk(S, t) and line_at(S, t) == 0) else "smile",
                       "closed" if blinking(t, 1) else "open"),
              cx + 250 + 0 * k, cy + 150 - 40 * k)
    if t > S.cue(2):
        rnd = random.Random(7)
        for i in range(14):
            a = rnd.uniform(0, 2 * math.pi)
            rr = rnd.uniform(60, 200)
            F.put(round_drop(22), cx + rr * math.cos(a + t * 0.4), cy + 0.45 * rr * math.sin(a + t * 0.4),
                  alpha=0.85 * clamp(t - S.cue(2)) * (1 - shift))


s_cumulo = companion(topic2("CUMULO LE NUAGE", [
    "Plic s'écrie : Oh ! Bonjour ! Mais qui es-tu, toi ?",
    "Je te présente Cumulo, un gros nuage tout doux. Plic et ses amies les gouttelettes vivent maintenant dans son ventre !",
    "Un nuage n'est pas fait de coton : il est fait de minuscules gouttelettes d'eau, ou de tout petits cristaux de glace.",
    "Le savais-tu ? Un nuage peut peser aussi lourd que des dizaines d'éléphants ! Mais ses gouttelettes sont si petites qu'elles flottent dans l'air.",
    "Reste bien avec nous : tout à l'heure, il y aura un petit quiz !",
], lambda: bg_highsky(1), cumulo_actor, extras=sky_light,
    chip_items=[(2, "Nuage = gouttelettes", "#4dabf7")],
    fact=(3, "Un nuage peut peser aussi lourd que des dizaines d'éléphants ! Ses gouttelettes sont si petites qu'elles flottent."),
    lab_bg="#5c7cfa", fact_cx=1300), [0])


# ================================================================ 7. la pluie
def rain_actor(F, S, t, shift):
    cx, cy = 560 - shift * 120, 300
    grow = ease_in_out(prog(t, 0.3, S.cue(1) - 0.6))
    shake = math.sin(t * 30) * 5 * grow if t < S.cue(1) else 0
    F.put(cumulo(blinking(t, 5), "smile", True, 500), cx + shake, cy, sc=1 + 0.08 * grow)
    if t > S.cue(1) - 0.3:
        k = clamp((t - S.cue(1) + 0.3) * 2)
        rain_fx(F, S, t, cx - 220, cx + 220, cy + 120, 1000, 34, k, seed=2)
    # Plic hangs below the cloud, swinging
    sw = math.sin(t * 2.4) * 12
    if t > 0.8:
        F.put(art.drop(120, "open" if comp_talk(S, t) else "smile", "closed" if blinking(t, 1) else "open"),
              cx + 230, cy + 150, rot=sw)
    # real drop shapes (fact)
    if t > S.cue(4) - 0.3:
        pass


s_rain = companion(topic2("LA PLUIE", [
    "Dans Cumulo, les gouttelettes se collent ensemble. Elles grossissent, et deviennent de plus en plus lourdes...",
    "Trop lourdes ! Des milliers de gouttes tombent du nuage : c'est la pluie !",
    "Plic s'accroche à Cumulo et crie : Pas encore moi ! Je veux voir la montagne !",
    "La pluie, la neige et la grêle, c'est de l'eau qui tombe du ciel. On les appelle les précipitations.",
    "Le savais-tu ? Les vraies gouttes de pluie n'ont pas la forme d'une larme ! Les petites sont rondes comme des billes, et les grosses ressemblent à un petit pain aplati.",
], bg_rain, rain_actor,
    chip_items=[(1, "La pluie tombe", "#4dabf7"), (3, "= les précipitations", "#ff6b81")],
    fact=(4, "Les vraies gouttes de pluie n'ont pas la forme d'une larme : les petites sont rondes, les grosses ressemblent à un petit pain !"),
    lab_bg="#4dabf7", fact_cx=1300), [2])
_r = s_rain.sfx_fn
s_rain.sfx_fn = lambda S: _r(S) + [("whoosh", S.cue(1) - 0.3)]


# ================================================================ 8. la neige
def snow_actor(F, S, t, shift):
    k_move = ease_in_out(prog(t, 0.3, S.cue(1) - 0.5))
    cx = -150 + k_move * 800 - shift * 150
    F.put(cumulo(blinking(t, 5), "smile", True, 400), cx, 310)
    if t > S.cue(1) - 0.5:
        snow_fx(F, t, 45, 4, 0, 1150, 0, 1000, clamp(t - S.cue(1) + 0.5))
    t1 = S.cue(1) + 1.4
    if t < t1:
        F.put(art.drop(100, "smile", "closed" if blinking(t, 1) else "open"), cx + 150, 440)
    else:
        k = ease_in_out(prog(t, t1, 4.5))
        x = 790 + 40 * math.sin(t * 1.6) - shift * 300
        y = 440 + k * 190
        if line_at(S, t) >= 4:
            y = 630 + ease_in_out(prog(t, S.cue(4), 2.5)) * 70
        sx, sy, r, hop = bob(S, t, 0.5)
        F.put(flocon(blinking(t, 1), 220), x, y, rot=math.sin(t * 1.2) * 15)
        sparkle_burst(F, x, y, t, t1, 12, 180, seed=11)


s_snow = companion(topic2("LA NEIGE", [
    "Le vent pousse Cumulo au-dessus d'une très haute montagne. Là-haut, il fait très, très froid.",
    "L'eau gèle et forme de minuscules cristaux de glace. Plic tombe tout doucement... en flocon de neige !",
    "Plic s'émerveille : Regarde-moi ! J'ai six jolies branches !",
    "Le savais-tu ? Presque tous les flocons de neige ont six branches. Et on dit qu'il n'existe pas deux flocons exactement pareils !",
    "Plic se pose sur la montagne, et dort sous la neige tout l'hiver.",
], lambda: bg_mountain(True), snow_actor,
    chip_items=[(1, "Il gèle : la neige", "#74c0fc")],
    fact=(3, "Presque tous les flocons ont six branches. Et on dit qu'il n'existe pas deux flocons exactement pareils !"),
    lab_bg="#339af0", fact_cx=1300), [2])
_n = s_snow.sfx_fn
s_snow.sfx_fn = lambda S: _n(S) + [("sparkle", S.cue(1) + 1.4)]


# ================================================================ 9. la fonte
def along(path, k):
    k = clamp(k)
    i = k * (len(path) - 1)
    a = int(i)
    b = min(a + 1, len(path) - 1)
    f = i - a
    return path[a][0] * (1 - f) + path[b][0] * f, path[a][1] * (1 - f) + path[b][1] * f


def melt_actor(F, S, t, shift):
    t_wake = S.cue(1) + 0.5
    if t < t_wake:
        F.put(flocon(blinking(t, 1) or True, 160), 690, 360)
    else:
        km = ease_in_out(prog(t, t_wake, 0.8))
        if km < 1:
            F.put(flocon(True, 160), 690, 360, alpha=1 - km)
        kpath = ease_in_out(prog(t, S.cue(2), S.end(3) - S.cue(2)))
        x, y = along(STREAM, kpath)
        plic(F, S, t, x, y - 40, 120, alpha=km)
    if t > S.cue(2):
        rnd = random.Random(5)
        for i in range(10):
            ph = (t * 0.25 + i / 10) % 1
            x, y = along(STREAM, ph)
            F.put(round_drop(28), x + rnd.uniform(-12, 12), y - 10, alpha=0.9)


s_melt = companion(topic2("LA FONTE DES NEIGES", [
    "Puis le printemps arrive. Le soleil réchauffe la montagne.",
    "La neige fond, et redevient de l'eau liquide. Plic se réveille : Bonjour, le printemps !",
    "Avec des milliers d'autres gouttes, elle glisse le long de la pente, et forme un petit ruisseau.",
    "Les ruisseaux se rejoignent, et deviennent une grande rivière. Ce voyage de l'eau sur le sol s'appelle le ruissellement.",
    "Le savais-tu ? Dans certaines régions, une grande partie de l'eau des rivières vient de la neige fondue des montagnes !",
], lambda: bg_mountain(False), melt_actor, extras=sky_light,
    chip_items=[(1, "La neige fond", "#ff922b"), (2, "Le ruisseau", "#4dabf7"), (3, "= le ruissellement", "#1c7ed6")],
    fact=(4, "Dans certaines régions, une grande partie de l'eau des rivières vient de la neige fondue des montagnes !"),
    lab_bg="#51cf66", fact_cx=1300), [])
# Plic speaks only the second half of line 1; keep Mini as narrator there.


# ================================================================ 10. sous la terre
def ground_actor(F, S, t, shift):
    # infiltrating drops
    if t > S.cue(0):
        for i in range(8):
            ph = (t * 0.35 + i / 8) % 1
            x = 220 + i * 110
            F.put(round_drop(30), x + 10 * math.sin(t + i), GROUND_Y + 30 + ph * 420,
                  alpha=math.sin(ph * math.pi) * clamp(t - S.cue(0)))
    # Plic travels down then to the roots
    kd = ease_in_out(prog(t, S.cue(0) + 0.5, 4.0))
    px, py = 380, GROUND_Y + 60 + kd * 420
    if t > S.cue(2):
        kr = ease_in_out(prog(t, S.cue(2), 2.0))
        px = 380 + kr * 330
        py = GROUND_Y + 480 - kr * 280
    if t > S.cue(3) + 0.3:
        kv = ease_in_out(prog(t, S.cue(3) + 0.3, 3.0))
        if kv < 1:
            plic(F, S, t, px, py, 90, alpha=1 - kv)
    else:
        plic(F, S, t, px, py, 90)
    # Pousse with roots
    k = back_out(prog(t, S.cue(2) - 0.3, 0.6), 2.2)
    if k > 0:
        px0 = 760
        p_roots = _roots()
        F.put(p_roots, px0, GROUND_Y + 10, sc=max(0.05, k), anchor="c")
        sx, sy, r, hop = bob(S, t, 0.6)
        F.put(pousse(blinking(t, 6), "open" if comp_talk(S, t) else "smile"), px0, GROUND_Y + 20 - hop,
              sc=max(0.05, k), anchor="b", sx=sx, sy=sy, rot=r)
    # transpiration wisps
    if t > S.cue(3):
        for j in range(4):
            ph = (t * 0.5 + j / 4) % 1
            F.put(art.steam(40), 700 + j * 40, GROUND_Y - 220 - ph * 160, alpha=math.sin(ph * math.pi) * 0.85)
        kv = ease_in_out(prog(t, S.cue(3) + 0.3, 3.0))
        if kv > 0:
            F.put(vapeur(blinking(t, 4)), 760 + 60 * kv, GROUND_Y - 260 - 120 * kv, 0.55, alpha=kv)


@lru_cache(None)
def _roots():
    p = Pen(300, 420)
    for ang, L in ((-0.5, 300), (0.0, 360), (0.45, 290), (-0.9, 180), (0.9, 170)):
        pts = [(150 + math.sin(ang) * L * k / 30 + 8 * math.sin(k / 3), 210 + math.cos(ang) * L * k / 30 * 0.55)
               for k in range(31)]
        p.stroke(pts, "#e8d2a6", 10, 3)
    return p.done()


s_ground = companion(topic2("SOUS LA TERRE", [
    "Sur le chemin, une partie de l'eau rentre dans le sol. Elle se faufile entre les grains de terre et les cailloux.",
    "Elle remplit des réserves cachées sous nos pieds : ce sont les nappes d'eau souterraines.",
    "Là, Plic rencontre Pousse, une jeune plante. Pousse dit : Merci Plic ! Je bois l'eau avec mes racines. Glouglou !",
    "Ensuite, la plante relâche de la vapeur d'eau par ses feuilles. C'est encore un chemin vers le ciel !",
    "Le savais-tu ? Un grand arbre peut relâcher des centaines de litres d'eau en une seule journée !",
], bg_ground, ground_actor,
    chip_items=[(0, "L'eau entre dans le sol", "#a0682e"), (1, "Les nappes souterraines", "#1c7ed6"), (2, "Les racines boivent", "#2f9e44")],
    fact=(4, "Un grand arbre peut relâcher des centaines de litres d'eau en une seule journée !"),
    lab_bg="#a0682e", fact_cx=1300, chips_y0=520), [2])


# ================================================================ 11. retour à la mer
PATH_RIVER = art.bezier((420, 880), (650, 980), (900, 900), (1150, 930), 60) + \
    art.bezier((1150, 930), (1300, 920), (1420, 880), (1520, 860), 30)


def return_actor(F, S, t, shift):
    k = ease_in_out(prog(t, 0.6, S.end(1) - 0.8))
    x, y = along(PATH_RIVER, k)
    plic(F, S, t, x, y - 50, 110)
    t0 = S.cue(1) + 1.2
    if t > t0:
        kk = prog(t, t0, 1.0)
        jump = math.sin(math.pi * min(1, kk)) * 160 if kk < 1 else 0
        F.put(bulle(blinking(t, 2), "open" if comp_talk(S, t) else "smile"), 1350, 960 - jump, 0.75,
              rot=-20 * math.sin(math.pi * min(1, kk)), flip=True)
        sparkle_burst(F, 1350, 900, t, t0 + 0.9, 10, 160, seed=12)


s_return = companion(topic2("RETOUR À LA MER", [
    "Plic, elle, continue son chemin dans la rivière. Elle coule, coule, à travers les prés et les villages...",
    "Jusqu'à... la mer ! Bulle saute de joie : Plic ! Tu es revenue !",
    "Plic a fait un tour complet ! Et bientôt, le soleil la réchauffera, et le voyage recommencera.",
], bg_world, return_actor, extras=sky_light,
    chip_items=[(0, "La rivière coule", "#4dabf7"), (1, "Retour à la mer", "#1c7ed6")],
    lab_bg="#1c7ed6"), [])
_rt = s_return.sfx_fn
s_return.sfx_fn = lambda S: _rt(S) + [("boing", S.cue(1) + 1.2), ("sparkle", S.cue(1) + 2.0)]


# ================================================================ 12. le cycle
STAGES = [("Évaporation", "#ff922b"), ("Condensation", "#845ef7"), ("Précipitations", "#4dabf7"), ("Ruissellement", "#1c7ed6")]


@lru_cache(None)
def ring():
    p = Pen(760, 760, 2)
    for i in range(4):
        a0 = -90 + i * 90 + 14
        p.arc(380, 380, 300, 300, a0, a0 + 62, (255, 255, 255, 230), 18)
        a = math.radians(a0 + 70)
        x, y = 380 + 300 * math.cos(a), 380 + 300 * math.sin(a)
        d = a + math.pi / 2
        pts = [(x + 26 * math.cos(d), y + 26 * math.sin(d)),
               (x + 22 * math.cos(d + 2.4), y + 22 * math.sin(d + 2.4)),
               (x + 22 * math.cos(d - 2.4), y + 22 * math.sin(d - 2.4))]
        p.poly(pts, (255, 255, 255, 230))
    return p.done()


def cycle_actor(F, S, t, shift):
    cx, cy = 900 - shift * 470, 590
    sc = 1 - 0.28 * shift
    F.put(ring(), cx, cy, sc=sc)
    pos = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    icons = [lambda: vapeur(blinking(t, 4)), lambda: cumulo(blinking(t, 5), size=220),
             lambda: art.cloud(200, "#d5dde8", "#9fb0c2", True, "o"), lambda: art.drop(100)]
    t0, t1 = S.cue(0), S.end(0)
    for i, (name, col) in enumerate(STAGES):
        ts = t0 + i * (t1 - t0) / 4.4
        if t < ts:
            continue
        k = back_out(prog(t, ts, 0.5))
        dx, dy = pos[i]
        x, y = cx + dx * 330 * sc, cy + dy * 300 * sc
        F.put(icons[i](), x, y - 20 * sc, sc=max(0.01, k * sc * (0.6 if i == 0 else 1)))
        if i == 2:
            rain_fx(F, S, t, x - 60, x + 60, y + 20, y + 80, 6, k, seed=3)
        F.put(label(name, 44, col), x, y + 95 * sc, sc=max(0.01, k * sc))
    if t > t1:
        a = -(t - t1) * 1.4
        F.put(art.drop(80, "smile", "closed" if blinking(t, 1) else "open"),
              cx + 300 * sc * math.cos(a), cy + 300 * sc * math.sin(a))


s_cycle = topic2("LE CYCLE DE L'EAU", [
    "Évaporation, condensation, précipitations, ruissellement... et ça recommence !",
    "C'est le cycle de l'eau. Il tourne, encore et encore, sans jamais s'arrêter.",
    "Le savais-tu ? L'eau de la Terre voyage ainsi depuis des milliards d'années. L'eau que tu bois a peut-être été bue par un dinosaure !",
], bg_sky, cycle_actor, extras=lambda F, S, t: drift_clouds(F, t, 3, 140, seed=21, scale=0.5),
    fact=(2, "L'eau voyage ainsi depuis des milliards d'années. Un dinosaure a peut-être bu la même eau que toi !"),
    lab_bg="#845ef7", fact_cx=1330)
_c = s_cycle.sfx_fn
s_cycle.sfx_fn = lambda S: _c(S) + [("pop", S.cue(0) + i * (S.end(0) - S.cue(0)) / 4.4) for i in range(4)]


# ================================================================ 13. prendre soin de l'eau
def save_actor(F, S, t, shift):
    k = back_out(prog(t, 0.3, 0.6))
    fx = 520 - shift * 140
    F.put(faucet(), fx, 400, sc=max(0.01, k))
    off = S.cue(1) + 2.0
    if t < off:
        for i in range(12):
            ph = (t * 2.2 + i / 12) % 1
            F.put(art.raindrop(26), fx + 50 + 8 * math.sin(i), 530 + ph * 270, alpha=0.9)
    else:
        kk = back_out(prog(t, off, 0.5))
        F.put(art.check(130), fx + 270, 330, sc=max(0.01, kk))
    if S.cue(1) < t:
        kb = back_out(prog(t, S.cue(1) + 0.3, 0.5))
        F.put(toothbrush(), fx - 60, 760, sc=max(0.05, kb * 0.9), rot=8 * math.sin(t * 6), alpha=1 - shift)
    plic(F, S, t, fx - 300 + shift * 140, 760, 150)
    if t > S.cue(2):
        kb = back_out(prog(t, S.cue(2), 0.6))
        sx, sy, r, hop = bob(S, t, 0.8, 0.2)
        F.put(bulle(blinking(t, 2)), fx + 260, 760 - hop, sc=max(0.05, kb * 0.75), rot=r)


s_save = topic2("PRENDS SOIN DE L'EAU", [
    "L'eau douce est précieuse : les plantes, les animaux et toi, vous en avez tous besoin pour vivre.",
    "Alors, ferme bien le robinet pendant que tu te brosses les dents.",
    "Et ne jette jamais rien dans les rivières : Plic, Bulle et leurs amis aiment l'eau bien propre !",
    "Le savais-tu ? Plus de la moitié de ton corps est faite d'eau ! Toi aussi, tu fais partie du grand voyage de l'eau.",
], lambda: bg_room(1), save_actor,
    chip_items=[(1, "Ferme le robinet", "#51cf66"), (2, "Garde l'eau propre", "#4dabf7")],
    fact=(3, "Plus de la moitié de ton corps est faite d'eau ! Toi aussi, tu fais partie du voyage de l'eau."),
    lab_bg="#51cf66", fact_cx=1300)


# ================================================================ 14. récap
def recap_actor(F, S, t, shift):
    items = [(vapeur, 0.95, "Évaporation", "#ff922b"), (lambda b: cumulo(b, size=260), 1.0, "Condensation", "#845ef7"),
             (lambda b: cumulo(b, "smile", True, 260), 1.0, "Précipitations", "#4dabf7"),
             (plic_fn, 1.0, "Ruissellement", "#1c7ed6")]
    for i, (fn, sc, txt, col) in enumerate(items):
        t0 = S.cue(i + 1) - 0.2
        x = 230 + i * 400
        if t > t0:
            k = back_out(prog(t, t0, 0.5), 2.2)
            sx, sy, r, hop = bob(S, t, 0.8, i * 0.25)
            F.put(fn(blinking(t, i)), x, 720 - hop, sc=max(0.05, k * sc), anchor="b", rot=r, sx=sx, sy=sy)
            if i == 2:
                rain_fx(F, S, t, x - 80, x + 80, 650, 760, 8, clamp(k), seed=6)
        pop_label(F, S, t, txt, x, 830, t0, 46, col)


s_recap = topic2("RÉCAPITULONS", [
    "Récapitulons le grand voyage de Plic !",
    "Le soleil chauffe la mer, et l'eau s'envole en vapeur : c'est l'évaporation.",
    "En haut, il fait froid : la vapeur forme un nuage. C'est la condensation.",
    "L'eau retombe du ciel en pluie ou en neige : ce sont les précipitations.",
    "Puis elle glisse dans les ruisseaux et les rivières, jusqu'à la mer : c'est le ruissellement.",
    "Et maintenant, place au quiz ! Tu es prêt ?",
], lambda: bg_sea(0), recap_actor, extras=sea_sky, lab_bg="#845ef7")
_rc = s_recap.sfx_fn
s_recap.sfx_fn = lambda S: _rc(S) + [("boing", S.cue(i + 1)) for i in range(4)] + [("sparkle", S.cue(5))]


# ================================================================ quiz + outro
q1 = quiz2(1, "Comment s'appelle le moment où l'eau devient vapeur ?", ["La condensation", "L'évaporation", "La neige"], 1, [
    "Première question ! Comment s'appelle le moment où l'eau se transforme en vapeur ? La condensation, l'évaporation, ou la neige ?",
    "C'est l'évaporation ! Le soleil chauffe l'eau, et elle s'envole en vapeur.",
])
q2 = quiz2(2, "De quoi est fait un nuage ?", ["De coton", "De fumée", "De gouttelettes d'eau"], 2, [
    "Deuxième question ! De quoi est fait un nuage ? De coton, de fumée, ou de minuscules gouttelettes d'eau ?",
    "Bravo ! Comme Cumulo, un nuage est fait de minuscules gouttelettes d'eau.",
])
q3 = quiz2(3, "Combien de branches a un flocon de neige ?", ["6 branches", "4 branches", "10 branches"], 0, [
    "Dernière question ! Combien de branches a presque toujours un flocon de neige ? Six, quatre, ou dix ?",
    "Oui ! Six branches, comme Plic quand elle était un flocon !",
])

s_out = outro2([
    "Super ! Maintenant, tu connais le grand voyage de l'eau !",
    "Plic te dit : Merci d'avoir voyagé avec moi ! La prochaine fois qu'il pleut, fais-moi un petit coucou !",
    "À très vite pour une nouvelle aventure sur MiniWonder !",
], lambda: bg_sea(0), parade=[(plic_fn, 1.0), (bulle_fn, 0.8), (cumulo_fn, 0.85), (flocon_fn, 1.0), (pousse_fn, 0.8)],
    extras=sea_sky)

SCENES = [s_intro, s_planet, s_ocean, s_evap, s_states, s_cond, s_cumulo, s_rain, s_snow, s_melt, s_ground,
          s_return, s_cycle, s_save, s_recap, q1, q2, q3, s_out]

STYLE = 1  # len(published.videos) % 4

if __name__ == "__main__":
    import sys
    only = set(map(int, sys.argv[1:])) if len(sys.argv) > 1 else None
    render_video("MiniWonder_02_Le_voyage_de_l_eau", SCENES, "/home/claude/mw/out/eau",
                 music_fn=music_for(SCENES, STYLE), sfx_fn=music2.sfx, music_gain=0.5, duck_depth=0.6, only=only)
