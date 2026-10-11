#!/usr/bin/env python3
"""FOUNDRY v2 deterministic checks (prototype). stdlib only, no network, no LLM.
  foundry_check.py testrun OUTPUT.txt [--expect-fail]   # parse a test run's output
  foundry_check.py receipt RECEIPT.json [--root DIR]     # cross-check a verification receipt
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

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c')
    a = sp.add_parser('testrun'); a.add_argument('file'); a.add_argument('--expect-fail', action='store_true')
    b = sp.add_parser('receipt'); b.add_argument('file'); b.add_argument('--root')
    p = sp.add_parser('review-packet'); p.add_argument('file'); p.add_argument('--root'); p.add_argument('--out', required=True)
    n = ap.parse_args()
    if n.c == 'testrun': sys.exit(cmd_testrun(n.file, n.expect_fail))
    if n.c == 'receipt': sys.exit(cmd_receipt(n.file, n.root))
    if n.c == 'review-packet': sys.exit(cmd_review_packet(n.file, n.root, n.out))
    ap.print_usage(); sys.exit(2)
if __name__ == '__main__': main()
