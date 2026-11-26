"""Reusable scene templates for MiniWonder episodes."""
import math
from engine import *
import art


def drop_label(F, text, t, t0=0.15, x=60, y=50, bg="#ff6b81"):
    lb = label(text, 72, bg)
    k = back_out(prog(t, t0, 0.6))
    F.put(lb, x + lb.width / 2, y + lb.height / 2 - (1 - k) * 260, alpha=clamp(k * 2))


def show_fact(F, S, t, text, cue_i, cx=1270, cy=520):
    t0 = S.cue(cue_i) - 0.25
    if t < t0:
        return
    k = back_out(prog(t, t0, 0.55), 1.2)
    card = fact_card(text, 1040)
    F.put(card, cx + (1 - k) * 1300, cy)


def chips(F, S, t, items, x=1400, y0=330, dy=150, hide_at=None):
    out = ease_in_out(prog(t, hide_at - 0.3, 0.35)) if hide_at is not None else 0
    for n, (ci, txt, col) in enumerate(items):
        t0 = S.cue(ci) - 0.1
        if t < t0:
            continue
        k = back_out(prog(t, t0, 0.5))
        lb = label(txt, 54, col)
        F.put(lb, x + out * 900, y0 + n * dy, sc=max(0.01, k), alpha=1 - out)


def topic(title, lines, bg_fn, actor, chip_items=(), fact=None, extras=None, lab_bg="#ff6b81", mini_on=True, fact_cx=1270):
    """actor(F, S, t, shift): shift 0..1 eases in when the fact card appears."""
    fact_cue = fact[0] if fact else None

    def draw(S, t):
        F = Frame(bg_fn())
        if extras:
            extras(F, S, t)
        shift = ease_in_out(prog(t, S.cue(fact_cue) - 0.4, 0.7)) if fact else 0
        actor(F, S, t, shift)
        chips(F, S, t, chip_items, hide_at=S.cue(fact_cue) if fact else None)
        if fact:
            show_fact(F, S, t, fact[1], fact_cue, cx=fact_cx)
        drop_label(F, title, t, bg=lab_bg)
        if mini_on:
            k = back_out(prog(t, 0.3, 0.6))
            mini(F, S, t, W - 150, H - 140 + (1 - k) * 300, 210)
        scene_fade(F, t, S)
        return F

    def sfx(S):
        ev = [("whoosh", 0.05)]
        ev += [("pop", S.cue(ci) - 0.1) for ci, _, _ in chip_items]
        if fact:
            ev.append(("chime", S.cue(fact_cue) - 0.25))
        return ev

    return Scene(lines, draw, sfx=sfx)


def intro(title, lines, bg_fn, extras=None, title_cue=1, music_title="MiniWonder"):
    def draw(S, t):
        F = Frame(bg_fn())
        if extras:
            extras(F, S, t)
        # logo text
        k = back_out(prog(t, 0.2, 0.7))
        F.put(big_title("MiniWonder", 96, "#ffd43b", "#1b3a6b"), W / 2, 110 - (1 - k) * 250)
        # mascot bounce in
        kk = back_out(prog(t, 0.0, 0.9))
        mini(F, S, t, 460, 560 + (1 - kk) * 700, 420)
        # title
        tt = S.cue(title_cue) - 0.2
        kt = back_out(prog(t, tt, 0.7), 1.4)
        if t > tt:
            F.put(big_title(title, 112, "#ffffff", "#e8590c", 1000), 1240, 560, sc=0.4 + 0.6 * kt, alpha=clamp(kt * 2))
        scene_fade(F, t, S, 0.01, 0.35)
        return F

    return Scene(lines, draw, lead=1.0, sfx=lambda S: [("whoosh", 0.1), ("chime", S.cue(title_cue) - 0.2)])


def quiz(num, question, options, good, lines, intro_line=False):
    """lines: [question narration, answer narration]. options: 3 strings, good: index."""
    letters = "ABC"
    narr = list(lines[:1]) + [5.4] + list(lines[1:])

    def draw(S, t):
        F = Frame(bg_quiz())
        k = back_out(prog(t, 0.1, 0.6))
        F.put(label(f"QUIZ  {num}/3", 64, "#ffd43b", "#3b1f9e"), W / 2, 90 - (1 - k) * 200)
        qc = text_card(question, 1400, 62, "#ffffff", "#2b2b52", "#ffd43b")
        kq = back_out(prog(t, 0.35, 0.6))
        F.put(qc, W / 2, 290, sc=0.6 + 0.4 * kq, alpha=clamp(kq * 2))
        reveal = S.cue(1) - 0.3
        for i, op in enumerate(options):
            ko = back_out(prog(t, 0.9 + i * 0.25, 0.5))
            state = "idle" if t < reveal else ("good" if i == good else "bad")
            x = W / 2 + (i - 1) * 590
            pulse = 1 + (0.06 * math.sin((t - reveal) * 8) * math.exp(-(t - reveal) * 1.5) if (t >= reveal and i == good) else 0)
            F.put(option_card(letters[i], op, state), x, 600 + (1 - ko) * 600, sc=pulse)
            if t >= reveal and i == good:
                kc = back_out(prog(t, reveal, 0.4))
                F.put(art.check(120, True), x + 240, 520, sc=max(0.01, kc))
        # countdown
        c0 = S.end(0) + 0.2
        if c0 <= t < reveal:
            rem = (reveal - t)
            n = max(1, min(5, int(math.ceil(rem - 0.4))))
            fq = int(clamp(rem / 5.2) * 20)
            F.put(countdown_ring(n, fq), W / 2, 880)
        mini(F, S, t, 210, 900, 250)
        scene_fade(F, t, S)
        return F

    def sfx(S):
        c0 = S.end(0) + 0.2
        reveal = S.cue(1) - 0.3
        ev = [("pop", 0.9 + i * 0.25) for i in range(3)]
        tt = c0 + 0.2
        while tt < reveal - 0.5:
            ev.append(("tick", tt))
            tt += 1.0
        ev.append(("ding", reveal))
        return ev

    return Scene(narr, draw, sfx=sfx, tail=1.2)


def outro(lines, bg_fn, extras=None):
    def draw(S, t):
        F = Frame(bg_fn())
        if extras:
            extras(F, S, t)
        kk = back_out(prog(t, 0.0, 0.8))
        mini(F, S, t, W / 2, 470 + (1 - kk) * 600, 420)
        kb = back_out(prog(t, 0.6, 0.7))
        F.put(big_title("BRAVO !", 150, "#ffd43b", "#e8590c"), W / 2, 150, sc=max(0.01, kb))
        ke = back_out(prog(t, S.cue(len(S.cues) - 1) - 0.2, 0.7))
        if t > S.cue(len(S.cues) - 1) - 0.2:
            F.put(label("À très vite sur MiniWonder !", 70, "#4dabf7"), W / 2, 880, sc=max(0.01, ke))
        # confetti
        rnd = random.Random(1)
        cols = ["#ff6b81", "#ffd43b", "#51cf66", "#4dabf7", "#ff922b"]
        for i in range(40):
            x0 = rnd.uniform(0, W)
            sp = rnd.uniform(120, 260)
            y = (rnd.uniform(-H, 0) + t * sp) % (H + 100) - 50
            x = x0 + 30 * math.sin(t * 2 + i)
            F.put(_confetti(cols[i % 5]), x, y, rot=(t * 120 + i * 40) % 360)
        scene_fade(F, t, S, 0.35, 1.2)
        return F

    return Scene(lines, draw, tail=2.5, sfx=lambda S: [("chime", 0.6)])


@lru_cache(None)
def _confetti(col):
    p = Pen(30, 18, 2)
    p.rect(0, 0, 30, 18, 4, col)
    return p.done()


def walk_in(F, sp, t, t0, x_from, x_to, y, d=1.6, sc=1.0, flip=False, bob=12):
    k = ease_out(prog(t, t0, d))
    x = x_from + (x_to - x_from) * k
    moving = 0 < (t - t0) < d
    yy = y - (abs(math.sin((t - t0) * 7)) * bob if moving else 0)
    breathe = 1 + 0.012 * math.sin(t * 2.4)
    F.put(sp, x, yy, sc * breathe, flip=flip, anchor="b")
    return x


def drifting_clouds(F, t, n=3, y=120, seed=0, scale=0.7):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W)
        sp = rnd.uniform(12, 25)
        x = (x0 + t * sp) % (W + 500) - 250
        F.put(art.cloud(int(300 * scale * rnd.uniform(0.8, 1.2))), x, y + rnd.uniform(-40, 60))
