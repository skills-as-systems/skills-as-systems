#!/usr/bin/env python3
"""SITECRAFT deterministic checker (v2 prototype). No network, no LLM, stdlib only.
Scans .html/.css files for objective, statically checkable issues and writes a
JSON gate-log entry. Rules are our own. Exit 1 if any 'error' finding.
Usage: sitecraft_check.py PATH [--sheet design-sheet.json] [--log gate-log.json] [--ban "word,word"]
"""
import sys, re, json, os, argparse, datetime
from html.parser import HTMLParser

NAMED = {'white': '#ffffff', 'black': '#000000', 'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff', 'yellow': '#ffff00',
         'gray': '#808080', 'grey': '#808080', 'silver': '#c0c0c0', 'orange': '#ffa500', 'purple': '#800080', 'navy': '#000080',
         'teal': '#008080', 'maroon': '#800000', 'olive': '#808000', 'lime': '#00ff00', 'aqua': '#00ffff', 'cyan': '#00ffff',
         'fuchsia': '#ff00ff', 'magenta': '#ff00ff', 'pink': '#ffc0cb', 'brown': '#a52a2a', 'gold': '#ffd700', 'lightgray': '#d3d3d3',
         'lightgrey': '#d3d3d3', 'darkgray': '#a9a9a9', 'darkgrey': '#a9a9a9', 'dimgray': '#696969', 'whitesmoke': '#f5f5f5'}
COLOR = (r'(#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|(?<![-\w])(?:' + '|'.join(NAMED) + r')(?![-\w]))')

def to_hex(s):
    """Colour string -> '#rrggbb', or None when it cannot be resolved (alpha < 1, odd syntax)."""
    s = s.strip().lower()
    if s.startswith('#'): return s if len(s) in (4, 7) else None
    if s in NAMED: return NAMED[s]
    m = re.fullmatch(r'(rgb|hsl)a?\(([^)]*)\)', s)
    if not m: return None
    parts = [x for x in re.split(r'[\s,/]+', m.group(2).strip()) if x]
    if len(parts) == 4:
        a = parts[3]; av = float(a[:-1]) / 100 if a.endswith('%') else float(a)
        if av < 1: return None
    if len(parts) < 3: return None
    try:
        if m.group(1) == 'rgb':
            v = [round(float(x[:-1]) * 2.55) if x.endswith('%') else round(float(x)) for x in parts[:3]]
        else:
            import colorsys
            h = float(parts[0].replace('deg', '')) / 360 % 1; sat = float(parts[1].rstrip('%')) / 100; l = float(parts[2].rstrip('%')) / 100
            v = [round(x * 255) for x in colorsys.hls_to_rgb(h, l, sat)]
    except ValueError: return None
    return '#%02x%02x%02x' % tuple(max(0, min(255, x)) for x in v)

def lum(hexc):
    h = hexc.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.f = []; self.labels_for = set(); self.inputs = []; self.has_lang = False
        self.has_viewport = False; self.h = []; self.title = False; self.in_a = False; self.a_text = ''; self.a_aria = False
        self.ids = {}; self.in_btn = False; self.btn_text = ''; self.btn_named = False
    def add(self, rule, sev, msg): self.f.append((rule, sev, msg, self.getpos()[0]))
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html' and a.get('lang'): self.has_lang = True
        if tag == 'meta' and a.get('name') == 'viewport': self.has_viewport = True
        if tag == 'title': self.title = True
        if a.get('id'):
            if a['id'] in self.ids: self.add('duplicate-id', 'error', f'id "{a["id"]}" is used again (first on line {self.ids[a["id"]]})')
            else: self.ids[a['id']] = self.getpos()[0]
        if tag == 'button': self.in_btn = True; self.btn_text = ''; self.btn_named = bool(a.get('aria-label', '').strip() or a.get('aria-labelledby') or a.get('title', '').strip())
        if tag == 'input' and a.get('type') == 'image' and not a.get('alt', '').strip() and not a.get('aria-label'): self.add('input-image-alt', 'error', 'image input without alt text')
        if tag == 'input' and a.get('type') in ('submit', 'button', 'reset') and not (a.get('value', '').strip() or a.get('aria-label') or a.get('title')) and a.get('type') != 'submit': self.add('button-name', 'error', 'input button with no value or label')
        if tag == 'img' and self.in_btn and (a.get('alt', '').strip() or a.get('aria-label')): self.btn_named = True
        if tag == 'img' and 'alt' not in a: self.add('img-alt', 'error', 'img without alt attribute')
        if tag == 'label' and a.get('for'): self.labels_for.add(a['for'])
        if tag == 'input' and a.get('type', 'text') not in ('hidden', 'submit', 'button', 'image'):
            self.inputs.append((a.get('id'), 'aria-label' in a or 'aria-labelledby' in a, self.getpos()[0]))
        if tag in ('h1','h2','h3','h4','h5','h6'): self.h.append((int(tag[1]), self.getpos()[0]))
        if tag == 'a':
            self.in_a = True; self.a_text = ''; self.a_aria = 'aria-label' in a
            if not a.get('href'): self.add('link-href', 'warn', 'anchor without href')
        if tag == 'button' and False: pass
    def handle_endtag(self, tag):
        if tag == 'title': self.title = False
        if tag == 'button':
            if not self.btn_text.strip() and not self.btn_named: self.add('button-name', 'error', 'button with no accessible name')
            self.in_btn = False
        if tag == 'a':
            if not self.a_text.strip() and not self.a_aria: self.add('link-name', 'error', 'link with no accessible name')
            self.in_a = False
    def handle_data(self, d):
        if self.in_a: self.a_text += d
        if self.in_btn: self.btn_text += d

def check_html(src):
    p = P(); p.feed(src)
    if not p.has_lang: p.add('html-lang', 'error', '<html> has no lang attribute')
    if not p.has_viewport: p.add('viewport', 'error', 'no viewport meta tag')
    for i, lab, ln in p.inputs:
        if not (i and i in p.labels_for) and not lab: p.f.append(('input-label', 'error', 'input without label', ln))
    ones = [x for x in p.h if x[0] == 1]
    if len(ones) != 1: p.f.append(('h1-count', 'warn', f'{len(ones)} h1 elements (expect 1)', 1))
    prev = 0
    for lv, ln in p.h:
        if prev and lv > prev+1: p.f.append(('heading-skip', 'warn', f'heading jumps h{prev} to h{lv}', ln))
        prev = lv
    return p.f

CSS_BLOCK = re.compile(r'([^{}]+)\{([^{}]*)\}')

VAR_DEF = re.compile(r'(--[\w-]+)\s*:\s*' + COLOR)
VAR_USE = re.compile(r'var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)')
VARS = {}
PAGE_BG = None

def check_css(src):
    global VARS, PAGE_BG
    f = []
    VARS = dict(VAR_DEF.findall(src))
    PAGE_BG = None
    for sel, body in CSS_BLOCK.findall(src):
        if re.fullmatch(r'\s*(html|body)\s*', sel):
            body2 = VAR_USE.sub(lambda m: VARS.get(m.group(1), m.group(0)), body)
            m = re.search(r'background(?:-color)?\s*:\s*(?:[^;]*?\s)?' + COLOR, body2, re.I)
            if m and to_hex(m.group(1)): PAGE_BG = to_hex(m.group(1))
    if re.search(r'(animation|transition)\s*:', src) and 'prefers-reduced-motion' not in src:
        f.append(('reduced-motion', 'error', 'animation/transition used but no prefers-reduced-motion handling', 1))
    for sel, body in CSS_BLOCK.findall(src):
        line = src[:src.find(body)].count('\n')+1
        if re.search(r'outline\s*:\s*(none|0)\b', body) and ':focus' in sel and not re.search(r'box-shadow|border|outline-offset|background', body):
            f.append(('focus-style', 'error', f'focus style removed with no replacement in "{sel.strip()}"', line))
        body = VAR_USE.sub(lambda m: VARS.get(m.group(1), m.group(0)), body)
        c = re.search(r'(?<![-\w])color\s*:\s*' + COLOR, body, re.I)
        b = re.search(r'background(?:-color)?\s*:\s*(?:[^;]*?\s)?' + COLOR, body, re.I)
        cx = to_hex(c.group(1)) if c else None; bx = to_hex(b.group(1)) if b else None
        okhex = lambda x: x is not None
        if c and b and cx and bx:
            r = ratio(cx, bx)
            if r < 1.05:
                f.append(('hidden-text', 'warn', f'text colour equals its background in "{sel.strip()}" (fine only if it is hidden until a state rule changes the background)', line))
            elif r < 4.5: f.append(('contrast', 'error', f'contrast {r:.2f}:1 below 4.5:1 in "{sel.strip()}"', line))
        elif c and not b and PAGE_BG and cx:
            r = ratio(cx, PAGE_BG)
            if 1.5 <= r < 4.5:
                f.append(('contrast-page', 'warn', f'contrast {r:.2f}:1 against the page background {PAGE_BG} in "{sel.strip()}" (parent background may differ)', line))
        if re.search(r'transition\s*:\s*all\b', body): f.append(('transition-all', 'warn', 'transition: all (animates everything)', line))
        if re.search(r'(cubic-bezier\([^)]*-?\d*\.?\d+\s*,\s*-\d|elastic|bounce)', body, re.I):
            f.append(('bounce-easing', 'warn', 'bounce/elastic style easing', line))
        m = re.search(r'font-size\s*:\s*(\d+)px', body)
        if m and int(m.group(1)) < 12: f.append(('tiny-text', 'warn', f'font-size {m.group(1)}px under 12px', line))
    return f

COLOR_PROPS = re.compile(r'^(?:--[\w-]+|color|background(?:-color)?|border(?:-(?:top|right|bottom|left))?(?:-color)?|outline(?:-color)?|fill|stroke|box-shadow|text-decoration-color|caret-color|accent-color)$')
GENERIC_FONTS = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace', 'ui-rounded', 'inherit', 'initial', 'unset', 'revert', 'emoji', 'math'}
DECL = re.compile(r'([\w-]+)\s*:\s*([^;{}]+)')

def norm_hex(h):
    h = to_hex(h) if h else None
    if h and len(h) == 4: h = '#' + ''.join(c * 2 for c in h[1:])
    return h

def check_tokens(src, sheet):
    """Compare a CSS source against a design-sheet JSON: {"colors": {role: colour}, "fonts": [names], "spacing": [px,...]}.
    Colours and fonts off the sheet are errors; spacing off the scale is a warning. Alpha colours and var() uses are skipped."""
    f = []
    colours = {norm_hex(v) for v in (sheet.get('colors') or {}).values()} - {None}
    fonts = {x.strip().strip('\'"').lower() for x in sheet.get('fonts') or []}
    scale = {float(x) for x in sheet.get('spacing') or []}
    for sel, body in CSS_BLOCK.findall(src):
        line = src[:src.find(body)].count('\n') + 1
        for prop, val in DECL.findall(body):
            prop = prop.lower()
            if colours and COLOR_PROPS.match(prop):
                for m in re.finditer(COLOR, val, re.I):
                    h = norm_hex(m.group(1))
                    if h and h not in colours: f.append(('token-colour', 'error', f'{m.group(1)} ({h}) in "{sel.strip()}" is not a colour in the design sheet', line))
            elif fonts and prop == 'font-family':
                for name in val.split(','):
                    n = name.strip().strip('\'"').lower()
                    if n and n not in GENERIC_FONTS and not n.startswith('var(') and n not in fonts:
                        f.append(('token-font', 'error', f'font "{n}" in "{sel.strip()}" is not in the design sheet', line))
            elif scale and re.match(r'^(margin|padding)(-(top|right|bottom|left|inline|block)(-(start|end))?)?$|^(row-|column-)?gap$', prop):
                for num, unit in re.findall(r'(-?\d*\.?\d+)(px|rem|em)\b', val):
                    px = abs(float(num)) * (1 if unit == 'px' else 16)
                    if px and px not in scale: f.append(('token-spacing', 'warn', f'{prop}: {num}{unit} ({px:g}px) in "{sel.strip()}" is off the sheet spacing scale', line))
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('--log'); ap.add_argument('--ban', default=''); ap.add_argument('--sheet')
    a = ap.parse_args(); ban = [w.strip().lower() for w in a.ban.split(',') if w.strip()]
    files = [a.path] if os.path.isfile(a.path) else [os.path.join(r, n) for r, _, ns in os.walk(a.path) for n in ns]
    sheet = json.load(open(a.sheet, encoding='utf-8-sig')) if a.sheet else None
    out = []
    for fp in sorted(files):
        if not fp.endswith(('.html', '.htm', '.css')): continue
        src = open(fp, encoding='utf-8', errors='replace').read()
        fs = check_html(src) if fp.endswith(('.html', '.htm')) else check_css(src)
        if sheet:
            css = src if fp.endswith('.css') else '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', src, re.S | re.I))
            fs += check_tokens(css, sheet)
        for w in ban:
            for m in re.finditer(re.escape(w), src, re.I):
                fs.append(('buyer-ban', 'error', f'banned pattern "{w}" (from buyer sheet)', src[:m.start()].count('\n')+1))
        for rule, sev, msg, ln in fs: out.append({'file': fp, 'line': ln, 'rule': rule, 'severity': sev, 'message': msg})
    errs = sum(1 for x in out if x['severity'] == 'error')
    entry = {'gate': 'detector', 'time': datetime.datetime.now().isoformat(timespec='seconds'), 'path': a.path, 'errors': errs, 'warnings': len(out)-errs, 'findings': out}
    if a.log:
        log = json.load(open(a.log)) if os.path.exists(a.log) else []
        log.append(entry); json.dump(log, open(a.log, 'w'), indent=2)
    for x in out: print(f"{x['severity'].upper():5} {x['file']}:{x['line']} [{x['rule']}] {x['message']}")
    print(f"{errs} error(s), {len(out)-errs} warning(s)")
    sys.exit(1 if errs else 0)
if __name__ == '__main__': main()
