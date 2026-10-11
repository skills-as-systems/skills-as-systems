#!/usr/bin/env python3
"""FOUNDRY v2 deterministic checks (prototype). stdlib only, no network, no LLM.
  foundry_check.py testrun OUTPUT.txt [--expect-fail]   # parse a test run's output
  foundry_check.py receipt RECEIPT.json [--root DIR]     # cross-check a verification receipt
  foundry_check.py test-weakening (--diff FILE | --base REF) [--repo DIR] [--allow-weakening "owner reason"]
  foundry_check.py scope-drift (--diff FILE | --base REF) --contract CONTRACT.json [--repo DIR]
(test-weakening and scope-drift read a unified diff; they are checkers, not locks: a renamed or moved assertion can slip past.)
Exit 0 ok, 1 problems, 2 usage."""
import sys, re, json, os, argparse

def parse_testrun(t):
    """Return (executed, failed). executed None means could not tell."""
    m = re.search(r'^Ran (\d+) tests? in', t, re.M)                      # unittest
    if m:
        ex = int(m.group(1)); f = re.search(r'FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?', t)
        fl = sum(int(x) for x in f.groups() if x) if f else 0; return ex, fl
    if re.search(r'^collected 0 items|no tests ran', t, re.M | re.I): return 0, 0   # pytest
    m = re.search(r'=+ (?:(\d+) failed)?,? ?(?:(\d+) passed)?', t)
    if m and (m.group(1) or m.group(2)):
        fl = int(m.group(1) or 0); ps = int(m.group(2) or 0); return fl + ps, fl
    m = re.search(r'Tests:\s+(?:(\d+) failed, )?(?:(\d+) passed, )?(\d+) total', t)   # jest
    if m: return int(m.group(3)), int(m.group(1) or 0)
    m = re.search(r'(\d+) tests?, (\d+) failures?', t)                                  # misc runners
    if m: return int(m.group(1)), int(m.group(2))
    return None, None

def cmd_testrun(path, expect_fail):
    t = open(path, encoding='utf-8', errors='replace').read()
    ex, fl = parse_testrun(t)
    if ex is None: print('PROBLEM: cannot tell how many tests ran; not counted as evidence'); return 1
    if ex == 0: print('PROBLEM: 0 tests executed; an empty run is not a pass'); return 1
    if expect_fail and fl == 0: print(f'PROBLEM: {ex} tests ran but none failed; a red-first run must fail'); return 1
    if not expect_fail and fl: print(f'PROBLEM: {fl} of {ex} tests failed'); return 1
    print(f'ok: {ex} executed, {fl} failed'); return 0

def cmd_receipt(path, root):
    r = json.load(open(path, encoding='utf-8-sig')); root = root or os.path.dirname(os.path.abspath(path)); probs = []
    checks = {c['check_id']: c for c in r.get('checks', [])}
    for cl in r.get('claims', []):
        cid, st = cl.get('claim_id'), cl.get('status')
        if st not in ('TESTED', 'OBSERVED', 'INFERRED', 'UNVERIFIED'): probs.append(f'{cid}: missing or unknown claim label {st!r}')
        if st in ('TESTED', 'OBSERVED'):
            ev = [checks.get(e) for e in cl.get('evidence_ids', [])]
            if not ev or any(e is None for e in ev): probs.append(f'{cid}: labelled {st} but evidence check missing'); continue
            if any(e.get('outcome') != 'passed' for e in ev): probs.append(f'{cid}: labelled {st} but a supporting check did not pass')
            for e in ev:
                ref = e.get('evidence_ref')
                if not ref: probs.append(f'{cid}: check {e["check_id"]} has no evidence_ref'); continue
                p = os.path.join(root, ref)
                if not os.path.exists(p): probs.append(f'{cid}: evidence file {ref} not found'); continue
                if e.get('kind') in ('focused', 'regression', 'unit', 'full'):
                    ex, fl = parse_testrun(open(p, encoding='utf-8', errors='replace').read())
                    if ex in (None, 0): probs.append(f'{cid}: evidence {ref} shows no executed tests')
        if st == 'TESTED' and any(checks.get(e, {}).get('boundary') == 'simulated' for e in cl.get('evidence_ids', [])) and not cl.get('limitations'):
            probs.append(f'{cid}: TESTED on a simulated boundary with no stated limitation')
    if r.get('verdict') == 'passed' and any(c.get('status') == 'UNVERIFIED' for c in r.get('claims', [])):
        probs.append('verdict "passed" but some claims are UNVERIFIED (use passed_with_limits)')
    def valid_independent(x):
        if x.get('kind') == 'self': return False
        if x.get('kind') == 'automated': return True  # a CI or tool pass; says nothing about a human or second agent
        for k in ('reviewer_id', 'builder_id', 'review_file'):
            if not x.get(k): probs.append(f'independent review missing {k}'); return False
        if x['reviewer_id'] == x['builder_id']: probs.append('independent review: reviewer_id equals builder_id'); return False
        rp = os.path.join(root, x['review_file'])
        if not os.path.exists(rp): probs.append(f'independent review: {x["review_file"]} not found'); return False
        try: rv = json.load(open(rp, encoding='utf-8-sig'))
        except Exception: probs.append('independent review: review file is not valid JSON'); return False
        if rv.get('reviewer_id') != x['reviewer_id']: probs.append('independent review: reviewer_id mismatch with review file'); return False
        if not rv.get('checks_rerun'): probs.append('independent review: reviewer re-ran no checks'); return False
        if rv.get('saw_builder_reasoning') is not False: probs.append('independent review: must state saw_builder_reasoning=false'); return False
        if rv.get('outcome') != 'agree': probs.append(f'independent review outcome is {rv.get("outcome")!r}, not agree'); return False
        return True
    if r.get('verdict') in ('passed', 'passed_with_limits') and not any(valid_independent(x) for x in r.get('review_provenance', [])):
        probs.append('only self-review recorded; say so in the verdict or add an independent pass')
    for p in probs: print('PROBLEM:', p)
    print(f'{len(probs)} problem(s)'); return 1 if probs else 0


REVIEW_INSTRUCTIONS = """# Independent review (read this first)
You are the REVIEWER, not the builder. You have only this packet: the receipt, the contract, the evidence files and the changed files.
You were NOT given the builder's reasoning or gate log; do not ask for it.
1. Read receipt.json. For every TESTED/OBSERVED claim, open its evidence file and check it supports exactly that claim.
2. Re-run at least one check yourself (tests or checker) from the files in changed/ and record the command and result in review.json "checks_rerun".
3. Look for: weakened or deleted tests, claims wider than their evidence, unlabelled UNVERIFIED gaps, files changed outside the contract.
4. Write review.json: {"reviewer_id": "<your own agent id>", "saw_builder_reasoning": false, "checks_rerun": [{"command": "...", "result": "..."}], "findings": ["..."], "outcome": "agree" | "disagree"}
Never write "agree" without a re-run you actually executed. Say "disagree" and list why if anything is unsupported.
"""

def cmd_review_packet(path, root, out):
    import shutil
    r = json.load(open(path, encoding='utf-8-sig')); root = root or os.path.dirname(os.path.abspath(path))
    os.makedirs(out, exist_ok=True)
    shutil.copy(path, os.path.join(out, 'receipt.json'))
    for name in ('contract.json',):
        if os.path.exists(os.path.join(root, name)): shutil.copy(os.path.join(root, name), os.path.join(out, name))
    for c in r.get('checks', []):
        ref = c.get('evidence_ref')
        if ref and os.path.exists(os.path.join(root, ref)):
            dst = os.path.join(out, ref); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(os.path.join(root, ref), dst)
    open(os.path.join(out, 'REVIEWER-INSTRUCTIONS.md'), 'w').write(REVIEW_INSTRUCTIONS)
    print(f'review packet written to {out} (no gate log, no builder notes)'); return 0

import fnmatch, subprocess
TEST_PATH = re.compile(r'(^|/)(tests?|__tests__|spec|specs)/|(^|/)test_[^/]*$|[._-](test|spec)\.[A-Za-z0-9]+$|_test\.[A-Za-z0-9]+$', re.I)
SNAP_PATH = re.compile(r'(^|/)(__snapshots__|snapshots?)/|\.snap$', re.I)
ASSERT_RE = re.compile(r'\bassert\w*\b|\bexpect\s*\(|\.should\b|\bverify\s*\(|\bt\.(?:Error|Fatal|Fail)\w*\(', re.I)
SKIP_RE = re.compile(r'@(?:unittest\.)?skip\w*|pytest\.mark\.(?:skip|xfail)|pytest\.(?:skip|xfail)\(|\bxfail\b|\b(?:it|test|describe)\.(?:skip|only|todo)\b|\b(?:xit|xdescribe|xtest|fit|fdescribe)\s*\(|@Ignore\b|@Disabled\b|\bt\.Skip\w*\(|\bt\.skip\b', re.I)
LOOSE_RE = re.compile(r'assertTrue\(\s*True\s*\)|assert\s+True\b|expect\([^)]*\)\.(?:toBeTruthy|toBeDefined)\(\)|\bpass\s*$')
LOCKFILES = {'package-lock.json','yarn.lock','pnpm-lock.yaml','poetry.lock','Pipfile.lock','Cargo.lock','go.sum','Gemfile.lock','composer.lock','uv.lock'}
CI_RE = re.compile(r'^\.github/workflows/|^\.gitlab-ci\.yml$|^\.circleci/|^Jenkinsfile$|^azure-pipelines\.ya?ml$|^\.travis\.yml$', re.I)

def get_diff(a):
    if a.diff: return open(a.diff, encoding='utf-8', errors='replace').read()
    r = subprocess.run(['git', '-C', a.repo or '.', 'diff', '-U0', '--no-color', a.base], capture_output=True, text=True)
    if r.returncode: raise SystemExit('git diff failed: ' + r.stderr.strip())
    return r.stdout

def parse_diff(d):
    """-> {path: {'added': [...], 'removed': [...], 'deleted': bool, 'new': bool}}"""
    files = {}; cur = None
    for ln in d.splitlines():
        m = re.match(r'diff --git a/(.*) b/(.*)$', ln)
        if m: cur = files.setdefault(m.group(2), {'added': [], 'removed': [], 'deleted': False, 'new': False}); cur['old'] = m.group(1); continue
        if cur is None: continue
        if ln.startswith('deleted file mode'): cur['deleted'] = True
        elif ln.startswith('new file mode'): cur['new'] = True
        elif ln.startswith('+++ ') or ln.startswith('--- '): continue
        elif ln.startswith('+'): cur['added'].append(ln[1:])
        elif ln.startswith('-'): cur['removed'].append(ln[1:])
    return files

def cmd_test_weakening(a):
    files = parse_diff(get_diff(a)); probs = []
    for path, f in sorted(files.items()):
        if SNAP_PATH.search(path) and not f['new']: probs.append(f'{path}: snapshot file rewritten (check the new snapshot is intended)')
        if not TEST_PATH.search(path): continue
        if f['deleted']: probs.append(f'{path}: test file deleted'); continue
        ra = sum(1 for l in f['removed'] if ASSERT_RE.search(l)); aa = sum(1 for l in f['added'] if ASSERT_RE.search(l))
        if ra > aa: probs.append(f'{path}: {ra} assertion line(s) removed, {aa} added (net {aa - ra})')
        for l in f['added']:
            if SKIP_RE.search(l): probs.append(f'{path}: skip/xfail/only added: {l.strip()[:80]}')
            if LOOSE_RE.search(l): probs.append(f'{path}: trivially true check added: {l.strip()[:80]}')
    if not probs: print(f'ok: {len(files)} changed file(s), no test weakening found'); return 0
    for x in probs: print('PROBLEM:', x)
    if a.allow_weakening:
        print(f'ALLOWED by owner reason: {a.allow_weakening!r}. Copy this reason into the receipt and the contract.'); return 0
    print('Test weakening found. Fail the receipt unless the contract names it and the owner approved (use --allow-weakening "reason").'); return 1

def _match(path, pats):
    for p in pats:
        p = p.strip()
        if not p: continue
        if fnmatch.fnmatch(path, p) or path == p.rstrip('/') or path.startswith(p.rstrip('/') + '/'): return p
    return None

def cmd_scope_drift(a):
    c = json.load(open(a.contract, encoding='utf-8-sig')); s = c.get('surfaces', {})
    allowed, affected, forbidden = s.get('allowed', []), s.get('affected', []), s.get('forbidden', [])
    files = parse_diff(get_diff(a)); probs = []; notes = []
    for path in sorted(files):
        base = os.path.basename(path); named = _match(path, allowed)
        if _match(path, forbidden): probs.append(f'{path}: in the contract forbidden list'); continue
        special = 'lockfile' if base in LOCKFILES else 'CI config' if CI_RE.search(path) else 'test file' if TEST_PATH.search(path) else ''
        if special and not named: probs.append(f'{path}: {special} changed but not named in surfaces.allowed')
        elif not named and not _match(path, affected): probs.append(f'{path}: outside surfaces.allowed (scope drift)')
        elif not named: notes.append(f'{path}: only in surfaces.affected (touching it needs a reason)')
    for n in notes: print('NOTE:', n)
    if not probs: print(f'ok: {len(files)} changed file(s) inside the contract surfaces'); return 0
    for x in probs: print('PROBLEM:', x)
    return 1

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c')
    a = sp.add_parser('testrun'); a.add_argument('file'); a.add_argument('--expect-fail', action='store_true')
    b = sp.add_parser('receipt'); b.add_argument('file'); b.add_argument('--root')
    p = sp.add_parser('review-packet'); p.add_argument('file'); p.add_argument('--root'); p.add_argument('--out', required=True)
    for nm, extra in (('test-weakening', True), ('scope-drift', False)):
        q = sp.add_parser(nm); q.add_argument('--diff'); q.add_argument('--base'); q.add_argument('--repo')
        if extra: q.add_argument('--allow-weakening')
        else: q.add_argument('--contract', required=True)
    n = ap.parse_args()
    if n.c in ('test-weakening', 'scope-drift') and bool(n.diff) == bool(n.base): print('give exactly one of --diff or --base'); sys.exit(2)
    if n.c == 'test-weakening': sys.exit(cmd_test_weakening(n))
    if n.c == 'scope-drift': sys.exit(cmd_scope_drift(n))
    if n.c == 'testrun': sys.exit(cmd_testrun(n.file, n.expect_fail))
    if n.c == 'receipt': sys.exit(cmd_receipt(n.file, n.root))
    if n.c == 'review-packet': sys.exit(cmd_review_packet(n.file, n.root, n.out))
    ap.print_usage(); sys.exit(2)
if __name__ == '__main__': main()
