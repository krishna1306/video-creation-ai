"""Measure animation/voice sync in a rendered vidcast.

Reads <video>.timeline.json (written by render_video.py), detects when the picture actually
changes in <video>, and transcribes the audio with Whisper to find when each cue word is
actually heard. Reports per step:
  heard   - when Whisper hears the cue word (falls back to the TTS estimate if not found)
  visual  - when the screen first changes after the step fired
  lag     - visual - heard (positive: animation late; negative: early)
Usage: ~/.venvs/vidcast/bin/python scripts/check_sync.py video.mp4 [max_abs_lag_seconds]
Exit code 1 if any step lags more than the threshold (default 0.5 s).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
KOKORO_PY = Path.home() / ".venvs/kokoro/bin/python"


def norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def heard_words(video: Path):
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio16k.wav"
        subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        env = {**os.environ, "HF_HUB_DISABLE_XET": "1"}
        r = subprocess.run([str(KOKORO_PY), str(Path(__file__).with_name("word_times.py")), str(wav)],
                           capture_output=True, text=True, env=env)
    if r.returncode:
        sys.exit(f"word_times.py failed:\n{r.stderr[-2000:]}")
    return [(norm(w["w"]), w["t"]) for w in json.loads(r.stdout)[str(wav)]]


def visual_changes(video: Path):
    r = subprocess.run(
        [FF, "-hide_banner", "-i", str(video), "-an", "-vf", "scale=960:-1,select='gt(scene,0.0002)',showinfo", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def speech_onsets(video: Path):
    r = subprocess.run(
        [FF, "-hide_banner", "-i", str(video), "-vn", "-af", "silencedetect=n=-45dB:d=0.25", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return [float(t) for t in re.findall(r"silence_end: ([\d.]+)", r.stderr)]


def silences(media: Path):
    """(start, end) of each pause; Whisper often places a word that follows a pause inside it."""
    r = subprocess.run([FF, "-hide_banner", "-i", str(media), "-vn", "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(t) for t in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(t) for t in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends))


def snap(t: float, gaps, est=None) -> float:
    """Whisper may put a post-pause word inside, or just before, the pause. Candidates: t, or
    the end of a pause containing t or starting within 0.7 s after it; the TTS estimate decides."""
    cands = [t] + [e for s, e in gaps if s <= t < e or t < s <= t + 0.7]
    if est is None:
        return next((e for s, e in gaps if s <= t < e), t)
    return min(cands, key=lambda c: abs(c - est))


def main():
    video = Path(sys.argv[1])
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    timeline = json.loads(video.with_suffix(".timeline.json").read_text())
    changes = visual_changes(video)
    onsets = speech_onsets(video)
    words = heard_words(video)
    gaps = silences(video)
    worst, bad = 0.0, 0
    for k, sl in enumerate(timeline):
        end = timeline[k + 1]["start"] if k + 1 < len(timeline) else float("inf")
        first_voice = next((t for t in onsets if t >= sl["start"]), None)
        voice = f"voice starts +{first_voice - sl['start']:.2f}s" if first_voice is not None else "no voice"
        print(f"slide {sl['slide']:>2} @ {sl['start']:7.2f}s  ({voice})")
        cursor = sl["start"] - 0.3
        prev_word, stagger = None, 0
        for st in sl["steps"]:
            stagger = stagger + 1 if st["word"] == prev_word else 0
            prev_word = st["word"]
            vis = next((t for t in changes if t >= st["fired"] - 0.05), None)
            phrase = [p for p in (norm(w) for w in (st["word"] or "").split()) if p][:3]
            heard = None
            for k, (w, t) in enumerate(words):
                if not (cursor <= t < end) or not phrase:
                    continue
                if all(k + j < len(words) and words[k + j][0].startswith(p[:6]) for j, p in enumerate(phrase)):
                    heard = snap(t, gaps, st["spoken"])
                    break
            src = "heard" if heard is not None else "tts"
            if heard is None:
                heard = st["spoken"]
            else:
                cursor = heard
            if heard is None or vis is None:
                print(f"    {st['word'] or '?':<16} fired {st['fired']:7.2f}  (no cue or no visual change)")
                continue
            lag = vis - heard
            # Consecutive markers on one word are staggered on purpose (render_video MIN_STEP_GAP).
            excess = max(0.0, abs(lag) - 0.35 * stagger) if lag > 0 else abs(lag)
            worst = max(worst, excess)
            flag = "  <-- OUT OF SYNC" if excess > limit else ""
            bad += bool(flag)
            tts = f"tts {st['spoken'] - heard:+.2f}" if st["spoken"] is not None else ""
            print(f"    {st['word'] or '?':<16} {src} {heard:7.2f}  fired {st['fired']:7.2f}  visual {vis:7.2f}  lag {lag:+.2f}s  {tts}{flag}")
    print(f"\nworst lag {worst:.2f}s; {bad} step(s) beyond ±{limit}s")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
