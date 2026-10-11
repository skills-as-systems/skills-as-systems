import subprocess, sys, os
H = os.path.dirname(__file__); S = os.path.join(H, '..', 'scripts', 'foundry_check.py'); F = os.path.join(H, 'fixtures')
def run(*a): r = subprocess.run([sys.executable, S, *a], capture_output=True, text=True); return r.returncode, r.stdout
def test_empty_run_rejected(): rc, o = run('testrun', F + '/empty.txt'); assert rc == 1 and '0 tests executed' in o
def test_green_ok(): assert run('testrun', F + '/green.txt')[0] == 0
def test_pytest_ok(): assert run('testrun', F + '/pytest_ok.txt')[0] == 0
def test_red_first_requires_failure(): assert run('testrun', F + '/green.txt', '--expect-fail')[0] == 1; assert run('testrun', F + '/red.txt', '--expect-fail')[0] == 0
def test_red_not_a_pass(): assert run('testrun', F + '/red.txt')[0] == 1
def test_receipt_good(): rc, o = run('receipt', F + '/receipt_good.json'); assert rc == 0, o
def test_receipt_bad():
    rc, o = run('receipt', F + '/receipt_bad.json'); assert rc == 1
    for k in ['shows no executed tests', 'did not pass', 'not found', 'simulated boundary', 'unknown claim label', 'UNVERIFIED', 'only self-review']: assert k in o, k
def _indep(tmp, reviewer='agent-B', builder='agent-A', review=None):
    import json, shutil, tempfile
    d = tempfile.mkdtemp(); shutil.copy(F + '/green.txt', d)
    r = {"checks": [{"check_id": "c1", "claim_ids": ["a"], "kind": "focused", "outcome": "passed", "evidence_ref": "green.txt", "boundary": "real"}],
         "claims": [{"claim_id": "a", "status": "TESTED", "evidence_ids": ["c1"]}], "verdict": "passed",
         "review_provenance": [{"kind": "second_agent", "reviewer_id": reviewer, "builder_id": builder, "review_file": "review.json"}]}
    json.dump(r, open(d + '/receipt.json', 'w'))
    if review is not None: json.dump(review, open(d + '/review.json', 'w'))
    return d
GOOD = {"reviewer_id": "agent-B", "saw_builder_reasoning": False, "checks_rerun": [{"command": "python test.py", "result": "ok"}], "findings": [], "outcome": "agree"}
def test_independent_review_passes(): d = _indep(None, review=GOOD); rc, o = run('receipt', d + '/receipt.json'); assert rc == 0, o
def test_independent_same_agent_rejected(): d = _indep(None, reviewer='agent-A', review=dict(GOOD, reviewer_id='agent-A')); rc, o = run('receipt', d + '/receipt.json'); assert rc == 1 and 'equals builder_id' in o
def test_independent_without_review_file_rejected(): d = _indep(None); rc, o = run('receipt', d + '/receipt.json'); assert rc == 1 and 'not found' in o
def test_independent_no_rerun_rejected(): d = _indep(None, review=dict(GOOD, checks_rerun=[])); rc, o = run('receipt', d + '/receipt.json'); assert rc == 1 and 're-ran no checks' in o
def test_independent_disagree_rejected(): d = _indep(None, review=dict(GOOD, outcome='disagree')); rc, o = run('receipt', d + '/receipt.json'); assert rc == 1 and 'not agree' in o
def test_independent_saw_reasoning_rejected(): d = _indep(None, review=dict(GOOD, saw_builder_reasoning=True)); rc, o = run('receipt', d + '/receipt.json'); assert rc == 1 and 'saw_builder_reasoning' in o
def test_review_packet_has_no_gate_log():
    import tempfile, shutil; d = _indep(None, review=GOOD); open(d + '/GATE-LOG.md', 'w').write('secret reasoning'); out = tempfile.mkdtemp() + '/p'
    rc, o = run('review-packet', d + '/receipt.json', '--out', out); assert rc == 0 and os.path.exists(out + '/REVIEWER-INSTRUCTIONS.md') and not os.path.exists(out + '/GATE-LOG.md') and os.path.exists(out + '/green.txt')
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
