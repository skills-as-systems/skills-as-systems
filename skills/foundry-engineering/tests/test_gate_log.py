import subprocess, sys, os, json, tempfile, copy
H = os.path.dirname(__file__); S = os.path.join(H, '..', 'scripts', 'gate_log.py'); T = os.path.join(H, '..', 'assets', 'gate-log.template.json')
def run(*a): r = subprocess.run([sys.executable, S, *a], capture_output=True, text=True); return r.returncode, r.stdout
def tmp(log):
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(log, f); f.close(); return f.name
def base(): return copy.deepcopy(json.load(open(T)))
def test_template_is_valid(): rc, o = run('validate', T); assert rc == 0, o
def test_done_without_evidence():
    l = base(); l['gates'][0]['status'] = 'done'; rc, o = run('validate', tmp(l)); assert rc == 1 and 'no evidence' in o
def test_waived_without_reason():
    l = base(); l['gates'][0].update(status='waived'); rc, o = run('validate', tmp(l)); assert rc == 1 and 'no reason' in o
def test_skipped_gate_detected():
    l = base(); l['gates'][2].update(status='done', evidence='x'); rc, o = run('validate', tmp(l)); assert rc == 1 and 'skipped' in o
def test_level_claims_checked():
    l = base(); l['level'] = 3; rc, o = run('validate', tmp(l)); assert rc == 1 and 'shell' in o and 'enforcer' in o
    l = base(); l['level'] = 2; l['capabilities']['shell'] = True; rc, o = run('validate', tmp(l)); assert rc == 0, o
def test_report_across_runs():
    a = base(); a['gates'][0].update(status='done', evidence='PRODUCT.md'); b = base(); b['gates'][0].update(status='waived', waiver='existing')
    rc, o = run('report', tmp(a), tmp(b)); assert rc == 0 and 'across runs' in o and f'next: gate {a["gates"][1]["gate"]}' in o and 'waived: ' in o
def test_bad_json_shape():
    rc, o = run('validate', tmp({'gates': []})); assert rc == 1

def _pair():
    root = os.path.join(H, '..', '..')
    s = json.load(open(os.path.join(root, 'sitecraft', 'assets', 'gate-log.template.json'))); f = json.load(open(os.path.join(root, 'foundry-engineering', 'assets', 'gate-log.template.json')))
    for lg, me, peer in ((s, 'S1', 'F1'), (f, 'F1', 'S1')):
        lg['run_id'] = me; lg['level'] = 1; lg['linked'] = {'peer_run_id': peer}
        for g in lg['gates']: g.update(status='done', evidence='x')
    return s, f
def test_cross_check_ok():
    s, f = _pair(); rc, o = run('cross-check', tmp(s), tmp(f)); assert rc == 0 and 'both sides done' in o, o
def test_cross_check_needs_link_and_both_sides():
    s, f = _pair(); s['linked']['peer_run_id'] = 'other'; rc, o = run('cross-check', tmp(s), tmp(f)); assert rc == 1 and 'does not link' in o
    s, f = _pair(); [g.update(status='pending', evidence='') for g in f['gates'] if g['name'] == 'claims']; rc, o = run('cross-check', tmp(s), tmp(f)); assert rc == 1 and ('claims gate' in o or 'skipped' in o), o
    s, f = _pair(); [g.update(status='waived', waiver='no ui', evidence='') for g in s['gates'] if g['name'] == 'shots']; rc, o = run('cross-check', tmp(s), tmp(f)); assert rc == 1 and 'shots gate' in o, o
def test_cross_check_wrong_skill():
    s, f = _pair(); rc, o = run('cross-check', tmp(f), tmp(s)); assert rc == 1 and 'not a sitecraft log' in o
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
