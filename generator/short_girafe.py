import os
os.environ["MW_VERTICAL"] = "1"
import math
from kit_short import *
import art

BG = lambda: bg_savanna(0, False)


def sky(F, S, t):
    sun2(F, S, t, 880, 560, 200)
    drift_clouds(F, t, 2, 520, seed=4 + S.idx, scale=0.6)
    birds(F, S, t, 620)


def gir(F, S, t):
    hop_in(F, S, t, art.giraffe, 0.5 if S.idx == 0 else -1, -400, W / 2 - 60, 1420, 1.25, 3, 1.5, seed=1)


SCENES = [
    short_scene(["Salut ! C'est Mini ! Voici trois faits incroyables sur la girafe !"], BG, gir,
                "3 FAITS SUR LA GIRAFE", "#ff922b", extras=sky, first=True),
    short_scene(["Un : c'est l'animal le plus haut du monde. Elle peut mesurer jusqu'à cinq mètres et demi !"], BG, gir,
                "L'animal le plus haut", "#ff922b", card="Jusqu'à 5,5 mètres de haut !", badge=1, extras=sky),
    short_scene(["Deux : sa langue est bleu foncé, et elle mesure presque cinquante centimètres !"], BG, gir,
                "Une langue géante", "#845ef7", card="Une langue bleue de presque 50 cm !", badge=2, extras=sky),
    short_scene(["Trois : son long cou n'a que sept vertèbres... exactement comme le tien !"], BG, gir,
                "Un cou surprenant", "#4dabf7", card="7 vertèbres dans le cou, comme toi !", badge=3, extras=sky),
    short_quiz("Combien de vertèbres a le cou de la girafe ?", ["Deux", "Sept", "Cinquante"], 1, [
        "Petit quiz ! Combien de vertèbres a le cou de la girafe ? Deux, sept, ou cinquante ?",
        "Sept ! Exactement comme toi !"]),
    short_scene(["Bravo ! Tu veux découvrir d'autres animaux ? Regarde nos vidéos sur MiniWonder !"], BG, gir,
                "BRAVO !", "#e8590c", extras=sky, last=True, title_size=120),
]

if __name__ == "__main__":
    render_short("MiniWonder_Short_01_Girafe", SCENES, "/home/claude/mw/out/short01")
