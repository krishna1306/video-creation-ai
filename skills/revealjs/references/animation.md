# Reveal.js Animation Reference

Read the current official pages before using version-sensitive behavior:

- Fragments: https://revealjs.com/fragments/
- Transitions: https://revealjs.com/transitions/
- Auto-Animate: https://revealjs.com/auto-animate/
- Code: https://revealjs.com/code/
- Events: https://revealjs.com/events/
- Backgrounds: https://revealjs.com/backgrounds/
- Media: https://revealjs.com/media/

## Choose Motion by Narrative Purpose

| Need | Reveal mechanism |
|---|---|
| disclose steps or control attention | fragments |
| establish pacing between slides | slide/background transitions |
| preserve object continuity across states | Auto-Animate |
| walk through implementation | stepped code highlights |
| demonstrate moving content | video, GIF, or animated background |
| coordinate a bespoke visualization | CSS/JS using Reveal events |

If a user asks only to "add animations," ask which narrative purpose matters and
recommend one mechanism. Do not ask when the requested effect is explicit.

## Fragments

Add `fragment` to step an element before advancing the slide. Supported built-in
styles include:

- default fade-in
- `fade-out`, `fade-up`, `fade-down`, `fade-left`, `fade-right`
- `fade-in-then-out`, `current-visible`, `fade-in-then-semi-out`
- `grow`, `shrink`, `semi-fade-out`, `strike`
- `highlight-red`, `highlight-green`, `highlight-blue`
- `highlight-current-red`, `highlight-current-green`,
  `highlight-current-blue`

Use `data-fragment-index` to control order. Elements sharing an index appear or
change together. Nest fragment wrappers when one element needs sequential
effects.

For custom fragments, add both `fragment` and `custom`, then style the initial
class and `.visible` or `.current-fragment` state:

```css
.fragment.custom.blur { filter: blur(0.35em); }
.fragment.custom.blur.visible { filter: none; }
```

Test backward navigation as well as forward navigation. Use `fragmentshown` and
`fragmenthidden` events only when CSS states are insufficient.

## Slide and Background Transitions

Core transition styles are `none`, `fade`, `slide`, `convex`, `concave`, and
`zoom`. Set a deck default with `transition` and override a slide with
`data-transition`. Speeds are `default`, `fast`, and `slow` via
`transitionSpeed` or `data-transition-speed`.

Combine `-in` and `-out` suffixes when entrance and exit differ, for example
`data-transition="slide-in fade-out"`. Set background motion independently with
`backgroundTransition` or `data-background-transition`.

Use one restrained default across the deck. Per-slide variation should express a
real narrative boundary, not novelty.

## Auto-Animate

Add `data-auto-animate` to adjacent slides. Reveal matches identical text/node
types, media sources, and DOM order. Add matching `data-id` values when implicit
matching is ambiguous.

Available controls include:

- `data-auto-animate-easing`
- `data-auto-animate-duration`
- element-level `data-auto-animate-delay`
- `data-auto-animate-unmatched`
- `data-auto-animate-id` to group adjacent sequences
- `data-auto-animate-restart` to break continuity

Deck defaults include `autoAnimate`, `autoAnimateEasing`,
`autoAnimateDuration`, and `autoAnimateUnmatched`.

Auto-Animate can transition position, scale, color, background, padding, type,
line height, letter spacing, borders, outlines, lists, and compatible code
blocks. For code, use matching `data-id` values and `data-line-numbers`.

Use Auto-Animate for meaningful state change. Duplicate markup across states
carefully and keep semantic reading order valid.

## Code Walkthroughs

Load `RevealHighlight`. Use `data-line-numbers` for line numbers or provide a
range such as `data-line-numbers="3,8-10"`. Separate highlight steps with `|`:

```html
<pre><code class="language-js" data-line-numbers="1-2|4|6-9">
// code
</code></pre>
```

Use `data-ln-start-from` for excerpts from larger files. Combine stepped
highlights with Auto-Animate only when the audience needs both code evolution and
line-level focus.

## Media and Custom Motion

Animated GIF backgrounds restart when their slide opens. Video backgrounds can
loop and should normally be muted. Embedded media can use `data-autoplay`; Reveal
pauses supported media when leaving the slide.

For custom animation, prefer CSS tied to Reveal state classes. Use JavaScript
only when the animation must coordinate with deck state. Relevant events include
`ready`, `slidechanged`, `slidetransitionend`, `fragmentshown`,
`fragmenthidden`, `autoanimate`, `resize`, `sync`, and `slidesync`.

Initialize third-party renderers on `ready`, refresh them on `slidechanged` or
`slidetransitionend` when hidden-slide transforms affect rendering, and clean up
long-running animation when the slide is no longer current.

In scroll view, Reveal converts fragment and Auto-Animate steps into scroll
triggers. Test the sequence in both slide and scroll modes when automatic narrow-
screen scroll activation is enabled; timing and focus should remain meaningful
without relying on a transition completing first.

## Reduced Motion and Safety

Provide a low-motion state even when motion was requested:

```css
@media (prefers-reduced-motion: reduce) {
  .reveal .slides section,
  .reveal .fragment,
  .reveal [data-auto-animate-target] {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

Avoid flashing, rapid oscillation, autoplay with sound, and motion that blocks
reading or navigation. Never hide essential meaning permanently when motion is
disabled. Validate with reduced motion enabled and with keyboard navigation.

## Third-Party Plugins

Core Reveal features plus CSS/JS extension hooks are the default ecosystem.
Before adding a community plugin, confirm that core features cannot meet the
need, then check maintenance recency, compatibility, license, loading method,
accessibility, and exact version pinning. Ask the user before adding it.