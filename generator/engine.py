"""Scene engine: backgrounds, UI, timing, audio mix, rendering."""
import math, os, random, subprocess, textwrap, wave
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art
from art import Pen, W, H, font, hexc
import tts

FPS = 30
AR = 44100


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def back_out(x, s=1.7):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def prog(t, t0, d):
    return clamp((t - t0) / d)


# ------------------------------------------------------------------ backgrounds
def vgrad(top, bottom, h=H, w=W):
    a = np.array(hexc(top)[:3], np.float32)
    b = np.array(hexc(bottom)[:3], np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    row = a[None, :] * (1 - t) + b[None, :] * t
    return np.repeat(row[:, None, :], w, axis=1)


def radial(inner, outer, cx=W / 2, cy=H / 2, r=1200):
    a = np.array(hexc(inner)[:3], np.float32)
    b = np.array(hexc(outer)[:3], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(np.hypot(xx - cx, yy - cy) / r, 0, 1)[..., None]
    return a * (1 - t) + b * t


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def hills(p, y0, amp, col, seed, freq=1.0):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6) for _ in range(3)]
    pts = [(x, y0 + amp * (0.5 * math.sin(x / 300 * freq + ph[0]) + 0.3 * math.sin(x / 170 * freq + ph[1])
                          + 0.2 * math.sin(x / 90 * freq + ph[2]))) for x in range(0, W + 21, 20)]
    p.poly(pts + [(W, H), (0, H)], col)


@lru_cache(None)
def bg_savanna(variant=0, sun=True):
    img = to_img(vgrad("#7cc8f5", "#ffe2a8"))
    if sun:
        s = art.sun(260, face=False)
        img.alpha_composite(s, (1500, 60))
    p = Pen(W, H, 2)
    hills(p, 640, 40, "#e9c07a", 1, 0.7)
    hills(p, 700, 30, "#d9a548", 2)
    hills(p, 800, 20, "#c98f2f", 3, 1.4)
    rnd = random.Random(7 + variant)
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(820, H)
        hgt = rnd.uniform(18, 40)
        p.line([(x, y), (x + rnd.uniform(-8, 8), y - hgt)], "#b77d24", 4)
    img.alpha_composite(p.done())
    for (x, y, sc) in ((60, 360, 0.75), (1280, 330, 0.9), (820, 470, 0.45)) if variant == 0 else ((1450, 340, 0.85), (120, 430, 0.5)):
        a = art.acacia(sc)
        img.alpha_composite(a, (int(x), int(y)))
    return img.convert("RGB")


@lru_cache(None)
def bg_sky():
    return to_img(vgrad("#6ec3f7", "#d6f0ff")).convert("RGB")


@lru_cache(None)
def bg_world():
    """Water cycle landscape: mountain left, river, sea right."""
    img = to_img(vgrad("#78c6f5", "#d9f1ff"))
    p = Pen(W, H, 2)
    # mountains
    p.poly([(-100, 900), (330, 330), (760, 900)], "#7d8fa3")
    p.poly([(330, 330), (255, 425), (300, 410), (340, 440), (380, 405), (405, 425)], "#ffffff")
    p.poly([(250, 900), (560, 470), (900, 900)], "#93a6ba")
    p.poly([(560, 470), (510, 535), (548, 522), (575, 545), (610, 530)], "#ffffff")
    # land
    hills(p, 820, 25, "#7cc35a", 4, 0.8)
    # sea on right
    p.poly([(1150, 860), (W, 760), (W, H), (1050, H)], "#2d8fe0")
    for i in range(7):
        y = 800 + i * 40
        x0 = 1150 - i * 15
        for x in range(int(x0), W, 120):
            p.arc(x + 30, y, 30, 10, 200, 340, "#8fd0ff", 4)
    # river
    river = art.bezier((420, 880), (650, 980), (900, 900), (1150, 930), 60)
    p.stroke(river, "#3da7ec", 40, 70)
    # trees
    for x in (720, 820, 980):
        p.rect(x - 8, 820, x + 8, 880, 6, "#7a4b2a")
        p.circ(x, 800, 40, "#4caf50")
        p.circ(x - 20, 815, 28, "#5dbb63")
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_garden(cut=True):
    img = to_img(vgrad("#8fd3ff", "#e8f7ff"))
    p = Pen(W, H, 2)
    hills(p, 560, 25, "#a5d68a", 11, 0.8)
    gy = 640
    p.rect(-10, gy, W + 10, H + 10, 0, "#8a5a33")
    p.rect(-10, gy, W + 10, gy + 30, 0, "#6abf4b")
    rnd = random.Random(2)
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(gy + 50, H)
        p.ell(x, y, rnd.uniform(4, 12), rnd.uniform(3, 8), "#74482a")
    for _ in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(gy + 60, H)
        p.ell(x, y, rnd.uniform(8, 16), rnd.uniform(6, 10), "#9e9e9e")
    for x in range(0, W, 14):
        p.line([(x, gy + 6), (x + rnd.uniform(-5, 5), gy - rnd.uniform(10, 26))], "#5aad3e", 4)
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_quiz():
    arr = radial("#7b5cff", "#3b1f9e", r=1300)
    img = to_img(arr)
    p = Pen(W, H, 2)
    rnd = random.Random(9)
    for _ in range(60):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 9)
        p.circ(x, y, r, (255, 255, 255, int(rnd.uniform(40, 120))))
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_intro():
    arr = radial("#6cc4ff", "#1c64c8", cy=500, r=1300)
    img = to_img(arr)
    p = Pen(W, H, 2)
    rnd = random.Random(4)
    cols = ["#ff6b81", "#ffd43b", "#51cf66", "#ffffff", "#ff922b"]
    for _ in range(45):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(5, 14)
        p.circ(x, y, r, hexc(rnd.choice(cols), 200))
    img.alpha_composite(p.done())
    return img.convert("RGB")


# ------------------------------------------------------------------ frame canvas
from collections import OrderedDict
_XC = OrderedDict()


def _xform(sp_id, sp, sc, alpha, rot):
    key = (sp_id, sc, alpha, rot)
    if isinstance(sc, tuple) and sc[0] == sc[1]:
        sc = sc[0]
        key = (sp_id, sc, alpha, rot)
    if key in _XC:
        _XC.move_to_end(key)
        return _XC[key][1]
    im = _xform_raw(sp, sc, alpha, rot)
    _XC[key] = (sp, im)  # keep sp alive so id stays unique
    if len(_XC) > 700:
        _XC.popitem(last=False)
    return im


def _xform_raw(sp, sc, alpha, rot):
    im = sp
    sx, sy = sc if isinstance(sc, tuple) else (sc, sc)
    if (sx, sy) != (1.0, 1.0):
        im = im.resize((max(1, int(im.width * sx)), max(1, int(im.height * sy))), Image.BILINEAR)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    return im


class Frame:
    def __init__(self, bg):
        self.img = bg.copy()

    def put(self, sp, cx, cy, sc=1.0, alpha=1.0, rot=0.0, flip=False, anchor="c", sx=1.0, sy=1.0):
        if sc <= 0.01 or alpha <= 0.01:
            return
        if flip:
            sp = _flip(sp)
        if sx != 1.0 or sy != 1.0:
            sc = (round(sc * sx, 2), round(sc * sy, 2))
        else:
            sc = round(sc, 2)
        alpha = round(alpha, 2)
        rot = round(rot)
        im = _xform(id(sp), sp, sc, alpha, rot)
        x = int(cx - im.width / 2)
        y = int(cy - im.height / 2) if anchor == "c" else int(cy - im.height)
        self.img.paste(im, (x, y), im)


_FL = {}


def _flip(sp):
    k = id(sp)
    if k not in _FL:
        _FL[k] = (sp, sp.transpose(Image.FLIP_LEFT_RIGHT))
    return _FL[k][1]


# ------------------------------------------------------------------ UI pieces
@lru_cache(None)
def label(text, size=78, bg="#ff6b81", fg="#ffffff"):
    f = font("Fredoka-Bold.ttf", size)
    l, t, r, b = f.getbbox(text)
    w, h = r - l + size * 1.1, size * 1.45
    p = Pen(int(w) + 20, int(h) + 24, 2)
    p.rect(10, 16, w + 10, h + 16, h / 2, (0, 0, 0, 60))
    p.rect(10, 6, w + 10, h + 6, h / 2, bg, "#ffffff", 6)
    p.text(((w + 20) / 2, h / 2 + 6), text, "Fredoka-Bold.ttf", size, fg)
    return p.done()


@lru_cache(None)
def big_title(text, size=120, fg="#ffffff", ol="#1b3a6b", maxw=1700):
    f = font("Fredoka-Bold.ttf", size)
    lines = wrap(text, f, maxw)
    lh = size * 1.12
    w = max(f.getbbox(l)[2] for l in lines) + 60
    h = int(lh * len(lines) + 50)
    p = Pen(int(w), h, 2)
    for i, ln in enumerate(lines):
        y = 25 + lh * (i + 0.5)
        p.text((w / 2, y + 8), ln, "Fredoka-Bold.ttf", size, (0, 0, 0, 70), stroke=size * 0.1, sfill=(0, 0, 0, 70))
        p.text((w / 2, y), ln, "Fredoka-Bold.ttf", size, fg, stroke=size * 0.1, sfill=ol)
    return p.done()


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if f.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


@lru_cache(None)
def fact_card(text, w=1180, head="LE SAVAIS-TU ?"):
    f = font("Nunito-ExtraBold.ttf", 48)
    lines = wrap(text, f, w - 120)
    h = 130 + 62 * len(lines)
    p = Pen(w + 20, h + 70, 2)
    p.rect(10, 52, w + 10, h + 62, 40, (0, 0, 0, 50))
    p.rect(10, 40, w + 10, h + 50, 40, "#fffaf0", "#ffb84d", 7)
    p.rect(60, 10, 520, 86, 38, "#ff922b", "#ffffff", 5)
    p.text((310, 48), head, "Fredoka-Bold.ttf", 46, "#ffffff")
    for i, ln in enumerate(lines):
        p.text((70, 130 + 62 * i), ln, "Nunito-ExtraBold.ttf", 48, "#3b2f5c", anchor="lm")
    img = p.done()
    img.alpha_composite(art.bulb(80), (8, 0))
    return img


@lru_cache(None)
def text_card(text, w=900, size=50, bg="#ffffff", fg="#2b2b52", border="#8ecbff"):
    f = font("Nunito-ExtraBold.ttf", size)
    lines = wrap(text, f, w - 80)
    h = 60 + int(size * 1.25) * len(lines)
    p = Pen(w + 20, h + 20, 2)
    p.rect(10, 18, w + 10, h + 18, 34, (0, 0, 0, 45))
    p.rect(10, 8, w + 10, h + 8, 34, bg, border, 6)
    for i, ln in enumerate(lines):
        p.text((w / 2 + 10, 38 + size * 0.62 + int(size * 1.25) * i), ln, "Nunito-ExtraBold.ttf", size, fg)
    return p.done()


@lru_cache(None)
def option_card(letter, text, state="idle"):
    w, h = 520, 190
    col = {"idle": "#ffffff", "good": "#2ecc71", "bad": "#d6d0ea"}[state]
    fg = {"idle": "#2b2b52", "good": "#ffffff", "bad": "#8a82a8"}[state]
    lc = {"A": "#ff6b81", "B": "#ffa94d", "C": "#4dabf7"}[letter]
    p = Pen(w + 20, h + 30, 2)
    p.rect(10, 22, w + 10, h + 22, 40, (0, 0, 0, 60))
    p.rect(10, 10, w + 10, h + 10, 40, col, "#ffffff", 6)
    p.circ(85, h / 2 + 10, 50, lc if state != "bad" else "#b9b2d3", "#ffffff", 5)
    p.text((85, h / 2 + 10), letter, "Fredoka-Bold.ttf", 60, "#ffffff")
    f = font("Fredoka-SemiBold.ttf", 50)
    lines = wrap(text, f, w - 190)
    for i, ln in enumerate(lines):
        p.text((160, h / 2 + 10 + (i - (len(lines) - 1) / 2) * 56), ln, "Fredoka-SemiBold.ttf", 50, fg, anchor="lm")
    return p.done()


@lru_cache(None)
def countdown_ring(n, frac_q):
    """n = number shown, frac_q = remaining fraction quantised."""
    p = Pen(220, 220, 2)
    p.circ(110, 110, 96, "#ffffff", None)
    p.arc(110, 110, 88, 88, -90, -90 + 360 * frac_q / 20, "#ff6b81", 16)
    p.text((110, 112), str(n), "Fredoka-Bold.ttf", 100, "#3b1f9e")
    return p.done()


# ------------------------------------------------------------------ scenes
class Scene:
    def __init__(self, lines, draw, lead=0.6, tail=0.9, gap=0.4, sfx=None, speed=1.08, min_dur=0, pitch=1.0):
        self.lines, self.draw, self.lead, self.tail, self.gap = lines, draw, lead, tail, gap
        self.sfx_fn, self.speed, self.min_dur, self.pitch = sfx, speed, min_dur, pitch
        self.t0, self.idx = 0.0, 0

    def build(self):
        segs, cues, subs = [], [], []
        t = self.lead
        for item in self.lines:
            if isinstance(item, (int, float)):
                t += item
                continue
            a = tts.say(item, self.speed, self.pitch)
            cues.append(t)
            d = len(a) / tts.SR
            segs.append((t, a))
            subs.append((t, t + d, item))
            t += d + self.gap
        dur = max(t - self.gap + self.tail, self.min_dur)
        self.nframes = int(round(dur * FPS))
        self.dur = self.nframes / FPS
        self.cues = cues
        self.ends = [s[1] for s in subs]
        self.subs = subs
        # voice track at AR
        n = int(self.dur * AR)
        v = np.zeros(n, np.float32)
        for t0, a in segs:
            r = _resample(a, tts.SR, AR)
            i0 = int(t0 * AR)
            v[i0:i0 + len(r)] += r[:max(0, n - i0)]
        self.voice = v
        # mouth envelope per frame
        env = []
        hop = AR // FPS
        for i in range(self.nframes):
            seg = v[i * hop:(i + 1) * hop]
            env.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
        self.env = env
        self.sfx = self.sfx_fn(self) if self.sfx_fn else []
        return self

    def talking(self, t):
        i = int(t * FPS)
        if 0 <= i < len(self.env):
            return self.env[i] > 0.04 and (i // 3) % 2 == 0
        return False

    def cue(self, i):
        return self.cues[i] if i < len(self.cues) else self.dur

    def end(self, i):
        return self.ends[i] if i < len(self.ends) else self.dur


def _resample(a, sr0, sr1):
    n = int(len(a) * sr1 / sr0)
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


def mini(F, S, t, x, y, size=300, bob=True, sc=1.0):
    """Draw the star mascot, talking when narration plays."""
    blink = (t % 3.7) < 0.12
    mouth = "open" if S.talking(t) else "smile"
    sp = art.star(size, mouth, "closed" if blink else "open")
    yy = y + (math.sin(t * 3) * 10 if bob else 0)
    F.put(sp, x, yy, sc, rot=math.sin(t * 2) * 4)


def scene_fade(F, t, S, fin=0.35, fout=0.35):
    """Fade from/to white at scene edges."""
    a = 0
    if t < fin:
        a = 1 - t / fin
    elif t > S.dur - fout:
        a = (t - (S.dur - fout)) / fout
    if a > 0.01:
        F.img = Image.blend(F.img, _white(), clamp(a) * 0.9)


@lru_cache(None)
def _white():
    return Image.new("RGB", (W, H), (255, 255, 255))


# ------------------------------------------------------------------ audio
def tone(freq, dur, amp=0.3, decay=6.0, harm=(1, 0.5, 0.25)):
    t = np.arange(int(dur * AR)) / AR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    env = np.exp(-decay * t) * np.minimum(1, t * 200)
    return (amp * s * env).astype(np.float32)


def sfx_sound(name):
    if name == "pop":
        t = np.arange(int(0.12 * AR)) / AR
        f = 500 + 1400 * t / 0.12
        return (0.35 * np.sin(2 * np.pi * np.cumsum(f) / AR) * np.exp(-25 * t)).astype(np.float32)
    if name == "ding":
        return np.concatenate([tone(1046.5, 0.18, 0.25, 8), tone(1568, 0.9, 0.3, 4)])
    if name == "tick":
        return tone(1200, 0.08, 0.15, 40, (1,))
    if name == "whoosh":
        n = int(0.5 * AR)
        noise = np.random.RandomState(1).randn(n).astype(np.float32)
        k = np.ones(40) / 40
        noise = np.convolve(noise, k, "same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        return (0.5 * noise * env).astype(np.float32)
    if name == "chime":
        out = np.zeros(int(1.6 * AR), np.float32)
        for i, f in enumerate((784, 988, 1175, 1568)):
            tt = tone(f, 1.2, 0.18, 4)
            i0 = int(i * 0.09 * AR)
            out[i0:i0 + len(tt)] += tt[:len(out) - i0]
        return out
    raise ValueError(name)


def music(dur, seed=0, bpm=96):
    """Gentle procedural ukulele/glockenspiel loop."""
    rnd = random.Random(seed)
    n = int(dur * AR)
    out = np.zeros(n + AR * 3, np.float32)
    beat = 60 / bpm
    prog_ = [(60, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7]), (55, [0, 4, 7])]
    if seed % 3 == 1:
        prog_ = [(53, [0, 4, 7]), (55, [0, 4, 7]), (60, [0, 4, 7]), (57, [0, 3, 7])]
    elif seed % 3 == 2:
        prog_ = [(60, [0, 4, 7]), (55, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7])]
    mf = lambda m: 440 * 2 ** ((m - 69) / 12)
    pluck = {}
    t = 0.0
    bar = 0
    scale = [0, 2, 4, 7, 9]
    while t < dur:
        root, ch = prog_[bar % 4]
        # bass
        b = tone(mf(root - 24), beat * 2, 0.22, 2.5, (1, 0.3))
        for k in (0, 2):
            i0 = int((t + k * beat) * AR)
            out[i0:i0 + len(b)] += b
        # arpeggio eighths
        pat = [0, 1, 2, 1, 0, 1, 2, 1]
        for k, pi in enumerate(pat):
            m = root + ch[pi]
            key = m
            if key not in pluck:
                pluck[key] = tone(mf(m), 0.6, 0.09, 7, (1, 0.6, 0.3, 0.15))
            i0 = int((t + k * beat / 2) * AR)
            out[i0:i0 + len(pluck[key])] += pluck[key]
        # bell melody every other bar
        if bar % 2 == 0:
            for k in range(4):
                if rnd.random() < 0.7:
                    m = root + 12 + rnd.choice(scale)
                    bl = tone(mf(m), 0.9, 0.05, 4, (1, 0, 0.2))
                    i0 = int((t + k * beat) * AR)
                    out[i0:i0 + len(bl)] += bl
        t += beat * 4
        bar += 1
    out = out[:n]
    fade = int(2 * AR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[:int(0.5 * AR)] *= np.linspace(0, 1, int(0.5 * AR))
    return out


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    st = (a * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(AR)
        w.writeframes(st.tobytes())


# ------------------------------------------------------------------ render
def render_video(name, scenes, outdir, music_seed=0, preview=None, music_fn=None, sfx_fn=None,
                 music_gain=0.55, duck_depth=0.55, only=None):
    os.makedirs(outdir, exist_ok=True)
    acc = 0.0
    for i, s in enumerate(scenes):
        s.idx, s.t0 = i, acc
        s.build()
        acc += s.dur
    total = sum(s.dur for s in scenes)
    print(name, "duration", round(total, 1), "s", [round(s.dur, 1) for s in scenes], flush=True)
    if preview is not None:
        return scenes
    files = []
    for i, s in enumerate(scenes):
        fn = os.path.join(outdir, f"scene{i:02d}.mp4")
        files.append(fn)
        if only is not None and i not in only and os.path.exists(fn):
            continue
        tmp = fn[:-4] + ".tmp.mp4"
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19",
                                 "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp],
                                stdin=subprocess.PIPE)
        for fi in range(s.nframes):
            t = fi / FPS
            F = s.draw(s, t)
            proc.stdin.write(F.img.convert("RGB").tobytes())
        proc.stdin.close()
        if proc.wait() == 0:
            os.replace(tmp, fn)
        print(" scene", i, "done", flush=True)
    # audio
    n = int(round(total * AR))
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    t0 = 0.0
    subs = []
    for s in scenes:
        i0 = int(round(t0 * AR))
        v = s.voice[:n - i0]
        voice[i0:i0 + len(v)] += v
        for nm, ts in s.sfx:
            a = (sfx_fn or sfx_sound)(nm)
            j = int((t0 + ts) * AR)
            if 0 <= j < n:
                fx[j:j + len(a)] += a[:n - j]
        for a, b, txt in s.subs:
            subs.append((t0 + a, t0 + b, txt))
        t0 += s.dur
    voice /= max(1e-6, np.abs(voice).max()) / 0.85
    mus = music_fn(total, scenes) if music_fn else music(total, music_seed)
    # duck music under voice
    env = np.abs(voice)
    k = int(0.25 * AR)
    env = np.convolve(env, np.ones(k) / k, "same")
    duck = 1 - duck_depth * np.clip(env / 0.05, 0, 1)
    mix = voice + music_gain * mus * duck + 0.7 * fx
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    wav = os.path.join(outdir, "audio.wav")
    write_wav(wav, mix)
    lst = os.path.join(outdir, "list.txt")
    with open(lst, "w") as f:
        for fn in files:
            f.write(f"file '{os.path.abspath(fn)}'\n")
    silent = os.path.join(outdir, "video_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    final = os.path.join(outdir, name + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    write_srt(os.path.join(outdir, name + ".srt"), subs)
    print("FINAL", final, flush=True)
    return final


def _ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, subs):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(subs, 1):
            f.write(f"{i}\n{_ts(a)} --> {_ts(b)}\n{textwrap.fill(txt, 48)}\n\n")
