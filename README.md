# Video Creation AI

**Two agent skills. One idea-to-video workflow.**

[Watch the example](https://youtu.be/NSbSgm9Kfvc) | [Open the slides](example/deck.html)

## What This Is

A pair of reusable agent skills that turn an idea into an animated presentation and a narrated video.

| Skill | Job |
| --- | --- |
| [revealjs](skills/revealjs/SKILL.md) | Build story-first Reveal.js slides with purposeful animation. |
| [revealjs-vidcast](skills/revealjs-vidcast/SKILL.md) | Add local narration, word-timed animation, captions, and MP4 rendering. |

Both bundles include their supporting scripts and references. The finished demo lives in [example/](example/).

## How It Works

`Idea -> HTML slides -> Narration + cue timing -> MP4 + captions`

Your agent creates the deck and writes narration in speaker notes. `[>]` markers connect spoken words to animation steps. Kokoro generates the voice, Whisper refines cue timing, and a virtual clock renders frames deterministically. A separate sync check verifies the result.

The example includes the [HTML deck](example/deck.html), [video](https://youtu.be/NSbSgm9Kfvc), [captions](example/deck.srt), and [timing data](example/deck.timeline.json).

## Run It

Ask your coding agent to use the two skill files above to create a deck, then turn it into a narrated video. To render the included example manually, install [uv](https://docs.astral.sh/uv/) and run from the repository root:

```bash
S="$PWD/skills/revealjs-vidcast/scripts"
bash "$S/setup.sh"
~/.venvs/vidcast/bin/python "$S/inspect_deck.py" example/deck.html
~/.venvs/vidcast/bin/python "$S/render_video.py" example/deck.html example/deck.mp4
~/.venvs/vidcast/bin/python "$S/check_sync.py" example/deck.mp4
```

Setup downloads the models and browser. Narration and rendering run locally; CDN-hosted deck assets still need network access.