"""Épisode 3 : Comment pousse une plante ?"""
import math
from collections import OrderedDict
from kit import *
import art

GROUND = 640
_PC = OrderedDict()


def plant_img(g, flower=0.0, fruit=0.0):
    key = (round(g, 2), round(flower, 1), round(fruit, 1))
    if key not in _PC:
        _PC[key] = art.plant(*key[:1], flower=key[1], fruit=key[2])
        if len(_PC) > 70:
            _PC.popitem(last=False)
    else:
        _PC.move_to_end(key)
    return _PC[key]


def put_plant(F, x, g, flower=0.0, fruit=0.0):
    im = plant_img(g, flower, fruit)
    # seed sits at image y=630 (ground=560 + 70); place it at GROUND + 70
    F.put(im, x, GROUND + 70 - 630 + im.height / 2)


def bg():
    return bg_garden()


# ---------------------------------------------------------------- intro
s_intro = intro("Comment pousse une plante ?", [
    "Salut les explorateurs ! C'est moi, Mini, l'étoile de MiniWonder !",
    "Regarde ce que j'ai trouvé : une toute petite graine ! Comment une si petite graine peut-elle devenir une grande plante ?",
    "On va le découvrir ensemble. Et à la fin, il y aura un quiz !",
], bg_intro)
_d0 = s_intro.draw


@lru_cache(None)
def seed_small():
    p = Pen(120, 90, 3)
    p.ell(60, 45, 50, 34, "#a0682e", "#5b3a1a", 4)
    p.ell(46, 36, 18, 9, (255, 255, 255, 80))
    return p.done()


def _intro_draw(S, t):
    F = _d0(S, t)
    t0 = S.cue(1) + 0.4
    if t > t0:
        k = back_out(prog(t, t0, 0.6))
        F.put(seed_small(), 720, 760 + math.sin(t * 3) * 6, sc=max(0.01, k))
    return F


s_intro.draw = _intro_draw


# ---------------------------------------------------------------- la graine
def seed_actor(F, S, t, shift):
    k = back_out(prog(t, 0.2, 0.8))
    F.put(art.seed_cut(620), 640, 520 + math.sin(t * 1.5) * 6, sc=max(0.01, k))
    # pointers
    marks = [(1, (800, 430), "#51cf66"), (2, (560, 560), "#ff922b"), (3, (390, 420), "#a0682e")]
    for ci, (x, y), col in marks:
        if t > S.cue(ci):
            kk = back_out(prog(t, S.cue(ci), 0.4))
            F.put(_ring(col), x, y, sc=max(0.01, kk) * (1 + 0.06 * math.sin(t * 6)))


@lru_cache(None)
def _ring(col):
    p = Pen(140, 140, 3)
    p.circ(70, 70, 60, None, col, 9)
    return p.done()


s_seed = topic("LA GRAINE", [
    "Une graine, c'est comme une petite boîte à goûter.",
    "À l'intérieur, il y a un bébé plante, qu'on appelle l'embryon.",
    "Il y a aussi des réserves de nourriture, pour l'aider à grandir au début.",
    "Et tout autour, une enveloppe solide la protège.",
], bg_sky, seed_actor,
    chip_items=[(1, "Bébé plante = embryon", "#51cf66"), (2, "Réserves de nourriture", "#ff922b"), (3, "Enveloppe protectrice", "#a0682e")],
    lab_bg="#a0682e")


# ---------------------------------------------------------------- besoins
def needs_actor(F, S, t, shift):
    items = [(1, "water", "L'eau", "#4dabf7", 520), (2, "heat", "La chaleur", "#ff6b81", 960), (3, "air", "L'air", "#74c0fc", 1400)]
    out = ease_in_out(prog(t, S.cue(4) - 0.2, 0.6))
    for ci, ic, txt, col, x in items:
        if t < S.cue(ci) - 0.1:
            continue
        k = back_out(prog(t, S.cue(ci) - 0.1, 0.5))
        y = 330 - out * 600
        F.put(art.icon(ic, 220), x, y + math.sin(t * 2 + x) * 8, sc=max(0.01, k))
        F.put(label(txt, 54, col), x, y + 160, sc=max(0.01, k))
    # seed in soil wakes up
    g = 0.12 * ease_in_out(prog(t, S.cue(4) + 0.5, 3.0))
    put_plant(F, 960, g)
    if t > S.cue(4) + 0.3:
        kk = back_out(prog(t, S.cue(4) + 0.3, 0.6))
        F.put(label("= la germination", 60, "#2f9e44"), 960, 400, sc=max(0.01, kk))


def _needs_scene():
    sc = topic("DE QUOI A-T-ELLE BESOIN ?", [
        "Pour se réveiller, la graine a besoin de trois choses.",
        "De l'eau...",
        "De la chaleur...",
        "Et de l'air !",
        "Quand tout est prêt, la graine se réveille, et commence à pousser : c'est la germination.",
    ], bg, needs_actor, lab_bg="#4dabf7")
    base = sc.sfx_fn
    sc.sfx_fn = lambda S: base(S) + [("pop", S.cue(i) - 0.1) for i in (1, 2, 3)] + [("chime", S.cue(4) + 0.3)]
    return sc


s_needs = _needs_scene()


# ---------------------------------------------------------------- germination
def germ_actor(F, S, t, shift):
    g1 = 0.12 + 0.23 * ease_in_out(prog(t, S.cue(0), S.end(1) - S.cue(0)))
    g2 = 0.35 * 0 + 0.27 * ease_in_out(prog(t, S.cue(2), S.end(3) - S.cue(2) + 0.5))
    put_plant(F, 760, g1 + g2)
    # water sucked by root
    if S.cue(1) < t < S.cue(2):
        for i in range(5):
            ph = (t * 0.7 + i / 5) % 1
            F.put(art.raindrop(20), 690 + (i % 3) * 70, 960 - ph * 220, alpha=math.sin(ph * math.pi))
    if S.cue(2) < t:
        F.put(art.sun(200), 1150, 170, sc=1 + 0.04 * math.sin(t * 2.5), rot=math.sin(t * 1.3) * 6)


s_germ = topic("LA GERMINATION", [
    "D'abord, une petite racine sort de la graine. Elle pousse toujours vers le bas.",
    "La racine accroche la plante dans le sol, et elle boit l'eau de la terre.",
    "Ensuite, une petite tige pousse vers le haut, vers la lumière.",
    "Et bientôt, les premières feuilles apparaissent !",
], bg, germ_actor,
    chip_items=[(0, "La racine descend", "#a0682e"), (2, "La tige monte", "#51cf66"), (3, "Les premières feuilles", "#2f9e44")],
    lab_bg="#2f9e44")


# ---------------------------------------------------------------- photosynthèse
def photo_actor(F, S, t, shift):
    x = 760 - shift * 330
    g = 0.62 + 0.38 * ease_in_out(prog(t, 0.0, 4.0))
    sx, sy = 1100 - shift * 330, 150
    F.put(art.sun(220), sx, sy, sc=1 + 0.04 * math.sin(t * 2.5), rot=math.sin(t * 1.3) * 6)
    put_plant(F, x, g)
    leaf_y = 380
    if S.cue(1) < t < S.cue(4):
        a = 1 - ease_in_out(prog(t, S.cue(4) - 0.6, 0.5))
        # light rays
        for i in range(3):
            ph = (t * 0.9 + i / 3) % 1
            px = sx + (x + 40 - sx) * ph
            py = sy + (leaf_y - sy) * ph
            F.put(_ray(), px, py, alpha=a * math.sin(ph * math.pi))
        # water up the stem
        for i in range(3):
            ph = (t * 0.6 + i / 3) % 1
            F.put(art.raindrop(18), x + 6, 760 - ph * 380, alpha=a * math.sin(ph * math.pi))
        # CO2 in
        for i in range(2):
            ph = (t * 0.5 + i / 2) % 1
            F.put(art.icon("co2", 110), x - 380 + ph * 300, 330 + i * 120, alpha=a * math.sin(ph * math.pi))
    if S.cue(2) < t < S.cue(4):
        a = 1 - ease_in_out(prog(t, S.cue(4) - 0.6, 0.5))
        for i in range(3):
            ph = (t * 0.5 + i / 3) % 1
            F.put(art.icon("o2", 110), x + 110 + ph * 260, 420 - ph * 200 + i * 40, alpha=a * math.sin(ph * math.pi))


@lru_cache(None)
def _ray():
    p = Pen(60, 60, 3)
    p.circ(30, 30, 22, (255, 220, 80, 230))
    p.circ(30, 30, 12, (255, 250, 200, 255))
    return p.done()


s_photo = topic("LA PHOTOSYNTHÈSE", [
    "Les feuilles sont de vraies petites usines !",
    "Avec la lumière du soleil, l'eau puisée par les racines, et un gaz de l'air appelé dioxyde de carbone, elles fabriquent la nourriture de la plante.",
    "Et en même temps, elles rejettent de l'oxygène : l'air que nous respirons. Merci les plantes !",
    "C'est la photosynthèse.",
    "Le savais-tu ? Les feuilles sont vertes grâce à la chlorophylle, qui capture la lumière du soleil.",
], bg, photo_actor,
    chip_items=[(1, "Lumière + eau + air", "#ff922b"), (2, "Rejette de l'oxygène", "#51cf66"), (3, "= la photosynthèse", "#845ef7")],
    fact=(4, "Les feuilles sont vertes grâce à la chlorophylle, qui capture la lumière du soleil."),
    lab_bg="#845ef7")


# ---------------------------------------------------------------- fleur
def flower_actor(F, S, t, shift):
    x = 760
    fl = ease_in_out(prog(t, 0.3, 2.5))
    fr = ease_in_out(prog(t, S.cue(2) + 0.3, 2.5))
    put_plant(F, x, 1.0, flower=fl * (1 - fr), fruit=fr)
    top = 710 - 20 - 470 - 10  # flower centre y in screen space (seed_y-20-560-10)
    # bee
    if S.cue(1) - 0.5 < t < S.cue(2) + 1.0:
        k = ease_in_out(prog(t, S.cue(1) - 0.5, 2.0))
        leave = ease_in_out(prog(t, S.cue(2) - 0.5, 1.5))
        bx = -200 + (x + 60 + 200) * k + leave * 1400
        by = top - 50 + 30 * math.sin(t * 4) - leave * 300
        F.put(art.bee(150, int(t * 20) % 2), bx, by)
        # pollen dots trailing
        for i in range(6):
            F.put(_pollen(), bx - 60 - i * 26, by + 30 + 10 * math.sin(t * 6 + i), alpha=max(0, 0.9 - i * 0.14) * clamp(k * 3))
    if t > S.cue(3):
        for i in range(4):
            kk = back_out(prog(t, S.cue(3) + 0.3 + i * 0.25, 0.5))
            a = -math.pi / 2 + (i - 1.5) * 0.7
            F.put(seed_small(), x + 160 * math.cos(a) * 1.4, top + 20 + 140 * math.sin(a) + 60, sc=max(0.01, kk) * 0.55)


@lru_cache(None)
def _pollen():
    p = Pen(24, 24, 3)
    p.circ(12, 12, 8, "#ffd23f", "#e0a800", 2)
    return p.done()


s_flower = topic("LA FLEUR", [
    "Quand la plante a bien grandi, une jolie fleur apparaît.",
    "Une abeille vient boire son nectar. Sans le savoir, elle transporte du pollen d'une fleur à l'autre : c'est la pollinisation.",
    "Grâce au pollen, la fleur se transforme petit à petit en fruit.",
    "Et dans le fruit, il y a... de nouvelles graines ! Le cycle peut recommencer.",
], bg, flower_actor,
    chip_items=[(1, "La pollinisation", "#f59f00"), (2, "La fleur devient fruit", "#ff6b81"), (3, "De nouvelles graines", "#a0682e")],
    lab_bg="#ff6b81")


# ---------------------------------------------------------------- expérience
def exp_actor(F, S, t, shift):
    k = back_out(prog(t, 0.3, 0.7))
    F.put(art.jar(400), 620, 540, sc=max(0.01, k))
    if t > S.cue(2) + 2.0:
        for i in range(3):
            kk = back_out(prog(t, S.cue(2) + 2.0 + i * 0.5, 0.4))
            F.put(label(f"Jour {i * 2 + 1}", 40, "#495057"), 360 + i * 260, 920, sc=max(0.01, kk))


s_exp = topic("À TOI DE JOUER !", [
    "À toi de jouer ! Tu veux voir une graine germer ?",
    "Avec un adulte, mets du coton mouillé dans un pot en verre, et glisse un haricot sec contre la paroi.",
    "Garde le coton humide, et observe chaque jour. En quelques jours, tu verras sortir la racine, puis la tige !",
    "Maintenant, c'est l'heure du quiz ! Tu es prêt ?",
], bg_sky, exp_actor,
    chip_items=[(1, "1. Coton mouillé + haricot", "#4dabf7"), (2, "2. Garder humide", "#51cf66"), (2, "3. Observer chaque jour", "#ff922b")],
    lab_bg="#ff922b")


# ---------------------------------------------------------------- quiz + outro
q1 = quiz(1, "Qu'est-ce qui sort en premier de la graine ?", ["La fleur", "La racine", "Le fruit"], 1, [
    "Question numéro un ! Qu'est-ce qui sort en premier de la graine ? La fleur, la racine, ou le fruit ?",
    "C'est la racine ! Elle pousse vers le bas pour boire l'eau de la terre.",
])
q2 = quiz(2, "Que rejettent les feuilles pendant la photosynthèse ?", ["De l'oxygène", "Du chocolat", "De la fumée"], 0, [
    "Question numéro deux ! Que rejettent les feuilles pendant la photosynthèse ? De l'oxygène, du chocolat, ou de la fumée ?",
    "Bravo, de l'oxygène ! C'est l'air que nous respirons.",
])
q3 = quiz(3, "Quel insecte aide la fleur à devenir un fruit ?", ["La fourmi", "L'abeille", "Le moustique"], 1, [
    "Dernière question ! Quel insecte transporte le pollen, et aide la fleur à devenir un fruit ? La fourmi, l'abeille, ou le moustique ?",
    "Oui, l'abeille ! Grâce à la pollinisation.",
])


def outro_extra(F, S, t):
    F.put(art.flower(130), 1450, 980, anchor="b", rot=math.sin(t * 2) * 4)
    F.put(art.flower(110, "#845ef7"), 470, 1000, anchor="b", rot=math.sin(t * 2 + 1) * 4)


s_out = outro([
    "Bravo ! Maintenant, tu sais comment pousse une plante !",
    "Essaie l'expérience du haricot avec un adulte, et observe bien.",
    "À très vite pour une nouvelle découverte sur MiniWonder !",
], bg_intro, outro_extra)

SCENES = [s_intro, s_seed, s_needs, s_germ, s_photo, s_flower, s_exp, q1, q2, q3, s_out]

if __name__ == "__main__":
    render_video("MiniWonder_03_Comment_pousse_une_plante", SCENES, "/home/claude/mw/out/ep3", music_seed=2)
