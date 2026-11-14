#!/usr/bin/env python3
"""Write site/data.js from the latest release and render the README images with Playwright."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
rel = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(p for p in (ROOT / 'results').glob('v*') if (p / 'summary.json').exists())[-1]
S = json.loads((rel / 'summary.json').read_text())
(ROOT / 'site/data.js').write_text('window.PHONEBENCH = ' + json.dumps(S) + ';\n')

from playwright.sync_api import sync_playwright  # noqa: E402

SHOTS = {'leaderboard': '#cap-leaderboard', 'speed': '#cap-speed', 'failures': '#cap-failures', 'matrix': '#cap-matrix'}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1240, 'height': 900}, device_scale_factor=2, color_scheme='dark')
    pg.goto((ROOT / 'site/index.html').as_uri() + '?render')
    pg.wait_for_timeout(400)
    for name, sel in SHOTS.items():
        box = pg.locator(sel).bounding_box()
        pad = 24
        pg.screenshot(path=str(ROOT / f'site/assets/{name}.png'), clip={'x': max(0, box['x'] - pad), 'y': max(0, box['y'] - pad), 'width': box['width'] + 2 * pad, 'height': box['height'] + 2 * pad}, full_page=True)
    pg.set_viewport_size({'width': 390, 'height': 844})
    pg.goto((ROOT / 'site/index.html').as_uri())
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(ROOT / 'site/.render-mobile.png'), full_page=True)
    b.close()
print('rendered', ', '.join(SHOTS), 'from', rel.name)
