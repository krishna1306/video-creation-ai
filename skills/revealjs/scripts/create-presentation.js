#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const REVEAL_VERSION = '6.0.2';
const LUCIDE_VERSION = '0.468.0';
const BASE_STYLES_PATH = path.join(__dirname, '..', 'references', 'base-styles.css');

function parseArgs(args) {
  const options = {
    slides: null,
    structure: null,
    output: 'presentation.html',
    title: 'Presentation',
    stylesFile: 'styles.css'
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === '--slides' || arg === '-s') {
      options.slides = Number.parseInt(args[++index], 10);
    } else if (arg === '--structure') {
      options.structure = args[++index].split(',').map((value) =>
        value === 'd' ? 'd' : Number.parseInt(value, 10));
    } else if (arg === '--output' || arg === '-o') {
      options.output = args[++index];
    } else if (arg === '--title') {
      options.title = args[++index];
    } else if (arg === '--styles') {
      options.stylesFile = args[++index];
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return options;
}

function printHelp() {
  console.log(`
create-presentation.js - Generate a reveal.js presentation scaffold

Usage: node create-presentation.js [options]

Options:
  --slides, -s <num>    Number of horizontal slides
  --structure <list>    Comma-separated slides, vertical-stack sizes, and d dividers
                        Example: "1,1,d,3,1"
  --output, -o <file>   Output HTML filename (default: presentation.html)
  --title <text>        Presentation title (default: Presentation)
  --styles <file>       CSS filename (default: styles.css)
  --help, -h            Show this help
`);
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  })[character]);
}

function slideMarkup(id, label, title, className = '') {
  const classes = className ? ` class="${className}"` : '';
  return `      <section id="${id}"${classes}>
        <div class="frame">
          <p class="label">${label}</p>
          <h2 class="slide-title">${title}</h2>
          <p class="dek">Replace this text with evidence that supports the slide title.</p>
        </div>
        <aside class="notes">0:45. State the claim, show the evidence, and explain why it matters.</aside>
      </section>`;
}

function generateSlides(structure, presentationTitle) {
  const output = [];
  let horizontalIndex = 1;
  let dividerIndex = 1;

  for (const item of structure) {
    if (item === 'd') {
      output.push(`      <section id="divider-${dividerIndex}">
        <div class="frame frame--center">
          <p class="label">Section ${String(dividerIndex).padStart(2, '0')}</p>
          <h2 class="title">Section title</h2>
        </div>
        <aside class="notes">0:15. Name the next section and connect it to the previous idea.</aside>
      </section>`);
      dividerIndex += 1;
    } else if (item === 1 && horizontalIndex === 1) {
      output.push(`      <section id="title">
        <div class="frame frame--center">
          <p class="eyebrow">Presentation</p>
          <h1 class="title">${escapeHtml(presentationTitle)}</h1>
          <p class="dek">A concise statement of what the audience will understand or do.</p>
        </div>
        <aside class="notes">0:30. Set the context and state the audience promise.</aside>
      </section>`);
    } else if (item === 1) {
      output.push(slideMarkup(`slide-${horizontalIndex}`, 'Key point', `Slide ${horizontalIndex} title`));
    } else {
      const verticalSlides = [];
      for (let verticalIndex = 1; verticalIndex <= item; verticalIndex += 1) {
        verticalSlides.push(slideMarkup(
          `slide-${horizontalIndex}-${verticalIndex}`,
          `Detail ${verticalIndex}`,
          `Slide ${horizontalIndex}.${verticalIndex} title`
        ).replace(/^      /gm, '        '));
      }
      output.push(`      <section>
${verticalSlides.join('\n')}
      </section>`);
    }
    horizontalIndex += 1;
  }

  return output.join('\n');
}

function generateHtml(options) {
  const title = escapeHtml(options.title);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/dist/reveal.css">
  <link rel="stylesheet" href="${options.stylesFile}">
</head>
<body>
  <div class="reveal">
    <div class="slides">
${generateSlides(options.structure, options.title)}
    </div>
  </div>
  <script src="https://unpkg.com/lucide@${LUCIDE_VERSION}/dist/umd/lucide.js"></script>
  <script type="module">
    import Reveal from "https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/dist/reveal.mjs";
    import RevealNotes from "https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/dist/plugin/notes.mjs";

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

    const renderIcons = () => window.lucide?.createIcons({
      attrs: { width: 28, height: 28, "stroke-width": 1.8 }
    });

    deck.on("ready", renderIcons);
    deck.on("slidechanged", renderIcons);
    deck.initialize();
  </script>
</body>
</html>
`;
}

function validateOptions(options) {
  if (options.slides !== null && options.structure !== null) {
    throw new Error('Cannot use both --slides and --structure.');
  }

  if (options.slides !== null) {
    if (!Number.isInteger(options.slides) || options.slides < 1) {
      throw new Error('Slide count must be a positive integer.');
    }
    options.structure = Array(options.slides).fill(1);
  } else if (options.structure === null) {
    options.structure = Array(5).fill(1);
  }

  if (options.structure.some((item) => item !== 'd' && (!Number.isInteger(item) || item < 1))) {
    throw new Error('Structure values must be positive integers or "d".');
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  try {
    validateOptions(options);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }

  const outputDirectory = path.dirname(options.output);
  fs.mkdirSync(outputDirectory, { recursive: true });
  fs.writeFileSync(options.output, generateHtml(options));

  const stylesPath = path.join(outputDirectory, options.stylesFile);
  if (!fs.existsSync(stylesPath)) {
    fs.mkdirSync(path.dirname(stylesPath), { recursive: true });
    fs.copyFileSync(BASE_STYLES_PATH, stylesPath);
  }

  const slideCount = options.structure.reduce((total, item) => total + (item === 'd' ? 1 : item), 0);
  console.log(`Created ${options.output} with ${slideCount} slides.`);
  console.log(`Customize semantic tokens and layouts in ${stylesPath}.`);
}

main();