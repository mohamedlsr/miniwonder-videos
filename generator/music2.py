"""Upbeat kid-pop backing track + cartoon sound effects (pure numpy)."""
import numpy as np

AR = 44100
BPM = 116
BEAT = 60 / BPM
RS = np.random.RandomState(7)


def mf(m):
    return 440 * 2 ** ((m - 69) / 12)


def _t(d):
    return np.arange(int(d * AR)) / AR


def env_adsr(n, a=0.005, d=0.08, s=0.6, r=0.08, hold=None):
    t = np.arange(n) / AR
    dur = n / AR
    e = np.ones(n, np.float32) * s
    e[t < a] = t[t < a] / a
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / d
    rel = t > dur - r
    e[rel] *= np.clip((dur - t[rel]) / r, 0, 1)
    return e


def kick():
    t = _t(0.3)
    f = 48 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / AR
    return (0.9 * np.sin(ph) * np.exp(-t * 9)).astype(np.float32)


def clap():
    t = _t(0.22)
    n = RS.randn(len(t)).astype(np.float32)
    n = n - np.convolve(n, np.ones(6) / 6, "same")
    env = np.exp(-t * 22)
    # three quick hand hits
    for o in (0.0, 0.011, 0.022):
        i = int(o * AR)
        env[i:i + 200] += 0.6 * np.exp(-np.arange(min(200, len(t) - i)) / 60)
    body = 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35)
    return (0.45 * n * env + body).astype(np.float32)


def hat(open_=False):
    t = _t(0.18 if open_ else 0.05)
    n = RS.randn(len(t)).astype(np.float32)
    n = n - np.convolve(n, np.ones(3) / 3, "same")
    return (0.12 * n * np.exp(-t * (14 if open_ else 70))).astype(np.float32)


def pluck_bass(m, d):
    t = _t(d)
    f = mf(m)
    s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in range(1, 7))
    return (0.32 * s * np.exp(-t * 4.5) * np.minimum(1, t * 300)).astype(np.float32)


def marimba(m, d=0.35, amp=0.12):
    t = _t(d)
    f = mf(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    return (amp * s * np.exp(-t * 11) * np.minimum(1, t * 500)).astype(np.float32)


def lead(m, d, amp=0.13):
    t = _t(d + 0.12)
    f = mf(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t * 4))
    ph = 2 * np.pi * np.cumsum(f) / AR
    s = np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    bell = 0.5 * np.sin(4 * ph) * np.exp(-t * 25)
    e = env_adsr(len(t), 0.008, 0.12, 0.55, 0.1)
    return (amp * (s + bell) * e).astype(np.float32)


PROG = [(48, [0, 4, 7]), (43, [0, 4, 7]), (45, [0, 3, 7]), (41, [0, 4, 7])]  # C G Am F
MEL_A = [
    [(0, 76, .5), (.5, 79, .5), (1, 81, .5), (1.5, 79, .5), (2, 76, 1), (3, 72, 1)],
    [(0, 74, .5), (.5, 76, .5), (1, 79, 1), (2, 74, 1), (3, 71, 1)],
    [(0, 72, .5), (.5, 76, .5), (1, 81, .5), (1.5, 79, .5), (2, 76, 1), (3, 72, .5), (3.5, 74, .5)],
    [(0, 77, .5), (.5, 76, .5), (1, 74, .5), (1.5, 72, .5), (2, 74, 1.5), (3.5, 76, .5)],
]
MEL_B = [
    [(0, 79, .5), (.5, 79, .5), (1, 81, .5), (1.5, 79, .5), (2, 84, 1), (3, 79, 1)],
    [(0, 79, .5), (.5, 77, .5), (1, 76, .5), (1.5, 74, .5), (2, 71, 1), (3, 74, 1)],
    [(0, 76, .5), (.5, 77, .5), (1, 76, .5), (1.5, 72, .5), (2, 69, 1), (3, 72, 1)],
    [(0, 74, .5), (.5, 72, .5), (1, 69, .5), (1.5, 72, .5), (2, 72, 2)],
]


STYLES = {0: (0, 0), 1: (2, 1), 2: (5, 0), 3: (-3, 1)}  # style -> (transpose, melody-section swap)


def track(dur, transpose=0, quiet=(), style=None):
    """quiet: list of (t0,t1) where drums/lead drop for suspense (quiz countdowns)."""
    swap = 0
    if style is not None:
        transpose, swap = STYLES[style % len(STYLES)]
    n = int(dur * AR) + AR * 4
    drums = np.zeros(n, np.float32)
    bass = np.zeros(n, np.float32)
    keys = np.zeros(n, np.float32)
    mel = np.zeros(n, np.float32)
    K, C, H, HO = kick(), clap(), hat(), hat(True)

    def add(buf, s, t):
        i = int(t * AR)
        if 0 <= i < n:
            buf[i:i + len(s)] += s[:n - i]

    def is_quiet(t):
        return any(a <= t < b for a, b in quiet)

    bar = 0
    t = 0.0
    cache = {}
    while t < dur + BEAT * 4:
        root, ch = PROG[bar % 4]
        root += transpose
        section = ((bar // 8) + swap) % 2  # 0: with lead, 1: lighter
        q = is_quiet(t)
        for b in range(4):
            tb = t + b * BEAT
            qb = is_quiet(tb)
            if not qb:
                if b in (0, 2):
                    add(drums, K, tb)
                if b == 2 and bar % 2 == 1:
                    add(drums, K * 0.6, tb + BEAT * 0.5)
                if b in (1, 3):
                    add(drums, C, tb)
                add(drums, H, tb)
                add(drums, HO if b == 3 else H, tb + BEAT / 2)
            else:
                add(drums, H * 0.8, tb)
        # bass pattern
        if not q:
            pat = [(0, 0), (0.5, 12), (1.5, 7), (2, 0), (2.5, 12), (3.5, 7)]
            for pos, iv in pat:
                key = ("b", root + iv)
                if key not in cache:
                    cache[key] = pluck_bass(root + iv, BEAT * 0.5)
                add(bass, cache[key], t + pos * BEAT)
        else:
            key = ("b", root)
            cache.setdefault(key, pluck_bass(root, BEAT * 0.5))
            add(bass, cache[key] * 0.6, t)
        # marimba offbeat chords
        for pos in (0.5, 1.5, 2.5, 3.5):
            for iv in ch:
                m = root + 24 + iv
                key = ("m", m)
                if key not in cache:
                    cache[key] = marimba(m)
                add(keys, cache[key] * (0.7 if q else 1), t + pos * BEAT)
        # lead melody
        if not q:
            mel_src = MEL_A if section == 0 else MEL_B
            for pos, m, d in mel_src[bar % 4]:
                add(mel, lead(m + transpose, d * BEAT, 0.17 if section == 0 else 0.12), t + pos * BEAT)
        t += 4 * BEAT
        bar += 1
    out = (drums * 0.9 + bass * 0.9 + keys + mel)[:int(dur * AR)]
    out /= np.abs(out).max() + 1e-6
    fi = int(0.3 * AR)
    out[:fi] *= np.linspace(0, 1, fi)
    fo = int(2.5 * AR)
    out[-fo:] *= np.linspace(1, 0, fo)
    return out.astype(np.float32)


# ------------------------------------------------------------------ sfx
def tone(f, d, amp=0.3, decay=6, harm=(1, .5, .25)):
    t = _t(d)
    s = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm))
    return (amp * s * np.exp(-decay * t) * np.minimum(1, t * 300)).astype(np.float32)


def sfx(name):
    if name == "pop":
        t = _t(0.13)
        f = 380 + 1500 * (t / 0.13) ** 0.7
        return (0.35 * np.sin(2 * np.pi * np.cumsum(f) / AR) * np.exp(-22 * t)).astype(np.float32)
    if name == "boing":
        t = _t(0.55)
        f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4) + 160 * t
        return (0.35 * np.sin(2 * np.pi * np.cumsum(f) / AR) * np.exp(-t * 5)).astype(np.float32)
    if name == "whoosh":
        n = int(0.55 * AR)
        x = RS.randn(n).astype(np.float32)
        out = np.zeros(n, np.float32)
        # sweeping lowpass
        a = 0.0
        cut = np.linspace(0.05, 0.4, n) * np.sin(np.linspace(0, np.pi, n)) + 0.02
        for i in range(n):
            a += cut[i] * (x[i] - a)
            out[i] = a
        return (0.4 * out * np.sin(np.linspace(0, np.pi, n)) ** 2).astype(np.float32)
    if name == "sparkle":
        out = np.zeros(int(0.9 * AR), np.float32)
        r = np.random.RandomState(3)
        for i in range(9):
            f = r.choice([2093, 2349, 2637, 3136, 3520])
            s = tone(f, 0.4, 0.07, 12, (1,))
            j = int(i * 0.05 * AR)
            out[j:j + len(s)] += s[:len(out) - j]
        return out
    if name == "fanfare":
        out = np.zeros(int(1.8 * AR), np.float32)
        notes = [(0.0, [72, 76, 79], 0.14), (0.16, [72, 76, 79], 0.14), (0.32, [77, 81, 84], 1.3)]
        for t0, chord, d in notes:
            for m in chord:
                t = _t(d + 0.25)
                f = mf(m)
                s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 8))
                e = env_adsr(len(t), 0.02, 0.1, 0.7, 0.25)
                seg = 0.07 * s * e
                j = int(t0 * AR)
                out[j:j + len(seg)] += seg[:len(out) - j]
        return out
    if name == "drumroll":
        d = 1.3
        out = np.zeros(int(d * AR), np.float32)
        tt = 0.0
        C = clap() * 0.35
        while tt < d - 0.05:
            j = int(tt * AR)
            g = 0.3 + 0.7 * tt / d
            out[j:j + len(C)] += (C * g)[:len(out) - j]
            tt += 0.06 - 0.03 * tt / d
        return out
    if name == "tick":
        t = _t(0.07)
        return (0.25 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 70)).astype(np.float32)
    if name == "chime":
        out = np.zeros(int(1.6 * AR), np.float32)
        for i, f in enumerate((784, 988, 1175, 1568)):
            s = tone(f, 1.2, 0.16, 4)
            j = int(i * 0.08 * AR)
            out[j:j + len(s)] += s[:len(out) - j]
        return out
    if name == "jingle":
        out = np.zeros(int(2.4 * AR), np.float32)
        seq = [(0, 72), (0.12, 76), (0.24, 79), (0.36, 84), (0.6, 83), (0.72, 84)]
        for t0, m in seq:
            s = lead(m, 0.25 if t0 < 0.7 else 1.2, 0.22)
            j = int(t0 * AR)
            out[j:j + len(s)] += s[:len(out) - j]
        sp = sfx("sparkle")
        j = int(0.7 * AR)
        out[j:j + len(sp)] += sp[:len(out) - j]
        return out
    raise ValueError(name)
