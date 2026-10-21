#!/usr/bin/env bash
# One-time setup for the revealjs-vidcast skill: two venvs, Chromium, Kokoro and Whisper models.
set -euo pipefail

command -v uv >/dev/null || { echo "uv is required: https://docs.astral.sh/uv/" >&2; exit 1; }
export HF_HUB_DISABLE_XET=1

# Renderer: Playwright + bundled ffmpeg.
if [ ! -x ~/.venvs/vidcast/bin/python ]; then
  uv venv -q -p 3.12 ~/.venvs/vidcast
fi
uv pip install -q -p ~/.venvs/vidcast/bin/python playwright imageio-ffmpeg
~/.venvs/vidcast/bin/python -m playwright install chromium

# TTS + speech recognition: Kokoro needs Python <= 3.12.
if [ ! -x ~/.venvs/kokoro/bin/python ]; then
  uv venv -q -p 3.12 ~/.venvs/kokoro
fi
uv pip install -q -p ~/.venvs/kokoro/bin/python "kokoro>=0.9.4" soundfile faster-whisper \
  "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

# Warm the model caches so the first render doesn't stall.
~/.venvs/kokoro/bin/python - <<'PY'
from kokoro import KPipeline
from faster_whisper import WhisperModel
list(KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")("Setup check.", voice="af_heart"))
WhisperModel("base.en", device="cpu", compute_type="int8")
print("revealjs-vidcast setup complete")
PY
