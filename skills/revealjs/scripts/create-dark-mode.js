#!/usr/bin/env node

/**
 * Convert a presentation to dark mode or create a dark mode variant
 * 
 * Usage:
 *   node create-dark-mode.js <presentation.html>
 * 
 * This will:
 * 1. Copy base-styles-dark.css as styles-dark.css
 * 2. Create a dark mode HTML variant (presentation-dark.html)
 * 3. Update the HTML to use the dark stylesheet
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
  console.log(`
Create Dark Mode Variant

Usage:
  node create-dark-mode.js <presentation.html>

This creates:
  - styles-dark.css (dark mode stylesheet)
  - presentation-dark.html (dark mode HTML variant)

Example:
  node create-dark-mode.js presentation.html
  
This will create:
  - presentation-dark.html (links to styles-dark.css)
  - styles-dark.css (dark mode colors)

You can then open presentation-dark.html for the dark version.
`);
  process.exit(0);
}

const inputFile = args[0];

if (!fs.existsSync(inputFile)) {
  console.error(`Error: File not found: ${inputFile}`);
  process.exit(1);
}

const inputDir = path.dirname(inputFile);
const inputBasename = path.basename(inputFile, '.html');
const outputHtml = path.join(inputDir, `${inputBasename}-dark.html`);
const outputCss = path.join(inputDir, 'styles-dark.css');

// Find the base-styles-dark.css in the skill directory
const scriptDir = __dirname;
const skillDir = path.dirname(scriptDir);
const darkStylesSource = path.join(skillDir, 'references', 'base-styles-dark.css');

if (!fs.existsSync(darkStylesSource)) {
  console.error('Error: base-styles-dark.css not found in skill references');
  process.exit(1);
}

console.log('\n🌙 Creating dark mode variant...\n');

// Read the HTML and identify the deck's local stylesheet.
let htmlContent = fs.readFileSync(inputFile, 'utf-8');
const stylesheetMatches = [...htmlContent.matchAll(/<link\s+rel="stylesheet"\s+href="([^"]+\.css)">/g)];
const localStylesheet = stylesheetMatches.find((match) => !/^https?:\/\//.test(match[1]));

if (!localStylesheet) {
  console.error('Error: Could not find a local presentation stylesheet');
  process.exit(1);
}

const overlay = fs.readFileSync(darkStylesSource, 'utf-8')
  .replace('./styles.css', localStylesheet[1]);
fs.writeFileSync(outputCss, overlay);
console.log(`✅ Created ${path.basename(outputCss)}`);

htmlContent = htmlContent.replace(localStylesheet[0], '<link rel="stylesheet" href="styles-dark.css">');

// Update title to indicate dark mode
htmlContent = htmlContent.replace(
  /<title>(.*?)<\/title>/,
  '<title>$1 (Dark Mode)</title>'
);

// Write dark mode HTML
fs.writeFileSync(outputHtml, htmlContent);
console.log(`✅ Created ${path.basename(outputHtml)}`);

console.log(`\n🎨 Dark mode variant created successfully!`);
console.log(`\nTo view:`);
console.log(`  Light mode: open ${inputFile}`);
console.log(`  Dark mode:  open ${outputHtml}`);
console.log(`\nBoth files share the same content, just different stylesheets.`);
