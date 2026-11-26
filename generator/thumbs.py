import math
from engine import *
import art, ep2

def thumb(name, bg, title, sprites, col_ol):
    F = Frame(bg)
    for sp, x, y, sc in sprites:
        F.put(sp, x, y, sc=sc, anchor="b")
    F.put(art.star(360), 1640, 820, rot=-8)
    t = big_title(title, 150, "#ffffff", col_ol, 1250)
    F.put(t, 720, 310)
    F.put(label("MiniWonder", 64, "#ffd43b", "#1b3a6b"), 230, 80)
    F.put(label("+ QUIZ", 70, "#ff6b81"), 1700, 120, rot=8)
    F.img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(f"out/{name}.jpg", quality=92)

thumb("Miniature_01_Savane", bg_savanna(0), "Les animaux de la savane",
      [(art.elephant(), 360, 1060, 0.95), (art.giraffe(), 860, 1060, 0.85), (art.lion(), 1250, 1070, 0.8)], "#e8590c")
F2 = [(art.cloud(520, face=True), 520, 820, 1.0), (art.drop(220), 1000, 1000, 1.0), (art.sun(300), 1300, 960, 1.0)]
thumb("Miniature_02_Eau", bg_world(), "Le voyage de la goutte d'eau", F2, "#1864ab")
import ep3
F3 = [(ep3.plant_img(1.0, 1.0, 0.0), 700, 1180, 0.95), (art.bee(220), 1100, 700, 1.0), (art.seed_cut(380), 380, 1040, 1.0)]
thumb("Miniature_03_Plante", bg_garden(), "Comment pousse une plante ?", F3, "#2b8a3e")
