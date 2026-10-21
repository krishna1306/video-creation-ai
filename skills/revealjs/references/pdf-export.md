# PDF Export

Reveal has a browser print mode, while the bundled helper uses DeckTape. Choose
one workflow and do not combine their URL modes.

## Browser Print Mode

1. Serve the deck over HTTP.
2. Open `http://localhost:8000/?print-pdf` in Chrome or Chromium.
3. Print with landscape layout, no margins, and background graphics enabled.

Reveal reads the authored presentation size and creates print pages. A tall
slide may span multiple pages; cap it with `pdfMaxPagesPerSlide` when needed.

Fragments print as separate incremental pages by default. Set
`pdfSeparateFragments: false` to print their final visible state on one page.
Include notes with `showNotes: true`, or put notes on their own pages with
`showNotes: "separate-page"`. Enable `slideNumber` and a print-compatible
`showSlideNumber` value when the PDF needs page numbers.

## DeckTape Helper

```bash
node scripts/export-pdf.js presentation.html
node scripts/export-pdf.js presentation.html handout.pdf
node scripts/export-pdf.js presentation.html --with-screenshots
```

DeckTape's Reveal adapter navigates and captures slides individually. The helper
therefore does not append `?print-pdf`; DeckTape explicitly warns against using
Reveal's print view during this workflow. Screenshots are written beneath a
timestamped `screenshots/` directory.

The helper invokes `npx decktape`. Confirm dependency installation is acceptable
before the first run, and use a pinned project dependency for reproducible CI.

## Validation

- Wait for web fonts, images, charts, syntax highlighting, and async data.
- Check that the export machine has the intended fonts; do not assume a branded
	font is installed.
- Inspect fragment policy, notes, page count, backgrounds, links, and contrast.
- Optimize source images when the result is too large.
- For DeckTape layout differences, set an explicit viewport with its `--size`
	option or serve the deck over HTTP when `file://` restrictions interfere.

Official references:

- https://revealjs.com/pdf-export/
- https://github.com/astefanutti/decktape
