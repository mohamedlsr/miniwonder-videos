import sys, importlib, time
from engine import *
mod = importlib.import_module(sys.argv[1])
picks = [tuple(map(float, a.split(':'))) for a in sys.argv[2:]]
t0=time.time()
acc=0
for i,s in enumerate(mod.SCENES):
    s.idx,s.t0=i,acc; s.build(); acc+=s.dur
print("tts", round(time.time()-t0,1), "durations", [round(s.dur,1) for s in mod.SCENES], round(sum(s.dur for s in mod.SCENES),1))
for k,(si, frac) in enumerate(picks):
    s = mod.SCENES[int(si)]
    t = frac * s.dur if frac <= 1 else frac
    t1=time.time()
    F = s.draw(s, t)
    F.img.convert("RGB").save(f"/tmp/pv_{sys.argv[1]}_{k}.jpg", quality=85)
    print(k, si, round(t,2), "ms", int((time.time()-t1)*1000))
