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

import json, tempfile
def _diff(body):
    f = tempfile.NamedTemporaryFile('w', suffix='.diff', delete=False); f.write(body); f.close(); return f.name
def _d(path, removed=(), added=(), extra=''):
    return f'diff --git a/{path} b/{path}\n{extra}--- a/{path}\n+++ b/{path}\n@@ -1,3 +1,3 @@\n' + ''.join('-' + l + '\n' for l in removed) + ''.join('+' + l + '\n' for l in added)
def test_weakening_removed_assert(): rc, o = run('test-weakening', '--diff', _diff(_d('tests/test_a.py', removed=['    assert x == 2'], added=['    pass']))); assert rc == 1 and 'assertion' in o
def test_weakening_skip_added(): rc, o = run('test-weakening', '--diff', _diff(_d('tests/test_a.py', added=['@pytest.mark.skip']))); assert rc == 1 and 'skip' in o
def test_weakening_js_only_and_snapshot():
    rc, o = run('test-weakening', '--diff', _diff(_d('src/a.test.js', added=["it.only('x', () => {})"]) + _d('src/__snapshots__/a.snap', removed=['a'], added=['b']))); assert rc == 1 and 'only' in o and 'snapshot' in o
def test_weakening_deleted_test_file(): rc, o = run('test-weakening', '--diff', _diff(_d('tests/test_a.py', extra='deleted file mode 100644\n'))); assert rc == 1 and 'deleted' in o
def test_weakening_clean_change_passes(): rc, o = run('test-weakening', '--diff', _diff(_d('tests/test_a.py', removed=['    assert x == 1'], added=['    assert x == 2', '    assert y']) + _d('src/a.py', added=['x = 2']))); assert rc == 0, o
def test_weakening_allowed_with_reason(): rc, o = run('test-weakening', '--diff', _diff(_d('tests/test_a.py', added=['@pytest.mark.skip'])), '--allow-weakening', 'owner approved C-2'); assert rc == 0 and 'ALLOWED' in o
def _contract(allowed, forbidden=(), affected=()):
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump({'surfaces': {'allowed': list(allowed), 'affected': list(affected), 'forbidden': list(forbidden), 'generated_or_external': []}}, f); f.close(); return f.name
def test_scope_inside_ok(): rc, o = run('scope-drift', '--diff', _diff(_d('src/a.py', added=['x'])), '--contract', _contract(['src/'])); assert rc == 0, o
def test_scope_outside_flagged(): rc, o = run('scope-drift', '--diff', _diff(_d('lib/b.py', added=['x'])), '--contract', _contract(['src/'])); assert rc == 1 and 'scope drift' in o
def test_scope_lockfile_ci_test_flagged():
    d = _d('package-lock.json', added=['x']) + _d('.github/workflows/ci.yml', added=['x']) + _d('tests/test_a.py', added=['x'])
    rc, o = run('scope-drift', '--diff', _diff(d), '--contract', _contract(['src/'], affected=['package-lock.json', '.github/workflows/ci.yml', 'tests/']))
    assert rc == 1 and 'lockfile' in o and 'CI config' in o and 'test file' in o
def test_scope_named_test_allowed(): rc, o = run('scope-drift', '--diff', _diff(_d('tests/test_a.py', added=['x'])), '--contract', _contract(['src/', 'tests/test_a.py'])); assert rc == 0, o
def test_scope_forbidden(): rc, o = run('scope-drift', '--diff', _diff(_d('src/secret.py', added=['x'])), '--contract', _contract(['src/'], forbidden=['src/secret.py'])); assert rc == 1 and 'forbidden' in o
def test_base_mode_with_git():
    import shutil
    if not shutil.which('git'): return
    d = tempfile.mkdtemp(); g = lambda *a: subprocess.run(['git', '-C', d, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], capture_output=True, text=True, check=True)
    g('init', '-q'); os.makedirs(d + '/tests'); open(d + '/tests/test_a.py', 'w').write('assert 1 == 1\n'); g('add', '.'); g('commit', '-qm', 'a')
    open(d + '/tests/test_a.py', 'w').write('pass\n'); rc, o = run('test-weakening', '--base', 'HEAD', '--repo', d); assert rc == 1, o
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
