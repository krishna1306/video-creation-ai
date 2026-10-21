"""Inspect a reveal.js deck's animation steps and its voice-over cue markers.

For every top-level slide, lists each fragment step in the order Reveal plays it, with the
text that step reveals, then the slide's "VO:" script (from speaker notes) and whether the
number of "[>]" markers matches the number of steps.
Usage: ~/.venvs/vidcast/bin/python inspect_deck.py deck.html [--json]
Exit code 1 if any narrated slide's marker count differs from its step count.
"""

import asyncio
import functools
import json
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

MARKER = "[>]"

STEPS_JS = r"""
() => [...document.querySelectorAll('.reveal .slides > section')].map((s, i) => {
  const groups = new Map();
  [...s.querySelectorAll('.fragment')].forEach((f, j) => {
    const k = f.getAttribute('data-fragment-index') ?? ('n' + j);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(f);
  });
  const order = [...groups.keys()].sort((a, b) => (+a) - (+b));
  const text = el => (el.innerText || el.textContent || el.getAttribute('aria-label') || el.tagName.toLowerCase()).replace(/\s+/g, ' ').trim();
  const steps = order.map(k => groups.get(k).map(f => `${[...f.classList].filter(c => c !== 'fragment' && c !== 'visible').join('.') || 'fade'}: ${text(f).slice(0, 70)}`));
  const notes = s.querySelector('aside.notes')?.textContent || '';
  const m = notes.match(/VO:\s*"([\s\S]*)"\s*$/);
  const title = (s.querySelector('h1,h2')?.textContent || '').replace(/\s+/g, ' ').trim();
  return { slide: i + 1, title, steps, vo: m ? m[1].trim() : '' };
})
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


async def inspect(deck: Path):
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(deck.parent)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            await page.goto(f"http://127.0.0.1:{httpd.server_port}/{quote(deck.name)}")
            await page.wait_for_selector(".reveal.ready")
            slides = await page.evaluate(STEPS_JS)
            await browser.close()
    finally:
        httpd.shutdown()
    return slides


def main():
    deck = Path(sys.argv[1]).resolve()
    slides = asyncio.run(inspect(deck))
    for s in slides:
        s["markers"] = s["vo"].count(MARKER)
        s["ok"] = not s["vo"] or s["markers"] == len(s["steps"])
    if "--json" in sys.argv:
        print(json.dumps(slides, indent=1))
    else:
        for s in slides:
            status = "ok" if s["ok"] else f"MISMATCH: {len(s['steps'])} steps, {s['markers']} markers"
            if not s["vo"]:
                status = f"no VO ({len(s['steps'])} steps will fire with no narration)" if s["steps"] else "no VO"
            print(f"\nSlide {s['slide']}: {s['title']}  [{status}]")
            for n, group in enumerate(s["steps"], 1):
                print(f"  step {n}: " + " | ".join(group))
            if s["vo"]:
                print(f"  VO: {s['vo']}")
    sys.exit(0 if all(s["ok"] for s in slides) else 1)


if __name__ == "__main__":
    main()
