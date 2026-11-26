"""Épisode 1 (version animée) : Les animaux de la savane."""
import math
from kit2 import *
import art
from ep1 import car, _wind, _ruler, _lioness, _wave, _fly

BG = [lambda: bg_savanna(0, False), lambda: bg_savanna(1, False)]


def sky(F, S, t):
    sun2(F, S, t, 1640, 170, 230)
    drift_clouds(F, t, 3, 150, seed=2 + S.idx)
    birds(F, S, t, 230)
    butterflies(F, t, [(300, 760), (1500, 800)], seed=S.idx)


EL = art.elephant
GI = art.giraffe
LI = art.lion
ZE = art.zebra


def lioness(b=False):
    return _lioness()


# ---------------------------------------------------------------- intro
def intro_bg_extras(F, S, t):
    # floating bubbles
    for i in range(14):
        x = (i * 173 + 60) % W
        y = H + 80 - ((t * (60 + i * 7) + i * 140) % (H + 200))
        F.put(art.mini_star(40 + (i % 3) * 14, WIPE_COLS[i % 6]), x + 30 * math.sin(t + i), y,
              rot=(t * 40 + i * 30) % 360, alpha=0.8)


s_intro = intro2("Les animaux de la savane", [
    "Salut les explorateurs ! C'est moi, Mini, l'étoile de MiniWonder !",
    "Aujourd'hui, on part en voyage en Afrique, pour découvrir les animaux de la savane !",
    "Ouvre grand tes yeux et tes oreilles : à la fin, il y aura un petit quiz !",
], bg_intro, extras=intro_bg_extras)


# ---------------------------------------------------------------- la savane
def savane_actor(F, S, t, shift):
    pop_label(F, S, t, "Un acacia", 330, 300, S.cue(0) + 2.2, 50, "#51cf66")
    if t > S.cue(1):
        out = ease_in_out(prog(t, S.cue(2) - 0.3, 0.4))
        k1 = back_out(prog(t, S.cue(1) + 1.2, 0.5), 2.2)
        k2 = back_out(prog(t, S.cue(1) + 2.6, 0.5), 2.2)
        if k1 > 0.02:
            x = 760 - out * 1500
            F.put(art.cloud(300, "#cfd8e3", "#9fb0c2", True, "o"), x, 380 + math.sin(t * 3) * 10, sc=k1)
            for i in range(10):
                yy = 470 + ((t * 320 + i * 53) % 170)
                F.put(art.raindrop(26), x - 110 + i * 24, yy, alpha=k1)
            pop_label(F, S, t, "Saison des pluies", x, 700, S.cue(1) + 1.2, 46, "#4dabf7")
        if k2 > 0.02:
            x = 1220 + out * 1500
            F.put(art.sun_rays(240), x, 420, sc=k2, rot=(t * 40) % 360)
            F.put(art.sun_body(240), x, 420, sc=k2)
            pop_label(F, S, t, "Saison sèche", x, 700, S.cue(1) + 2.6, 46, "#ff922b")
    if t > S.cue(2):
        crew = [(EL, 0.45), (GI, 0.42), (LI, 0.45), (ZE, 0.45)]
        for i, (fn, sc) in enumerate(crew):
            x = 330 + i * 370
            hop_in(F, S, t, fn, S.cue(2) + 0.2 + i * 0.3, x, x, 1010, sc, 1, 0.6, seed=i, amp=1.4)


def _hop_up_sfx(S):
    return [("boing", S.cue(2) + 0.5 + i * 0.3) for i in range(4)]


s_savane = topic2("LA SAVANE", [
    "La savane, c'est une immense plaine couverte de hautes herbes, avec quelques arbres, comme l'acacia.",
    "Il y fait chaud toute l'année. Il y a une saison des pluies, et une saison sèche.",
    "Beaucoup d'animaux incroyables y vivent. Allons les rencontrer !",
], BG[0], savane_actor, extras=sky, lab_bg="#ff922b")
_b = s_savane.sfx_fn
s_savane.sfx_fn = lambda S: _b(S) + _hop_up_sfx(S) + [("pop", S.cue(0) + 2.2), ("pop", S.cue(1) + 1.2), ("pop", S.cue(1) + 2.6)]


# ---------------------------------------------------------------- animals
def animal(fn, home, y=1000, sc=1.0, extra=None, x0=-500, shift_to=430):
    def actor(F, S, t, shift):
        if extra:
            extra(F, S, t, shift)
        hop_in(F, S, t, fn, 0.6, x0, home - shift * (home - shift_to), y, sc, 3, 1.8, seed=S.idx)
    return actor


def landing_sfx(S):
    return [("boing", 0.6 + 1.8 - 0.1)]


def eleph_extra(F, S, t, shift):
    t0, t1 = S.cue(1) + 1.0, S.cue(2) - 0.2
    if t0 < t < t1 + 0.4:
        out = ease_in_out(prog(t, t1, 0.4))
        for i in range(5):
            k = back_out(prog(t, t0 + i * 0.18, 0.4), 2.4)
            sx, sy, rot, hop = dance_params(S, t, 0.8, i * 0.2)
            F.put(car(), 1130 + i * 150, 480 + out * 600 - hop, sc=max(0.05, k), rot=rot)
    if S.cue(3) < t < S.cue(4) - 0.3:
        for i in range(3):
            a = (t * 2 + i / 3) % 1
            F.put(_wind(), 360 - a * 120, 560 + i * 40, alpha=1 - a)


s_eleph = topic2("L'ÉLÉPHANT", [
    "Voici l'éléphant d'Afrique. C'est le plus gros animal qui vit sur la terre ferme !",
    "Il peut peser six tonnes. C'est aussi lourd que cinq voitures !",
    "Avec sa trompe, il respire, il sent les odeurs, il boit, et il attrape sa nourriture.",
    "Et ses grandes oreilles ? Il les agite comme des éventails pour se rafraîchir.",
    "Le savais-tu ? Sa trompe possède des dizaines de milliers de muscles ! C'est pour ça qu'elle est si agile.",
], BG[1], animal(EL, 620, extra=eleph_extra), extras=sky,
    chip_items=[(1, "6 tonnes", "#ff6b81"), (2, "Trompe = nez + main", "#4dabf7"), (3, "Oreilles = éventails", "#51cf66")],
    fact=(4, "Sa trompe possède des dizaines de milliers de muscles ! C'est pour ça qu'elle est si agile."))


def gir_extra(F, S, t, shift):
    if S.cue(1) < t < S.cue(3):
        k = ease_out(prog(t, S.cue(1) + 0.2, 0.8))
        out = ease_in_out(prog(t, S.cue(3) - 0.5, 0.4))
        F.put(_ruler(), 900, 1000 - 380, alpha=k * (1 - out), sy=max(0.05, k), sx=1.0)


s_gir = topic2("LA GIRAFE", [
    "Lève la tête... encore plus haut ! Voici la girafe, l'animal le plus haut du monde.",
    "Elle peut mesurer jusqu'à cinq mètres et demi : aussi haut qu'une maison de deux étages !",
    "Grâce à son long cou, elle attrape les feuilles tout en haut des acacias.",
    "Le savais-tu ? Sa langue est bleu foncé, et elle mesure presque cinquante centimètres !",
    "Et son long cou n'a que sept vertèbres, exactement comme le tien !",
], BG[0], animal(GI, 600, 1010, x0=-400, extra=gir_extra), extras=sky,
    chip_items=[(1, "Jusqu'à 5,5 mètres", "#ff922b"), (2, "Mange les feuilles d'acacia", "#51cf66")],
    fact=(3, "Sa langue bleu foncé mesure presque 50 cm. Et son long cou a 7 vertèbres, comme le tien !"),
    lab_bg="#ff922b")


def lion_actor(F, S, t, shift):
    if 2.6 < t < S.cue(1):
        for i in range(3):
            a = ((t - 2.6) * 1.2 + i / 3) % 1
            F.put(_wave(), 930 + a * 180, 640, sc=0.6 + a * 0.6, alpha=1 - a)
    if t > S.cue(1) + 0.4:
        out = ease_in_out(prog(t, S.cue(3) - 0.4, 0.5))
        for i, xx in enumerate((470, 190)):
            hop_in(F, S, t, lioness, S.cue(1) + 0.4 + i * 0.4, -300, xx - out * 900, 900, 0.55, 3, 1.4, seed=i + 3)
    hop_in(F, S, t, LI, 0.6, -500, 620 - shift * 190, 1000, 1.0, 3, 1.8, seed=2)


s_lion = topic2("LE LION", [
    "Écoute bien... Voici le lion, qu'on appelle souvent le roi de la savane !",
    "Les lions vivent en famille. Un groupe de lions s'appelle une troupe.",
    "Ce sont surtout les lionnes qui chassent, en équipe.",
    "Le savais-tu ? Son rugissement peut s'entendre jusqu'à huit kilomètres ! Et le lion dort jusqu'à vingt heures par jour.",
], BG[1], lion_actor, extras=sky,
    chip_items=[(1, "Un groupe = une troupe", "#ff922b"), (2, "Les lionnes chassent", "#ff6b81")],
    fact=(3, "Son rugissement s'entend jusqu'à 8 km ! Et le lion dort jusqu'à 20 heures par jour."),
    lab_bg="#e8590c")


def zebra_actor(F, S, t, shift):
    if t > S.cue(1):
        out = ease_in_out(prog(t, S.cue(3) - 0.4, 0.5))
        for i, (xx, y) in enumerate(((620, 860), (880, 830))):
            hop_in(F, S, t, ZE, S.cue(1) + i * 0.5, -300, xx - out * 1500, y, 0.5, 3, 1.6, seed=i + 5)
    hop_in(F, S, t, ZE, 0.6, -500, 620 - shift * 190, 1000, 1.0, 3, 1.8, seed=4)
    if S.cue(2) < t < S.cue(3) - 0.3:
        for i in range(3):
            a = t * 1.5 + i * 2.1
            F.put(_fly(), 640 + 260 * math.cos(a) * (1 + 0.3 * math.sin(a * 2)), 560 + 100 * math.sin(a * 1.3))


s_zebra = topic2("LE ZÈBRE", [
    "Et voici le zèbre, avec son joli pyjama à rayures !",
    "Les zèbres vivent en troupeaux, et voyagent ensemble pour trouver de l'herbe fraîche.",
    "Les scientifiques pensent que leurs rayures aident à éloigner les mouches qui piquent.",
    "Le savais-tu ? Il n'existe pas deux zèbres avec les mêmes rayures. Elles sont uniques, comme tes empreintes de doigts !",
], BG[0], zebra_actor, extras=sky,
    chip_items=[(1, "Vit en troupeau", "#4dabf7"), (2, "Rayures anti-mouches", "#845ef7")],
    fact=(3, "Il n'existe pas deux zèbres avec les mêmes rayures, comme tes empreintes de doigts !"),
    lab_bg="#495057")

for sc in (s_eleph, s_gir, s_lion, s_zebra):
    _f = sc.sfx_fn
    sc.sfx_fn = (lambda f: lambda S: f(S) + landing_sfx(S))(_f)


# ---------------------------------------------------------------- recap
def recap_actor(F, S, t, shift):
    items = [(EL, 0.5, "Le plus gros", "#ff6b81"), (GI, 0.42, "Le plus haut", "#ff922b"),
             (LI, 0.5, "Vit en troupe", "#e8590c"), (ZE, 0.5, "Rayures uniques", "#4dabf7")]
    for i, (fn, sc, txt, col) in enumerate(items):
        t0 = S.cue(i + 1) - 0.2
        x = 230 + i * 420
        hop_in(F, S, t, fn, t0, x, x, 760, sc, 1, 0.6, seed=i, amp=1.3)
        pop_label(F, S, t, txt, x, 840, t0, 46, col)


s_recap = topic2("RÉCAPITULONS", [
    "Récapitulons !",
    "L'éléphant est le plus gros animal terrestre.",
    "La girafe est l'animal le plus haut.",
    "Les lions vivent en troupe.",
    "Et chaque zèbre a des rayures uniques.",
    "Maintenant, c'est l'heure du quiz ! Tu es prêt ?",
], BG[1], recap_actor, extras=sky, lab_bg="#845ef7")
_r = s_recap.sfx_fn
s_recap.sfx_fn = lambda S: _r(S) + [("boing", S.cue(i + 1)) for i in range(4)] + [("sparkle", S.cue(5))]

# ---------------------------------------------------------------- quiz + outro
q1 = quiz2(1, "Quel animal est le plus haut du monde ?", ["Le lion", "La girafe", "Le zèbre"], 1, [
    "Question numéro un ! Quel animal est le plus haut du monde ? Le lion, la girafe, ou le zèbre ?",
    "C'est la girafe ! Elle peut mesurer jusqu'à cinq mètres et demi.",
])
q2 = quiz2(2, "Comment s'appelle un groupe de lions ?", ["Une meute", "Une troupe", "Un essaim"], 1, [
    "Question numéro deux ! Comment s'appelle un groupe de lions ? Une meute, une troupe, ou un essaim ?",
    "Bravo, c'est une troupe !",
])
q3 = quiz2(3, "À quoi servent les grandes oreilles de l'éléphant ?", ["À se rafraîchir", "À voler", "À nager"], 0, [
    "Dernière question ! À quoi servent les grandes oreilles de l'éléphant ? À se rafraîchir, à voler, ou à nager ?",
    "Oui ! Il les agite pour se rafraîchir.",
])
s_out = outro2([
    "Bravo ! Tu es un vrai explorateur de la savane !",
    "Raconte à ta famille tout ce que tu as appris aujourd'hui.",
    "À très vite pour une nouvelle découverte sur MiniWonder !",
], lambda: bg_savanna(0, False), parade=[(EL, 0.5), (GI, 0.42), (LI, 0.5), (ZE, 0.5)], extras=sky)

SCENES = [s_intro, s_savane, s_eleph, s_gir, s_lion, s_zebra, s_recap, q1, q2, q3, s_out]

if __name__ == "__main__":
    import sys
    only = set(map(int, sys.argv[1:])) if len(sys.argv) > 1 else None
    render_video("MiniWonder_01_Animaux_de_la_savane_ANIME", SCENES, "/home/claude/mw/out/ep1b",
                 music_fn=music_for(SCENES), sfx_fn=music2.sfx, music_gain=0.5, duck_depth=0.6, only=only)
