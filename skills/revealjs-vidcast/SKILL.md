---
name: revealjs-vidcast
description: Turn a reveal.js presentation into a narrated MP4 whose animations fire exactly on the words that introduce them. Writes or adapts a voice-over script per slide with "[>]" cue markers tied to each fragment step, synthesises narration locally with Kokoro TTS, renders the deck frame-by-frame on a virtual clock, muxes audio, writes captions, and verifies sync with Whisper. Use this skill whenever the user wants to make a video, vidcast, screencast, MP4, explainer video or recorded walkthrough from a reveal.js / HTML slide deck, add a voice-over or narration to slides, auto-advance a deck with timed animations, or fix animations that drift out of sync with narration, even if they don't say "vidcast".
---

# reveal.js → narrated, synced vidcast

The deliverable is an MP4 where each fragment appears on the word that introduces it, plus
captions (`.srt`), a timeline (`.timeline.json`) and a sync report. Sync comes from three things:

1. **Script–step alignment.** Each slide's voice-over has one `[>]` marker per fragment step,
   placed immediately before the word that should reveal that step.
2. **Word-accurate timing.** Kokoro returns word timestamps as a first estimate. Whisper then
   transcribes each synthesised clip, and each marker's time becomes the moment the next word
   is actually heard. Kokoro alone can be ~0.5–0.8 s off at sentence starts.
3. **Deterministic capture.** Frames are rendered on a virtual clock. Timers, rAF and every CSS
   animation are paused and seeked per frame. A step fired at frame *n* is on screen at frame
   *n*, however slowly frames are captured. Never use real-time screen capture (CDP screencast,
   screen recorders): it lags 1–14 s behind under load. That is the root cause of "almost
   synced" videos.

## Scripts (in `scripts/`)

All commands below assume `S=~/.agents/skills/revealjs-vidcast/scripts`.

| Script | Runs in | Purpose |
|---|---|---|
| `setup.sh` | shell | Creates both Python environments, installs Chromium and Kokoro, downloads models |
| `inspect_deck.py` | vidcast venv | Lists every slide's fragment steps (what each reveals) and checks marker counts |
| `render_video.py` | vidcast venv | TTS → cue times → deterministic frames → MP4 + `.srt` + `.timeline.json` |
| `check_sync.py` | vidcast venv | Whisper-heard word time vs. on-screen change for every step; exit 1 if any lag > 0.5 s |
| `kokoro_tts.py`, `word_times.py` | kokoro venv | Called by the scripts above; not run directly |

Environments: `~/.venvs/vidcast` (Python 3.12+, playwright, imageio-ffmpeg) and
`~/.venvs/kokoro` (Python 3.12, kokoro, soundfile, en_core_web_sm, faster-whisper).
Run `bash $S/setup.sh` once if either is missing. See "Troubleshooting" for network quirks.

## Workflow

### 1. Inspect the deck

```bash
~/.venvs/vidcast/bin/python $S/inspect_deck.py path/to/deck.html
```

You get each slide's steps in play order. Grouped fragments (same `data-fragment-index`)
are one step. Read this before writing a word of narration: the script must follow the
steps, not the other way round. Note slides that auto-animate on entry (CSS animations on
`.present`), because their narration should open by describing what is already moving.

### 2. Write or adapt the voice-over script

Narration lives in each slide's speaker notes as the last line:
`VO: "… [>] word …"` inside `<aside class="notes">`. Follow
`references/script-writing.md` (read it now). The essentials:

- **One `[>]` per step, in step order.** Place it immediately before the noun phrase that names
  what the step reveals: "we write the [>] high-level design", not before "we write".
- **Narration must reach each step in order.** If the script mentions B before A but the
  fragments reveal A then B, reorder the sentence or the fragments. Do not leave it mismatched.
- **Give each step room.** Leave at least ~1.5 s of speech between markers. Several items that
  appear together can share one sentence with consecutive markers ("at the [>] [>] [>] commit
  milestones"); the renderer staggers them by 0.35 s.
- **Slides without steps** still need a VO sized to the content. Title slides may have no VO
  (they hold for 6 s).
- Spell out acronyms on first use. Write numbers the way they should be spoken.

Then re-run `inspect_deck.py`. It must exit 0 (every narrated slide's marker count equals its
step count) before you render.

### 3. Render a short test first

```bash
VIDCAST_LIMIT=4 ~/.venvs/vidcast/bin/python $S/render_video.py deck.html /tmp/test.mp4
~/.venvs/vidcast/bin/python $S/check_sync.py /tmp/test.mp4
```

`check_sync.py` prints, per step, the cue phrase, when Whisper heard it, when the step fired,
when the screen changed, and the lag. Fix any `OUT OF SYNC` rows before the full render
(see "Reading the sync report").

### 4. Full render and verification

```bash
~/.venvs/vidcast/bin/python $S/render_video.py deck.html deck.mp4
~/.venvs/vidcast/bin/python $S/check_sync.py deck.mp4
```

Rendering time scales with the number of distinct frames, not video length. Static stretches
cost almost nothing. Infinite CSS animations (pulses, spinners) force a screenshot every frame
while visible.

Deliver: the MP4, the `.srt`, the worst lag from the report, and any assumptions.

## Options (environment variables)

| Variable | Default | Effect |
|---|---|---|
| `VIDCAST_VOICE` | `af_heart` | Kokoro voice (`af_bella`, `am_michael`, `bf_emma`, `bm_george`, …) |
| `VIDCAST_TTS` | `kokoro` | `say` uses macOS voices (no word timestamps: steps spread evenly) |
| `VIDCAST_SILENT` | off | `1` renders silent at 140 wpm pacing, for a human to record over |
| `VIDCAST_LIMIT` | all | Render only the first N slides |

Constants at the top of `render_video.py`: `LEAD` (pause before the voice starts on a new
slide, 0.6 s), `HOLD` (read time after narration, 1.5 s), `ANTICIPATE` (show a step 0.1 s
before its word), `MIN_STEP_GAP` (0.35 s), `FPS` (30), resolution (1920×1080).

## Reading the sync report

- **`heard`** comes from Whisper (ground truth). **`tts`** in that column means the cue phrase
  wasn't found in the transcript, and the TTS estimate was used instead. That happens with
  hyphenated or unusual words, and it is usually fine.
- **`tts ±x`** at the end of a row is how far Kokoro's estimate was from what Whisper heard.
  Values within ±0.25 s are normal.
- **Lag ≈ fired − heard, and fired is wrong:** the marker is in the wrong place in the script.
  Move it.
- **Visual much later than fired:** the change is too subtle for detection (a small colour
  change), or the step reveals something off-screen. Check the frame at that time with ffmpeg
  before assuming a bug.
- **"no cue or no visual change":** the step has no marker, or reveals nothing visible.

## Troubleshooting

- **Hugging Face downloads fail with 403 (Xet CDN):** set `HF_HUB_DISABLE_XET=1`. The scripts
  already do.
- **Kokoro exits silently on first run:** it tried to `pip install` spaCy's `en_core_web_sm`
  into a uv venv that has no pip. Install the wheel explicitly (`setup.sh` does).
- **Kokoro needs Python ≤3.12:** keep it in its own venv. The renderer calls it as a subprocess.
- **faster-whisper `metadata_errors` TypeError:** PyAV mismatch. `check_sync.py` decodes the
  audio with ffmpeg and passes a 16 kHz WAV, which avoids it.
- **Deck loads Reveal from a CDN:** rendering needs network access, unless the deck vendors
  reveal.js locally.
- **A step "fires" but nothing moves:** the deck may use JS animation libraries (GSAP, anime.js)
  driven by their own clocks. The virtual clock overrides timers, rAF and `performance.now`,
  which covers most of them. Canvas/WebGL that reads `Date` objects directly may still drift.
