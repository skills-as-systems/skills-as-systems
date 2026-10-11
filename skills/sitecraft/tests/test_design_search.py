import subprocess, sys, os, json, tempfile
H = os.path.dirname(__file__); S = os.path.join(H, '..', 'scripts', 'design_search.py'); C = os.path.join(H, '..', 'scripts', 'sitecraft_check.py')
def run(*a): r = subprocess.run([sys.executable, S, *a], capture_output=True, text=True); return r.returncode, r.stdout
def test_all_palettes_pass_contrast(): rc, o = run('verify'); assert rc == 0, o
def test_search_finds_relevant():
    rc, o = run('search', 'bakery warm'); assert rc == 0 and 'warm-bakery' in o.split('## font pairings')[0] and 'serif-warm' in o
def test_propose_writes_sheets_the_checker_accepts():
    d = tempfile.mkdtemp(); rc, o = run('propose', '--brief', 'law firm serious', '--out', d); assert rc == 0 and 'legal-navy' in o and 'nothing here is approved' in o
    sh = json.load(open(d + '/direction-1.json')); assert set(sh) == {'colors', 'fonts', 'spacing'} and sh['colors']['canvas'].startswith('#')
    css = d + '/a.css'; open(css, 'w').write('body{color:%s;background:%s;font-family:"%s",serif}' % (sh['colors']['text'], sh['colors']['canvas'], sh['fonts'][0]))
    r = subprocess.run([sys.executable, C, css, '--sheet', d + '/direction-1.json'], capture_output=True, text=True); assert r.returncode == 0, r.stdout
def test_weak_match_is_flagged_not_hidden():
    rc, o = run('propose', '--brief', 'zzz qqq'); assert 'NOTE: no palette matched' in o and 'weak' in o
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
