"""White Bunny, épisode 1 (version 3D) : Bunny et le pique-nique des amis (leçon : partager)."""
import math
from story import *
import bunny_art as B

GROUND = 1010
BGM = lambda: B.bg3d('meadow')
BGK = lambda: B.bg3d('kitchen')
BGP = lambda: B.bg3d('picnic')
BGB = lambda: B.bg3d('bedroom')
PG = 830   # feet line on the picnic blanket
PS = 0.64  # character scale on the blanket


def sky(F, S, t):
    drift_clouds(F, t, 3, 140, seed=S.idx)
    butterflies(F, t, [(1500, 520)], seed=S.idx)


# ---------------------------------------------------------------- 0. titre
s0 = title_scene(1, "Bunny et le pique-nique des amis", [
    ("narrateur", "Bonjour les amis ! Bienvenue au Pré des Trèfles, où vit un petit lapin tout blanc..."),
    ("bunny", "C'est moi, White Bunny !"),
    ("narrateur", "Aujourd'hui : Bunny et le pique-nique des amis !"),
], BGM)

# ---------------------------------------------------------------- 1. le matin
s1 = StoryScene([
    ("narrateur", "Ce matin, le soleil brille sur le Pré des Trèfles. Bunny sort de son terrier en sautillant."),
    ("bunny", "Bonjour, soleil ! Aujourd'hui, c'est le jour du pique-nique avec mes amis !"),
    ("maman", "Bonjour, mon petit lapin ! Tu as bien dormi ?"),
    ("bunny", "Oh oui, Maman ! Je peux préparer mon panier ?"),
    ("maman", "Bien sûr. Papa a cueilli des carottes toutes fraîches. Viens vite dans la cuisine !"),
], BGM, {"bunny": (820, 960), "maman": (1200, 960, True)},
    enter={"bunny": (2.2, 380, 1.8), "maman": (8.5, 2100, 1.8)}, extras=sky,
    sfx=lambda S: [("whoosh", 0.0), ("boing", 2.3), ("boing", 8.6)])

# ---------------------------------------------------------------- 2. la cuisine
def kitchen_props(F, S, t):
    c1 = S.cue(1)
    n = 0 if t < c1 else min(4, 1 + int((t - c1 - 1.0) / 0.55))
    F.put(B.prop3d("basket_empty", 190), 930, 985, anchor="b")
    for i in range(n):
        F.put(B.prop3d("carrot", 46), 885 + i * 30, 905, rot=-10 + i * 7)
    if t > S.cue(8):
        for i in range(5):
            ph = ((t - S.cue(8)) * 0.7 + i / 5) % 1
            F.put(B.heart(46), 430 + 60 * math.sin(i * 2 + t), 640 - ph * 260, alpha=1 - ph)


s2 = StoryScene([
    ("papa", "Voilà quatre belles carottes pour ton panier, Bunny !"),
    ("bunny", "Merci, Papa ! Une, deux, trois... quatre carottes !"),
    ("noisette", "Bunny, Bunny ! Je peux venir au pique-nique avec toi ?"),
    ("bunny", "Non, Noisette. Tu es trop petite..."),
    ("noisette", "Oh... d'accord...", "sad"),
    ("narrateur", "Noisette baisse ses grandes oreilles. Elle est toute triste."),
    ("papa", "Bunny, regarde ta petite sœur. Elle aimerait tellement jouer avec vous..."),
    ("bunny", "Hmm... Bon, d'accord ! Tu peux venir, Noisette !"),
    ("noisette", "Youpi ! Merci, Bunny !", "happy"),
], BGK, {"noisette": (500, 960), "bunny": (760, 960), "papa": (1230, 960, True)},
    front=kitchen_props, title="Dans la cuisine",
    sfx=lambda S: [("whoosh", 0.0)] + [("pop", S.cue(1) + 1.0 + i * 0.55) for i in range(4)] + [("sparkle", S.cue(8))])


# ---------------------------------------------------------------- 3. le pique-nique
def picnic_props(F, S, t):
    pass


s3 = StoryScene([
    ("narrateur", "Bunny et Noisette arrivent près de l'étang. Leurs amis les attendent déjà... enfin, presque !"),
    ("pipo", "Coucou Bunny ! Coucou Noisette ! Regardez, j'ai apporté des noisettes !"),
    ("noisette", "Des noisettes ? Comme mon prénom !"),
    ("pipo", "Ha ha ! Exactement !"),
    ("lila", "Bonjour... tout... le... monde... J'arrive !"),
    ("narrateur", "C'est Lila, la petite tortue. Elle marche toujours très, très lentement."),
    ("bunny", "Bonjour, Lila ! On t'attendait. Le pique-nique peut commencer !"),
], BGP, {"lila": (420, PG, False, PS), "noisette": (760, PG, False, PS), "bunny": (1010, PG, False, PS), "pipo": (1500, PG, True, PS)},
    extras=lambda F, S, t: (sky(F, S, t), picnic_props(F, S, t)),
    title="Le pique-nique",
    sfx=lambda S: [("whoosh", 0.0), ("boing", S.cue(1) - 1.0)])
s3.enter = {"pipo": (None, 2200, 1.4), "lila": (None, -350, 4.5)}


def _fix_enter(S):
    S.enter = {"pipo": (S.cue(1) - 1.6, 2200, 1.4), "lila": (S.cue(4) - 4.0, -350, 4.0)}
    return [("whoosh", 0.0), ("boing", S.cue(1) - 0.3)]


s3.sfx_fn = _fix_enter


# ---------------------------------------------------------------- 4. le dilemme
def dilemma_props(F, S, t):
    picnic_props(F, S, t)
    F.put(B.prop3d("basket", 140), 1240, 845, anchor="b")
    F.put(B.prop3d("nut", 40), 1330, 840, anchor="b")
    F.put(B.prop3d("nut", 40), 1365, 846, anchor="b")
    # thought bubble: memory of Noisette sad -> happy
    t0 = S.cue(4) + 2.5
    if t > t0:
        k = back_out(prog(t, t0, 0.5), 1.8)
        F.put(_bubble(), 980, 330, sc=max(0.05, k))
        happy = t > t0 + 2.6
        F.put(B.char3d("noisette", "smile", False, "happy" if happy else "sad"), 1000, 470, 0.3 * k, anchor="b")


@lru_cache(None)
def _bubble():
    p = art.Pen(420, 320, 2)
    for x, y, r in ((210, 150, 140), (100, 170, 80), (320, 170, 80), (210, 70, 90)):
        p.circ(x, y, r + 6, "#cfd8e3")
    for x, y, r in ((210, 150, 140), (100, 170, 80), (320, 170, 80), (210, 70, 90)):
        p.circ(x, y, r, "#ffffff")
    p.circ(110, 290, 18, "#ffffff", "#cfd8e3", 4)
    p.circ(70, 315, 10, "#ffffff", "#cfd8e3", 3)
    return p.done()


s4 = StoryScene([
    ("narrateur", "Bunny ouvre son panier. Ses quatre carottes sont orange, croquantes... délicieuses !"),
    ("bunny", "Hmm... Ce sont MES carottes. Je vais toutes les manger !"),
    ("pipo", "Oh... moi, je n'ai que des noisettes. Et elles sont un peu dures...", "sad"),
    ("lila", "Et moi... j'ai marché si lentement... que j'ai oublié mon goûter à la maison...", "sad"),
    ("narrateur", "Bunny regarde ses amis. Puis il se souvient de Noisette, ce matin. Elle était si triste... et si heureuse quand il a dit oui !"),
], BGP, {"lila": (420, PG, False, PS), "noisette": (760, PG, False, PS), "bunny": (1010, PG, False, PS), "pipo": (1500, PG, True, PS)},
    extras=lambda F, S, t: (sky(F, S, t), dilemma_props(F, S, t)), title="Mes carottes ?",
    sfx=lambda S: [("whoosh", 0.0), ("pop", S.cue(4) + 2.5)])


# ---------------------------------------------------------------- 5. le partage
def share_props(F, S, t):
    picnic_props(F, S, t)
    F.put(B.prop3d("basket_empty", 140), 1240, 845, anchor="b")
    c0, e0 = S.cue(0), S.end(0)
    targets = [(470, 700), (1470, 650), (760, 680)]  # Lila, Pipo, Noisette
    # carrots fly one by one during Bunny's first line
    for i in range(4):
        start = (1200 + i * 26, 775)
        if i < 3:
            tf = c0 + (e0 - c0) * (0.12 + 0.3 * i)
            k = ease_in_out(prog(t, tf, 0.9))
            tx, ty = targets[i]
            x = start[0] + (tx - start[0]) * k
            y = start[1] + (ty - start[1]) * k - math.sin(math.pi * k) * 220
            F.put(B.prop3d("carrot", 42), x, y, rot=(k * 360) % 360 if 0 < k < 1 else 0)
            if t > tf:
                sparkle_burst(F, tx, ty, t, tf + 0.9, 8, 90, seed=i)
        else:
            F.put(B.prop3d("carrot", 42), start[0], start[1])
    # nuts shared
    if t > S.cue(2):
        for i, (tx, ty) in enumerate([(500, 770), (800, 770), (1060, 770)]):
            k = ease_in_out(prog(t, S.cue(2) + 0.6 + i * 0.3, 0.8))
            F.put(B.prop3d("nut", 40), 1350 + (tx - 1350) * k, 830 + (ty - 830) * k - math.sin(math.pi * k) * 160)
    if t > S.cue(4):
        for i in range(8):
            ph = ((t - S.cue(4)) * 0.5 + i / 8) % 1
            F.put(B.heart(50, ["#ff8fab", "#ff6b81"][i % 2]), 500 + i * 140, 560 - ph * 400, alpha=1 - ph)


s5 = StoryScene([
    ("bunny", "Lila, tiens ! Je te donne une carotte. Et une pour toi, Pipo ! Et une pour toi, Noisette !", "happy"),
    ("lila", "Oh, merci Bunny ! Tu es un vrai ami.", "happy"),
    ("pipo", "Alors moi, je partage mes noisettes avec tout le monde !", "happy"),
    ("noisette", "Miam ! C'est le meilleur pique-nique du monde !"),
    ("bunny", "C'est bizarre... Je n'ai plus qu'une carotte, mais je suis encore plus content qu'avant !"),
    ("narrateur", "Quand on partage, il y a moins dans le panier... mais plus de joie dans le cœur."),
], BGP, {"lila": (420, PG, False, PS), "noisette": (760, PG, False, PS), "bunny": (1010, PG, False, PS), "pipo": (1500, PG, True, PS)},
    extras=lambda F, S, t: (sky(F, S, t), share_props(F, S, t)), title="Le partage",
    sfx=lambda S: [("whoosh", 0.0)] + [("pop", S.cue(0) + (S.end(0) - S.cue(0)) * (0.12 + 0.3 * i)) for i in range(3)]
    + [("sparkle", S.cue(4))])

# ---------------------------------------------------------------- 6. la leçon
s6 = lesson_scene("Partager, c'est faire plaisir aux autres... et à soi-même !", [
    ("narrateur", "Et toi ? Avec qui aimes-tu partager ? Ton goûter, tes jouets, ou tes crayons ?"),
    3.0,
    ("narrateur", "Partager, c'est faire plaisir aux autres... et à soi-même !"),
])


# ---------------------------------------------------------------- 7. bonne nuit
def night_front(F, S, t):
    if t > S.cue(5):
        for i in range(3):
            ph = ((t - S.cue(5)) * 0.6 + i / 3) % 1
            F.put(B.zzz(60 + i * 10), 560 + ph * 120 + i * 20, 520 - ph * 200, alpha=1 - ph)


s7 = StoryScene([
    ("narrateur", "Le soir, au terrier, c'est l'heure d'aller au lit."),
    ("maman", "Alors, mon lapin, c'était bien, le pique-nique ?"),
    ("bunny", "Oh oui, Maman ! On a tout partagé. C'était la plus belle journée !"),
    ("papa", "Nous sommes très fiers de toi, Bunny."),
    ("bunny", "Merci... Bonne nuit, tout le monde..."),
    ("narrateur", "Bonne nuit, White Bunny. Fais de beaux rêves."),
], BGB, {"bunny": (520, 1000), "maman": (1250, 1000, True), "papa": (1600, 1000, True)},
    front=night_front, sfx=lambda S: [("whoosh", 0.0), ("chime", S.cue(5))])

# ---------------------------------------------------------------- 8. fin
s8 = end_scene([
    ("narrateur", "C'est la fin de l'histoire ! À bientôt pour une nouvelle aventure de White Bunny !"),
], BGM)

SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8]

if __name__ == "__main__":
    import sys
    only = set(map(int, sys.argv[1:])) if len(sys.argv) > 1 else None
    render_video("WhiteBunny_E01_Le_pique-nique_des_amis_3D", SCENES, "/home/claude/mw/out/bunny01_3d", music_fn=story_music(0),
                 sfx_fn=music2.sfx, music_gain=0.42, duck_depth=0.65, only=only)
