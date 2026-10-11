#!/usr/bin/env python3
"""SITECRAFT starter library: search it and turn a brief into 2 or 3 PROPOSED directions.
It proposes; the buyer's approved design sheet decides. Palettes are contrast-checked (run `verify`).
  design_search.py search "bakery warm"            # ranked palettes, font pairings, styles
  design_search.py propose --brief "bakery warm friendly" [--n 3] [--out DIR]   # writes direction-N.json design sheets
  design_search.py verify                           # check every library palette's contrast
Stdlib only, no network. Output sheets work with `sitecraft_check.py --sheet`."""
import sys, os, csv, re, json, argparse
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'library')

def rows(name):
    with open(os.path.join(LIB, name), encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def lum(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

CHECKS = (('text', 'canvas', 4.5), ('text2', 'canvas', 4.5), ('text', 'surface', 4.5), ('text2', 'surface', 4.5),
          ('on_primary', 'primary', 4.5), ('primary', 'canvas', 3.0), ('error', 'canvas', 4.5))

def verify_palette(p):
    return [f'{p["id"]}: {a} on {b} is {ratio(p[a], p[b]):.2f}:1 (needs {need})' for a, b, need in CHECKS if ratio(p[a], p[b]) < need]

def words(s): return {w for w in re.findall(r'[a-z0-9]+', s.lower())}

def score(row, q):
    tags = words(row.get('tags', '').replace(';', ' ')) | words(row.get('mood', ''))
    return len(q & tags) * 2 + len(q & words(row.get('name', '') + ' ' + row.get('id', '')))

def ranked(name, q):
    rs = rows(name); rs.sort(key=lambda r: (-score(r, q), r['id'])); return rs

def cmd_search(query):
    q = words(query)
    for name, title in (('palettes.csv', 'palettes'), ('fonts.csv', 'font pairings'), ('styles.csv', 'styles')):
        print(f'## {title}')
        for r in ranked(name, q)[:4]:
            if score(r, q) > 0: print(f'- {r["id"]} ({score(r, q)}): ' + (r.get('mood') or r.get('layout', '')))
    return 0

def sheet(p, f):
    return {'colors': {k: p[k] for k in ('canvas', 'surface', 'text', 'text2', 'primary', 'on_primary', 'border', 'error')},
            'fonts': [f['display']] + ([f['body']] if f['body'] != f['display'] else []), 'spacing': [4, 8, 12, 16, 24, 32, 48]}

def cmd_propose(brief, n, out):
    q = words(brief); P, Fo, S = ranked('palettes.csv', q), ranked('fonts.csv', q), ranked('styles.csv', q)
    if not any(score(r, q) for r in P): print('NOTE: no palette matched the brief words; showing neutral defaults. Ask the buyer for an industry and a mood.')
    dirs = []
    for i in range(min(n, len(P))):
        p, f, s = P[i], Fo[i % len(Fo)], S[i % len(S)]
        bad = verify_palette(p)
        weak = score(p, q) == 0
        dirs.append({'direction': i + 1, 'match': ('weak (no tag overlap with the brief)' if weak else 'ok') + ('' if score(s, q) else '; style is a weak match'), 'palette': p['id'], 'fonts': f['id'], 'style': s['id'], 'sheet': sheet(p, f), 'style_notes': {'layout': s['layout'], 'do': s['do'], 'avoid': s['avoid']},
                     'font_licence': f['licence'], 'contrast_problems': bad})
    for d in dirs:
        print(f'Direction {d["direction"]} [{d["match"]}]: palette {d["palette"]}, fonts {d["fonts"]}, style {d["style"]}\n  layout: {d["style_notes"]["layout"]}\n  do: {d["style_notes"]["do"]}\n  avoid: {d["style_notes"]["avoid"]}')
        if d['contrast_problems']: print('  CONTRAST PROBLEMS:', d['contrast_problems'])
    if out:
        os.makedirs(out, exist_ok=True)
        for d in dirs: json.dump(d['sheet'], open(os.path.join(out, f'direction-{d["direction"]}.json'), 'w'), indent=2)
        print(f'wrote {len(dirs)} design-sheet file(s) to {out}')
    print('These are proposals. Show them to the buyer; nothing here is approved until they approve the design sheet (gate 1).')
    return 0

def cmd_verify():
    bad = [x for p in rows('palettes.csv') for x in verify_palette(p)]
    for x in bad: print('PROBLEM:', x)
    if not bad: print(f'ok: {len(rows("palettes.csv"))} palettes pass their contrast checks')
    return 1 if bad else 0

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c')
    s = sp.add_parser('search'); s.add_argument('query')
    p = sp.add_parser('propose'); p.add_argument('--brief', required=True); p.add_argument('--n', type=int, default=3); p.add_argument('--out')
    sp.add_parser('verify')
    a = ap.parse_args()
    if a.c == 'search': sys.exit(cmd_search(a.query))
    if a.c == 'propose': sys.exit(cmd_propose(a.brief, max(1, min(a.n, 3)), a.out))
    if a.c == 'verify': sys.exit(cmd_verify())
    ap.print_usage(); sys.exit(2)
if __name__ == '__main__': main()
