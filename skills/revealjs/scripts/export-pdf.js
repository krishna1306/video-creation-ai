#!/usr/bin/env node

/**
 * Export a RevealJS presentation to PDF using Decktape
 * 
 * Usage:
 *   node export-pdf.js <presentation.html> [output.pdf]
 *   node export-pdf.js presentation.html
 *   node export-pdf.js presentation.html my-slides.pdf
 * 
 * Options:
 *   --with-screenshots    Also generate PNG screenshots in a timestamped folder
 */

const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

// Parse arguments
const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
  console.log(`
Export RevealJS Presentation to PDF

Usage:
  node export-pdf.js <presentation.html> [output.pdf] [options]

Arguments:
  presentation.html    Path to the HTML presentation file (required)
  output.pdf          Output PDF filename (optional, defaults to same name as HTML)

Options:
  --with-screenshots  Also generate PNG screenshots in screenshots/ folder
  --help, -h          Show this help message

Examples:
  node export-pdf.js presentation.html
  node export-pdf.js presentation.html slides.pdf
  node export-pdf.js presentation.html --with-screenshots
  node export-pdf.js presentation.html my-deck.pdf --with-screenshots
`);
  process.exit(0);
}

// Extract options
const withScreenshots = args.includes('--with-screenshots');
const fileArgs = args.filter(arg => !arg.startsWith('--'));

if (fileArgs.length === 0) {
  console.error('Error: No presentation file specified');
  console.error('Usage: node export-pdf.js <presentation.html> [output.pdf]');
  process.exit(1);
}

const inputFile = fileArgs[0];
const outputFile = fileArgs[1] || inputFile.replace(/\.html?$/i, '.pdf');

// Validate input file exists
if (!fs.existsSync(inputFile)) {
  console.error(`Error: Input file not found: ${inputFile}`);
  process.exit(1);
}

// Get absolute path for the input file
const absoluteInputPath = path.resolve(inputFile);
const inputDir = path.dirname(absoluteInputPath);
const absoluteOutputPath = path.resolve(outputFile);

console.log(`\n📄 Exporting presentation to PDF...`);
console.log(`   Input:  ${inputFile}`);
console.log(`   Output: ${outputFile}`);

// DeckTape captures Reveal slides directly; do not enable Reveal's print view.
const commandArgs = [
  'decktape',
  'reveal',
  pathToFileURL(absoluteInputPath).href,
  absoluteOutputPath
];

// Add screenshots if requested
if (withScreenshots) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const screenshotsDir = path.join(inputDir, 'screenshots', timestamp);
  
  // Create screenshots directory
  fs.mkdirSync(screenshotsDir, { recursive: true });
  
  commandArgs.push('--screenshots', '--screenshots-directory', screenshotsDir);
  console.log(`   Screenshots: ${path.relative(process.cwd(), screenshotsDir)}/`);
}

console.log('');

try {
  // Execute decktape
  execFileSync('npx', commandArgs, {
    stdio: 'inherit',
    cwd: inputDir
  });
  
  console.log(`\n✅ PDF exported successfully!`);
  console.log(`   ${outputFile}`);
  
  if (withScreenshots) {
    console.log(`\n📸 Screenshots saved in screenshots/ folder`);
  }
  
  // Show file size
  const stats = fs.statSync(absoluteOutputPath);
  const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
  console.log(`   File size: ${fileSizeMB} MB`);
  
} catch (error) {
  console.error('\n❌ Error exporting PDF');
  console.error(error.message);
  process.exit(1);
}
