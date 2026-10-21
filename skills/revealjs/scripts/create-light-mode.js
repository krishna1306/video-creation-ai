#!/usr/bin/env node

/**
 * Convert a dark mode presentation to light mode
 * 
 * Usage:
 *   node create-light-mode.js <presentation.html>
 * 
 * This will:
 * 1. Copy base-styles-light.css as styles-light.css
 * 2. Create a light mode HTML variant (presentation-light.html)
 * 3. Update the HTML to use the light stylesheet
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
  console.log(`
Create Light Mode Variant

Usage:
  node create-light-mode.js <presentation.html>

This creates:
  - styles-light.css (light mode stylesheet)
  - presentation-light.html (light mode HTML variant)

Example:
  node create-light-mode.js presentation.html
  
This will create:
  - presentation-light.html (links to styles-light.css)
  - styles-light.css (light mode colors)

You can then open presentation-light.html for the light version.
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
const outputHtml = path.join(inputDir, `${inputBasename}-light.html`);
const outputCss = path.join(inputDir, 'styles-light.css');

// Find the base-styles-light.css in the skill directory
const scriptDir = __dirname;
const skillDir = path.dirname(scriptDir);
const lightStylesSource = path.join(skillDir, 'references', 'base-styles-light.css');

if (!fs.existsSync(lightStylesSource)) {
  console.error('Error: base-styles-light.css not found in skill references');
  process.exit(1);
}

console.log('\n☀️  Creating light mode variant...\n');

// Read the HTML and identify the deck's local stylesheet.
let htmlContent = fs.readFileSync(inputFile, 'utf-8');
const stylesheetMatches = [...htmlContent.matchAll(/<link\s+rel="stylesheet"\s+href="([^"]+\.css)">/g)];
const localStylesheet = stylesheetMatches.find((match) => !/^https?:\/\//.test(match[1]));

if (!localStylesheet) {
  console.error('Error: Could not find a local presentation stylesheet');
  process.exit(1);
}

const overlay = fs.readFileSync(lightStylesSource, 'utf-8')
  .replace('./styles.css', localStylesheet[1]);
fs.writeFileSync(outputCss, overlay);
console.log(`✅ Created ${path.basename(outputCss)}`);

htmlContent = htmlContent.replace(localStylesheet[0], '<link rel="stylesheet" href="styles-light.css">');

// Update title to indicate light mode
htmlContent = htmlContent.replace(
  /<title>(.*?)<\/title>/,
  '<title>$1 (Light Mode)</title>'
);

// Write light mode HTML
fs.writeFileSync(outputHtml, htmlContent);
console.log(`✅ Created ${path.basename(outputHtml)}`);

console.log(`\n🎨 Light mode variant created successfully!`);
console.log(`\nTo view:`);
console.log(`  Dark mode:  open ${inputFile}`);
console.log(`  Light mode: open ${outputHtml}`);
console.log(`\nBoth files share the same content, just different stylesheets.`);
