"""Render the reveal.js deck to a narrated MP4, auto-advancing fragments and slides.

The "VO:" text in each slide's speaker notes is spoken with Kokoro-82M (or macOS `say`); each
clip's length sets how long its slide stays up, plus HOLD seconds to read the finished slide.
Each "[>]" marker in the VO fires the next fragment step on the following word: Kokoro's word
timestamps give a first estimate, refined by when Whisper hears that word in the clip. Frames
are rendered deterministically on a virtual clock (see record()), encoded to H.264 and muxed
with an AAC narration track. A <out>.timeline.json records when each cue word is spoken and
when its step fires; check_sync.py verifies the finished video against it.

Usage: ~/.venvs/vidcast/bin/python scripts/render_video.py deck.html [out.mp4]
Env: VIDCAST_TTS=kokoro|say (default kokoro), VIDCAST_VOICE (default af_heart / Samantha),
     VIDCAST_SILENT=1 (no audio, 140 wpm pacing), VIDCAST_LIMIT=N (first N slides only).
"""

import asyncio
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import wave
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

import imageio_ffmpeg
from playwright.async_api import async_playwright

WPM = 140
HOLD = 1.5
# Pause after a slide appears before the voice starts, so the transition finishes first.
LEAD = 0.6
SILENT_HOLD = 6.0
FPS = 30
W, H = 1920, 1080
TTS = os.environ.get("VIDCAST_TTS", "kokoro")
VOICE = os.environ.get("VIDCAST_VOICE", "af_heart" if TTS == "kokoro" else "Samantha")
KOKORO_PY = Path.home() / ".venvs/kokoro/bin/python"
SILENT = os.environ.get("VIDCAST_SILENT") == "1"
RATE = 24000
# "[>]" in a VO script marks where the next fragment step fires.
MARKER = "[>]"
MIN_STEP_GAP = 0.35
# Show each step this long before its cue word; a visual just ahead of the word reads as in sync.
ANTICIPATE = 0.1
# Render only the first N slides, for quick test renders.
LIMIT = int(os.environ.get("VIDCAST_LIMIT", "0"))

HIDE_UI = ".reveal .controls,.reveal .progress,.reveal .slide-number{display:none!important}*{cursor:none!important}"

# Virtual clock: after __vt.start(), timers, rAF, Date.now and performance.now follow
# __vt.tick(ms), and every Web Animation (CSS transitions and keyframe animations) is paused
# and seeked to its age, so each screenshot shows the page exactly at that video time.
VT_JS = r"""
(() => {
  const real = { st: setTimeout.bind(window), ct: clearTimeout.bind(window), si: setInterval.bind(window),
    ci: clearInterval.bind(window), raf: requestAnimationFrame.bind(window), caf: cancelAnimationFrame.bind(window),
    now: performance.now.bind(performance), dnow: Date.now };
  let virtual = false, vnow = 0, base = 0, dbase = 0, nextId = 1e6;
  const timers = new Map(), rafs = new Map();
  window.setTimeout = (fn, ms, ...a) => {
    if (!virtual) return real.st(fn, ms, ...a);
    const id = nextId++; timers.set(id, { due: vnow + Math.max(0, +ms || 0), fn, a }); return id;
  };
  window.setInterval = (fn, ms, ...a) => {
    if (!virtual) return real.si(fn, ms, ...a);
    const every = Math.max(1, +ms || 1), id = nextId++; timers.set(id, { due: vnow + every, fn, a, every }); return id;
  };
  window.clearTimeout = id => { timers.delete(id); real.ct(id); };
  window.clearInterval = id => { timers.delete(id); real.ci(id); };
  window.requestAnimationFrame = fn => { if (!virtual) return real.raf(fn); const id = nextId++; rafs.set(id, fn); return id; };
  window.cancelAnimationFrame = id => { rafs.delete(id); real.caf(id); };
  performance.now = () => virtual ? base + vnow : real.now();
  Date.now = () => virtual ? dbase + vnow : real.dnow();
  const run = fn => { try { fn(); } catch (e) { console.error(e); } };
  window.__vt = {
    start() { base = real.now(); dbase = real.dnow(); vnow = 0; virtual = true; },
    tick(t) {
      let fired = 0;
      for (;;) {
        let next = null;
        for (const e of timers) if (e[1].due <= t && (!next || e[1].due < next[1].due)) next = e;
        if (!next) break;
        const [id, tm] = next;
        vnow = Math.max(vnow, tm.due);
        if (tm.every) tm.due += tm.every; else timers.delete(id);
        run(() => typeof tm.fn === 'function' ? tm.fn(...tm.a) : (0, eval)(tm.fn));
        fired++;
      }
      vnow = t;
      const cbs = [...rafs.values()]; rafs.clear();
      for (const cb of cbs) { run(() => cb(base + vnow)); fired++; }
      let active = 0;
      for (const anim of document.getAnimations()) {
        if (anim.__born === undefined) anim.__born = vnow;
        anim.pause();
        const age = vnow - anim.__born;
        const end = anim.effect ? anim.effect.getComputedTiming().endTime : 0;
        if (Number.isFinite(end) && age >= end) { anim.finish(); continue; }
        anim.currentTime = age;
        active++;
      }
      return { fired, active };
    },
  };
})();
"""

SLIDE_INFO_JS = r"""
() => [...document.querySelectorAll('.reveal .slides > section')].map(s => {
  const keys = new Set([...s.querySelectorAll('.fragment')].map((f, i) => f.getAttribute('data-fragment-index') ?? 'n' + i));
  const notes = s.querySelector('aside.notes')?.textContent || '';
  const m = notes.match(/VO:\s*"([\s\S]*)"\s*$/);
  return { steps: keys.size, vo: m ? m[1].trim() : '' };
})
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(directory: Path) -> ThreadingHTTPServer:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(directory)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def synth(slides, audio_dir: Path):
    """Speak each slide's VO to a WAV; return (path or None, seconds, cue times or None) per slide."""
    jobs = []
    for i, s in enumerate(slides):
        if not SILENT and s["vo"]:
            jobs.append({"text": s["cued_vo"], "out": str(audio_dir / f"vo{i:02}.wav")})
    if jobs and TTS == "kokoro":
        jobs_file = audio_dir / "jobs.json"
        jobs_file.write_text(json.dumps(jobs))
        # Hugging Face's Xet CDN returns 403 on this network; plain HTTPS downloads work.
        env = {**os.environ, "HF_HUB_DISABLE_XET": "1"}
        subprocess.run([str(KOKORO_PY), str(Path(__file__).with_name("kokoro_tts.py")), str(jobs_file), VOICE], check=True, env=env)
    elif jobs:
        for job in jobs:
            subprocess.run(["say", "-v", VOICE, "-o", job["out"], f"--data-format=LEI16@{RATE}", job["text"].replace(MARKER, "")], check=True)
    clips = []
    for i, s in enumerate(slides):
        path = audio_dir / f"vo{i:02}.wav"
        if not path.exists():
            clips.append((None, len(s["vo"].split()) / WPM * 60, None))
            continue
        meta = Path(str(path) + ".json")
        cues = json.loads(meta.read_text())["cues"] if meta.exists() else None
        with wave.open(str(path)) as w:
            clips.append((path, w.getnframes() / w.getframerate(), cues))
    if TTS == "kokoro" and any(c for _, _, c in clips):
        clips = refine_cues(slides, clips, audio_dir)
    return clips


def norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def cue_phrases(cued_vo: str, n: int = 3):
    """The first n spoken words after each marker."""
    parts = cued_vo.split(MARKER)[1:]
    out = []
    for k, part in enumerate(parts):
        rest = " ".join([part] + parts[k + 1:])
        out.append(" ".join(re.findall(r"[A-Za-z0-9][\w'\-]*", rest)[:n]))
    return out


def clip_silences(wav: Path):
    """(start, end) of pauses in a clip; Whisper often starts a post-pause word inside the pause."""
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(wav), "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(t) for t in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(t) for t in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends))


def refine_cues(slides, clips, audio_dir: Path):
    """Replace Kokoro's cue estimates with when Whisper hears the cue phrase in each clip.

    Kokoro's timestamps can run ~0.5-0.8 s early or late around sentence starts; Whisper's
    word starts on the synthesised audio are what a listener hears.
    """
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wavs = {}
    for (path, _, cues) in clips:
        if path is not None and cues:
            w16 = audio_dir / (path.stem + ".16k.wav")
            subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "16000", str(w16)], check=True)
            wavs[path] = w16
    env = {**os.environ, "HF_HUB_DISABLE_XET": "1"}
    r = subprocess.run([str(KOKORO_PY), str(Path(__file__).with_name("word_times.py")), *map(str, wavs.values())],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        print(f"  warning: Whisper cue refinement failed, using Kokoro timestamps\n{r.stderr[-500:]}", flush=True)
        return clips
    heard = json.loads(r.stdout)
    out = []
    for s, (path, dur, cues) in zip(slides, clips):
        if path not in wavs:
            out.append((path, dur, cues))
            continue
        words = [(norm(w["w"]), w["t"]) for w in heard[str(wavs[path])]]
        gaps = clip_silences(wavs[path])
        refined, floor = [], -1.0
        for est, phrase in zip(cues, cue_phrases(s["cued_vo"])):
            target = [p for p in map(norm, phrase.split()) if p]
            best = None
            for k, (w, t) in enumerate(words):
                if t < floor or abs(t - est) > 1.5 or not target:
                    continue
                if all(k + j < len(words) and words[k + j][0].startswith(p[:6]) for j, p in enumerate(target[:2])):
                    t = min([t] + [e for gs, e in gaps if gs <= t < e or t < gs <= t + 0.7], key=lambda c: abs(c - est))
                    if best is None or abs(t - est) < abs(best - est):
                        best = t
            t = best if best is not None else est
            refined.append(round(t, 3))
            floor = t
        moved = [f"{b - a:+.2f}" for a, b in zip(cues, refined) if abs(b - a) > 0.15]
        if moved:
            print(f"  {path.name}: cues adjusted by Whisper {', '.join(moved)}", flush=True)
        out.append((path, dur, refined))
    return out


def plan(slides, clips):
    """Return per-slide (talk_seconds, total_seconds, step_offsets)."""
    out = []
    for n, (s, (_, talk, cues)) in enumerate(zip(slides, clips), 1):
        k = s["steps"]
        if not s["vo"]:
            out.append((0, SILENT_HOLD, [0] * k))
            continue
        if cues is not None and len(cues) == k:
            steps, last = [], -1.0
            for c in cues:
                last = max(c - ANTICIPATE, last + MIN_STEP_GAP)
                steps.append(LEAD + last)
        else:
            if k:
                print(f"  warning: slide {n} has {k} steps but {0 if cues is None else len(cues)} cue markers; spacing evenly", flush=True)
            steps = [LEAD + talk * j / (k + 1) for j in range(1, k + 1)]
        out.append((talk, LEAD + talk + HOLD, steps))
    return out


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(path: Path, slides, timings, starts):
    cues = []
    for s, (talk, _, _), start in zip(slides, timings, starts):
        sentences = [x for x in re.split(r"(?<=[.?!])\s+", s["vo"]) if x]
        total_words = sum(len(x.split()) for x in sentences) or 1
        t = start + LEAD
        for sentence in sentences:
            d = talk * len(sentence.split()) / total_words
            cues.append((t, t + d, sentence))
            t += d
    with path.open("w") as f:
        for i, (a, b, text) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n")


async def record(url: str, frames_dir: Path, audio_dir: Path):
    """Render frame by frame on a virtual clock: video time t is exactly frame / FPS.

    Page timers, rAF and Date/performance clocks run on virtual time (VT_JS), and every CSS
    animation/transition is paused and seeked to its exact age before each screenshot, so a
    step fired at frame n is on screen at frame n no matter how slowly frames are captured.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        await page.add_init_script(VT_JS)
        await page.goto(url)
        await page.wait_for_selector(".reveal.ready")
        await page.add_style_tag(content=HIDE_UI)
        await page.evaluate("document.fonts.ready.then(() => true)")
        await page.wait_for_timeout(1500)

        slides = await page.evaluate(SLIDE_INFO_JS)
        for s in slides:
            s["cued_vo"] = s["vo"]
            s["vo"] = re.sub(r"\s+", " ", s["vo"].replace(MARKER, "")).strip()
        if LIMIT:
            slides = slides[:LIMIT]
        print(f"synthesising narration for {len(slides)} slides...", flush=True)
        clips = synth(slides, audio_dir)
        timings = plan(slides, clips)

        # Snap every event to the frame grid.
        events, starts, fires, frame = {}, [], [], 0
        for i, (_, total, steps) in enumerate(timings):
            start, last, slide_fires = frame, frame, []
            for at in steps:
                last = max(start + round(at * FPS), last + 1)
                events.setdefault(last, []).append(("step", i))
                slide_fires.append(last / FPS)
            starts.append(start / FPS)
            fires.append(slide_fires)
            frame = max(start + round(total * FPS), last + 1)
            if i < len(timings) - 1:
                events.setdefault(frame, []).append(("next", i + 1))
        end_frame = frame
        print(f"{len(slides)} slides, {end_frame / FPS / 60:.1f} min, rendering {end_frame} frames...", flush=True)

        await page.evaluate("__vt.start()")
        frames, prev_active = [], True
        for f in range(end_frame):
            evs = events.get(f, [])
            for kind, i in evs:
                await page.keyboard.press("Space")
                if kind == "next":
                    now = await page.evaluate("[...document.querySelectorAll('.reveal .slides > section')].findIndex(s => s.classList.contains('present'))")
                    if now != i:
                        print(f"  warning: expected slide {i + 1}, on slide {now + 1}", flush=True)
                    print(f"  slide {i + 1}/{len(slides)} at {f / FPS:.1f}s", flush=True)
            st = await page.evaluate(f"__vt.tick({f * 1000 / FPS})")
            if not frames or evs or st["fired"] or st["active"] or prev_active:
                path = frames_dir / f"f{len(frames):06}.jpg"
                await page.screenshot(path=str(path), type="jpeg", quality=92)
                frames.append([path, 1])
            else:
                frames[-1][1] += 1
            prev_active = bool(st["active"])
        await browser.close()
    print(f"  {len(frames)} distinct frames captured", flush=True)
    return slides, clips, timings, starts, fires, frames


def encode(frames, frames_dir: Path, out: Path):
    lines = ["ffconcat version 1.0"]
    for path, count in frames:
        lines += [f"file '{path.name}'", f"duration {count / FPS:.6f}"]
    lines.append(f"file '{frames[-1][0].name}'")
    concat = frames_dir / "list.ffconcat"
    concat.write_text("\n".join(lines) + "\n")
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat),
         "-vf", f"fps={FPS},scale={W}:{H}:out_range=tv,format=yuv420p",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", str(out)],
        check=True,
    )


def write_timeline(path: Path, slides, clips, starts, fires):
    """Video-time record of each slide start and each step: when the cue word is spoken vs. when the step fired."""
    out = []
    for n, (s, (_, _, cues), start, fs) in enumerate(zip(slides, clips, starts, fires), 1):
        words = cue_phrases(s["cued_vo"])
        steps = []
        for j, fired in enumerate(fs):
            spoken = start + LEAD + cues[j] if cues and j < len(cues) else None
            steps.append({"word": words[j] if j < len(words) else None,
                          "spoken": None if spoken is None else round(spoken, 3), "fired": round(fired, 3)})
        out.append({"slide": n, "start": round(start, 3), "steps": steps})
    path.write_text(json.dumps(out, indent=1))


def build_track(clips, starts, length: float, path: Path):
    """Lay each narration clip at its slide start + LEAD on one mono WAV of the video's length."""
    pcm = bytearray(int(length * RATE) * 2)
    for (clip, _, _), start in zip(clips, starts):
        if clip is None:
            continue
        with wave.open(str(clip)) as w:
            data = w.readframes(w.getnframes())
        at = max(0, int((start + LEAD) * RATE)) * 2
        data = data[: max(0, len(pcm) - at)]
        pcm[at : at + len(data)] = data
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(pcm))


def mux(video: Path, audio: Path, out: Path):
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(video), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-shortest", "-movflags", "+faststart", str(out)],
        check=True,
    )


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: render_video.py deck.html [out.mp4]")
    deck = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else deck.with_suffix(".mp4")

    httpd = serve(deck.parent)
    frames_dir = Path(tempfile.mkdtemp(prefix="vidcast-"))
    try:
        url = f"http://127.0.0.1:{httpd.server_port}/{quote(deck.name)}"
        slides, clips, timings, starts, fires, frames = asyncio.run(record(url, frames_dir, frames_dir))
        print("encoding...", flush=True)
        length = sum(n for _, n in frames) / FPS
        if SILENT:
            encode(frames, frames_dir, out)
        else:
            silent = frames_dir / "video.mp4"
            encode(frames, frames_dir, silent)
            track = frames_dir / "narration.wav"
            build_track(clips, starts, length, track)
            mux(silent, track, out)
        write_srt(out.with_suffix(".srt"), slides, timings, starts)
        write_timeline(out.with_suffix(".timeline.json"), slides, clips, starts, fires)
        print(f"wrote {out} and {out.with_suffix('.srt')}")
    finally:
        httpd.shutdown()
        shutil.rmtree(frames_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
