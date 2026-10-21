# Presentation Composition Guide

Use this as a menu, not a checklist. Pick the compositions that best express the
story and adapt them to the subject, brand, audience, and available evidence.

The patterns come from the strongest parts of the MyAgent presentation. Their
structure is reusable; its Cisco navy/cyan palette and product-specific details
are not universal defaults.

## Foundation

Keep visible content inside a bounded frame and size typography relative to the
Reveal canvas:

```css
.reveal { font-size: 32px; }
.frame { width: min(100%, 36.875em); margin-inline: auto; text-align: left; }
.label { font-size: 0.52em; }
.slide-title { font-size: 1.45em; }
.dek { max-width: 29em; font-size: 0.76em; line-height: 1.4; }
```

Treat these as relationships, not mandatory values. Establish a clear hierarchy:

1. optional label that locates the audience in the story
2. short title that states the slide's claim
3. visual evidence or a meaningful content structure
4. optional takeaway, source, or footnote

Use semantic color tokens. Reserve the accent for labels, key values, meaningful
icons, progress, links, or one emphasized state. Use relative sizing and stable
media dimensions so late-loading assets and fragments do not shift the layout.

## Composition 1: Hero Promise

Use for an opening, section reset, or final commitment.

- Place a small wordmark or eyebrow above the title.
- Make the title a literal promise or tension, usually two or three short lines.
- Add one concise supporting sentence.
- Use a thin rule, icon-plus-promise line, or small footer as the visual anchor.
- Keep the primary experience unboxed. Do not put the hero inside a card.

The opening should identify the product, person, place, or offer immediately.

## Composition 2: Evidence and Explanation

Use when a screenshot, photograph, diagram, code sample, or chart proves the
claim.

```css
.evidence-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: 1.2em;
  align-items: center;
}
```

Give the evidence the larger track. Keep the explanation to a short paragraph
and two or three signals. Show the real product state at useful scale; do not
replace it with an icon or decorative mockup. Use a lightbox when inspection
matters.

## Composition 3: Outcomes With a Reveal

Use for three or four benefits, results, constraints, or responsibilities.

- Arrange concise items in equal tracks.
- Use open space and a top rule before reaching for cards.
- Give each item an icon, short heading, and one supporting sentence.
- Reveal items in the order they are spoken.
- Emphasize only the subset whose ownership or meaning changes.

Avoid six identical cards. Split the slide when the audience must read dense
copy or compare subtle differences.

## Composition 4: System Flow

Use for inputs, transformation, and outputs or any small process with clear
handoffs.

```text
[signals in]  →  [system or decision]  →  [results]
```

Make nodes visually stable and connectors subordinate. Reveal the flow in causal
order. On narrow screens, stack nodes vertically and rotate or replace arrows.
For a complex architecture, use a dedicated diagram rather than shrinking more
nodes into this pattern.

## Composition 5: Guided Exercise

Use for setup instructions, workshop steps, prerequisites, or a repeated series
of actions.

- Put the purpose and expected result on the left.
- Put the concrete steps, prompt, or checklist on the right.
- Use one grouped surface only where it makes the actionable material easier to
  distinguish.
- Repeat the structure across a short numbered sequence so the audience learns
  how to scan it.
- Change the evidence or emphasis on each slide so the sequence does not feel
  mechanically duplicated.

## Composition 6: Timeline or Daily Rhythm

Use for a real sequence anchored in time, stage, or responsibility.

- Use three to five stable moments.
- Give each moment a visible time or stage label, icon, heading, and one sentence.
- Reveal in order when presenting live.
- Use a line only when it clarifies continuity; spacing and alignment may be
  enough.
- Switch to a vertical sequence on narrow screens.

## Composition 7: Before and After

Use when the change itself is the message.

- Keep both states structurally parallel so differences are easy to scan.
- Use neutral styling for the current state and a restrained accent for the
  improved state.
- Reveal the current state first, then the improved state.
- Describe observable changes rather than vague adjectives.
- Do not rely on color alone; headings and wording must identify each state.

## Composition 8: Connected Tools or Capabilities

Use for a compact inventory whose members have equal importance.

- Use a row or grid of icon, name, and one-line role.
- Keep each item open or separated by rules rather than enclosing every item.
- Add one distinct callout beneath the grid only when it applies to the whole
  system.
- Reduce track count responsively before text becomes cramped.

## Composition 9: Action Path

Use for a close that asks the audience to do something.

- Limit the path to two or three explicit steps.
- Use numbered markers and a subtle connector to show order.
- Keep the final supporting sentence short and concrete.
- Make the first action possible immediately after the presentation.

## Visual Identity

Choose a direction from the subject instead of defaulting to the neutral starter
CSS. Define:

- one background family and one contrasting surface
- one text color, one muted color, and one high-intent accent
- a display/body type pairing or one expressive family with clear weight changes
- one image treatment, such as edge-to-edge product crops or clean contained
  screenshots
- two recurring motifs, such as top rules, numbered circles, editorial captions,
  or a specific connector style

For an existing deck, reuse its tokens, motifs, and spacing before inventing new
ones. For branded work, use the real brand system when available.

## Motion and Notes

Use fragments to match the spoken sequence, not to repair an overloaded slide.
Use Auto-Animate only when continuity between states matters. Keep a restrained
transition default across the deck.

Speaker notes should contain timing, presenter action, and context:

```html
<aside class="notes">
  0:40. Reveal the stages in order. Pause on the ownership handoff.
</aside>
```

## Quality Check

Before delivery, ask:

- Is each title a useful claim or promise?
- Does every substantive slide contain evidence or a meaningful visual structure?
- Do consecutive slides vary because their content relationships differ?
- Is the subject visible, not merely described?
- Can the smallest text be read at presentation distance?
- Are cards used only for real grouping, state, or interaction?
- Do mobile and reduced-motion modes preserve the story?
