"""Démo : les animaux parlent (style MiniWonder)."""
from kit2 import *
import art
from ep1b import sky

BG = lambda: bg_savanna(1, False)
cast = {
    "lion": dict(fn=lambda b, m: art.lion(b, m), x=560, y=1000, sc=0.95, voice="grave", name="Léo le lion", tag="#e8590c"),
    "elephant": dict(fn=lambda b, m: art.elephant(b, m), x=1250, y=1000, sc=0.9, flip=True, voice="doux",
                     name="Ella l'éléphante", tag="#845ef7", enter=("c2", 2300, 1.6)),
}
s1 = talk2("LES ANIMAUX PARLENT !", [
    ("mini", "Bonjour Léo ! Tu veux bien te présenter aux enfants ?"),
    ("lion", "Bonjour les amis ! Je suis Léo, le lion. Mon rugissement s'entend jusqu'à huit kilomètres !"),
    ("mini", "Waouh ! Et voici notre amie Ella !"),
    ("elephant", "Coucou ! Moi, je suis une éléphante. J'utilise ma trompe pour boire, sentir, et attraper ma nourriture."),
    ("lion", "Et tu peux même t'en servir pour prendre une douche !"),
    ("elephant", "Exactement, Léo ! Pschhh !"),
], BG, cast, extras=sky, chip_items=[(1, "Rugissement : 8 km", "#e8590c"), (3, "Trompe = nez + main", "#845ef7")])
SCENES = [s1]

if __name__ == "__main__":
    render_video("MiniWonder_demo_animaux_parlent", SCENES, "/home/claude/mw/out/demo_talk",
                 music_fn=music_for(SCENES, 1), sfx_fn=music2.sfx, music_gain=0.45, duck_depth=0.65)
