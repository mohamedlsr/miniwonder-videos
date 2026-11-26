"""Livelier scene templates: beat-synced dancing, star wipes, confetti, camera moves."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw
from engine import *
import art
import music2
from music2 import BEAT

PITCH = 1.07
SPEED = 1.10
WIPE = 0.5
WIPE_COLS = ["#ff6b81", "#ffd43b", "#4dabf7", "#51cf66", "#845ef7", "#ff922b"]


# ------------------------------------------------------------------ rhythm
def beat_phase(S, t):
    return ((S.t0 + t) / BEAT) % 1.0


def beat_count(S, t):
    return int((S.t0 + t) / BEAT)


def dance_params(S, t, amp=1.0, off=0.0):
    ph = (beat_phase(S, t) + off) % 1.0
    land = math.exp(-ph * 9)
    hop = math.sin(math.pi * ph) * 16 * amp
    sx = 1 + 0.06 * land * amp
    sy = 1 - 0.07 * land * amp
    side = 1 if (beat_count(S, t) % 2) else -1
    rot = side * 3.5 * amp * math.sin(math.pi * ph)
    return sx, sy, rot, hop


def blinking(t, seed=0):
    period = 2.6 + (seed % 5) * 0.37
    return ((t + seed * 0.71) % period) < 0.13


def dancer(F, S, t, sprite_fn, x, y, sc=1.0, amp=1.0, seed=0, flip=False):
    """Draw a character standing at (x, y=feet) dancing to the beat, blinking."""
    sx, sy, rot, hop = dance_params(S, t, amp, (seed * 0.13) % 1)
    sp = sprite_fn(blinking(t, seed))
    F.put(sp, x, y - hop, sc, rot=rot, flip=flip, anchor="b", sx=sx, sy=sy)


def hop_in(F, S, t, sprite_fn, t0, x0, x1, y, sc=1.0, hops=3, d=1.6, seed=0, amp=1.0):
    k = prog(t, t0, d)
    if k <= 0:
        return None
    if k < 1:
        e = ease_in_out(k)
        x = x0 + (x1 - x0) * e
        jump = abs(math.sin(math.pi * hops * k)) * 90 * sc
        land = math.exp(-((hops * k) % 1) * 10)
        F.put(sprite_fn(False), x, y - jump, sc, anchor="b", sx=1 + 0.08 * land, sy=1 - 0.1 * land,
              rot=-6 * math.sin(math.pi * hops * k))
        return x
    dancer(F, S, t, sprite_fn, x1, y, sc, amp, seed)
    return x1


def mini2(F, S, t, x, y, size=230, amp=1.2, jump_at=(), spin_at=()):
    """Mascot: talks, dances, jumps (and spins) at given times."""
    sx, sy, rot, hop = dance_params(S, t, amp)
    extra = 0
    for tj in jump_at:
        k = prog(t, tj, 0.7)
        if 0 < k < 1:
            extra = max(extra, math.sin(math.pi * k) * 140)
    for ts in spin_at:
        k = prog(t, ts, 0.7)
        if 0 < k < 1:
            rot += 360 * ease_in_out(k)
    mouth = "open" if S.talking(t) else "smile"
    sp = art.star(size, mouth, "closed" if blinking(t, 3) else "open")
    F.put(sp, x, y - hop - extra, rot=rot % 360, sx=sx, sy=sy)


# ------------------------------------------------------------------ particles
def sparkle_burst(F, x, y, t, t0, n=10, R=170, seed=0, size=46):
    k = prog(t, t0, 0.8)
    if k <= 0 or k >= 1:
        return
    rnd = random.Random(seed)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
        r = R * ease_out(k) * rnd.uniform(0.7, 1.1)
        col = WIPE_COLS[(i + seed) % len(WIPE_COLS)]
        F.put(art.mini_star(size, col), x + r * math.cos(a), y + r * math.sin(a),
              sc=max(0.05, 1 - k * 0.8), rot=(k * 360 + i * 30) % 360, alpha=1 - k ** 2)


@lru_cache(None)
def _conf(col, w=26, h=14):
    p = art.Pen(w, h, 2)
    p.rect(0, 0, w, h, 3, col)
    return p.done()


def confetti_burst(F, x, y, t, t0, n=70, seed=0, power=1.0):
    k = t - t0
    if k <= 0 or k > 3.0:
        return
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(-math.pi, 0)
        v = rnd.uniform(500, 1300) * power
        vx, vy = v * math.cos(a) * 0.9, v * math.sin(a)
        px = x + vx * k * 0.75
        py = y + vy * k + 900 * k * k
        if py > H + 50:
            continue
        col = WIPE_COLS[i % len(WIPE_COLS)]
        F.put(_conf(col), px, py, rot=(k * rnd.uniform(200, 700) + i * 37) % 360, alpha=clamp(3 - k))


def confetti_rain(F, t, n=50, seed=1):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W)
        sp = rnd.uniform(140, 280)
        y = (rnd.uniform(0, H) + t * sp) % (H + 100) - 50
        x = x0 + 40 * math.sin(t * 2 + i)
        F.put(_conf(WIPE_COLS[i % 6]), x, y, rot=(t * 160 + i * 40) % 360)


def birds(F, S, t, y=200, seed=0):
    rnd = random.Random(seed + S.idx)
    period = 11.0
    k = ((t + rnd.uniform(0, period)) % period) / period
    x = -150 + k * (W + 300)
    for j in range(3):
        fr = int((t * 6 + j) % 2)
        F.put(art.bird(fr, 60 - j * 8), x - j * 90, y + j * 35 + math.sin(t * 3 + j) * 12)


def butterflies(F, t, spots, seed=0):
    rnd = random.Random(seed)
    cols = ["#ff6fa5", "#845ef7", "#ffa94d", "#4dabf7"]
    for i, (cx, cy) in enumerate(spots):
        a = t * 0.9 + i * 2
        x = cx + 140 * math.sin(a) + 40 * math.sin(a * 2.3)
        y = cy + 70 * math.sin(a * 1.4)
        fr = [0, 1, 2, 1][int(t * 14 + i) % 4]
        F.put(art.butterfly(fr, cols[i % 4], 70), x, y)


def sun2(F, S, t, x, y, size=240):
    F.put(art.sun_rays(size), x, y, rot=(t * 25) % 360)
    sx, sy, rot, hop = dance_params(S, t, 0.5)
    F.put(art.sun_body(size, blinking(t, 7)), x, y - hop * 0.5, rot=rot)


def drift_clouds(F, t, n=3, y=140, seed=2, scale=0.7):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W)
        sp = rnd.uniform(18, 35)
        x = (x0 + t * sp) % (W + 500) - 250
        F.put(art.cloud(int(300 * scale * rnd.uniform(0.8, 1.2))), x, y + rnd.uniform(-40, 60) + 8 * math.sin(t + i))


# ------------------------------------------------------------------ camera & wipes
def camera(img, S, t, zoom=0.05, pan=22):
    z = 1.0 + zoom * ease_in_out(t / max(S.dur, 0.1)) + 0.012
    px = pan * math.sin(t * 0.35 + S.idx)
    py = 8 * math.sin(t * 0.5)
    cx, cy = W / 2 + px, H / 2 + py
    return img.transform((W, H), Image.AFFINE, (1 / z, 0, cx - W / (2 * z), 0, 1 / z, cy - H / (2 * z)),
                         resample=Image.BILINEAR)


def _star_poly(cx, cy, R, rot):
    pts = []
    for i in range(10):
        a = math.radians(rot) - math.pi / 2 + i * math.pi / 5
        r = R if i % 2 == 0 else R * 0.45
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def star_wipe(F, S, t, last=False, first=False):
    d = ImageDraw.Draw(F.img)
    if not first and t < WIPE:
        k = 1 - ease_in_out(t / WIPE)
        col = WIPE_COLS[(S.idx - 1) % len(WIPE_COLS)]
        R = 2600 * k
        if R > 2:
            d.polygon(_star_poly(W / 2, H / 2, R + 30, -k * 120), fill=(255, 255, 255))
            d.polygon(_star_poly(W / 2, H / 2, R, -k * 120), fill=hexc(col)[:3])
    if not last and t > S.dur - WIPE:
        k = ease_in_out((t - (S.dur - WIPE)) / WIPE)
        col = WIPE_COLS[S.idx % len(WIPE_COLS)]
        R = 2600 * k
        if R > 2:
            d.polygon(_star_poly(W / 2, H / 2, R + 30, k * 120), fill=(255, 255, 255))
            d.polygon(_star_poly(W / 2, H / 2, R, k * 120), fill=hexc(col)[:3])


# ------------------------------------------------------------------ text
@lru_cache(None)
def word_sprite(word, size, fg, ol):
    f = font("Fredoka-Bold.ttf", size)
    l, tp, r, b = f.getbbox(word)
    w, h = r - l + size * 0.5, size * 1.5
    p = art.Pen(int(w), int(h), 2)
    p.text((w / 2, h / 2 + 7), word, "Fredoka-Bold.ttf", size, (0, 0, 0, 80), stroke=size * 0.1, sfill=(0, 0, 0, 80))
    p.text((w / 2, h / 2), word, "Fredoka-Bold.ttf", size, fg, stroke=size * 0.1, sfill=ol)
    return p.done()


def wavy_text(F, text, x, y, size, t, t_in, fg="#ffffff", ol="#e8590c", maxw=1000, wave=10, stagger=0.12):
    f = font("Fredoka-Bold.ttf", size)
    lines = wrap(text, f, maxw)
    lh = size * 1.15
    n = 0
    for li, ln in enumerate(lines):
        words = ln.split()
        sps = [word_sprite(wd, size, fg, ol) for wd in words]
        gap = -size * 0.22
        total = sum(s.width for s in sps) + gap * (len(sps) - 1)
        cx = x - total / 2
        cy = y + (li - (len(lines) - 1) / 2) * lh
        for sp in sps:
            tw = t_in + n * stagger
            k = back_out(prog(t, tw, 0.55), 2.2)
            if k > 0.01:
                dy = -(1 - k) * 260 - abs(math.sin((t - tw) * 4 + n * 0.7)) * wave * clamp(t - tw - 0.5)
                F.put(sp, cx + sp.width / 2, cy + dy, sc=max(0.05, 0.5 + 0.5 * k), alpha=clamp(k * 2),
                      rot=math.sin((t - tw) * 3 + n) * 2)
            cx += sp.width + gap
            n += 1


@lru_cache(None)
def letter_sprite(ch, size, col):
    f = font("Fredoka-Bold.ttf", size)
    l, tp, r, b = f.getbbox(ch)
    w, h = r - l + size * 0.45, size * 1.5
    p = art.Pen(int(w), int(h), 2)
    p.text((w / 2, h / 2 + 6), ch, "Fredoka-Bold.ttf", size, (0, 0, 0, 90), stroke=size * 0.12, sfill=(0, 0, 0, 90))
    p.text((w / 2, h / 2), ch, "Fredoka-Bold.ttf", size, col, stroke=size * 0.12, sfill="#ffffff")
    return p.done()


def logo(F, S, t, x, y, size=110, t_in=0.3):
    cols = ["#ff6b81", "#ff922b", "#fab005", "#51cf66", "#339af0", "#845ef7"]
    word = "MiniWonder"
    sps = [letter_sprite(c, size, cols[i % 6]) for i, c in enumerate(word)]
    gap = -size * 0.36
    total = sum(s.width for s in sps) + gap * (len(sps) - 1)
    cx = x - total / 2
    for i, sp in enumerate(sps):
        tw = t_in + i * 0.07
        k = back_out(prog(t, tw, 0.5), 2.5)
        bob = math.sin((S.t0 + t) / BEAT * math.pi + i * 0.6) * 8
        if k > 0.01:
            F.put(sp, cx + sp.width / 2, y - (1 - k) * 300 + bob, sc=max(0.05, k), rot=math.sin(t * 3 + i) * 5)
        cx += sp.width + gap


def pop_label(F, S, t, text, x, y, t0, size=56, col="#ff6b81", fg="#ffffff", out=0.0):
    if t < t0:
        return
    k = back_out(prog(t, t0, 0.5), 2.4)
    wob = math.sin((t - t0) * 14) * 8 * math.exp(-(t - t0) * 3)
    lb = label(text, size, col, fg)
    F.put(lb, x + out * 1000, y, sc=max(0.05, k), rot=wob, alpha=1 - out)
    sparkle_burst(F, x, y, t, t0, 10, lb.width * 0.55, seed=hash(text) % 97)


# ------------------------------------------------------------------ templates
def topic2(title, lines, bg_fn, actor, chip_items=(), fact=None, extras=None, lab_bg="#ff6b81",
           fact_cx=1270, mini_pos=(W - 160, H - 140), chips_x=1400, chips_y0=330, last=False):
    fact_cue = fact[0] if fact else None

    def draw(S, t):
        world = Frame(bg_fn())
        if extras:
            extras(world, S, t)
        shift = ease_in_out(prog(t, S.cue(fact_cue) - 0.4, 0.7)) if fact else 0
        actor(world, S, t, shift)
        F = Frame.__new__(Frame)
        F.img = camera(world.img, S, t)
        # UI
        hide = ease_in_out(prog(t, S.cue(fact_cue) - 0.3, 0.35)) if fact else 0
        for n, (ci, txt, col) in enumerate(chip_items):
            pop_label(F, S, t, txt, chips_x, chips_y0 + n * 150, S.cue(ci) - 0.1, 54, col, out=hide)
        if fact:
            t0 = S.cue(fact_cue) - 0.25
            if t > t0:
                k = back_out(prog(t, t0, 0.6), 2.0)
                wob = math.sin((t - t0) * 10) * 4 * math.exp(-(t - t0) * 2.5)
                F.put(fact_card(fact[1], 1040), fact_cx, 520 + (1 - k) * 700, rot=wob)
                sparkle_burst(F, fact_cx, 360, t, t0 + 0.3, 14, 560, seed=5)
        # title label drops & wobbles
        lb = label(title, 72, lab_bg)
        k = back_out(prog(t, WIPE * 0.6, 0.6), 2.0)
        F.put(lb, 60 + lb.width / 2, 50 + lb.height / 2 - (1 - k) * 260,
              rot=math.sin(t * 2.2) * 1.5 + math.sin(t * 12) * 6 * math.exp(-t * 2.5) * (k > 0))
        jumps = [S.cue(ci) - 0.1 for ci, _, _ in chip_items]
        k2 = back_out(prog(t, 0.3, 0.6))
        mini2(F, S, t, mini_pos[0], mini_pos[1] + (1 - k2) * 320, 220, jump_at=jumps)
        star_wipe(F, S, t, last=last)
        return F

    def sfx(S):
        ev = [("whoosh", 0.0), ("boing", WIPE * 0.6 + 0.15)]
        for ci, _, _ in chip_items:
            ev += [("pop", S.cue(ci) - 0.1), ("sparkle", S.cue(ci) - 0.05)]
        if fact:
            ev += [("chime", S.cue(fact_cue) - 0.25)]
        return ev

    return Scene(lines, draw, sfx=sfx, speed=SPEED, pitch=PITCH, lead=0.8)


def intro2(title, lines, bg_fn, title_cue=1, extras=None, title_ol="#e8590c"):
    def draw(S, t):
        world = Frame(bg_fn())
        if extras:
            extras(world, S, t)
        F = Frame.__new__(Frame)
        F.img = camera(world.img, S, t, 0.04, 10)
        logo(F, S, t, W / 2, 130, 120, 0.25)
        kk = prog(t, 0.9, 0.9)
        if kk > 0:
            y = 610 - math.sin(math.pi * min(1, kk)) * 260 * (kk < 1)
            if kk < 1:
                F.put(art.star(420), 460, 610 + (1 - kk) * 700 - math.sin(math.pi * kk) * 300, rot=360 * ease_out(kk))
            else:
                mini2(F, S, t, 460, 610, 420, 1.0, jump_at=[S.cue(title_cue) - 0.2], spin_at=[S.cue(title_cue) - 0.2])
        tt = S.cue(title_cue) - 0.2
        wavy_text(F, title, 1240, 560, 118, t, tt, "#ffffff", title_ol, 1000)
        confetti_burst(F, 1240, 700, t, tt + 0.4, 80, seed=2)
        star_wipe(F, S, t, first=True)
        return F

    return Scene(lines, draw, lead=2.2, speed=SPEED, pitch=PITCH,
                 sfx=lambda S: [("jingle", 0.25), ("boing", 1.3), ("whoosh", S.cue(title_cue) - 0.3),
                                ("fanfare", S.cue(title_cue) + 0.2), ("sparkle", S.cue(title_cue) + 0.5)])


@lru_cache(None)
def big_num(n):
    return letter_sprite(str(n), 170, "#ff6b81")


def quiz2(num, question, options, good, lines):
    letters = "ABC"
    narr = list(lines[:1]) + [5.6] + list(lines[1:])

    def times(S):
        c0 = S.end(0) + 0.2
        reveal = S.cue(1) - 0.35
        return c0, reveal

    def draw(S, t):
        F = Frame(bg_quiz())
        c0, reveal = times(S)
        # rotating light rays
        F.put(_rays(), W / 2, H / 2 + 100, rot=(t * 12) % 360, alpha=0.35)
        k = back_out(prog(t, 0.35, 0.6), 2.2)
        F.put(label(f"QUIZ  {num}/3", 66, "#ffd43b", "#3b1f9e"), W / 2, 90 - (1 - k) * 220,
              rot=math.sin(t * 3) * 3)
        qc = text_card(question, 1400, 62, "#ffffff", "#2b2b52", "#ffd43b")
        kq = back_out(prog(t, 0.6, 0.6), 2.0)
        F.put(qc, W / 2, 300, sc=max(0.05, 0.5 + 0.5 * kq), alpha=clamp(kq * 2))
        for i, op in enumerate(options):
            t_op = 1.1 + i * 0.3
            ko = back_out(prog(t, t_op, 0.5), 2.2)
            state = "idle" if t < reveal else ("good" if i == good else "bad")
            x = W / 2 + (i - 1) * 590
            y = 620 + (1 - ko) * 600
            sc = 1.0
            rot = 0
            if t < reveal:
                sx_, sy_, rot_, hop = dance_params(S, t, 0.4, i * 0.33)
                y -= hop * 0.5
            elif i == good:
                kk = t - reveal
                sc = 1 + 0.14 * math.sin(kk * 9) * math.exp(-kk * 2.2) + 0.05
                rot = math.sin(kk * 7) * 4 * math.exp(-kk * 1.5)
            F.put(option_card(letters[i], op, state), x, y, sc=sc, rot=rot)
            if t >= reveal and i == good:
                kc = back_out(prog(t, reveal, 0.4), 2.5)
                F.put(art.check(130, True), x + 245, 535, sc=max(0.05, kc))
        # countdown
        if c0 <= t < reveal:
            rem = reveal - t
            n = max(1, min(5, int(math.ceil(rem - 0.3))))
            frac = (rem - 0.3) % 1
            pulse = 1 + 0.35 * frac ** 3
            F.put(_ring_bg(), W / 2, 890)
            F.put(big_num(n), W / 2, 885, sc=pulse * 0.85)
        if t >= reveal:
            kb = back_out(prog(t, reveal + 0.15, 0.5), 2.5)
            F.put(word_sprite("BRAVO !", 110, "#ffd43b", "#e8590c"), W / 2, 890, sc=max(0.05, kb),
                  rot=math.sin((t - reveal) * 5) * 5)
            confetti_burst(F, W / 2 + (good - 1) * 590, 620, t, reveal, 90, seed=num)
            sparkle_burst(F, W / 2 + (good - 1) * 590, 620, t, reveal, 14, 330, seed=num)
        mini2(F, S, t, 200, 900, 250, 1.2, jump_at=[reveal], spin_at=[reveal])
        star_wipe(F, S, t)
        return F

    def sfx(S):
        c0, reveal = times(S)
        ev = [("whoosh", 0.0), ("boing", 0.45)] + [("pop", 1.1 + i * 0.3) for i in range(3)]
        tt = c0 + ((reveal - c0) - 0.3) % 1
        while tt < reveal - 1.4:
            ev.append(("tick", tt))
            tt += 1.0
        ev += [("drumroll", reveal - 1.3), ("fanfare", reveal), ("sparkle", reveal + 0.1)]
        return ev

    sc = Scene(narr, draw, sfx=sfx, tail=1.4, speed=SPEED, pitch=PITCH, lead=0.8)
    sc.quiet_fn = lambda S: (S.t0 + times(S)[0], S.t0 + times(S)[1])
    return sc


@lru_cache(None)
def _rays():
    p = art.Pen(1400, 1400, 1)
    for i in range(16):
        a0 = 2 * math.pi * i / 16
        p.poly([(700, 700), (700 + 1000 * math.cos(a0), 700 + 1000 * math.sin(a0)),
                (700 + 1000 * math.cos(a0 + 0.17), 700 + 1000 * math.sin(a0 + 0.17))], (255, 255, 255, 255))
    img = p.done()
    return img


@lru_cache(None)
def _ring_bg():
    p = art.Pen(230, 230, 2)
    p.circ(115, 115, 105, "#ffffff", "#ffd43b", 10)
    return p.done()


def outro2(lines, bg_fn, parade=(), extras=None):
    """parade: list of (sprite_fn, scale) that dance in a line."""

    def draw(S, t):
        world = Frame(bg_fn())
        if extras:
            extras(world, S, t)
        F = Frame.__new__(Frame)
        F.img = camera(world.img, S, t, 0.03, 10)
        n = len(parade)
        for i, (fn, sc) in enumerate(parade):
            x = W / 2 + (i - (n - 1) / 2) * 390
            hop_in(F, S, t, fn, 0.6 + i * 0.25, -400 if i < n / 2 else W + 400, x, 1040, sc, 3, 1.4, seed=i, amp=1.6)
        mini2(F, S, t, W / 2, 470, 360, 1.5, jump_at=[S.cue(0) - 0.1, S.cue(2)], spin_at=[S.cue(0) - 0.1])
        wavy_text(F, "BRAVO !", W / 2, 150, 160, t, 0.5, "#ffd43b", "#e8590c", 1600, 16)
        if t > S.cue(len(S.cues) - 1) - 0.2:
            pop_label(F, S, t, "À très vite sur MiniWonder !", W / 2, 690, S.cue(len(S.cues) - 1) - 0.2, 66, "#4dabf7")
        confetti_rain(F, t)
        confetti_burst(F, W / 2, 400, t, 0.6, 90, seed=9)
        star_wipe(F, S, t, last=True)
        # fade to white at end
        if t > S.dur - 1.0:
            F.img = Image.blend(F.img, Image.new("RGB", (W, H), (255, 255, 255)), clamp((t - (S.dur - 1.0)) / 1.0))
        return F

    return Scene(lines, draw, tail=3.0, speed=SPEED, pitch=PITCH, lead=0.8,
                 sfx=lambda S: [("whoosh", 0.0), ("fanfare", 0.5), ("sparkle", 0.7), ("jingle", S.cue(len(S.cues) - 1))])


def music_for(scenes):
    def fn(total, scs):
        quiet = []
        for s in scs:
            q = getattr(s, "quiet_fn", None)
            if q:
                quiet.append(q(s))
        return music2.track(total, 0, quiet)
    return fn


def make_thumbnail(path, bg_img, title, sprites, title_ol="#e8590c"):
    """16:9 YouTube thumbnail (1280x720 JPEG, < 2 MB). sprites: list of (sprite, x, y_bottom, scale)."""
    F = Frame(bg_img)
    for sp, x, y, sc in sprites:
        F.put(sp, x, y, sc=sc, anchor="b")
    F.put(art.star(360), 1640, 820, rot=-8)
    F.put(big_title(title, 150, "#ffffff", title_ol, 1250), 720, 310)
    F.put(label("MiniWonder", 64, "#ffd43b", "#1b3a6b"), 230, 80)
    F.put(label("+ QUIZ", 70, "#ff6b81"), 1700, 120, rot=8)
    F.img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=90)
    return path
