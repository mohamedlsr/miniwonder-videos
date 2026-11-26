"""Épisode 2 : Le voyage de la goutte d'eau (cycle de l'eau)."""
import math
from kit import *
import art


@lru_cache(None)
def bg_space():
    img = to_img(radial("#24357a", "#0b1236", r=1300))
    p = Pen(W, H, 2)
    rnd = random.Random(12)
    for _ in range(160):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.5, 4.5)
        p.circ(x, y, r, (255, 255, 255, int(rnd.uniform(90, 230))))
    img.alpha_composite(p.done())
    return img.convert("RGB")


def plic(F, S, t, x, y, size=150, alpha=1.0, talk=False):
    blink = (t % 3.1) < 0.12
    mouth = "open" if (talk and S.talking(t)) else "smile"
    F.put(art.drop(size, mouth, "closed" if blink else "open"), x, y + math.sin(t * 3.3) * 6, alpha=alpha)


# ---------------------------------------------------------------- intro
def intro_extras(F, S, t):
    pass


def _intro_after(F, S, t):
    pass


s_intro_base = intro("Le voyage de la goutte d'eau", [
    "Salut les explorateurs ! C'est moi, Mini, l'étoile de MiniWonder !",
    "Aujourd'hui, je te présente mon amie Plic, une petite goutte d'eau. Elle va faire un très grand voyage !",
    "Suis-la bien, car à la fin, il y aura un quiz !",
], bg_intro)
_draw0 = s_intro_base.draw


def _intro_draw(S, t):
    F = _draw0(S, t)
    t0 = S.cue(1) + 1.5
    if t > t0:
        k = back_out(prog(t, t0, 0.6))
        plic(F, S, t, 760, 800 + (1 - k) * 500, 170)
    return F


s_intro_base.draw = _intro_draw
s_intro = s_intro_base


# ---------------------------------------------------------------- earth
@lru_cache(None)
def grid_img(blue):
    p = Pen(560, 240, 2)
    for i in range(10):
        x, y = 20 + (i % 5) * 106, 20 + (i // 5) * 106
        col = "#2d8fe0" if i < blue else "#4caf50"
        p.rect(x, y, x + 92, y + 92, 18, col, "#ffffff", 5)
    return p.done()


def earth_actor(F, S, t, shift):
    k = back_out(prog(t, 0.2, 0.9))
    F.put(art.earth(470), 560, 560 + math.sin(t * 1.5) * 10, sc=max(0.01, k), rot=math.sin(t * 0.8) * 5)
    t1 = S.cue(1) + 1.8
    if t > t1:
        n = min(10, int((t - t1) / 0.18) + 1)
        blue = min(7, n)
        img = grid_img(blue) if n >= 10 else grid_img(min(blue, n))
        kk = back_out(prog(t, t1, 0.5))
        F.put(img, 1400, 340, sc=max(0.01, kk))
        if t > t1 + 2.0:
            F.put(label("7 sur 10 = eau", 52, "#1c7ed6"), 1400, 520, sc=max(0.01, back_out(prog(t, t1 + 2.0, 0.5))))


def earth_chips(F, S, t):
    for n, (ci, txt, col) in enumerate([(2, "Mers et océans : eau salée", "#4dabf7"), (3, "Eau douce : rare et précieuse", "#51cf66")]):
        t0 = S.cue(ci) - 0.1
        if t > t0:
            k = back_out(prog(t, t0, 0.5))
            F.put(label(txt, 52, col), 1400, 680 + n * 130, sc=max(0.01, k))


def _earth(F, S, t, shift):
    earth_actor(F, S, t, shift)
    earth_chips(F, S, t)


s_earth = topic("L'EAU SUR TERRE", [
    "Regarde notre planète, la Terre. Vue de l'espace, elle est presque toute bleue !",
    "C'est parce que l'eau recouvre environ sept dixièmes de sa surface. Sur dix carrés, sept sont bleus !",
    "Presque toute cette eau est salée : c'est l'eau des mers et des océans.",
    "L'eau douce, celle que l'on boit, est beaucoup plus rare. Il faut en prendre soin !",
], bg_space, _earth, lab_bg="#1c7ed6")


# ---------------------------------------------------------------- évaporation
def sun_glow(F, t, x=1650, y=170, size=260):
    F.put(art.sun(size), x, y, sc=1 + 0.04 * math.sin(t * 2.5), rot=math.sin(t * 1.3) * 6)


def evap_actor(F, S, t, shift):
    drifting_clouds(F, t, 2, 120, seed=5, scale=0.6)
    sun_glow(F, t)
    t1 = S.cue(1)
    if t < t1:
        plic(F, S, t, 1500, 840, 130)
    else:
        k = ease_in_out(prog(t, t1, 4.5))
        a = 1 - 0.75 * k
        plic(F, S, t, 1500 - 600 * k + 40 * math.sin(t * 2), 840 - 600 * k, 130, alpha=a)
    # steam wisps from sea
    if t > S.cue(0) + 2.5:
        for i in range(7):
            ph = (t * 0.45 + i / 7) % 1
            x = 1250 + i * 95 + 20 * math.sin(t + i)
            F.put(art.steam(60), x, 820 - ph * 380, alpha=math.sin(ph * math.pi) * 0.9)


s_evap = topic("L'ÉVAPORATION", [
    "Plic se repose tranquillement dans la mer. Mais là-haut, le soleil brille, et il chauffe l'eau...",
    "Pouf ! Plic se transforme en vapeur d'eau. Elle devient si légère qu'elle s'envole dans le ciel. On ne peut même plus la voir !",
    "Ce changement s'appelle l'évaporation.",
    "Le savais-tu ? C'est aussi grâce à l'évaporation que le linge mouillé sèche au soleil !",
], bg_world, evap_actor,
    chip_items=[(2, "L'eau devient vapeur", "#ff922b")],
    fact=(3, "C'est grâce à l'évaporation que le linge mouillé sèche au soleil !"), lab_bg="#ff922b")


# ---------------------------------------------------------------- condensation
def cond_actor(F, S, t, shift):
    sun_glow(F, t)
    cx, cy = 820 - shift * 330, 260
    t1 = S.cue(1) + 1.0
    kc = ease_out(prog(t, t1 + 1.5, 2.5))
    # droplets gathering
    rnd = random.Random(3)
    for i in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(250, 520)
        g = ease_in_out(prog(t, t1 + rnd.uniform(0, 1.2), 2.2))
        r = r0 * (1 - g) + 40 * g
        x, y = cx + r * math.cos(a), cy + 0.6 * r * math.sin(a)
        if t > 0.5:
            F.put(art.raindrop(18), x, y, alpha=0.8 * (1 - kc) + 0.0)
    if t > t1 + 1.5:
        F.put(art.cloud(460, face=True), cx, cy, sc=max(0.01, 0.3 + 0.7 * kc))
    if t < t1 + 2.5:
        aa = 0.35 * (1 - ease_in_out(prog(t, t1 + 1.6, 0.8)))
        plic(F, S, t, cx + 40, cy + 40 + 120 * (1 - ease_out(prog(t, 0, 3))), 120, alpha=aa)
    # thermometer cold
    kt = back_out(prog(t, 0.6, 0.5))
    if t < S.cue(2):
        F.put(art.icon("heat", 150), 250, 330, sc=max(0.01, kt) * (1 - ease_in_out(prog(t, S.cue(2) - 0.4, 0.3))))


s_cond = topic("LA CONDENSATION", [
    "Plus Plic monte, plus il fait froid.",
    "Le froid transforme la vapeur en minuscules gouttelettes. Elles se serrent les unes contre les autres, et forment... un nuage !",
    "C'est la condensation.",
    "Le savais-tu ? Tu peux observer la condensation chez toi : souffle sur une vitre froide, et elle se couvre de buée !",
], bg_world, cond_actor,
    chip_items=[(0, "En haut, il fait froid", "#4dabf7"), (2, "Vapeur = gouttelettes", "#845ef7")],
    fact=(3, "Souffle sur une vitre froide : elle se couvre de buée. C'est de la condensation !"),
    lab_bg="#845ef7")


# ---------------------------------------------------------------- précipitations
def rain_actor(F, S, t, shift):
    cx, cy = 440, 210
    grow = ease_in_out(prog(t, 0.2, S.cue(1) - 0.5))
    shake = math.sin(t * 30) * 4 * grow if t < S.cue(1) else 0
    F.put(art.cloud(420 + int(grow * 4) * 20, "#d5dde8", "#9fb0c2", True, "o"), cx + shake, cy)
    if t > S.cue(1) - 0.3:
        for i in range(22):
            x = cx - 170 + (i * 37) % 340
            ph = (t * 1.6 + i * 0.137) % 1
            F.put(art.raindrop(26), x, cy + 90 + ph * 520, alpha=0.95)
    if t > S.cue(2) - 0.2:
        for i in range(14):
            x = 300 + (i * 61) % 300 + 30 * math.sin(t + i)
            ph = (t * 0.5 + i * 0.21) % 1
            F.put(art.snowflake(36), x, cy + 120 + ph * 300, rot=(t * 60 + i * 20) % 360)
    # Plic falls
    t1 = S.cue(1) + 0.5
    if t > t1:
        k = prog(t, t1, 1.8)
        y = cy + 80 + k * k * 260
        plic(F, S, t, cx + 60, y, 120)


s_rain = topic("LES PRÉCIPITATIONS", [
    "Dans le nuage, les gouttelettes se collent ensemble. Elles deviennent de plus en plus grosses, et de plus en plus lourdes...",
    "Trop lourdes ! Elles tombent du nuage : c'est la pluie !",
    "Quand il fait très froid, l'eau tombe en neige, ou en grêle.",
    "La pluie, la neige et la grêle, ce sont les précipitations.",
], bg_world, rain_actor,
    chip_items=[(1, "La pluie", "#4dabf7"), (2, "La neige et la grêle", "#845ef7"), (3, "= les précipitations", "#ff6b81")],
    lab_bg="#4dabf7")


# ---------------------------------------------------------------- ruissellement
PATH1 = art.bezier((440, 470), (520, 620), (380, 760), (430, 875), 60)
PATH2 = art.bezier((420, 880), (650, 980), (900, 900), (1150, 930), 60) + art.bezier((1150, 930), (1300, 920), (1420, 880), (1520, 860), 30)


def along(path, k):
    k = clamp(k)
    i = k * (len(path) - 1)
    a = int(i)
    b = min(a + 1, len(path) - 1)
    f = i - a
    return path[a][0] * (1 - f) + path[b][0] * f, path[a][1] * (1 - f) + path[b][1] * f


def run_actor(F, S, t, shift):
    drifting_clouds(F, t, 2, 120, seed=8, scale=0.6)
    sun_glow(F, t)
    k1 = ease_in_out(prog(t, S.cue(0) + 0.5, 4.5))
    k2 = ease_in_out(prog(t, S.cue(2), 4.5))
    if k2 <= 0:
        x, y = along(PATH1, k1)
    else:
        x, y = along(PATH2, k2)
    # infiltration arrows
    if S.cue(1) < t < S.cue(2) + 0.5:
        a = 1 - ease_in_out(prog(t, S.cue(2), 0.5))
        for i in range(4):
            ph = (t * 0.8 + i / 4) % 1
            F.put(art.raindrop(24), 640 + i * 60, 870 + ph * 150, alpha=a * math.sin(ph * math.pi))
        F.put(art.flower(110), 760, 820, alpha=a * back_out(prog(t, S.cue(1) + 1.5, 0.5)), anchor="b")
    plic(F, S, t, x, y - 50, 110)


s_run = topic("LE RUISSELLEMENT", [
    "Plic atterrit sur la montagne. Elle glisse, rejoint un petit ruisseau, puis une grande rivière...",
    "Une partie de l'eau rentre aussi dans le sol. Elle remplit des réserves cachées sous la terre, et fait boire les plantes.",
    "Et la rivière coule, coule... jusqu'à la mer ! Plic est revenue à son point de départ.",
], bg_world, run_actor,
    chip_items=[(0, "Ruisseau, puis rivière", "#4dabf7"), (1, "L'eau entre dans le sol", "#a0682e"), (2, "Retour à la mer", "#1c7ed6")],
    lab_bg="#1c7ed6")


# ---------------------------------------------------------------- cycle diagram
STAGES = [("Évaporation", "#ff922b", 0), ("Condensation", "#845ef7", 1), ("Précipitations", "#4dabf7", 2), ("Ruissellement", "#1c7ed6", 3)]


@lru_cache(None)
def ring():
    p = Pen(760, 760, 2)
    for i in range(4):
        a0 = -90 + i * 90 + 14
        p.arc(380, 380, 300, 300, a0 - 90 + 90, a0 + 62, (255, 255, 255, 230), 18)
        a = math.radians(a0 + 70)
        x, y = 380 + 300 * math.cos(a), 380 + 300 * math.sin(a)
        d = a + math.pi / 2
        pts = [(x + 26 * math.cos(d), y + 26 * math.sin(d)),
               (x + 22 * math.cos(d + 2.4), y + 22 * math.sin(d + 2.4)),
               (x + 22 * math.cos(d - 2.4), y + 22 * math.sin(d - 2.4))]
        p.poly(pts, (255, 255, 255, 230))
    return p.done()


def cycle_actor(F, S, t, shift):
    cx, cy = 960 - shift * 500, 590
    sc = 1 - 0.22 * shift
    F.put(ring(), cx, cy, sc=sc)
    # stage icons: right=evap (sun), top=cloud, left=rain, bottom=river/sea
    t0, t1 = S.cue(0), S.end(0)
    pos = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    pos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    pos = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    icons = [lambda: art.sun(170), lambda: art.cloud(220, face=True), lambda: art.cloud(200, "#d5dde8", "#9fb0c2", True, "o"), lambda: art.drop(110)]
    order = [0, 1, 2, 3]
    # visual order clockwise from right going up: evaporation(right) -> condensation(top) -> precipitation(left) -> ruissellement(bottom)
    for i, (name, col, _) in enumerate(STAGES):
        ts = t0 + i * (t1 - t0) / 4.4
        if t < ts:
            continue
        k = back_out(prog(t, ts, 0.5))
        dx, dy = pos[i]
        x, y = cx + dx * 330 * sc, cy + dy * 300 * sc
        F.put(icons[i](), x, y - 20, sc=max(0.01, k * sc))
        F.put(label(name, 44, col), x, y + 95 * sc, sc=max(0.01, k * sc))
    # travelling Plic around ring (counter-clockwise visually: right->top->left->bottom)
    if t > t1:
        a = -(t - t1) * 1.4
        F.put(art.drop(70), cx + 300 * sc * math.cos(a), cy + 300 * sc * math.sin(a))


s_cycle = topic("LE CYCLE DE L'EAU", [
    "Évaporation, condensation, précipitations, ruissellement... et ça recommence !",
    "C'est le cycle de l'eau. Il tourne, encore et encore, sans jamais s'arrêter.",
    "Le savais-tu ? L'eau de la Terre voyage ainsi depuis des milliards d'années. L'eau que tu bois a peut-être été bue par un dinosaure !",
], bg_sky, cycle_actor,
    fact_cx=1370, fact=(2, "L'eau voyage ainsi depuis des milliards d'années. Un dinosaure a peut-être bu la même eau que toi !"),
    lab_bg="#845ef7")


# ---------------------------------------------------------------- save water
@lru_cache(None)
def faucet():
    p = Pen(420, 300, 2)
    p.rect(0, 60, 260, 130, 30, "#b0bec5", "#607d8b", 6)
    p.rect(200, 60, 300, 210, 34, "#b0bec5", "#607d8b", 6)
    p.rect(110, 20, 170, 70, 12, "#90a4ae", "#607d8b", 5)
    p.rect(60, 4, 220, 34, 14, "#ff6b81", "#c2255c", 5)
    p.rect(214, 200, 286, 230, 10, "#90a4ae", "#607d8b", 5)
    return p.done()


def save_actor(F, S, t, shift):
    k = back_out(prog(t, 0.2, 0.6))
    F.put(faucet(), 600, 380, sc=max(0.01, k))
    off = S.cue(1) + 1.5
    if t < off:
        for i in range(12):
            ph = (t * 2.2 + i / 12) % 1
            F.put(art.raindrop(26), 650 + 8 * math.sin(i), 520 + ph * 420, alpha=0.9)
    else:
        kk = back_out(prog(t, off, 0.5))
        F.put(art.check(140), 860, 330, sc=max(0.01, kk))
    plic(F, S, t, 380, 840, 150)


s_save = topic("PROTÉGEONS L'EAU", [
    "L'eau douce est précieuse. Alors, aidons Plic et ses amies !",
    "Ferme bien le robinet pendant que tu te brosses les dents.",
    "Et prends plutôt une douche rapide qu'un bain : ça économise beaucoup d'eau !",
    "Maintenant, c'est l'heure du quiz ! Tu es prêt ?",
], bg_sky, save_actor,
    chip_items=[(1, "Ferme le robinet", "#51cf66"), (2, "Douche rapide", "#4dabf7")], lab_bg="#51cf66")


# ---------------------------------------------------------------- quiz + outro
q1 = quiz(1, "Comment s'appelle le moment où l'eau devient vapeur ?", ["La condensation", "L'évaporation", "La pluie"], 1, [
    "Question numéro un ! Comment s'appelle le moment où l'eau se transforme en vapeur ? La condensation, l'évaporation, ou la pluie ?",
    "C'est l'évaporation ! Le soleil chauffe l'eau, et elle s'envole en vapeur.",
])
q2 = quiz(2, "De quoi est fait un nuage ?", ["De coton", "De fumée", "De gouttelettes d'eau"], 2, [
    "Question numéro deux ! De quoi est fait un nuage ? De coton, de fumée, ou de minuscules gouttelettes d'eau ?",
    "Bravo ! Un nuage est fait de minuscules gouttelettes d'eau.",
])
q3 = quiz(3, "Où se trouve la plus grande partie de l'eau sur Terre ?", ["Dans les océans", "Dans les rivières", "Dans les nuages"], 0, [
    "Dernière question ! Où se trouve la plus grande partie de l'eau sur Terre ? Dans les océans, dans les rivières, ou dans les nuages ?",
    "Oui ! Dans les mers et les océans. C'est de l'eau salée.",
])


def outro_plic(F, S, t):
    plic(F, S, t, 1350, 560, 170)


s_out = outro([
    "Bravo ! Maintenant, tu connais le grand voyage de l'eau !",
    "La prochaine fois qu'il pleut, pense à Plic !",
    "À très vite pour une nouvelle découverte sur MiniWonder !",
], bg_intro, outro_plic)

SCENES = [s_intro, s_earth, s_evap, s_cond, s_rain, s_run, s_cycle, s_save, q1, q2, q3, s_out]

if __name__ == "__main__":
    render_video("MiniWonder_02_Le_voyage_de_l_eau", SCENES, "/home/claude/mw/out/ep2", music_seed=1)
