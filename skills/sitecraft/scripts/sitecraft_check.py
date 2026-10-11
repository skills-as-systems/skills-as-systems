#!/usr/bin/env python3
"""SITECRAFT deterministic checker (v2 prototype). No network, no LLM, stdlib only.
Scans .html/.css files for objective, statically checkable issues and writes a
JSON gate-log entry. Rules are our own. Exit 1 if any 'error' finding.
Usage: sitecraft_check.py PATH [--sheet design-sheet.json] [--log gate-log.json] [--ban "word,word"]
"""
import sys, re, json, os, argparse, datetime
from html.parser import HTMLParser

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
    def add(self, rule, sev, msg): self.f.append((rule, sev, msg, self.getpos()[0]))
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html' and a.get('lang'): self.has_lang = True
        if tag == 'meta' and a.get('name') == 'viewport': self.has_viewport = True
        if tag == 'title': self.title = True
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
        if tag == 'a':
            if not self.a_text.strip() and not self.a_aria: self.add('link-name', 'error', 'link with no accessible name')
            self.in_a = False
    def handle_data(self, d):
        if self.in_a: self.a_text += d

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

VAR_DEF = re.compile(r'(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\b')
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
            m = re.search(r'background(?:-color)?\s*:\s*(?:[^;]*?\s)?(#[0-9a-fA-F]{3,6})\b', body2)
            if m and len(m.group(1)) in (4, 7): PAGE_BG = m.group(1)
    if re.search(r'(animation|transition)\s*:', src) and 'prefers-reduced-motion' not in src:
        f.append(('reduced-motion', 'error', 'animation/transition used but no prefers-reduced-motion handling', 1))
    for sel, body in CSS_BLOCK.findall(src):
        line = src[:src.find(body)].count('\n')+1
        if re.search(r'outline\s*:\s*(none|0)\b', body) and ':focus' in sel and not re.search(r'box-shadow|border|outline-offset|background', body):
            f.append(('focus-style', 'error', f'focus style removed with no replacement in "{sel.strip()}"', line))
        body = VAR_USE.sub(lambda m: VARS.get(m.group(1), m.group(0)), body)
        c = re.search(r'(?<![-\w])color\s*:\s*(#[0-9a-fA-F]{3,6})\b', body)
        b = re.search(r'background(?:-color)?\s*:\s*(?:[^;]*?\s)?(#[0-9a-fA-F]{3,6})\b', body)
        okhex = lambda x: len(x) in (4, 7)
        if c and b and okhex(c.group(1)) and okhex(b.group(1)):
            r = ratio(c.group(1), b.group(1))
            if r < 1.05:
                f.append(('hidden-text', 'warn', f'text colour equals its background in "{sel.strip()}" (fine only if it is hidden until a state rule changes the background)', line))
            elif r < 4.5: f.append(('contrast', 'error', f'contrast {r:.2f}:1 below 4.5:1 in "{sel.strip()}"', line))
        elif c and not b and PAGE_BG and okhex(c.group(1)):
            r = ratio(c.group(1), PAGE_BG)
            if 1.5 <= r < 4.5:
                f.append(('contrast-page', 'warn', f'contrast {r:.2f}:1 against the page background {PAGE_BG} in "{sel.strip()}" (parent background may differ)', line))
        if re.search(r'transition\s*:\s*all\b', body): f.append(('transition-all', 'warn', 'transition: all (animates everything)', line))
        if re.search(r'(cubic-bezier\([^)]*-?\d*\.?\d+\s*,\s*-\d|elastic|bounce)', body, re.I):
            f.append(('bounce-easing', 'warn', 'bounce/elastic style easing', line))
        m = re.search(r'font-size\s*:\s*(\d+)px', body)
        if m and int(m.group(1)) < 12: f.append(('tiny-text', 'warn', f'font-size {m.group(1)}px under 12px', line))
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('--log'); ap.add_argument('--ban', default='')
    a = ap.parse_args(); ban = [w.strip().lower() for w in a.ban.split(',') if w.strip()]
    files = [a.path] if os.path.isfile(a.path) else [os.path.join(r, n) for r, _, ns in os.walk(a.path) for n in ns]
    out = []
    for fp in sorted(files):
        if not fp.endswith(('.html', '.htm', '.css')): continue
        src = open(fp, encoding='utf-8', errors='replace').read()
        fs = check_html(src) if fp.endswith(('.html', '.htm')) else check_css(src)
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
