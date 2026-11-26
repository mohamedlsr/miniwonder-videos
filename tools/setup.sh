#!/usr/bin/env bash
# Prepares a fresh session to render MiniWonder videos. Safe to run several times.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
command -v ffmpeg >/dev/null || { echo "ffmpeg missing: install it (apt-get install -y ffmpeg)"; exit 1; }
pip install -q --break-system-packages piper-tts onnxruntime numpy pillow 2>&1 | grep -v -i warn || true
mkdir -p /home/claude/fonts /home/claude/voice
cp "$REPO"/fonts/*.ttf /home/claude/fonts/
if [ ! -f /home/claude/voice/fr-siwis-medium.onnx ]; then
  curl -sSL -o /tmp/voice.tgz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-fr-siwis-medium.tar.gz
  tar xzf /tmp/voice.tgz -C /home/claude/voice
fi
if [ -d /home/claude/mw ] && [ ! -L /home/claude/mw ]; then mv /home/claude/mw "/home/claude/mw.old.$(date +%s)"; fi
ln -sfn "$REPO/generator" /home/claude/mw
mkdir -p /home/claude/mw/out /home/claude/mw/cache_tts
python3 -c "import sys; sys.path.insert(0,'/home/claude/mw'); import tts; a=tts.say('Bonjour !'); print('voix OK', len(a))"
echo "SETUP OK"
