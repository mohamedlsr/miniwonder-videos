"""Cute flat-style illustrations drawn with PIL (supersampled)."""
import math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1920, 1080
SS = 3
FONT_DIR = "/home/claude/fonts/"


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def hexc(h, a=255):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Pen:
    """ImageDraw wrapper in unscaled coordinates."""

    def __init__(self, w, h, ss=SS):
        self.w, self.h, self.k = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def s(self, v):
        return v * self.k

    def _layer_begin(self, col):
        c = _c(col)
        if c is None or c[3] == 255 or getattr(self, "_in_layer", False):
            return c, None
        self._in_layer = True
        self._saved = self.d
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        self.d = ImageDraw.Draw(lay)
        return (c[0], c[1], c[2], 255), (lay, c[3])

    def _layer_end(self, tok):
        if tok is None:
            return
        lay, a = tok
        al = lay.split()[3].point(lambda v: v * a // 255)
        lay.putalpha(al)
        self.d = self._saved
        self._in_layer = False
        self.img.alpha_composite(lay)

    def P(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def ell(self, cx, cy, rx, ry, fill, ol=None, w=0):
        k = self.k
        fill, tok = self._layer_begin(fill)
        self.d.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k],
                       fill=fill, outline=_c(ol), width=int(w * k))
        self._layer_end(tok)

    def circ(self, cx, cy, r, fill, ol=None, w=0):
        self.ell(cx, cy, r, r, fill, ol, w)

    def rect(self, x0, y0, x1, y1, r, fill, ol=None, w=0):
        k = self.k
        fill, tok = self._layer_begin(fill)
        self.d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k,
                                 fill=fill, outline=_c(ol), width=int(w * k))
        self._layer_end(tok)

    def poly(self, pts, fill, ol=None, w=0):
        fill, tok = self._layer_begin(fill)
        self.d.polygon(self.P(pts), fill=fill)
        self._layer_end(tok)
        if ol and w:
            self.line(list(pts) + [pts[0]], ol, w)

    def line(self, pts, col, w):
        k = self.k
        col, tok = self._layer_begin(col)
        self.d.line(self.P(pts), fill=_c(col), width=int(w * k), joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([(x - w / 2) * k, (y - w / 2) * k, (x + w / 2) * k, (y + w / 2) * k], fill=_c(col))
        self._layer_end(tok)

    def stroke(self, pts, col, w0, w1=None, ol=None, olw=0):
        """Thick tapered stroke along polyline (circles)."""
        if w1 is None:
            w1 = w0
        dense = _densify(pts, 2)
        n = len(dense)
        col, tok = self._layer_begin(col)
        for pass_ in ([0] if not ol else [1, 0]):
            for i, (x, y) in enumerate(dense):
                r = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2 + (olw if pass_ else 0)
                self.circ(x, y, r, ol if pass_ else col)
        self._layer_end(tok)

    def arc(self, cx, cy, rx, ry, a0, a1, col, w):
        k = self.k
        col, tok = self._layer_begin(col)
        self.d.arc([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], a0, a1,
                   fill=_c(col), width=int(w * k))
        self._layer_end(tok)

    def text(self, xy, s, fnt, size, fill, anchor="mm", stroke=0, sfill=None):
        self.d.text((xy[0] * self.k, xy[1] * self.k), s, font=font(fnt, int(size * self.k)),
                    fill=_c(fill), anchor=anchor, stroke_width=int(stroke * self.k), stroke_fill=_c(sfill))

    def done(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def _c(c):
    if c is None:
        return None
    if isinstance(c, str):
        return hexc(c)
    return c


def _densify(pts, step):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for i in range(n):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    out.append(pts[-1])
    return out


def bezier(p0, p1, p2, p3=None, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        if p3 is None:
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        else:
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def rot_ell(cx, cy, rx, ry, ang, n=60):
    a = math.radians(ang)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return pts


def eye(p, x, y, r=13, look=(2, 0), closed=False):
    if closed:
        p.arc(x, y - 2, r, r * 0.8, 20, 160, "#2b2b2b", r * 0.35)
        return
    p.ell(x, y, r * 0.85, r, "#1f1f2e")
    p.circ(x - r * 0.3 + look[0], y - r * 0.4 + look[1], r * 0.36, "#ffffff")
    p.circ(x + r * 0.3 + look[0], y + r * 0.35, r * 0.15, "#ffffff")


def cheek(p, x, y, r=14):
    p.ell(x, y, r, r * 0.65, (255, 120, 140, 130))


# ---------------------------------------------------------------- mascot
@lru_cache(None)
def star(size=360, mouth="smile", eyes="open"):
    p = Pen(400, 400)
    cx, cy = 200, 215

    def star_pts(R, r):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = R if i % 2 == 0 else r
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return pts

    # rounded star via blurred-threshold mask
    def rstar(R, r, col, rad):
        m = Image.new("L", (400 * SS, 400 * SS), 0)
        ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in star_pts(R, r)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(rad * SS)).point(lambda v: 255 if v > 128 else 0)
        m = m.filter(ImageFilter.GaussianBlur(1))
        layer = Image.new("RGBA", m.size, hexc(col))
        layer.putalpha(m)
        p.img.alpha_composite(layer)
    rstar(198, 96, "#e8891a", 9)
    rstar(184, 88, "#ffd43b", 9)
    # highlight
    p.circ(cx, cy + 10, 70, "#ffd43b")
    # face
    closed = eyes == "closed"
    eye(p, cx - 34, cy - 2, 21, closed=closed)
    eye(p, cx + 34, cy - 2, 21, closed=closed)
    cheek(p, cx - 66, cy + 30, 17)
    cheek(p, cx + 66, cy + 30, 17)
    if mouth == "smile":
        p.arc(cx, cy + 22, 26, 20, 20, 160, "#7a2e0e", 6)
    elif mouth == "open":
        p.d.chord([(cx - 26) * SS, (cy + 10) * SS, (cx + 26) * SS, (cy + 58) * SS], 0, 180, fill=hexc("#7a2e0e"))
        p.d.chord([(cx - 14) * SS, (cy + 36) * SS, (cx + 14) * SS, (cy + 56) * SS], 180, 360, fill=hexc("#ff6b81"))
    elif mouth == "o":
        p.ell(cx, cy + 38, 14, 17, "#7a2e0e")
    img = p.done()
    return img.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- savanna animals
OL = "#3a2e2a"


@lru_cache(None)
def elephant(blink=False):
    p = Pen(640, 500)
    g, gd = "#a3adb8", "#8a95a1"
    p.stroke([(95, 240), (70, 290), (66, 330)], gd, 12, 8, OL, 3)
    p.ell(64, 338, 12, 16, OL)
    for x in (140, 250):
        p.rect(x, 300, x + 70, 460, 30, gd, OL, 4)
    p.ell(250, 260, 180, 135, g, OL, 5)
    for x in (360, 455):
        p.rect(x - 70, 310, x, 462, 30, g, OL, 4)
        for k in range(3):
            p.ell(x - 52 + k * 17, 450, 7, 6, "#f3efe6")
    p.circ(470, 190, 110, g, OL, 5)
    # trunk
    tr = bezier((545, 220), (600, 300), (560, 420), (620, 400), 50)
    p.stroke(tr, g, 70, 34, OL, 4)
    for i in range(4):
        x, y = tr[18 + i * 7]
        p.arc(x, y, 18, 6, 200, 340, gd, 3)
    p.stroke([(520, 262), (548, 290), (570, 296)], "#fffaf0", 18, 10, OL, 3)
    # ear
    p.ell(400, 200, 92, 112, gd, OL, 5)
    p.ell(400, 205, 62, 82, "#e9b6bd")
    eye(p, 512, 168, 15, closed=blink)
    cheek(p, 540, 210, 13)
    return p.done()


@lru_cache(None)
def giraffe(blink=False):
    w, h = 560, 780
    body = Pen(w, h)
    y, yo = "#f7c548", "#f0b234"
    spots = Pen(w, h)
    mask = Pen(w, h)
    neck = [(270, 420), (350, 160), (412, 172), (360, 450)]
    for pen, col, ol in ((body, y, OL), (mask, "#ffffff", None)):
        pen.poly(neck, col, ol, 5 if ol else 0)
        pen.ell(220, 440, 160, 92, col, ol, 5 if ol else 0)
    rnd = random.Random(3)
    for _ in range(40):
        sx, sy = rnd.uniform(60, 400), rnd.uniform(130, 540)
        r = rnd.uniform(14, 26)
        spots.poly(rot_ell(sx, sy, r, r * 0.8, rnd.uniform(0, 180), 7), "#c06a2b")
    sp = spots.done()
    m = mask.done().split()[3].filter(ImageFilter.MinFilter(9))
    legs = Pen(w, h)
    for x in (110, 180, 270, 330):
        col = yo if x in (110, 270) else y
        legs.rect(x, 450, x + 42, 745, 20, col, OL, 4)
        legs.rect(x - 2, 725, x + 44, 760, 14, "#5b3a22", OL, 3)
    legs.stroke([(70, 420), (40, 520)], y, 10, 8, OL, 3)
    legs.ell(38, 535, 12, 22, "#5b3a22")
    base = legs.done()
    base.alpha_composite(body.done())
    base.paste(sp, (0, 0), ImageChops.multiply(sp.split()[3], m))
    p = Pen(w, h)
    # mane
    for i in range(9):
        t = i / 8
        x, y2 = 300 + (360 - 300) * t - 24, 400 + (175 - 400) * t
        p.ell(x + 30 * t - 6, y2, 12, 14, "#b0602a")
    # head
    p.line([(385, 95), (380, 45)], OL, 8)
    p.line([(415, 95), (418, 45)], OL, 8)
    p.circ(380, 42, 11, "#5b3a22", OL, 3)
    p.circ(418, 42, 11, "#5b3a22", OL, 3)
    p.ell(355, 108, 26, 13, yo, OL, 4)
    p.ell(410, 130, 68, 52, y, OL, 5)
    p.ell(462, 148, 42, 36, "#fbe2a6", OL, 4)
    p.circ(478, 138, 4, OL)
    eye(p, 410, 116, 14, closed=blink)
    cheek(p, 440, 152, 11)
    p.arc(462, 160, 18, 10, 30, 150, OL, 3)
    base.alpha_composite(p.done())
    return base


@lru_cache(None)
def lion(blink=False):
    p = Pen(640, 520)
    gold, goldd = "#eeae45", "#d9952f"
    tail = bezier((120, 290), (50, 300), (60, 190), (30, 170), 30)
    p.stroke(tail, gold, 14, 10, OL, 3)
    p.ell(30, 165, 22, 26, "#9a4f16", OL, 3)
    for x in (150, 250):
        p.rect(x, 330, x + 64, 470, 28, goldd, OL, 4)
    p.ell(270, 320, 180, 110, gold, OL, 5)
    for x in (360, 440):
        p.rect(x, 340, x + 66, 474, 28, gold, OL, 4)
        for k in range(3):
            p.circ(x + 15 + k * 18, 466, 6, "#f8d79a")
    cx, cy = 460, 210
    for ring, (R, rr, col) in enumerate(((128, 46, "#8e4513"), (106, 42, "#b5601c"))):
        for i in range(16):
            a = 2 * math.pi * (i + ring * 0.5) / 16
            p.circ(cx + R * math.cos(a) * 0.95, cy + R * math.sin(a), rr, col)
    p.circ(cx - 58, cy - 62, 24, gold, OL, 4)
    p.circ(cx + 58, cy - 62, 24, gold, OL, 4)
    p.circ(cx - 58, cy - 62, 12, "#f5b9a0")
    p.circ(cx + 58, cy - 62, 12, "#f5b9a0")
    p.circ(cx, cy, 86, "#f4bd57", OL, 5)
    p.ell(cx, cy + 34, 48, 36, "#fde6b5")
    p.poly([(cx - 17, cy + 10), (cx + 17, cy + 10), (cx, cy + 28)], "#6b3412")
    p.arc(cx - 12, cy + 36, 12, 10, 10, 170, OL, 4)
    p.arc(cx + 12, cy + 36, 12, 10, 10, 170, OL, 4)
    eye(p, cx - 32, cy - 14, 15, closed=blink)
    eye(p, cx + 32, cy - 14, 15, closed=blink)
    cheek(p, cx - 58, cy + 22, 13)
    cheek(p, cx + 58, cy + 22, 13)
    return p.done()


@lru_cache(None)
def zebra(blink=False):
    w, h = 600, 520
    base = Pen(w, h)
    mask = Pen(w, h)
    wh = "#fbfbfb"
    head = rot_ell(470, 175, 52, 92, -35)
    neck = [(330, 270), (400, 120), (470, 150), (420, 320)]
    for pen, col, ol in ((base, wh, OL), (mask, "#fff", None)):
        ow = 5 if ol else 0
        pen.stroke([(105, 250), (80, 330)], col, 12, 9, ol, 3 if ol else 0)
        for x in (140, 240, 340, 420):
            pen.rect(x, 300, x + 56, 470, 26, col, ol, ow)
        pen.ell(250, 270, 170, 100, col, ol, ow)
        pen.poly(neck, col, ol, ow)
        pen.poly(head, col, ol, ow)
    m = mask.done().split()[3].filter(ImageFilter.MinFilter(11))
    st = Pen(w, h)
    for i in range(10):
        x = 110 + i * 24
        st.poly([(x, 160), (x + 14, 160), (x + 4 + 8 * math.sin(i), 368), (x - 10 + 8 * math.sin(i), 368)], "#222")
    for i in range(2):
        st.poly(rot_ell(436 + i * 12, 112 + i * 24, 30, 6, 30, 20), "#222")
    for i in range(5):
        t = i / 4
        x, y = 345 + 70 * t, 270 - 140 * t
        st.poly(rot_ell(x + 30, y + 20, 55, 7, 24, 20), "#222")
    stripes = st.done()
    img = base.done()
    img.paste(stripes, (0, 0), ImageChops.multiply(stripes.split()[3], m))
    p = Pen(w, h)
    for i in range(10):
        t = i / 9
        x, y = 335 + 72 * t, 255 - 150 * t
        p.ell(x - 10, y - 4, 14, 18, "#222")
    p.poly(rot_ell(518, 244, 36, 30, -35), "#3c3c44")
    p.circ(525, 236, 4, "#ddd")
    p.poly(rot_ell(430, 92, 12, 26, -20), wh, OL, 4)
    eye(p, 478, 168, 13, closed=blink)
    cheek(p, 500, 205, 10)
    p.ell(81, 345, 10, 18, "#222")
    for x in (140, 240, 340, 420):
        for j in range(4):
            y = 384 + j * 21
            p.rect(x + 4, y, x + 52, y + 10, 3, "#222")
    img.alpha_composite(p.done())
    return img


@lru_cache(None)
def acacia(scale=1.0):
    p = Pen(520, 420)
    p.poly([(240, 420), (280, 420), (272, 220), (250, 220)], "#7a4b2a")
    p.stroke([(262, 260), (190, 150)], "#7a4b2a", 22, 12)
    p.stroke([(262, 250), (340, 140)], "#7a4b2a", 22, 12)
    p.stroke([(262, 230), (262, 120)], "#7a4b2a", 18, 10)
    for cx, cy, rx, ry, col in ((260, 115, 240, 52, "#4f8a35"), (160, 120, 110, 42, "#5d9c3e"),
                                (360, 112, 120, 44, "#5d9c3e"), (260, 92, 150, 40, "#6aad46")):
        p.ell(cx, cy, rx, ry, col)
    img = p.done()
    if scale != 1:
        img = img.resize((int(520 * scale), int(420 * scale)), Image.LANCZOS)
    return img


# ---------------------------------------------------------------- water cycle
@lru_cache(None)
def drop(size=200, mouth="smile", eyes="open"):
    p = Pen(200, 240)
    pts = []
    for i in range(100):
        t = 2 * math.pi * i / 100
        x = 100 + 80 * math.sin(t) * (1 - 0.0) * ((1 - math.cos(t)) / 2) ** 0.55
        y = 150 - 135 * math.cos(t) * 0.5 - 135 * 0.0
        pts.append((x, y))
    # teardrop: round bottom circle + apex
    p.circ(100, 160, 72, "#1e88d6")
    p.poly([(36, 128), (100, 8), (164, 128)], "#1e88d6")
    p.circ(100, 160, 64, "#5ec3f5")
    p.poly([(44, 132), (100, 22), (156, 132)], "#5ec3f5")
    p.ell(72, 118, 12, 26, (255, 255, 255, 190))
    closed = eyes == "closed"
    eye(p, 80, 158, 12, closed=closed)
    eye(p, 120, 158, 12, closed=closed)
    cheek(p, 64, 184, 10)
    cheek(p, 136, 184, 10)
    if mouth == "open":
        p.d.chord([86 * SS, 172 * SS, 114 * SS, 200 * SS], 0, 180, fill=hexc("#0d3a66"))
    else:
        p.arc(100, 178, 14, 10, 20, 160, "#0d3a66", 4)
    img = p.done()
    return img.resize((size, int(size * 1.2)), Image.LANCZOS)


@lru_cache(None)
def sun(size=300, face=True):
    p = Pen(300, 300)
    for i in range(12):
        a = 2 * math.pi * i / 12
        c = (150 + 140 * math.cos(a), 150 + 140 * math.sin(a))
        l = (150 + 95 * math.cos(a - 0.17), 150 + 95 * math.sin(a - 0.17))
        r = (150 + 95 * math.cos(a + 0.17), 150 + 95 * math.sin(a + 0.17))
        p.poly([l, c, r], "#ffb300")
    p.circ(150, 150, 100, "#ffb300")
    p.circ(150, 150, 90, "#ffd84d")
    if face:
        eye(p, 122, 140, 13)
        eye(p, 178, 140, 13)
        cheek(p, 106, 172, 12)
        cheek(p, 194, 172, 12)
        p.arc(150, 168, 22, 16, 20, 160, "#b35a00", 5)
    img = p.done()
    return img.resize((size, size), Image.LANCZOS) if size != 300 else img


@lru_cache(None)
def cloud(size=360, col="#ffffff", shade="#d9ecfa", face=False, mood="smile"):
    p = Pen(360, 220)
    blobs = [(100, 140, 70), (170, 100, 85), (250, 125, 72), (300, 155, 48), (60, 165, 45), (180, 160, 70)]
    for x, y, r in blobs:
        p.circ(x, y + 6, r, shade)
    for x, y, r in blobs:
        p.circ(x, y, r - 4, col)
    p.rect(55, 150, 320, 205, 30, col)
    if face:
        eye(p, 150, 135, 11)
        eye(p, 210, 135, 11)
        cheek(p, 130, 160, 10)
        cheek(p, 230, 160, 10)
        if mood == "smile":
            p.arc(180, 152, 16, 11, 20, 160, "#55606e", 4)
        else:
            p.ell(180, 162, 9, 11, "#55606e")
    img = p.done()
    return img.resize((size, int(size * 220 / 360)), Image.LANCZOS)


@lru_cache(None)
def raindrop(size=34):
    p = Pen(40, 56)
    p.circ(20, 38, 15, "#3da7ec")
    p.poly([(6, 32), (20, 4), (34, 32)], "#3da7ec")
    p.ell(15, 34, 3, 6, (255, 255, 255, 180))
    img = p.done()
    return img.resize((size, int(size * 1.4)), Image.LANCZOS)


@lru_cache(None)
def snowflake(size=40):
    p = Pen(60, 60)
    for i in range(6):
        a = math.pi * i / 3
        p.line([(30, 30), (30 + 24 * math.cos(a), 30 + 24 * math.sin(a))], "#ffffff", 4)
    p.circ(30, 30, 5, "#ffffff")
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def steam(size=60):
    p = Pen(60, 140)
    pts = [(30 + 12 * math.sin(i / 6), 130 - i * 4) for i in range(30)]
    p.stroke(pts, (255, 255, 255, 170), 14, 5)
    return p.done().resize((size, int(size * 140 / 60)), Image.LANCZOS)


@lru_cache(None)
def earth(size=420):
    p = Pen(420, 420)
    p.circ(210, 210, 200, "#1565c0")
    p.circ(210, 210, 190, "#2d8fe0")
    rnd = random.Random(5)
    for cx, cy, rx, ry in ((140, 140, 70, 52), (120, 230, 40, 70), (280, 180, 60, 90), (300, 320, 50, 35), (220, 90, 50, 26)):
        p.poly(rot_ell(cx, cy, rx, ry, rnd.uniform(0, 90), 12), "#4caf50")
    p.ell(150, 120, 60, 30, (255, 255, 255, 60))
    img = p.done()
    m = Image.new("L", (420 * 1, 420 * 1), 0)
    ImageDraw.Draw(m).ellipse([10, 10, 410, 410], fill=255)
    img.putalpha(ImageChops.multiply(img.split()[3], m))
    eyes = Pen(420, 420)
    eye(eyes, 175, 205, 18)
    eye(eyes, 245, 205, 18)
    cheek(eyes, 145, 245, 16)
    cheek(eyes, 275, 245, 16)
    eyes.arc(210, 240, 26, 18, 20, 160, "#0b2e5c", 6)
    img.alpha_composite(eyes.done())
    return img.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- plants
def plant(g, w=700, h=900, ground=560, flower=0.0, fruit=0.0):
    """Growth g 0..1: roots and stem. Drawn per call (not cached)."""
    p = Pen(w, h, 2)
    cx = w // 2
    seed_y = ground + 70
    # seed coat
    p.ell(cx, seed_y, 34, 24, "#a0682e", "#5b3a1a", 3)
    p.ell(cx - 6, seed_y - 4, 14, 8, (255, 255, 255, 60))
    root = min(1, g / 0.35)
    if root > 0:
        L = 230 * root
        pts = [(cx + 12 * math.sin(i / 7), seed_y + 10 + i * L / 40) for i in range(41)]
        p.stroke(pts, "#f3e1b9", 14, 5, "#b9925a", 2)
        for k in range(int(6 * root)):
            yy = seed_y + 40 + k * 32
            side = 1 if k % 2 else -1
            l2 = 50 * root * (1 - k / 8)
            p.stroke([(cx, yy), (cx + side * l2 * 0.6, yy + l2 * 0.4), (cx + side * l2, yy + l2)], "#f3e1b9", 7, 3)
    stem = max(0, min(1, (g - 0.25) / 0.75))
    if stem > 0:
        top = seed_y - 20 - 470 * stem
        pts = [(cx + 10 * math.sin(i / 5) * stem, seed_y - 20 - i * (seed_y - 20 - top) / 40) for i in range(41)]
        p.stroke(pts, "#4caf50", 18, 12, "#2e7d32", 3)
        nleaf = int(1 + stem * 5)
        for k in range(nleaf):
            frac = (k + 1) / 6
            if frac > stem + 0.05:
                break
            y = seed_y - 20 - (seed_y - 20 - top) * (frac / max(stem, 0.01)) * stem * 0.92
            y = seed_y - 40 - 470 * frac * 0.92
            side = -1 if k % 2 == 0 else 1
            grow = min(1, (stem - frac + 0.15) / 0.2)
            L = 120 * grow
            lx, ly = cx + side * L * 0.55, y - L * 0.25
            p.poly(rot_ell(lx, ly, L * 0.55, L * 0.24, -20 * side, 30), "#66bb6a", "#2e7d32", 3)
            p.line([(cx, y), (lx + side * L * 0.4, ly - L * 0.1)], "#2e7d32", 3)
        if flower > 0:
            fy = top - 10
            R = 70 * flower
            for i in range(8):
                a = 2 * math.pi * i / 8
                p.circ(cx + R * 0.8 * math.cos(a), fy + R * 0.8 * math.sin(a), R * 0.5, "#ff6fa5", "#d0457c", 3)
            p.circ(cx, fy, R * 0.45, "#ffd23f", "#e0a800", 3)
        if fruit > 0:
            fy = top - 10
            p.circ(cx, fy + 20, 70 * fruit, "#ff5252", "#b71c1c", 4)
            p.ell(cx - 22 * fruit, fy - 5, 14 * fruit, 22 * fruit, (255, 255, 255, 120))
            p.poly(rot_ell(cx + 10, fy - 50 * fruit, 26 * fruit, 10 * fruit, -20, 20), "#4caf50")
    return p.done()


@lru_cache(None)
def seed_cut(size=520):
    p = Pen(520, 380)
    p.ell(260, 190, 240, 170, "#8d5524", "#4e2c10", 6)
    p.ell(260, 190, 222, 152, "#f3d9a4")
    p.ell(200, 190, 120, 115, "#f7e3b6", "#d9b77a", 3)
    p.ell(330, 190, 110, 110, "#f7e3b6", "#d9b77a", 3)
    # embryo
    p.stroke(bezier((380, 230), (420, 200), (430, 150), n=20), "#7cc46a", 26, 18, "#3f8a3a", 3)
    p.poly(rot_ell(420, 128, 30, 14, -40, 20), "#8fd17a", "#3f8a3a", 3)
    p.poly(rot_ell(445, 150, 26, 12, 20, 20), "#8fd17a", "#3f8a3a", 3)
    return p.done().resize((size, int(size * 380 / 520)), Image.LANCZOS)


@lru_cache(None)
def bee(size=160, wing=0):
    p = Pen(200, 160)
    wy = -6 if wing else 6
    p.ell(90, 50 + wy, 34, 26, (220, 240, 255, 200), "#7fb3d5", 3)
    p.ell(125, 46 + wy, 30, 22, (220, 240, 255, 200), "#7fb3d5", 3)
    p.ell(105, 100, 66, 44, "#ffd23f", "#3a2e2a", 4)
    for x in (80, 110):
        p.rect(x, 60, x + 16, 140, 4, "#3a2e2a")
    p.ell(105, 100, 66, 44, None, "#3a2e2a", 4)
    p.poly([(36, 96), (18, 100), (36, 106)], "#3a2e2a")
    p.circ(165, 92, 30, "#ffd23f", "#3a2e2a", 4)
    eye(p, 172, 86, 9)
    cheek(p, 182, 104, 7)
    p.line([(160, 64), (150, 36)], "#3a2e2a", 3)
    p.line([(175, 64), (182, 36)], "#3a2e2a", 3)
    p.circ(150, 34, 5, "#3a2e2a")
    p.circ(182, 34, 5, "#3a2e2a")
    return p.done().resize((size, int(size * 0.8)), Image.LANCZOS)


@lru_cache(None)
def flower(size=200, col="#ff6fa5", center="#ffd23f"):
    p = Pen(200, 300)
    p.stroke([(100, 300), (100, 110)], "#4caf50", 12, 10)
    p.poly(rot_ell(70, 220, 34, 14, -30, 20), "#66bb6a")
    p.poly(rot_ell(130, 200, 34, 14, 30, 20), "#66bb6a")
    for i in range(7):
        a = 2 * math.pi * i / 7
        p.circ(100 + 42 * math.cos(a), 100 + 42 * math.sin(a), 32, col)
    p.circ(100, 100, 30, center, "#e0a800", 3)
    return p.done().resize((size, int(size * 1.5)), Image.LANCZOS)


@lru_cache(None)
def jar(size=420):
    p = Pen(300, 380)
    p.rect(40, 40, 260, 370, 40, (220, 240, 255, 110), "#8fb8d8", 6)
    p.rect(30, 20, 270, 60, 14, "#b0bec5", "#78909c", 4)
    for i in range(18):
        x = 60 + (i % 6) * 36
        y = 200 + (i // 6) * 50
        p.circ(x, y, 34, "#ffffff")
    p.ell(90, 160, 34, 22, "#a0682e", "#5b3a1a", 3)
    pts = [(90 + 6 * math.sin(i / 4), 180 + i * 3.5) for i in range(30)]
    p.stroke(pts, "#f3e1b9", 9, 4, "#b9925a", 2)
    p.stroke([(90, 140), (96, 100), (90, 70)], "#4caf50", 10, 8)
    p.poly(rot_ell(70, 68, 20, 9, -20, 20), "#66bb6a")
    p.poly(rot_ell(110, 66, 20, 9, 20, 20), "#66bb6a")
    p.ell(240, 150, 8, 60, (255, 255, 255, 120))
    return p.done().resize((size, int(size * 380 / 300)), Image.LANCZOS)


# ---------------------------------------------------------------- icons
@lru_cache(None)
def icon(kind, size=200):
    p = Pen(200, 200)
    p.circ(100, 100, 96, "#ffffff", "#e0e6ef", 4)
    if kind == "water":
        p.circ(100, 120, 46, "#3da7ec")
        p.poly([(56, 104), (100, 30), (144, 104)], "#3da7ec")
        p.ell(84, 112, 8, 16, (255, 255, 255, 180))
    elif kind == "heat":
        p.rect(84, 30, 116, 130, 16, "#ffffff", "#e53935", 6)
        p.rect(94, 70, 106, 140, 5, "#e53935")
        p.circ(100, 145, 26, "#e53935")
        for y in (55, 75, 95):
            p.line([(118, y), (130, y)], "#e53935", 4)
    elif kind == "air":
        for i, y in enumerate((70, 100, 130)):
            pts = [(40 + x, y + 8 * math.sin(x / 14 + i)) for x in range(0, 110, 4)]
            p.stroke(pts, "#64b5f6", 10, 10)
            ex, ey = pts[-1]
            p.arc(ex + 6, ey - 12, 14, 14, 270, 520, "#64b5f6", 9)
    elif kind == "light":
        s = sun(150, face=False)
        img = p.done()
        img.alpha_composite(s, (25, 25))
        return img.resize((size, size), Image.LANCZOS)
    elif kind == "co2":
        p.text((100, 100), "CO₂" if False else "CO2", "Fredoka-Bold.ttf", 64, "#546e7a")
    elif kind == "o2":
        p.text((100, 100), "O2", "Fredoka-Bold.ttf", 72, "#2e7d32")
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def bulb(size=70):
    p = Pen(100, 100)
    p.circ(50, 42, 32, "#ffd43b", "#e8891a", 4)
    p.rect(36, 66, 64, 92, 6, "#9e9e9e", "#616161", 3)
    p.line([(42, 76), (58, 76)], "#616161", 3)
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def check(size=120, ok=True):
    p = Pen(120, 120)
    p.circ(60, 60, 56, "#2ecc71" if ok else "#e74c3c", "#ffffff", 6)
    if ok:
        p.line([(32, 62), (52, 82), (88, 40)], "#ffffff", 12)
    else:
        p.line([(38, 38), (82, 82)], "#ffffff", 12)
        p.line([(82, 38), (38, 82)], "#ffffff", 12)
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def sun_rays(size=300):
    p = Pen(300, 300)
    for i in range(12):
        a = 2 * math.pi * i / 12
        c = (150 + 145 * math.cos(a), 150 + 145 * math.sin(a))
        l = (150 + 95 * math.cos(a - 0.17), 150 + 95 * math.sin(a - 0.17))
        r = (150 + 95 * math.cos(a + 0.17), 150 + 95 * math.sin(a + 0.17))
        p.poly([l, c, r], "#ffb300")
    img = p.done()
    return img.resize((size, size), Image.LANCZOS) if size != 300 else img


@lru_cache(None)
def sun_body(size=300, blink=False):
    p = Pen(300, 300)
    p.circ(150, 150, 100, "#ffb300")
    p.circ(150, 150, 90, "#ffd84d")
    eye(p, 122, 140, 13, closed=blink)
    eye(p, 178, 140, 13, closed=blink)
    cheek(p, 106, 172, 12)
    cheek(p, 194, 172, 12)
    p.arc(150, 168, 22, 16, 20, 160, "#b35a00", 5)
    img = p.done()
    return img.resize((size, size), Image.LANCZOS) if size != 300 else img


@lru_cache(None)
def mini_star(size=60, col="#ffd43b"):
    p = Pen(100, 100)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 46 if i % 2 == 0 else 20
        pts.append((50 + r * math.cos(a), 52 + r * math.sin(a)))
    p.poly(pts, col)
    return p.done().resize((size, size), Image.LANCZOS)


@lru_cache(None)
def bird(frame=0, size=70):
    p = Pen(100, 60)
    wy = 10 if frame == 0 else 45
    p.stroke(bezier((8, wy), (30, 20 if frame == 0 else 40), (50, 34)), "#3a2e2a", 7, 5)
    p.stroke(bezier((92, wy), (70, 20 if frame == 0 else 40), (50, 34)), "#3a2e2a", 7, 5)
    return p.done().resize((size, int(size * 0.6)), Image.LANCZOS)


@lru_cache(None)
def butterfly(frame=0, col="#ff6fa5", size=80):
    p = Pen(100, 90)
    k = [1.0, 0.55, 0.2][frame]
    for side in (-1, 1):
        p.ell(50 + side * 24 * k, 32, 24 * k + 1, 26, col, "#7a2e4e", 3)
        p.ell(50 + side * 18 * k, 62, 17 * k + 1, 18, col, "#7a2e4e", 3)
    p.rect(46, 22, 54, 76, 4, "#3a2e2a")
    p.line([(48, 24), (40, 6)], "#3a2e2a", 3)
    p.line([(52, 24), (60, 6)], "#3a2e2a", 3)
    return p.done().resize((size, int(size * 0.9)), Image.LANCZOS)
