"""Épisode 1 : Les animaux de la savane."""
import sys, math
from kit import *
import art


def bg0():
    return bg_savanna(0)


def bg1():
    return bg_savanna(1)


def clouds(F, S, t):
    drifting_clouds(F, t, 3, 140, seed=2)


# ---------------------------------------------------------------- 1 intro
def intro_extras(F, S, t):
    pass


s_intro = intro("Les animaux de la savane", [
    "Salut les explorateurs ! C'est moi, Mini, l'étoile de MiniWonder !",
    "Aujourd'hui, on part en voyage en Afrique, pour découvrir les animaux de la savane.",
    "Ouvre grand tes yeux et tes oreilles : à la fin, il y aura un petit quiz !",
], bg_intro)


# ---------------------------------------------------------------- 2 la savane
def savane_actor(F, S, t, shift):
    clouds(F, S, t)
    # acacia tag
    if t > S.cue(0) + 2.2:
        k = back_out(prog(t, S.cue(0) + 2.2, 0.5))
        F.put(label("Un acacia", 50, "#51cf66"), 330, 300, sc=max(0.01, k))
    # seasons
    if t > S.cue(1):
        k1 = back_out(prog(t, S.cue(1) + 1.2, 0.5))
        k2 = back_out(prog(t, S.cue(1) + 2.6, 0.5))
        out = ease_in_out(prog(t, S.cue(2) - 0.3, 0.4))
        if k1 > 0:
            F.put(art.cloud(300, "#cfd8e3", "#9fb0c2", True, "o"), 760 - out * 1500, 380, sc=max(0.01, k1))
            for i in range(9):
                yy = 470 + ((t * 300 + i * 53) % 160)
                F.put(art.raindrop(26), 660 + i * 25 - out * 1500, yy, alpha=k1)
            F.put(label("Saison des pluies", 46, "#4dabf7"), 760 - out * 1500, 690, sc=max(0.01, k1))
        if k2 > 0:
            F.put(art.sun(240), 1220 + out * 1500, 420, sc=max(0.01, k2), rot=math.sin(t * 1.3) * 6)
            F.put(label("Saison sèche", 46, "#ff922b"), 1220 + out * 1500, 690, sc=max(0.01, k2))
    # animals peek
    if t > S.cue(2):
        sprites = [(art.elephant, 0.45), (art.giraffe, 0.42), (art.lion, 0.45), (art.zebra, 0.45)]
        for i, (fn, sc) in enumerate(sprites):
            k = back_out(prog(t, S.cue(2) + 0.3 + i * 0.35, 0.6))
            x = 360 + i * 380
            F.put(fn(), x, 1010 + (1 - k) * 450, sc=sc, anchor="b")


s_savane = topic("LA SAVANE", [
    "La savane, c'est une immense plaine couverte de hautes herbes, avec quelques arbres, comme l'acacia.",
    "Il y fait chaud toute l'année. Il y a une saison des pluies, et une saison sèche.",
    "Beaucoup d'animaux incroyables y vivent. Allons les rencontrer !",
], bg0, savane_actor, lab_bg="#ff922b")


# ---------------------------------------------------------------- animals
def animal_actor(sprite_fn, home_x, base_y=1000, sc=1.0, from_x=-500, extra=None):
    def actor(F, S, t, shift):
        clouds(F, S, t)
        if extra:
            extra(F, S, t, shift)
        x = walk_in(F, sprite_fn(), t, 0.2, from_x, home_x - shift * (home_x - 430), base_y, 1.8, sc)
    return actor


@lru_cache(None)
def car():
    p = Pen(160, 90, 3)
    p.rect(10, 30, 150, 70, 18, "#ff6b81", "#3a2e2a", 3)
    p.rect(40, 8, 115, 40, 14, "#ff8fa3", "#3a2e2a", 3)
    p.rect(52, 14, 76, 34, 4, "#cfefff")
    p.rect(82, 14, 106, 34, 4, "#cfefff")
    p.circ(45, 72, 15, "#3a2e2a")
    p.circ(118, 72, 15, "#3a2e2a")
    p.circ(45, 72, 6, "#cccccc")
    p.circ(118, 72, 6, "#cccccc")
    return p.done()


def eleph_extra(F, S, t, shift):
    # five cars for the weight comparison
    t0, t1 = S.cue(1) + 1.0, S.cue(2) - 0.2
    if t0 < t < t1 + 0.4:
        out = ease_in_out(prog(t, t1, 0.4))
        for i in range(5):
            k = back_out(prog(t, t0 + i * 0.18, 0.4))
            F.put(car(), 1130 + i * 150, 480 + out * 600, sc=max(0.01, k))
    # ear flapping hint: little wind lines
    if S.cue(3) < t < S.cue(4) - 0.3:
        for i in range(3):
            a = (t * 2 + i / 3) % 1
            F.put(_wind(), 360 - a * 120, 560 + i * 40, alpha=1 - a)


@lru_cache(None)
def _wind():
    p = Pen(120, 30, 2)
    p.stroke([(110, 15), (60, 8), (10, 15)], (255, 255, 255, 230), 8, 4)
    return p.done()


s_eleph = topic("L'ÉLÉPHANT", [
    "Voici l'éléphant d'Afrique. C'est le plus gros animal qui vit sur la terre ferme !",
    "Il peut peser six tonnes. C'est aussi lourd que cinq voitures !",
    "Avec sa trompe, il respire, il sent les odeurs, il boit, et il attrape sa nourriture.",
    "Et ses grandes oreilles ? Il les agite comme des éventails pour se rafraîchir.",
    "Le savais-tu ? Sa trompe possède des dizaines de milliers de muscles ! C'est pour ça qu'elle est si agile.",
], bg1, animal_actor(art.elephant, 620, 1000, 1.0, extra=eleph_extra),
    chip_items=[(1, "6 tonnes", "#ff6b81"), (2, "Trompe = nez + main", "#4dabf7"),
                (3, "Oreilles = éventails", "#51cf66")],
    fact=(4, "Sa trompe possède des dizaines de milliers de muscles ! C'est pour ça qu'elle est si agile."))
# 6-tonnes chip sits above cars: move chips with custom positions handled by default column


def gir_extra(F, S, t, shift):
    if S.cue(1) < t < S.cue(3):
        k = ease_out(prog(t, S.cue(1) + 0.2, 0.8))
        out = ease_in_out(prog(t, S.cue(3) - 0.5, 0.4))
        # height ruler
        x = 900
        top, bot = 240, 1000
        h = (bot - top) * k
        F.put(_ruler(), x, bot - 380, alpha=k * (1 - out))


@lru_cache(None)
def _ruler():
    p = Pen(70, 760, 2)
    p.rect(20, 0, 50, 760, 10, "#ffffff", "#3a2e2a", 3)
    for i in range(0, 760, 38):
        p.line([(20, i), (36 if i % 152 else 46, i)], "#3a2e2a", 3)
    return p.done()


s_gir = topic("LA GIRAFE", [
    "Lève la tête... encore plus haut ! Voici la girafe, l'animal le plus haut du monde.",
    "Elle peut mesurer jusqu'à cinq mètres et demi : aussi haut qu'une maison de deux étages !",
    "Grâce à son long cou, elle attrape les feuilles tout en haut des acacias.",
    "Le savais-tu ? Sa langue est bleu foncé, et elle mesure presque cinquante centimètres !",
    "Et son long cou n'a que sept vertèbres, exactement comme le tien !",
], bg0, animal_actor(art.giraffe, 600, 1010, 1.0, from_x=-400, extra=gir_extra),
    chip_items=[(1, "Jusqu'à 5,5 mètres", "#ff922b"), (2, "Mange les feuilles d'acacia", "#51cf66")],
    fact=(3, "Sa langue bleu foncé mesure presque 50 cm. Et son long cou a 7 vertèbres, comme le tien !"),
    lab_bg="#ff922b")


def lion_extra(F, S, t, shift):
    # roar waves at start
    if 2.0 < t < S.cue(1):
        for i in range(3):
            a = ((t - 2.0) * 1.2 + i / 3) % 1
            F.put(_wave(), 930 + a * 180, 640, sc=0.6 + a * 0.6, alpha=1 - a)
    # family: lionesses join
    if t > S.cue(1) + 0.4:
        out = ease_in_out(prog(t, S.cue(3) - 0.4, 0.5))
        for i, xx in enumerate((470, 190)):
            k = ease_out(prog(t, S.cue(1) + 0.4 + i * 0.4, 1.4))
            F.put(_lioness(), xx - 900 * (1 - k) - out * 900, 900, sc=0.55, anchor="b")


@lru_cache(None)
def _lioness():
    p = Pen(560, 420)
    gold, goldd, OL = "#f0b75a", "#dba045", "#3a2e2a"
    p.stroke(art.bezier((100, 230), (40, 240), (50, 150), (25, 135), 30), gold, 12, 9, OL, 3)
    p.ell(25, 130, 16, 20, "#9a4f16", OL, 3)
    for x in (130, 220):
        p.rect(x, 260, x + 56, 400, 26, goldd, OL, 4)
    p.ell(240, 250, 160, 95, gold, OL, 5)
    for x in (320, 390):
        p.rect(x, 270, x + 58, 404, 26, gold, OL, 4)
    cx, cy = 420, 180
    p.circ(cx - 40, cy - 52, 20, gold, OL, 4)
    p.circ(cx + 40, cy - 52, 20, gold, OL, 4)
    p.circ(cx, cy, 70, gold, OL, 5)
    p.ell(cx, cy + 28, 40, 30, "#fde6b5")
    p.poly([(cx - 14, cy + 8), (cx + 14, cy + 8), (cx, cy + 22)], "#6b3412")
    art.eye(p, cx - 26, cy - 12, 13)
    art.eye(p, cx + 26, cy - 12, 13)
    art.cheek(p, cx - 46, cy + 18, 11)
    art.cheek(p, cx + 46, cy + 18, 11)
    return p.done()


@lru_cache(None)
def _wave():
    p = Pen(80, 200, 2)
    p.arc(0, 100, 60, 90, -50, 50, (255, 255, 255, 240), 10)
    return p.done()


def lion_actor(F, S, t, shift):
    clouds(F, S, t)
    lion_extra(F, S, t, shift)
    walk_in(F, art.lion(), t, 0.2, -500, 620 - shift * 190, 1000, 1.8, 1.0)


s_lion = topic("LE LION", [
    "Écoute bien... Voici le lion, qu'on appelle souvent le roi de la savane !",
    "Les lions vivent en famille. Un groupe de lions s'appelle une troupe.",
    "Ce sont surtout les lionnes qui chassent, en équipe.",
    "Le savais-tu ? Son rugissement peut s'entendre jusqu'à huit kilomètres ! Et le lion dort jusqu'à vingt heures par jour.",
], bg1, lion_actor,
    chip_items=[(1, "Un groupe = une troupe", "#ff922b"), (2, "Les lionnes chassent", "#ff6b81")],
    fact=(3, "Son rugissement s'entend jusqu'à 8 km ! Et le lion dort jusqu'à 20 heures par jour."),
    lab_bg="#e8590c")


def zebra_actor(F, S, t, shift):
    clouds(F, S, t)
    if t > S.cue(1):
        out = ease_in_out(prog(t, S.cue(3) - 0.4, 0.5))
        for i, (dx, y) in enumerate(((-380, 860), (-120, 830))):
            k = ease_out(prog(t, S.cue(1) + i * 0.5, 2.0))
            F.put(art.zebra(), 1000 + dx - 1200 * (1 - k) - out * 1500, y, sc=0.5, anchor="b")
    walk_in(F, art.zebra(), t, 0.2, -500, 620 - shift * 190, 1000, 1.8, 1.0)
    if S.cue(2) < t < S.cue(3) - 0.3:
        for i in range(3):
            a = t * 1.5 + i * 2.1
            x = 640 + 260 * math.cos(a) * (1 + 0.3 * math.sin(a * 2))
            y = 560 + 100 * math.sin(a * 1.3)
            F.put(_fly(), x, y)


@lru_cache(None)
def _fly():
    p = Pen(60, 50, 2)
    p.ell(22, 14, 12, 9, (220, 240, 255, 220), "#7fb3d5", 2)
    p.ell(38, 14, 12, 9, (220, 240, 255, 220), "#7fb3d5", 2)
    p.ell(30, 30, 15, 11, "#333333")
    return p.done()


s_zebra = topic("LE ZÈBRE", [
    "Et voici le zèbre, avec son joli pyjama à rayures !",
    "Les zèbres vivent en troupeaux, et voyagent ensemble pour trouver de l'herbe fraîche.",
    "Les scientifiques pensent que leurs rayures aident à éloigner les mouches qui piquent.",
    "Le savais-tu ? Il n'existe pas deux zèbres avec les mêmes rayures. Elles sont uniques, comme tes empreintes de doigts !",
], bg0, zebra_actor,
    chip_items=[(1, "Vit en troupeau", "#4dabf7"), (2, "Rayures anti-mouches", "#845ef7")],
    fact=(3, "Il n'existe pas deux zèbres avec les mêmes rayures, comme tes empreintes de doigts !"),
    lab_bg="#495057")


# ---------------------------------------------------------------- recap
def recap_actor(F, S, t, shift):
    items = [(art.elephant, 0.5, "Le plus gros", "#ff6b81"), (art.giraffe, 0.42, "Le plus haut", "#ff922b"),
             (art.lion, 0.5, "Vit en troupe", "#e8590c"), (art.zebra, 0.5, "Rayures uniques", "#4dabf7")]
    for i, (fn, sc, txt, col) in enumerate(items):
        t0 = S.cue(i + 1) - 0.2
        if t < t0:
            continue
        k = back_out(prog(t, t0, 0.6))
        x = 230 + i * 420
        F.put(fn(), x, 760 + (1 - k) * 500, sc=sc, anchor="b")
        F.put(label(txt, 46, col), x, 840, sc=max(0.01, k))


s_recap = topic("RÉCAPITULONS", [
    "Récapitulons !",
    "L'éléphant est le plus gros animal terrestre.",
    "La girafe est l'animal le plus haut.",
    "Les lions vivent en troupe.",
    "Et chaque zèbre a des rayures uniques.",
    "Maintenant, c'est l'heure du quiz ! Tu es prêt ?",
], bg1, recap_actor, lab_bg="#845ef7")

# ---------------------------------------------------------------- quiz + outro
q1 = quiz(1, "Quel animal est le plus haut du monde ?", ["Le lion", "La girafe", "Le zèbre"], 1, [
    "Question numéro un ! Quel animal est le plus haut du monde ? Le lion, la girafe, ou le zèbre ?",
    "C'est la girafe ! Elle peut mesurer jusqu'à cinq mètres et demi.",
])
q2 = quiz(2, "Comment s'appelle un groupe de lions ?", ["Une meute", "Une troupe", "Un essaim"], 1, [
    "Question numéro deux ! Comment s'appelle un groupe de lions ? Une meute, une troupe, ou un essaim ?",
    "Bravo, c'est une troupe !",
])
q3 = quiz(3, "À quoi servent les grandes oreilles de l'éléphant ?", ["À se rafraîchir", "À voler", "À nager"], 0, [
    "Dernière question ! À quoi servent les grandes oreilles de l'éléphant ? À se rafraîchir, à voler, ou à nager ?",
    "Oui ! Il les agite pour se rafraîchir.",
])
s_out = outro([
    "Bravo ! Tu es un vrai explorateur de la savane !",
    "Raconte à ta famille tout ce que tu as appris aujourd'hui.",
    "À très vite pour une nouvelle découverte sur MiniWonder !",
], bg_intro)

SCENES = [s_intro, s_savane, s_eleph, s_gir, s_lion, s_zebra, s_recap, q1, q2, q3, s_out]

if __name__ == "__main__":
    render_video("MiniWonder_01_Animaux_de_la_savane", SCENES, "/home/claude/mw/out/ep1", music_seed=0)
