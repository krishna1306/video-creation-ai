"""Transcribe 16 kHz mono WAVs with faster-whisper and print word timings as JSON.

Runs in the Kokoro venv (Python 3.12). Used by render_video.py to time cue words from what
is actually heard, and by check_sync.py to verify the finished video.
Usage: ~/.venvs/kokoro/bin/python scripts/word_times.py a.wav [b.wav ...] > words.json
Output: {"a.wav": [{"w": "word", "t": seconds}, ...], ...}
"""

import json
import sys

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel


def main():
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    out = {}
    for path in sys.argv[1:]:
        audio, rate = sf.read(path, dtype="float32")
        if rate != 16000:
            sys.exit(f"{path}: expected 16 kHz audio, got {rate}")
        segments, _ = model.transcribe(np.asarray(audio), word_timestamps=True, vad_filter=False, language="en")
        out[path] = [{"w": w.word.strip(), "t": round(w.start, 3)} for seg in segments for w in seg.words]
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
