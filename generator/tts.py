"""French narration with Piper (siwis medium voice)."""
import io, wave, os, hashlib
import numpy as np
from piper import PiperVoice, SynthesisConfig

SR = 22050
_voice = None
CACHE = "/home/claude/mw/cache_tts"
os.makedirs(CACHE, exist_ok=True)


def voice():
    global _voice
    if _voice is None:
        _voice = PiperVoice.load("/home/claude/voice/fr-siwis-medium.onnx",
                                 config_path="/home/claude/voice/fr-siwis-medium.onnx.json")
    return _voice


def say(text, speed=1.08, pitch=1.0):
    """Return float32 mono samples at SR for text (cached). pitch>1 = brighter, cartoon-like."""
    if pitch != 1.0:
        a = say(text, speed * pitch, 1.0)
        n = int(len(a) / pitch)
        return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
    key = hashlib.md5(f"{text}|{speed}".encode()).hexdigest()
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice().synthesize_wav(text, w, syn_config=SynthesisConfig(
            length_scale=speed, noise_scale=0.6, noise_w_scale=0.7))
    buf.seek(0)
    with wave.open(buf, "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    # trim silence
    thr = 0.01
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - 200): idx[-1] + 600]
    np.save(path, a)
    return a
