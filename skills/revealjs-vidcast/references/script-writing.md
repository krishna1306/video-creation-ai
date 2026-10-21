# Writing a voice-over that stays in sync with the slides

The animation sequence is fixed by the deck. The script's job is to say things in the order
they appear and to name each item at the moment it appears. Write the script against the
`inspect_deck.py` output, slide by slide.

## Per-slide procedure

1. List the slide's steps from `inspect_deck.py` (step 1 … step N, with what each reveals).
2. Write an opening sentence that covers what is visible on entry (before step 1). On a slide
   with an entry animation (buildings rising, a line drawing), describe that first.
3. For each step in order, write the sentence that introduces it. Put `[>]` immediately before
   the words that name the revealed item, ideally the same words that appear on screen.
4. After the last step, add at most one or two sentences of takeaway. These run during the
   reading hold, so keep them short.
5. Count markers. The count must equal the number of steps.

## Marker placement

| Situation | Do | Avoid |
|---|---|---|
| Step reveals a labelled box "HLD" | "we write the [>] high-level design" | "[>] once things are clear, we write the HLD" (too early) |
| Step strikes through a statement | "It [>] doesn't choose for the customer" | Marker at the start of the sentence before "It" when "It" belongs to the previous clause |
| Several items appear as one step | One marker before the first item's name | One marker per item when they share one fragment index |
| Several steps should appear together | Consecutive markers "[>] [>] [>] milestones" (staggered 0.35 s) | Writing three filler clauses just to space them |
| Step reveals a takeaway line | Marker before the sentence that states it | Marker after the sentence has already been read |
| Question-and-answer steps | "[>] What can I ask it for? [>] What do I expect back?" | One marker for two steps |

## Pacing

- Kokoro speaks about 160–180 words per minute. A slide with N steps needs roughly
  (N + 1) × 8–15 words of narration.
- Keep at least ~1.5 s (four or five words) between markers. Steps closer than 0.35 s are pushed
  apart automatically, but rapid-fire reveals are hard to follow.
- A slide's duration is the narration length plus `LEAD` (0.6 s) plus `HOLD` (1.5 s). To keep a
  dense slide on screen longer, add a sentence; don't pad with silence.

## Words TTS handles badly

- Write acronyms the way they should be spoken. Kokoro reads "LDOS" letter by letter; if it
  should be a word, spell it phonetically in the VO only, not on the slide.
- Avoid slashes and symbols: "and/or" becomes "and or". Write "Q3" and "FY27" only if letter-by-letter
  reading is acceptable.
- Hyphenated words are fine to speak. Whisper may transcribe them differently, so the sync
  report may show `tts` instead of `heard` for those rows.

## When the narration order and the step order disagree

Do not leave a mismatch. Choose one:

- **Reorder the sentence** to follow the steps (usually the right fix).
- **Reorder the fragments** with `data-fragment-index` if the narrative order is better for the
  audience. Then re-run `inspect_deck.py`.
- **Merge steps** (give them the same `data-fragment-index`) if two steps are introduced by one
  phrase.
