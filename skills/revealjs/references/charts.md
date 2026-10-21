# Charts in Reveal.js

Charts are optional. Reveal.js does not include a core chart plugin, so do not
load Chart.js or a community integration in decks without charts.

## Choose the Visual First

Use a chart only when the audience needs to compare magnitude, distribution,
trend, relationship, or composition. Use a large number, short table, or direct
annotation when that communicates the point faster.

Choose chart type from the comparison:

- bars for category comparison
- lines for change over an ordered interval
- scatter plots for relationships
- dot plots for compact ranking or comparison
- pie/doughnut only for a small, unmistakable part-to-whole relationship

Write the conclusion in the slide title. Label the evidence directly where
possible and remove nonessential gridlines, legends, effects, and animation.

## Preferred Integration

Prefer Chart.js directly over a Reveal-specific wrapper unless existing deck
markup already depends on a wrapper. Pin an exact tested Chart.js version:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
```

Initialize charts after Reveal is ready. Store chart instances and resize or
update the current chart on `slidechanged` when hidden-slide layout affects it.
Disable or shorten chart animation for reduced motion and PDF export.

```js
let chart;

deck.on("ready", () => {
  const context = document.querySelector("#trend-chart");
  chart = new Chart(context, chartConfig);
});

deck.on("slidechanged", () => chart?.resize());
```

If a community Reveal chart plugin is genuinely useful, confirm the dependency
with the user, verify maintenance and Reveal compatibility, review its license,
and pin both it and Chart.js to exact versions. Never use `@latest`.

## Sizing

Give the chart a bounded responsive container rather than sizing the canvas
itself:

```css
.chart-frame {
  position: relative;
  min-width: 0;
  min-height: 0;
  height: 11em;
}
```

Set `maintainAspectRatio: false` when the chart should fill that container.
Use a full-width chart when the pattern is the evidence. Use an asymmetric split
when a short annotation or comparison must remain beside it. Avoid dashboard
grids unless the audience truly needs simultaneous metric comparison.

## Accessibility and Integrity

- Include a concise textual takeaway and source.
- Do not rely on color alone; use labels, patterns, shape, or line style.
- Keep axes honest and units explicit.
- Avoid truncated axes unless the analytical reason is clear and disclosed.
- Provide a table or equivalent text when the data itself must be accessible.
- Ensure labels and data marks have sufficient contrast at presentation size.

## Validation

Verify the chart on first load, direct navigation by hash, slide changes,
viewport resize, reduced motion, and PDF export when requested. Check for canvas
overflow and browser console errors.

`scripts/check-charts.js` validates the legacy `canvas[data-chart]` comment-based
plugin format only. Do not use it as validation for direct Chart.js instances.