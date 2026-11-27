"""Short 02 (vrai-ou-faux) : les nuages, avec Cumulo (le nuage de la vidéo « le cycle de l'eau »)."""
import os
os.environ["MW_VERTICAL"] = "1"
import math, random
from functools import lru_cache
from kit_short import *
import art
from art import Pen, eye, cheek

STYLE = 1  # len(published.shorts) % 4


# ---------------------------------------------------------------- Cumulo (même dessin que ep02_eau.py)
@lru_cache(None)
def cumulo(blink=False, size=440):
    p = Pen(440, 290)
    body, shade = "#ffffff", "#c9d6f5"
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
    p.arc(222, 196, 20, 13, 20, 160, "#55606e", 5)
    img = p.done()
    return img.resize((size, int(size * 290 / 440)), Image.LANCZOS) if size != 440 else img


def cumulo_fn(blink=False):
    return cumulo(blink, 420)


# ---------------------------------------------------------------- décors verticaux
@lru_cache(None)
def bg_ciel():
    img = to_img(vgrad("#4fa8ee", "#cfeeff")).convert("RGBA")
    p = Pen(W, H, 1)
    hills(p, 1700, 60, "#8fd18a", 3)
    hills(p, 1780, 50, "#6cbf6a", 8)
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_lourd():
    img = to_img(vgrad("#7f8fd6", "#f3d9ff")).convert("RGBA")
    p = Pen(W, H, 1)
    hills(p, 1720, 70, "#9ccf8f", 5)
    hills(p, 1800, 40, "#79b86f", 11)
    img.alpha_composite(p.done())
    return img.convert("RGB")


@lru_cache(None)
def bg_brume():
    img = to_img(vgrad("#a9c4d6", "#eef4f7")).convert("RGBA")
    p = Pen(W, H, 1)
    hills(p, 1450, 90, "#a7c4a4", 2)
    # petits arbres ronds
    for x in (150, 380, 760, 960):
        p.rect(x - 12, 1380, x + 12, 1470, 6, "#8a7a6a")
        p.circ(x, 1360, 70, "#93b98f")
    hills(p, 1620, 60, "#8fb48b", 9)
    for i, y in enumerate((1250, 1420, 1560, 1700)):
        p.rect(-100, y, W + 100, y + 90, 45, (255, 255, 255, 120 - i * 10))
    img.alpha_composite(p.done())
    return img.convert("RGB")


def sky(F, S, t):
    drift_clouds(F, t, 2, 560, seed=7 + S.idx, scale=0.55)


def heavy(F, S, t):
    drift_clouds(F, t, 2, 560, seed=3, scale=0.5)
    # cent petits éléphants ? non : une balance amusante, cumulo d'un côté
    birds(F, S, t, 980)


def fog(F, S, t):
    rnd = random.Random(5)
    for i in range(3):
        x = (rnd.uniform(0, W) + t * 25) % (W + 600) - 300
        F.put(art.cloud(520, "#ffffff", "#e6eef3"), x, 1200 + i * 140, alpha=0.55)


def sub(text, col, t0=1.0):
    def ex(F, S, t):
        sky(F, S, t)
        pop_label(F, S, t, text, W / 2, 640, t0, 80, col)
    return ex


def cumulo_actor(y=1370):
    def act(F, S, t):
        hop_in(F, S, t, cumulo_fn, 0.5 if S.idx == 0 else -1, -500, W / 2 - 60, y, 1.0, 3, 1.5, seed=2)
    return act


# ---------------------------------------------------------------- vrai / faux
GREEN, RED = "#2fb85a", "#ef4b4b"


def vrai_faux(sc, answer, explain=None, explain_col="#845ef7"):
    """Adds two VRAI / FAUX pills; at line 1 the right one grows with a check, the other fades.
    The pause between line 0 and line 1 is the thinking time (drumroll)."""
    base_draw, base_sfx = sc.draw, sc.sfx_fn

    def pills(F, S, t):
        rv = S.cue(1) - 0.15
        k = back_out(prog(t, 1.2, 0.5), 2.2)
        for i, (word, col) in enumerate((("VRAI", GREEN), ("FAUX", RED))):
            x = W / 2 + (-230 if i == 0 else 230)
            good = (word == answer)
            if t < rv:
                sc_ = max(0.05, k) * (1 + 0.05 * math.sin(t * 6 + i * 3))
                F.put(label(word, 92, col), x, 640, sc=sc_, rot=math.sin(t * 4 + i) * 4)
            else:
                kk = t - rv
                if good:
                    g = 1.25 * (1 + 0.15 * math.sin(kk * 9) * math.exp(-kk * 2.2))
                    gx = x + (W / 2 - x) * ease_out(prog(t, rv, 0.4))
                    F.put(label(word + " !", 104, col), gx, 640, sc=g)
                    F.put(art.check(130, answer == "VRAI"), gx + 270, 560,
                          sc=max(0.05, back_out(prog(t, rv, 0.4), 2.5)))
                    confetti_burst(F, gx, 640, t, rv, 70, seed=4)
        if explain and t > rv + 0.6:
            pop_label(F, S, t, explain, W / 2, 830, rv + 0.6, 64, explain_col)

    # inject pills into the world layer via the scene's extras hook
    sc._pills = pills

    def sfx(S):
        ev = base_sfx(S)
        rv = S.cue(1) - 0.15
        ev += [("pop", 1.2), ("pop", 1.35), ("drumroll", rv - 1.3),
               ("fanfare", rv), ("sparkle", rv + 0.1)]
        if explain:
            ev.append(("pop", rv + 0.6))
        return ev

    sc.sfx_fn = sfx
    return sc


def vf_scene(n, title, col, statement, reveal, answer, card, bg, extras, explain=None, actor_y=1370):
    holder = {}

    def ex(F, S, t):
        extras(F, S, t)
        holder["sc"]._pills(F, S, t)

    sc = short_scene([statement, 1.4, reveal], bg, cumulo_actor(actor_y), title, col, card=card, card_cue=0,
                     badge=n, extras=ex)
    holder["sc"] = sc
    return vrai_faux(sc, answer, explain)


SCENES = [
    short_scene(["Salut, c'est Mini ! Vrai ou faux ? Trois questions sur les nuages, avec mon ami Cumulo !"],
                bg_ciel, cumulo_actor(), "VRAI OU FAUX ?", "#4dabf7", extras=sub("LES NUAGES", "#4dabf7"), first=True,
                title_size=110),
    vf_scene(1, "De quoi est fait un nuage ?", "#4dabf7",
             "Un : un nuage est fait de milliards de toutes petites gouttes d'eau. Vrai ou faux ?",
             "Vrai ! Et quand il fait très froid, ce sont de minuscules cristaux de glace !",
             "VRAI", "Un nuage, c'est plein de gouttes d'eau ?", bg_ciel, sky, "+ des cristaux de glace"),
    vf_scene(2, "Un nuage, c'est lourd ?", "#845ef7",
             "Deux : un nuage ne pèse rien du tout, il est plus léger qu'une plume. Vrai ou faux ?",
             "Faux ! Un petit nuage pèse environ cinq cents tonnes, autant que cent éléphants ! "
             "Mais ses gouttes sont si petites qu'elles flottent dans l'air.",
             "FAUX", "Un nuage ne pèse rien du tout ?", bg_lourd, heavy, "Environ 500 tonnes !"),
    vf_scene(3, "Le brouillard", "#20a4a4",
             "Trois : le brouillard, c'est un nuage posé tout près du sol. Vrai ou faux ?",
             "Vrai ! Quand tu marches dans le brouillard, tu te promènes dans un nuage !",
             "VRAI", "Le brouillard, un nuage ?", bg_brume, fog, "Un nuage au ras du sol !"),
    short_scene(["Combien de bonnes réponses ? Pour suivre une goutte d'eau jusqu'aux nuages, "
                 "regarde notre vidéo sur le cycle de l'eau !"],
                bg_ciel, cumulo_actor(), "BRAVO !", "#e8590c", extras=sub("Le cycle de l'eau", "#1c7ed6", 2.2),
                last=True, title_size=120),
]

if __name__ == "__main__":
    render_short("MiniWonder_Short_02_Nuages", SCENES, "/home/claude/mw/out/short02", STYLE)
