#!/usr/bin/env python3
"""SITECRAFT Level 2.5 rendered check (optional). A checker, not a lock.
Loads a page in a real browser through Playwright at 320, 390 and 1440 px wide and reports:
  overflow (page wider than the viewport), small tap targets (under 24 px), focus after Tab
  (focus moves and shows an indicator), console errors, and axe-core violations.
Needs: `pip install playwright` and a Chromium or Chrome (`playwright install chromium`, or pass --chrome PATH).
axe-core is not bundled: pass --axe PATH to axe.min.js (npm i axe-core). Without it the axe step says "not run".
If Playwright is missing the script says so and exits 3: report the run as Level 2, not 2.5.
Usage: render_check.py PAGE.html|URL [--widths 320,390,1440] [--axe PATH] [--chrome PATH] [--min-target 24]
Exit 0 clean, 1 findings, 3 cannot render (nothing was verified)."""
import sys, os, argparse, json, pathlib

TARGETS_JS = """(min) => { const out = [];
  for (const el of document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[role=button],[role=link],summary')) {
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || (r.width === 0 && r.height === 0)) continue;
    if (r.width < min || r.height < min) out.push({tag: el.tagName.toLowerCase(), text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 30), w: Math.round(r.width), h: Math.round(r.height)}); }
  return out; }"""
FOCUS_JS = """() => { const el = document.activeElement; if (!el || el === document.body) return null;
  const cs = getComputedStyle(el); const outline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
  const shadow = cs.boxShadow && cs.boxShadow !== 'none';
  return {tag: el.tagName.toLowerCase(), indicator: !!(outline || shadow)}; }"""

def check_width(pw_page, width, min_target, axe_src):
    f = []; errors = []
    pw_page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pw_page.on('pageerror', lambda e: errors.append(str(e)))
    pw_page.set_viewport_size({'width': width, 'height': 800}); pw_page.reload(); pw_page.wait_for_load_state('load')
    sw = pw_page.evaluate('document.documentElement.scrollWidth')
    if sw > width + 1: f.append(('overflow', 'error', f'page is {sw}px wide in a {width}px viewport'))
    for t in pw_page.evaluate(TARGETS_JS, min_target):
        f.append(('tap-target', 'error', f'{t["tag"]} "{t["text"]}" is {t["w"]}x{t["h"]}px (under {min_target}px)'))
    pw_page.keyboard.press('Tab'); fo = pw_page.evaluate(FOCUS_JS)
    if fo is None: f.append(('focus', 'error', 'Tab did not move focus to any element'))
    elif not fo['indicator']: f.append(('focus', 'error', f'focused <{fo["tag"]}> shows no outline or box-shadow'))
    for e in errors: f.append(('console', 'error', e[:160]))
    if axe_src:
        pw_page.evaluate(axe_src)
        for v in pw_page.evaluate('async () => (await axe.run()).violations.map(v => ({id: v.id, impact: v.impact, n: v.nodes.length}))'):
            f.append(('axe', 'error' if v['impact'] in ('serious', 'critical') else 'warn', f'{v["id"]} ({v["impact"]}, {v["n"]} node(s))'))
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('page'); ap.add_argument('--widths', default='320,390,1440')
    ap.add_argument('--axe'); ap.add_argument('--chrome'); ap.add_argument('--min-target', type=int, default=24)
    a = ap.parse_args()
    try: from playwright.sync_api import sync_playwright
    except ImportError: print('NOT RUN: Playwright is not installed (pip install playwright). Nothing was verified; report Level 2, not 2.5.'); sys.exit(3)
    url = a.page if '://' in a.page else pathlib.Path(a.page).resolve().as_uri()
    axe_src = open(a.axe, encoding='utf-8').read() if a.axe else None
    if not axe_src: print('NOTE: axe-core not run (no --axe PATH).')
    bad = 0
    try:
        with sync_playwright() as p:
            kw = {'executable_path': a.chrome} if a.chrome else {}
            try: b = p.chromium.launch(**kw)
            except Exception:
                if a.chrome: raise
                b = p.chromium.launch(channel='chrome')   # fall back to an installed Google Chrome
            for w in [int(x) for x in a.widths.split(',')]:
                pg = b.new_page(); pg.goto(url)
                fs = check_width(pg, w, a.min_target, axe_src); pg.close()
                for rule, sev, msg in fs:
                    print(f'{sev.upper():5} {w}px [{rule}] {msg}'); bad += sev == 'error'
            b.close()
    except Exception as e: print(f'NOT RUN: could not start or drive the browser ({str(e).splitlines()[0][:150]}). Nothing was verified.'); sys.exit(3)
    print(f'{bad} error(s) across {a.widths}'); sys.exit(1 if bad else 0)
if __name__ == '__main__': main()
