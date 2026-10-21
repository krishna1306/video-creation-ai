# Reveal.js Core Reference

Use current official documentation as the source of truth:

- Markup: https://revealjs.com/markup/
- Layout helpers: https://revealjs.com/layout/
- Presentation size: https://revealjs.com/presentation-size/
- Configuration: https://revealjs.com/config/
- Backgrounds: https://revealjs.com/backgrounds/
- Media: https://revealjs.com/media/
- Scroll view: https://revealjs.com/scroll-view/
- Lightbox: https://revealjs.com/lightbox/
- Markdown: https://revealjs.com/markdown/
- Code: https://revealjs.com/code/
- Math: https://revealjs.com/math/
- Plugins: https://revealjs.com/plugins/
- Keyboard: https://revealjs.com/keyboard/
- Auto-slide: https://revealjs.com/auto-slide/
- Speaker view: https://revealjs.com/speaker-view/
- API: https://revealjs.com/api/
- Presentation state: https://revealjs.com/presentation-state/
- React: https://revealjs.com/react/
- Upgrading: https://revealjs.com/upgrading/

## Reveal 6 Imports

For direct files or CDN URLs, Reveal 6 uses `.mjs` and moves built-in plugin
bundles under `dist/plugin`:

```js
import Reveal from "https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist/reveal.mjs";
import RevealNotes from "https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist/plugin/notes.mjs";
```

The CDN stylesheet remains `dist/reveal.css`. In a bundled npm project, prefer
package exports instead: `reveal.js`, `reveal.js/reveal.css`,
`reveal.js/theme/<theme>.css`, and `reveal.js/plugin/<name>`. Reveal 6 bundles
TypeScript types; remove `@types/reveal.js` and use `RevealApi`, `RevealConfig`,
and `RevealPlugin` from `reveal.js`.

## Required Markup

Slides must follow `.reveal > .slides > section`:

```html
<div class="reveal">
  <div class="slides">
    <section>Horizontal slide</section>
    <section>
      <section>Vertical slide 1</section>
      <section>Vertical slide 2</section>
    </section>
  </div>
</div>
```

Nested sections form a vertical stack. Use one only when the audience can
meaningfully choose whether to drill down.

Add `data-state="name"` to a slide when the active slide needs a viewport-level
class or event. Do not use it as a substitute for ordinary component classes.

## Sizing and Positioning

Reveal authors slides at a normal size and scales them uniformly while
preserving aspect ratio. Defaults are `width: 960`, `height: 700`, `margin: 0.04`,
`minScale: 0.2`, and `maxScale: 2.0` unless the installed version says otherwise.

Slides are vertically centered by default. Set `center: false` only when the
design intentionally uses a fixed top-aligned canvas. Do not disable Reveal's
layout merely to gain normal CSS control inside a slide.

`disableLayout: true` transfers sizing, scaling, and centering responsibility to
the deck. Use it only for an intentionally custom responsive canvas. Call
`Reveal.layout()` when an embedded presentation's root dimensions change outside
the normal window resize flow.

Never set `position` or `transform` on `.reveal .slides section`; Reveal uses
those properties for navigation and transitions. Put custom layout inside a
child such as `.frame`.

## Built-in Layout Helpers

- `.r-stack` centers elements on top of one another; combine with fragments for
  staged diagrams or images.
- `.r-hstack` and `.r-vstack` arrange flexible horizontal or vertical groups;
  use the documented item-alignment and justification helpers with them.
- `.r-fit-text` expands a heading to the available width.
- `.r-stretch` gives one direct child the remaining vertical space. Only one
  direct child per slide can stretch.
- `.r-frame` adds Reveal's framed treatment to an element.

Prefer these helpers when their documented behavior matches the design.

## Backgrounds and Media

Use slide attributes rather than styling the section as a full-page background:

- `data-background-color`
- `data-background-gradient`
- `data-background-image`, with size, position, repeat, and opacity controls
- `data-background-video`, optionally looped and muted
- `data-background-iframe`, optionally interactive
- `data-background-transition`

Use `data-src` for lazy-loaded images, video, audio, and iframes in media-heavy
decks. Use `data-autoplay` only when automatic playback is appropriate. Reveal
pauses supported media when its slide is hidden unless `data-ignore` is present.
Never autoplay audible media without explicit user intent.

Add `data-preview-image`, `data-preview-video`, or `data-preview-link` when a
thumbnail, control, or link should open Reveal's built-in lightbox. The attribute
may be empty to reuse the element source or contain a different preview URL.
Use `data-preview-fit="scale-down|contain|cover"` for media sizing. Iframe
previews work only when the target permits embedding through its frame and CSP
headers. Keep visible labels and keyboard-accessible triggers.

## Slide View and Scroll View

Use `view: "scroll"` for a self-guided, document-like experience. Reveal maps
slides, fragments, and Auto-Animate sequences onto scroll triggers. Relevant
options are `scrollProgress`, `scrollSnap`, and the experimental
`scrollLayout: "compact"`; test experimental layout before relying on it.

Reveal 6 automatically switches to scroll view when the presentation width is at
or below `scrollActivationWidth` (435 by default). Set it to `null` or `0` when a
deck must retain slide navigation on narrow screens. A viewer can also append
`?view=scroll` without a configuration change. Scroll view flattens horizontal
and vertical slides into one linear flow, so do not depend on stack direction to
communicate hierarchy. Test both wide and narrow modes because controls, speaker
notes, and slide numbering are suppressed in scroll view.

## Plugins

Include a plugin's script or ES module and register it in `plugins`. Built-in
plugins include Notes, Highlight, Markdown, Search, Math, and Zoom. Load only
those the deck needs.

- Use Notes for live delivery and presenter pacing.
- Use Highlight for syntax coloring and stepped line focus.
- Use Markdown when source maintainability outweighs precise bespoke markup;
  external Markdown requires HTTP serving and separator/attribute validation.
- Use Math with one chosen renderer (KaTeX or the required MathJax generation),
  and load its assets only for decks containing equations.
- Use Search for long, reference-oriented decks where content retrieval matters.
- Use Zoom when the presenter genuinely needs to inspect dense details; do not
  use it to compensate for unreadably small slide content.

Reveal's overview, pause, fullscreen, auto-slide, touch, keyboard, and URL/hash
features are core behavior rather than reasons to add a plugin. Enable auto-slide
or looping only for unattended installations, and provide a way to pause. Add
custom keyboard behavior with `addKeyBinding` so it appears in the help overlay.

The legacy `dependencies` configuration is deprecated. Use normal script tags,
ES module imports, or the project's bundler. Pin exact dependency versions; do
not use `@latest`.

Charts are not a Reveal core plugin. Treat Chart.js integrations as optional
third-party dependencies and consult [charts.md](charts.md).

Custom plugins should expose a stable `id` and `init(deck)` and may return a
Promise. Use `destroy()` for cleanup when needed. Register keyboard actions with
`addKeyBinding` so they appear in Reveal's help overlay, and use `deck.on`/`off`
for lifecycle events. Do not create a plugin when a small deck-local listener is
clearer.

## Speaker Notes

Load `RevealNotes` and add `<aside class="notes">` inside a slide. Speaker view
opens with `S` and generally requires a local web server. Notes may alternatively
use `data-notes`, but an aside is easier to maintain for substantial notes.

Use `defaultTiming`, `totalTime`, or per-slide `data-timing` only when pacing is
part of the presentation requirements.

## Configuration Baseline

Start minimally and add behavior intentionally:

```js
const deck = new Reveal({
  hash: true,
  controls: true,
  progress: true,
  slideNumber: "c/t",
  postMessage: false,
  transition: "fade",
  backgroundTransition: "fade",
  plugins: [RevealNotes]
});

deck.initialize();
```

Choose `navigationMode: "linear"` for a strictly directed story. Keep the
default mode when vertical stacks are intentionally navigable. Standalone decks
should disable `postMessage`; enable it only for an intentional parent-window
integration. Do not copy every available configuration option into a deck.

## Navigation and Delivery Modes

Give destination slides stable IDs and link to them with `#/slide-id` when a
deck needs an agenda, branching demo, appendix jump, or return path. Prefer IDs
over numeric routes because slide reordering does not break them. Use Reveal's
documented `navigate-prev`, `navigate-next`, and directional classes for custom
controls instead of duplicating route logic.

Use `data-visibility="hidden"` for material that must be removed from navigation
and the initialized DOM, such as an unreleased section. Do not use it merely to
hide alternate responsive content; use CSS and accessible source order for that.

Overview, pause, fullscreen, keyboard, touch, and URL navigation are core
delivery features. Preserve them unless the presentation environment requires a
specific restriction. Use `autoSlide`, `loop`, or a custom `autoSlideMethod`
only for kiosks and unattended playback, and always retain an obvious pause or
exit path.

## Dynamic, Embedded, and Stateful Decks

After runtime DOM changes, use the narrowest update:

- `sync()` after adding, removing, reordering, or regrouping slides
- `syncSlide(slide)` after changing one slide's content or attributes
- `syncFragments(slide)` after changing fragment order or membership
- `layout()` after a geometry change that does not alter slide structure

Listen for `sync` or `slidesync` when dependent renderers need refreshing.
`getState()` and `setState()` serialize and restore navigation, fragment, pause,
overview, and preview state; use them for controlled integrations, not as content
storage.

For a deck inside another interface, set `embedded: true`, size the Reveal root,
and consider `keyboardCondition: "focused"`. Keep `preventIframeAutoFocus`
enabled unless an interactive iframe must receive keyboard input. Disable
`postMessage` when no parent integration needs remote control. When cross-window
messaging is required, validate origins and message shapes in application code
and never treat incoming payloads as trusted content.

## React Projects

Reveal 6's official `@revealjs/react` package supplies `Deck`, `Slide`, `Stack`,
`Fragment`, `Code`, and `Markdown`, plus event props, `useReveal()`, and
`deckRef`. It handles initialization, syncing, and cleanup. Use it in an existing
React application; keep the static HTML scaffold for standalone decks. Plugins
remain initialization-only, and Reveal CSS/theme imports are still required.