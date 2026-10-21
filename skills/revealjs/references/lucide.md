# Lucide Icons in Reveal.js

Use Lucide for modern interface-style icons when a meaningful icon exists.
Consult current documentation at https://lucide.dev/ and accessibility guidance
at https://lucide.dev/how-to/accessibility.

## Loading

Prefer the project's local vendored build when available. Otherwise pin an exact
Lucide version instead of using `@latest`:

```html
<script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.js"></script>
```

Use the version already approved by the project, or verify and pin a newer
version deliberately. Keep the script source consistent across the deck.

## Markup and Rendering

Use `data-lucide` placeholders:

```html
<i data-lucide="calendar-days" aria-hidden="true"></i>
```

Render after Reveal is ready. Re-render on slide changes when placeholders may
be introduced or restored dynamically:

```js
const renderIcons = () => window.lucide?.createIcons({
  attrs: {
    width: 28,
    height: 28,
    "stroke-width": 1.8
  }
});

deck.on("ready", renderIcons);
deck.on("slidechanged", renderIcons);
```

If all static placeholders are rendered once after `deck.initialize()` resolves,
a slide-change handler may be unnecessary. Do not repeatedly render without a
reason.

## Visual Consistency

- Use one standard size and stroke width for normal slide icons.
- Add a larger size only for a true focal icon.
- Let icons inherit `currentColor`; use the semantic accent token where needed.
- In flex layouts, apply `flex: 0 0 auto` to prevent icon distortion.
- Keep the same icon for the same meaning and different icons for distinct meanings.
- Choose universal symbols with a direct conceptual connection; avoid visual puns.
- Do not use icons to fill arbitrary empty space.

## Accessibility

Lucide icons are hidden from assistive technology by default in current builds,
but make intent explicit in authored placeholders where practical.

Decorative icon beside visible text:

```html
<div class="signal">
  <i data-lucide="calendar-days" aria-hidden="true"></i>
  <span>Today's meetings and focus windows</span>
</div>
```

Do not rely on an icon alone for unfamiliar actions or concepts. Provide visible
text. If a standalone icon carries meaning, label the semantic wrapper or add
reliable visually hidden text rather than depending on the SVG title.

For an icon button, put the accessible name on the button, not the SVG:

```html
<button type="button" aria-label="Open speaker notes">
  <i data-lucide="notebook-tabs" aria-hidden="true"></i>
</button>
```

Interactive wrappers must be semantic, keyboard focusable, visibly focused, and
at least 44 by 44 CSS pixels. Maintain sufficient contrast and never use icon
shape or color as the sole cue for status.

## Validation

Check that:

- the script loads without network or console errors
- every requested icon name exists in the pinned version
- placeholders become SVGs after Reveal initializes
- icons remain visible and aligned on every slide and fragment state
- decorative icons are hidden from assistive technology
- meaningful or interactive icons have visible text or an accessible wrapper
- no Font Awesome dependency remains unless the user explicitly required it