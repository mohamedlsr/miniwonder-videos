"""White Bunny story engine: dialogue scenes with per-character voices, lip-sync and a speaker-following camera."""
import math
import numpy as np
from PIL import Image, ImageDraw
from engine import *
from engine import _resample
import art, tts, music2
import bunny_art as B
from kit2 import (sparkle_burst, confetti_burst, wavy_text, word_sprite, star_wipe, WIPE, drift_clouds,
                  butterflies, birds, pop_label)

# character voices: (speed, pitch). One French voice, shaped per character.
VOICES = {
    "narrateur": (1.04, 1.0),
    "bunny": (1.0, 1.16),
    "noisette": (0.95, 1.30),
    "maman": (1.04, 1.04),
    "papa": (1.10, 0.86),
    "mamie": (1.15, 0.95),
    "pipo": (0.92, 1.30),
    "lila": (1.28, 0.93),
}


class StoryScene(Scene):
    """lines: (who, text) | (who, text, mood) | pause seconds.
    stage: {who: (x, feet_y, flip)}; draw_fn(F, S, t) draws extra things (props, entrances handled via enter)."""

    def __init__(self, lines, bg_fn, stage, enter=None, extras=None, front=None, lead=0.7, tail=1.0, gap=0.35,
                 sfx=None, zoom=0.05, title=None, cam=True):
        super().__init__([], None, lead=lead, tail=tail, gap=gap, sfx=sfx)
        self.story_lines, self.bg_fn, self.stage = lines, bg_fn, stage
        self.enter = enter or {}
        self.extras, self.front, self.zoom, self.title, self.cam = extras, front, zoom, title, cam
        self.draw = StoryScene._draw

    def build(self):
        t = self.lead
        segs, cues, subs, who_l, moods = [], [], [], [], []
        for item in self.story_lines:
            if isinstance(item, (int, float)):
                t += item
                continue
            who, text = item[0], item[1]
            mood = item[2] if len(item) > 2 else None
            sp, pi = VOICES.get(who, VOICES["narrateur"])
            a = tts.say(text, sp, pi)
            cues.append(t)
            d = len(a) / tts.SR
            segs.append((t, a))
            subs.append((t, t + d, text))
            who_l.append(who)
            moods.append((t, who, mood))
            t += d + self.gap
        dur = max(t - self.gap + self.tail, self.min_dur)
        self.nframes = int(round(dur * FPS))
        self.dur = self.nframes / FPS
        self.cues, self.subs, self.who = cues, subs, who_l
        self.ends = [s[1] for s in subs]
        self.moods = moods
        n = int(self.dur * AR)
        v = np.zeros(n, np.float32)
        for t0, a in segs:
            r = _resample(a, tts.SR, AR)
            i0 = int(t0 * AR)
            v[i0:i0 + len(r)] += r[:max(0, n - i0)]
        self.voice = v
        hop = AR // FPS
        self.env = [float(np.sqrt(np.mean(v[i * hop:(i + 1) * hop] ** 2))) for i in range(self.nframes)]
        self.sfx = self.sfx_fn(self) if self.sfx_fn else []
        return self

    # who is speaking at t (None if nobody)
    def speaker(self, t):
        for i, (a, b, _) in enumerate(self.subs):
            if a <= t <= b:
                return self.who[i]
        return None

    def mouth_open(self, who, t):
        if self.speaker(t) != who:
            return False
        i = int(t * FPS)
        return 0 <= i < len(self.env) and self.env[i] > 0.035 and (i // 3) % 2 == 0

    def mood_of(self, who, t):
        m = "happy"
        for (t0, w, mood) in self.moods:
            if t0 > t:
                break
            if w == who and mood:
                m = mood
        return m

    def focus_x(self, t):
        """Smoothly follow the current (or last) speaker."""
        pts = []
        for i, w in enumerate(self.who):
            x = self.stage.get(w, (W / 2,))[0] if w != "narrateur" else W / 2
            pts.append((self.cues[i], x))
        if not pts:
            return W / 2
        x = W / 2
        for (t0, px) in pts:
            if t0 - 0.3 > t:
                break
            k = ease_in_out(clamp((t - (t0 - 0.3)) / 0.8))
            x = x + (px - x) * k
        return x

    @staticmethod
    def _draw(S, t):
        world = Frame(S.bg_fn())
        if S.extras:
            S.extras(world, S, t)
        order = sorted(S.stage.items(), key=lambda kv: kv[1][1])  # back to front by feet y
        for who, pos in order:
            draw_char(world, S, t, who, *pos)
        if S.front:
            S.front(world, S, t)
        F = Frame.__new__(Frame)
        if S.cam:
            fx = S.focus_x(t)
            z = 1.07 + S.zoom * ease_in_out(t / max(S.dur, 0.1))
            hw, hh = W / (2 * z), H / (2 * z)
            cx = clamp(W / 2 + (fx - W / 2) * 0.35, hw, W - hw)
            cy = clamp(H / 2 + 25, hh, H - hh)
            F.img = world.img.transform((W, H), Image.AFFINE, (1 / z, 0, cx - W / (2 * z), 0, 1 / z, cy - H / (2 * z)),
                                        resample=Image.BILINEAR)
        else:
            F.img = world.img
        if S.title:
            lb = label(S.title, 60, "#ff8fab")
            k = back_out(prog(t, WIPE * 0.6, 0.6), 2.0)
            F.put(lb, 60 + lb.width / 2, 50 + lb.height / 2 - (1 - k) * 220, rot=math.sin(t * 2) * 1.2)
        star_wipe(F, S, t, first=(S.idx == 0))
        return F


USE3D = True


def _sprite(who, mouth, blink, mood, cheer=False):
    if USE3D and B.has3d(who):
        return B.char3d(who, mouth, blink, mood, cheer), B.SCALE3D
    return B.char_sprite(who, mouth, blink, mood), None


def draw_char(F, S, t, who, x, y, flip=False, sc=None):
    sp0, s3 = _sprite(who, "smile", False, "happy")
    sc = sc or (s3 if s3 else B.SIZES[who])
    # entrance: (t0, from_x, duration)
    if who in S.enter:
        t0, x0, d = S.enter[who]
        if t < t0:
            return
        k = prog(t, t0, d)
        if k < 1:
            e = ease_in_out(k)
            xx = x0 + (x - x0) * e
            if s3:
                F.put(B.shadow(int(sp0.width * sc * 0.9)), xx, y + 8)
            jump = abs(math.sin(math.pi * 4 * k)) * 50 * sc
            F.put(_sprite(who, "smile", False, S.mood_of(who, t))[0], xx, y - jump, sc, anchor="b",
                  flip=flip if x > x0 else not flip)
            return
    if s3:
        F.put(B.shadow(int(sp0.width * sc * 0.9)), x, y + 8)
    talking = S.speaker(t) == who
    mouth = "open" if S.mouth_open(who, t) else "smile"
    blink = ((t + hash(who) % 7 * 0.37) % 3.3) < 0.13
    mood = S.mood_of(who, t)
    breathe = 1 + 0.015 * math.sin(t * 2.2 + hash(who) % 5)
    bob = abs(math.sin(t * 7)) * 8 * sc if talking else 0
    rot = math.sin(t * 3.5) * 2.5 if talking else math.sin(t * 1.2 + hash(who) % 3) * 0.8
    cheer = mood == "cheer"
    F.put(_sprite(who, mouth, blink, "happy" if cheer else mood, cheer)[0], x, y - bob, sc, rot=rot, flip=flip, anchor="b", sy=breathe,
          sx=2 - breathe)


# ------------------------------------------------------------------ special scenes
def title_scene(ep_num, ep_title, lines, bg_fn):
    def draw(S, t):
        F = Frame(bg_fn())
        drift_clouds(F, t, 3, 140, seed=ep_num)
        butterflies(F, t, [(300, 750), (1600, 780)], seed=ep_num)
        k = back_out(prog(t, 0.3, 0.8), 1.8)
        F.put(B.logo_card(0.85), W / 2, 260 - (1 - k) * 500, rot=math.sin(t * 1.5) * 2)
        kk = back_out(prog(t, 1.2, 0.6), 2.2)
        F.put(label(f"Épisode {ep_num}", 60, "#4dabf7"), W / 2, 520, sc=max(0.05, kk))
        wavy_text(F, ep_title, W / 2, 680, 100, t, 1.6, "#ffffff", "#ff6b9a", 1500, 8)
        # Bunny waves from the bottom
        kb = back_out(prog(t, 2.2, 0.8), 1.6)
        mouth = "open" if S.mouth_open("bunny", t) else "smile"
        sp, s3 = _sprite("bunny", mouth, ((t % 3.1) < 0.12), "happy")
        F.put(sp, 1740, H + 40 + (1 - kb) * 500, s3 or 0.62, anchor="b", rot=math.sin(t * 3) * 5)
        confetti_burst(F, W / 2, 620, t, 1.8, 70, seed=ep_num)
        star_wipe(F, S, t, first=True)
        return F

    sc = StoryScene(lines, bg_fn, {"bunny": (1650, H + 40)}, cam=False, lead=2.6,
                    sfx=lambda S: [("jingle", 0.3), ("sparkle", 1.3), ("fanfare", 1.7)])
    sc.draw = draw
    return sc


def lesson_scene(text_card_txt, lines, bg_fn=None):
    """'Ce qu'on a appris' card with hearts; narrator asks the child a question."""
    def draw(S, t):
        F = Frame((bg_fn or bg_intro)())
        for i in range(10):
            x = (i * 211 + 90) % W
            y = H + 80 - ((t * (50 + i * 6) + i * 160) % (H + 200))
            F.put(B.heart(50 + (i % 3) * 18, ["#ff8fab", "#ffd43b", "#ffffff"][i % 3]), x, y, alpha=0.75)
        k = back_out(prog(t, 0.4, 0.7), 2.0)
        F.put(label("Ce qu'on a appris", 66, "#ff8fab"), W / 2, 170 - (1 - k) * 300)
        kc = back_out(prog(t, 0.9, 0.7), 2.0)
        F.put(text_card(text_card_txt, 1300, 72, "#ffffff", "#5a3d7a", "#ff8fab"), W / 2, 470, sc=max(0.05, 0.6 + 0.4 * kc))
        mouth = "open" if S.mouth_open("narrateur", t) else "smile"
        sp, s3 = _sprite("bunny", "smile", ((t % 3.3) < 0.12), "happy", cheer=t > 1.5)
        F.put(sp, W / 2, H - 10, (s3 or 0.62) * 0.85, anchor="b", rot=math.sin(t * 2) * 3)
        sparkle_burst(F, W / 2, 470, t, 1.2, 14, 640, seed=3)
        star_wipe(F, S, t)
        return F

    sc = StoryScene(lines, bg_fn or bg_intro, {}, cam=False, sfx=lambda S: [("whoosh", 0.0), ("chime", 0.9)])
    sc.draw = draw
    return sc


def end_scene(lines, bg_fn):
    def draw(S, t):
        F = Frame(bg_fn())
        k = back_out(prog(t, 0.4, 0.8), 1.8)
        F.put(B.logo_card(0.75), W / 2, 230 - (1 - k) * 400)
        for i, who in enumerate(("noisette", "maman", "bunny", "papa", "pipo")):
            x = 360 + i * 300
            hop = abs(math.sin(t * 4 + i)) * 25
            sp, s3 = _sprite(who, "smile", ((t + i) % 3.4) < 0.12, "happy", cheer=(int(t * 1.2 + i) % 3 == 0))
            F.put(sp, x, 1010 - hop, (s3 or B.SIZES[who]) * 0.9, anchor="b", rot=math.sin(t * 3 + i) * 4)
        wavy_text(F, "À bientôt !", W / 2, 470, 120, t, 1.0, "#ffffff", "#4dabf7", 1500, 10)
        confetti_burst(F, W / 2, 500, t, 1.0, 80, seed=7)
        star_wipe(F, S, t, last=True)
        if t > S.dur - 1.0:
            F.img = Image.blend(F.img, Image.new("RGB", (W, H), (255, 255, 255)), clamp((t - (S.dur - 1.0)) / 1.0))
        return F

    sc = StoryScene(lines, bg_fn, {}, cam=False, tail=3.0, sfx=lambda S: [("whoosh", 0.0), ("jingle", 0.6)])
    sc.draw = draw
    return sc


def story_music(style=0):
    def fn(total, scs):
        return music2.track(total, 0, (), style=style, soft=True)
    return fn


def render_episode(name, scenes, outdir, style=0):
    return render_video(name, scenes, outdir, music_fn=story_music(style), sfx_fn=music2.sfx,
                        music_gain=0.42, duck_depth=0.65)
