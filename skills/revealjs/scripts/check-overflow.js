/** Checks reveal.js slides for content overflow using Puppeteer */
const puppeteer = require('puppeteer');
const fs = require('fs');
const http = require('http');
const path = require('path');

const MIME_TYPES = {
  '.css': 'text/css',
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp'
};

function createStaticServer(rootDirectory) {
  return http.createServer((request, response) => {
    const requestPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const relativePath = requestPath === '/' ? '/index.html' : requestPath;
    const filePath = path.resolve(rootDirectory, `.${relativePath}`);

    if (!filePath.startsWith(`${path.resolve(rootDirectory)}${path.sep}`)) {
      response.writeHead(403).end('Forbidden');
      return;
    }

    fs.readFile(filePath, (error, content) => {
      if (error) {
        response.writeHead(error.code === 'ENOENT' ? 404 : 500).end(error.message);
        return;
      }
      response.writeHead(200, { 'Content-Type': MIME_TYPES[path.extname(filePath)] || 'application/octet-stream' });
      response.end(content);
    });
  });
}

async function checkSlideOverflow(htmlPath) {
  const absolutePath = path.resolve(htmlPath);
  const rootDirectory = path.dirname(absolutePath);
  const server = createStaticServer(rootDirectory);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  const pageUrl = `http://127.0.0.1:${port}/${encodeURIComponent(path.basename(absolutePath))}`;

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set viewport to standard presentation size
  await page.setViewport({ width: 1920, height: 1080 });

  try {
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => document.querySelector('.reveal.ready'), { timeout: 20000 });

    const results = await page.evaluate(() => {
    const allSlides = document.querySelectorAll('.slides > section, .slides > section > section');
    const slides = [];

    allSlides.forEach((slide, i) => {
      // Skip stack parents (sections that contain nested sections)
      const isStackParent = slide.parentElement.classList.contains('slides') && slide.querySelector('section');
      if (isStackParent) return;

      const id = slide.id || `slide-${i}`;
      const scrollHeight = slide.scrollHeight;
      const scrollWidth = slide.scrollWidth;
      const clientHeight = slide.clientHeight;
      const clientWidth = slide.clientWidth;

      const hasVerticalOverflow = scrollHeight > clientHeight;
      const hasHorizontalOverflow = scrollWidth > clientWidth;

      slides.push({
        index: i,
        id,
        hasOverflow: hasVerticalOverflow || hasHorizontalOverflow,
        hasVerticalOverflow,
        hasHorizontalOverflow,
        dimensions: {
          scrollHeight,
          clientHeight,
          scrollWidth,
          clientWidth,
          verticalDiff: scrollHeight - clientHeight,
          horizontalDiff: scrollWidth - clientWidth
        }
      });
    });

    return slides;
    });

    return results;
  } finally {
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

async function main() {
  const htmlPath = process.argv[2];
  if (!htmlPath) {
    console.error('Usage: node check-overflow.js <path-to-html>');
    process.exit(1);
  }

  console.log(`Checking slides for overflow: ${htmlPath}\n`);

  const results = await checkSlideOverflow(htmlPath);

  let hasAnyOverflow = false;

  for (const slide of results) {
    if (slide.hasOverflow) {
      hasAnyOverflow = true;
      console.log(`OVERFLOW: Slide ${slide.index} (${slide.id})`);
      if (slide.hasVerticalOverflow) {
        console.log(`  - Vertical overflow: ${slide.dimensions.verticalDiff}px (content: ${slide.dimensions.scrollHeight}px, container: ${slide.dimensions.clientHeight}px)`);
      }
      if (slide.hasHorizontalOverflow) {
        console.log(`  - Horizontal overflow: ${slide.dimensions.horizontalDiff}px (content: ${slide.dimensions.scrollWidth}px, container: ${slide.dimensions.clientWidth}px)`);
      }
    }
  }

  if (!hasAnyOverflow) {
    console.log('No overflow detected on any slides.');
  }

  console.log(`\nTotal slides checked: ${results.length}`);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
