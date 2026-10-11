import subprocess, sys, os, json
H = os.path.dirname(__file__); S = os.path.join(H, '..', 'scripts', 'sitecraft_check.py'); F = os.path.join(H, 'fixtures')
def run(name, *extra):
    r = subprocess.run([sys.executable, S, os.path.join(F, name), *extra], capture_output=True, text=True); return r.returncode, r.stdout
def test_bad_html_triggers():
    rc, out = run('bad.html')
    assert rc == 1
    for rule in ['html-lang', 'viewport', 'img-alt', 'link-name', 'input-label', 'h1-count', 'heading-skip']: assert f'[{rule}]' in out, rule
def test_good_html_clean():
    rc, out = run('good.html'); assert rc == 0, out
def test_bad_css_triggers():
    rc, out = run('bad.css')
    assert rc == 1
    for rule in ['contrast', 'focus-style', 'reduced-motion', 'transition-all', 'bounce-easing', 'tiny-text']: assert f'[{rule}]' in out, rule
def test_good_css_clean():
    rc, out = run('good.css'); assert rc == 0, out
def test_buyer_ban():
    rc, out = run('bad.html', '--ban', 'purple gradient'); assert '[buyer-ban]' in out
    rc, out = run('good.html', '--ban', 'purple gradient'); assert rc == 0
def test_log_written(tmp_path=None):
    import tempfile; d = tempfile.mkdtemp(); lg = os.path.join(d, 'g.json'); run('bad.html', '--log', lg)
    assert json.load(open(lg))[0]['gate'] == 'detector'
def test_css_variables_resolved():
    rc, out = run('var_contrast.css')
    assert rc == 1 and '[contrast] contrast 2.29:1' in out, out
def test_muted_text_on_page_bg_warned():
    rc, out = run('var_contrast.css'); assert '[contrast-page] contrast 2.82:1' in out, out
def test_same_colour_text_is_warning_not_error():
    rc, out = run('var_contrast.css'); assert 'WARN  ' in out and '[hidden-text]' in out and 'ERROR ' not in [l for l in out.splitlines() if 'hidden-text' in l][0]
def test_variable_palette_good_passes():
    rc, out = run('var_ok.css'); assert rc == 0, out
if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1; print('ok', k)
    print(n, 'tests passed')
