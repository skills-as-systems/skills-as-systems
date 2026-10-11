import subprocess, sys, os, shutil
H = os.path.dirname(__file__); S = os.path.join(H, '..', 'scripts', 'render_check.py'); F = os.path.join(H, 'fixtures')
AXE = os.environ.get('AXE_JS', '')
def run(name, *a):
    r = subprocess.run([sys.executable, S, os.path.join(F, name), *a], capture_output=True, text=True); return r.returncode, r.stdout
def _can():
    try: import playwright  # noqa
    except ImportError: return False
    return run('render_good.html')[0] != 3
def test_missing_playwright_is_not_a_pass():
    env = dict(os.environ); r = subprocess.run([sys.executable, '-c', 'import sys; sys.modules["playwright"]=None; sys.modules["playwright.sync_api"]=None; sys.argv=["x","a.html"]; exec(open(%r).read())' % S], capture_output=True, text=True)
    assert r.returncode == 3 and 'NOT RUN' in r.stdout, r.stdout + r.stderr
def test_good_page_clean():
    if not _can(): print('skip: no browser'); return
    rc, o = run('render_good.html'); assert rc == 0, o
def test_bad_page_findings():
    if not _can(): print('skip: no browser'); return
    rc, o = run('render_bad.html'); assert rc == 1
    for k in ('[overflow]', '[tap-target]', '[focus]', '[console]'): assert k in o, (k, o)
    assert '320px' in o and '1440px' in o
def test_axe_runs_when_given():
    if not (_can() and AXE and os.path.exists(AXE)): print('skip: no axe'); return
    rc, o = run('render_bad.html', '--axe', AXE); assert 'NOTE: axe-core not run' not in o
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
