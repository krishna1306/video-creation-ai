---
name: revealjs
description: "Create, redesign, or debug polished reveal.js presentations. Use whenever the user asks for Reveal.js slides, an HTML presentation, a web-based deck, speaker notes, slide animation, fragments, Auto-Animate, presentation transitions, or Lucide icons in slides. Produces distinctive, accessible, version-pinned decks whose story and visual composition lead the implementation."
---

# Reveal.js Presentations

Create presentations, not framework demonstrations. Prioritize the audience's
experience in this order:

1. story and audience outcome
2. visual evidence
3. composition
4. visual identity
5. purposeful motion
6. Reveal.js mechanics
7. browser validation

Use Reveal.js 6.0.2 for new standalone decks. Preserve an existing deck's visual
language unless the user asks for a redesign.

## Build the Deck

### 1. Find the story

Determine who is watching, what they should understand or do, and how the deck
will be delivered. Give every slide one job. Write titles as claims or useful
promises, not topic labels.

Do not begin by selecting a theme or generating placeholder slides. First map a
short narrative: setup, tension, evidence, resolution, and action. Use only the
parts that fit the material.

### 2. Collect visual evidence

Prefer real screenshots, product states, diagrams, charts, code, photography,
and concrete examples over decorative graphics. A primary visual should show
the thing being discussed clearly enough to inspect.

If important assets are missing, ask for them or use an honest placeholder that
states what belongs there. Do not disguise missing evidence with decoration.

### 3. Compose each slide for its content

Read [references/design-system.md](references/design-system.md) before creating
or substantially redesigning a deck. Select concrete compositions from that
reference and vary them with the story. Do not force every idea into cards or a
50/50 grid.

Use the MyAgent deck's strongest transferable habits: a bounded frame, short
titles, evidence-led layouts, disciplined accent color, relative typography,
purposeful fragments, and concise notes. Copy its Cisco palette, typography, or
product-specific components only when the presentation calls for them.

### 4. Establish a visual identity

Choose typography, palette, spacing, image treatment, and recurring graphic
language from the subject, audience, and brand. Define a small set of semantic
tokens and two or three recurring motifs, then allow individual slides to use
content-specific layouts.

Aim for a recognizable point of view rather than a neutral component library.
Use whitespace deliberately, but do not leave accidental empty regions.

### 5. Add motion only where it helps

Use fragments for spoken sequence, transitions for pacing, Auto-Animate for
continuity, stepped highlights for code, and Reveal events for genuinely custom
behavior. Read [references/animation.md](references/animation.md) only when the
deck uses motion.

When the user asks only to "add animation," ask one concise question about the
narrative purpose and recommend the most likely mechanism. Do not animate every
element.

### 6. Implement with Reveal-native structure

Use `.reveal > .slides > section` and place custom layout inside a child such as
`.frame`. Let Reveal own slide positioning, transforms, scaling, and navigation.
Use stable classes for repeated visual patterns and inline values only when they
belong to one specific state or visual.

Use Lucide for semantic interface-style icons; read
[references/lucide.md](references/lucide.md) when icons are present. Load charts
only for chart decks and read [references/charts.md](references/charts.md) first.

Add concise speaker notes when the deck is for live delivery. Notes should
capture timing, presenter action, and context rather than repeat slide text.

### 7. Validate the experience

Serve module-based decks over HTTP. Check the actual presentation in a browser,
not only the source:

- inspect representative desktop and mobile views
- navigate every slide and fragment in both directions
- check overflow, console errors, links, images, icons, and notes
- verify readable contrast, useful alt text, visible focus, and reduced motion
- test optional features only when the deck uses them

Do not declare a deck complete from static HTML inspection alone.

## Advanced Features

Read [references/reveal-core.md](references/reveal-core.md) only when the task
needs version-sensitive configuration or advanced behavior such as:

- vertical stacks, scroll view, lightboxes, backgrounds, or media
- Markdown, code, math, search, zoom, or custom plugins
- dynamic slides, runtime APIs, state, embedding, or postMessage integration
- React integration or custom keyboard/navigation behavior

Read [references/pdf-export.md](references/pdf-export.md) only for PDF work and
[references/cisco-brand.md](references/cisco-brand.md) only for explicitly
Cisco-branded decks. Official documentation at https://revealjs.com remains the
source of truth for unfamiliar or version-sensitive behavior.

## Guardrails

- Keep text readable at presentation distance.
- Use visual assets that reveal the actual subject.
- Do not nest cards or repeat one layout across the whole deck.
- Do not use color alone to communicate meaning.
- Pin dependency versions and load only dependencies the deck uses.
- Preserve keyboard navigation and meaningful source order.
- Ask before adding a community plugin.

## Fallback Scaffold

Author directly from the content and available design context whenever possible.
Use `scripts/create-presentation.js` and `references/base-styles.css` only when
the user explicitly requests a scaffold or no design context exists.

Validation helpers remain available:

```bash
python3 scripts/validate_html.py presentation.html
node scripts/check-overflow.js presentation.html
```
