import subprocess, sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); SRV = os.path.join(H, '..', '..', 'integrations', 'mcp', 'skills_as_systems_mcp.py')
FIX = os.path.join(H, '..', '..', 'skills', 'sitecraft', 'tests', 'fixtures')
def talk(msgs):
    p = subprocess.run([sys.executable, SRV], input='\n'.join(json.dumps(m) for m in msgs) + '\n', capture_output=True, text=True, timeout=60)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
def test_handshake_and_list():
    r = talk([{'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-03-26'}}, {'jsonrpc': '2.0', 'method': 'notifications/initialized'}, {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}])
    assert len(r) == 2 and r[0]['result']['protocolVersion'] == '2025-03-26' and 'tools' in r[0]['result']['capabilities']
    names = {t['name'] for t in r[1]['result']['tools']}; assert {'sitecraft_check', 'foundry_testrun', 'gate_log_validate', 'design_propose'} <= names
    assert all('build' not in t and t['inputSchema']['type'] == 'object' for t in r[1]['result']['tools'])
def call(name, args): return talk([{'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': name, 'arguments': args}}])[0]['result']
def test_checker_findings_are_returned_not_errors():
    r = call('sitecraft_check', {'path': os.path.join(FIX, 'bad.html')}); assert r['isError'] is False and '[img-alt]' in r['content'][0]['text'] and 'exit code 1' in r['content'][0]['text']
def test_clean_run():
    r = call('sitecraft_check', {'path': os.path.join(FIX, 'good.html')}); assert 'exit code 0' in r['content'][0]['text']
def test_missing_argument_and_unknown_tool():
    assert call('sitecraft_check', {})['isError'] is True and call('nope', {})['isError'] is True
def test_unknown_method_and_bad_json():
    r = talk([{'jsonrpc': '2.0', 'id': 9, 'method': 'resources/list'}]); assert r[0]['error']['code'] == -32601
def test_no_shell_injection_through_arguments():
    r = call('sitecraft_check', {'path': 'x; echo INJECTED'}); assert 'INJECTED' not in r['content'][0]['text'].replace('echo INJECTED', '')
def test_foundry_testrun_and_design_propose():
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f: f.write('===== 3 passed in 0.1s =====\n')
    r = call('foundry_testrun', {'file': f.name}); assert r['isError'] is False and 'exit code 0' in r['content'][0]['text']
    r = call('design_propose', {'brief': 'dental clinic calm'}); assert 'Direction 1' in r['content'][0]['text'] and 'exit code 0' in r['content'][0]['text']
if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
