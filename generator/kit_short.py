"""Vertical Shorts templates (1080x1920). Import with MW_VERTICAL=1 set BEFORE importing anything else."""
import os
assert os.environ.get("MW_VERTICAL"), "set MW_VERTICAL=1 before importing kit_short"
import math
from kit2 import *
from kit2 import _rays, _ring_bg
import art

assert (W, H) == (1080, 1920)


@lru_cache(None)
def num_badge(n, col="#ff6b81"):
    p = art.Pen(200, 200, 2)
    p.circ(100, 100, 92, col, "#ffffff", 10)
    p.text((100, 104), str(n), "Fredoka-Bold.ttf", 110, "#ffffff")
    return p.done()


def short_scene(lines, bg_fn, actor=None, title=None, title_col="#ff6b81", card=None, card_cue=0,
                badge=None, extras=None, first=False, last=False, title_size=88):
    """Generic vertical scene: wavy title at top, actor in the middle, text card at the bottom."""

    def draw(S, t):
        world = Frame(bg_fn())
        if extras:
            extras(world, S, t)
        if actor:
            actor(world, S, t)
        F = Frame.__new__(Frame)
        F.img = camera(world.img, S, t, 0.04, 10)
        if title:
            wavy_text(F, title, W / 2, 300 if badge is not None else 250, title_size, t, WIPE * 0.6, "#ffffff", title_col, 960, 10, 0.1)
        if badge is not None:
            k = back_out(prog(t, WIPE * 0.6, 0.5), 2.5)
            F.put(num_badge(badge, title_col), W / 2, 125, sc=max(0.05, k), rot=math.sin(t * 3) * 6)
            sparkle_burst(F, W / 2, 125, t, WIPE * 0.6, 10, 160, seed=badge)
        if card:
            t0 = S.cue(card_cue) - 0.2
            if t > t0:
                k = back_out(prog(t, t0, 0.6), 2.0)
                wob = math.sin((t - t0) * 10) * 3 * math.exp(-(t - t0) * 2.5)
                F.put(text_card(card, 980, 66, "#ffffff", "#2b2b52", title_col), W / 2, 1560 + (1 - k) * 700, rot=wob)
        k2 = back_out(prog(t, 0.3, 0.6))
        mini2(F, S, t, W - 140, H - 150 + (1 - k2) * 320, 200, jump_at=[S.cue(card_cue) - 0.2] if card else [])
        star_wipe(F, S, t, last=last, first=first)
        return F

    def sfx(S):
        ev = [] if first else [("whoosh", 0.0)]
        ev.append(("boing", WIPE * 0.6 + 0.1))
        if card:
            ev += [("pop", S.cue(card_cue) - 0.2), ("sparkle", S.cue(card_cue))]
        if first:
            ev.append(("jingle", 0.1))
        if last:
            ev.append(("fanfare", 0.4))
        return ev

    return Scene(lines, draw, sfx=sfx, speed=SPEED, pitch=PITCH, lead=0.7, tail=0.6 if not last else 1.6)


def short_quiz(question, options, good, lines, bg_fn=None):
    """Quick vertical quiz: options stacked, 3 s countdown, reveal."""
    letters = "ABC"
    narr = list(lines[:1]) + [3.4] + list(lines[1:])

    def times(S):
        return S.end(0) + 0.15, S.cue(1) - 0.35

    def draw(S, t):
        F = Frame((bg_fn or bg_quiz)())
        c0, reveal = times(S)
        F.put(_rays(), W / 2, H / 2, rot=(t * 12) % 360, alpha=0.35)
        k = back_out(prog(t, 0.35, 0.6), 2.2)
        F.put(label("QUIZ !", 80, "#ffd43b", "#3b1f9e"), W / 2, 150 - (1 - k) * 250, rot=math.sin(t * 3) * 4)
        kq = back_out(prog(t, 0.6, 0.6), 2.0)
        F.put(text_card(question, 960, 62, "#ffffff", "#2b2b52", "#ffd43b"), W / 2, 420, sc=max(0.05, 0.5 + 0.5 * kq),
              alpha=clamp(kq * 2))
        for i, op in enumerate(options):
            ko = back_out(prog(t, 1.0 + i * 0.25, 0.5), 2.2)
            state = "idle" if t < reveal else ("good" if i == good else "bad")
            y = 740 + i * 290
            x = W / 2 + (1 - ko) * 900
            sc = 1.45
            if t >= reveal and i == good:
                kk = t - reveal
                sc *= 1 + 0.12 * math.sin(kk * 9) * math.exp(-kk * 2.2)
            F.put(option_card(letters[i], op, state), x, y, sc=sc)
            if t >= reveal and i == good:
                F.put(art.check(150, True), W / 2 + 390, y - 100, sc=max(0.05, back_out(prog(t, reveal, 0.4), 2.5)))
        if c0 <= t < reveal:
            rem = reveal - t
            n = max(1, min(3, int(math.ceil(rem - 0.2))))
            F.put(_ring_bg(), W / 2, 1620)
            F.put(big_num(n), W / 2, 1615, sc=0.85 * (1 + 0.35 * ((rem - 0.2) % 1) ** 3))
        if t >= reveal:
            F.put(word_sprite("BRAVO !", 120, "#ffd43b", "#e8590c"), W / 2, 1620,
                  sc=max(0.05, back_out(prog(t, reveal + 0.15, 0.5), 2.5)), rot=math.sin((t - reveal) * 5) * 5)
            confetti_burst(F, W / 2, 740 + good * 290, t, reveal, 90, seed=3)
        mini2(F, S, t, 170, H - 170, 230, 1.2, jump_at=[reveal], spin_at=[reveal])
        star_wipe(F, S, t)
        return F

    def sfx(S):
        c0, reveal = times(S)
        ev = [("whoosh", 0.0)] + [("pop", 1.0 + i * 0.25) for i in range(3)]
        ev += [("tick", c0 + 0.2), ("drumroll", reveal - 1.3), ("fanfare", reveal), ("sparkle", reveal + 0.1)]
        return ev

    sc = Scene(narr, draw, sfx=sfx, tail=1.0, speed=SPEED, pitch=PITCH, lead=0.7)
    sc.quiet_fn = lambda S: (S.t0 + times(S)[0], S.t0 + times(S)[1])
    return sc


def render_short(name, scenes, outdir):
    return render_video(name, scenes, outdir, music_fn=music_for(scenes), sfx_fn=music2.sfx,
                        music_gain=0.5, duck_depth=0.6)
