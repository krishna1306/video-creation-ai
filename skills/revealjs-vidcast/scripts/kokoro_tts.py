"""Speak a list of texts with Kokoro-82M; write a 24 kHz 16-bit WAV and cue times per text.

Each "[>]" in a text is a cue marker: it is not spoken, and its time is the start of the
next spoken word, taken from Kokoro's word timestamps. Cue times go to <out>.json.
Runs in the Kokoro venv (Python 3.12); render_video.py calls it as a subprocess.
Usage: ~/.venvs/kokoro/bin/python scripts/kokoro_tts.py <jobs.json> [voice]
jobs.json: [{"text": "...", "out": "/path/file.wav"}, ...]
"""

import json
import re
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SAMPLE_RATE = 24000
MARKER = "[>]"


def split_markers(text):
    """Return text without markers and the character offset of each marker in that text."""
    text = re.sub(r"\s+", " ", text).strip()
    clean, offsets = "", []
    for i, part in enumerate(text.split(MARKER)):
        if i:
            clean = clean.rstrip() + " " if clean else ""
            offsets.append(len(clean))
            part = part.lstrip()
        clean += part
    return clean.strip(), offsets


def speak(pipeline, voice, text):
    clean, offsets = split_markers(text)
    chunks, words, t0, cursor = [], [], 0.0, 0
    for result in pipeline(clean, voice=voice):
        if result.audio is None:
            continue
        for tok in result.tokens or []:
            pos = clean.find(tok.text, cursor) if tok.text.strip() else -1
            if pos < 0:
                continue
            cursor = pos + len(tok.text)
            if tok.start_ts is not None and any(c.isalnum() for c in tok.text):
                words.append((pos, t0 + tok.start_ts))
        audio = result.audio.cpu().numpy() if hasattr(result.audio, "cpu") else np.asarray(result.audio)
        chunks.append(audio)
        t0 += len(audio) / SAMPLE_RATE
    cues = []
    for off in offsets:
        later = [t for pos, t in words if pos >= off]
        cues.append(round(later[0] if later else t0, 3))
    return np.concatenate(chunks), cues, t0


def main():
    jobs = json.loads(open(sys.argv[1]).read())
    voice = sys.argv[2] if len(sys.argv) > 2 else "af_heart"
    pipeline = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
    for job in jobs:
        audio, cues, duration = speak(pipeline, voice, job["text"])
        sf.write(job["out"], audio, SAMPLE_RATE, subtype="PCM_16")
        with open(job["out"] + ".json", "w") as f:
            json.dump({"cues": cues, "duration": round(duration, 3)}, f)
        print(f"spoke {job['out']} cues={cues}", flush=True)


if __name__ == "__main__":
    main()
