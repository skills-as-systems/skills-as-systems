#!/usr/bin/env python3
"""Skills-as-systems checks as a tiny MCP server (stdio, newline-delimited JSON-RPC). stdlib only, no network.
It only runs the bundled checker scripts with the file paths you pass, never a shell. Each tool returns the checker's
own output and exit code. These are checkers, not locks: a harness can still ignore the result.
Run:  python3 integrations/mcp/skills_as_systems_mcp.py      (point your harness's MCP config at this command)"""
import sys, os, json, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'skills'))
SC = os.path.join(ROOT, 'sitecraft', 'scripts'); FO = os.path.join(ROOT, 'foundry-engineering', 'scripts')
MAX = 20000

def S(**props): return {'type': 'object', 'properties': {k: {'type': 'string', 'description': v} for k, v in props.items()}}
def tool(name, desc, props, required, build): return {'name': name, 'description': desc, 'inputSchema': dict(S(**props), required=required), 'build': build}

def opt(args, flag, key):
    return [flag, args[key]] if args.get(key) else []

TOOLS = [
    tool('sitecraft_check', 'Check .html/.css files for accessibility and design problems (optionally against a design sheet and a ban list).', {'path': 'file or folder', 'sheet': 'design-sheet JSON (optional)', 'ban': 'comma-separated banned patterns (optional)'}, ['path'],
         lambda a: [os.path.join(SC, 'sitecraft_check.py'), a['path']] + opt(a, '--sheet', 'sheet') + opt(a, '--ban', 'ban')),
    tool('foundry_testrun', 'Read a saved test run output; reject empty, unreadable or wrongly red/green runs.', {'file': 'saved test output', 'expect_fail': '"true" for a red-first run'}, ['file'],
         lambda a: [os.path.join(FO, 'foundry_check.py'), 'testrun', a['file']] + (['--expect-fail'] if a.get('expect_fail') == 'true' else [])),
    tool('foundry_receipt', 'Cross-check a verification receipt against its evidence.', {'file': 'receipt JSON', 'root': 'evidence root (optional)'}, ['file'],
         lambda a: [os.path.join(FO, 'foundry_check.py'), 'receipt', a['file']] + opt(a, '--root', 'root')),
    tool('foundry_test_weakening', 'Flag removed assertions, new skips, rewritten snapshots in a unified diff.', {'diff': 'diff file', 'allow_weakening': 'owner reason (optional)'}, ['diff'],
         lambda a: [os.path.join(FO, 'foundry_check.py'), 'test-weakening', '--diff', a['diff']] + opt(a, '--allow-weakening', 'allow_weakening')),
    tool('foundry_scope_drift', 'Compare a unified diff with the change contract surfaces.', {'diff': 'diff file', 'contract': 'change contract JSON'}, ['diff', 'contract'],
         lambda a: [os.path.join(FO, 'foundry_check.py'), 'scope-drift', '--diff', a['diff'], '--contract', a['contract']]),
    tool('gate_log_validate', 'Validate a gate log (evidence, waivers, skipped gates, level claims).', {'file': 'gate-log.json'}, ['file'],
         lambda a: [os.path.join(SC, 'gate_log.py'), 'validate', a['file']]),
    tool('gate_log_cross_check', 'Check linked SITECRAFT and FOUNDRY gate logs for a change that touches UI and backend.', {'sitecraft_log': 'path', 'foundry_log': 'path'}, ['sitecraft_log', 'foundry_log'],
         lambda a: [os.path.join(SC, 'gate_log.py'), 'cross-check', a['sitecraft_log'], a['foundry_log']]),
    tool('design_propose', 'Propose 2-3 starter design directions from a brief. Proposals only; the buyer approves the sheet.', {'brief': 'industry and mood words', 'out': 'folder for direction-N.json (optional)'}, ['brief'],
         lambda a: [os.path.join(SC, 'design_search.py'), 'propose', '--brief', a['brief']] + opt(a, '--out', 'out')),
]
BY = {t['name']: t for t in TOOLS}

def run_tool(name, args):
    t = BY.get(name)
    if not t: return 'unknown tool', True
    miss = [k for k in t['inputSchema']['required'] if not args.get(k)]
    if miss: return 'missing argument(s): ' + ', '.join(miss), True
    cmd = [sys.executable] + t['build'](args)
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired: return 'checker timed out after 120 s', True
    out = (r.stdout + r.stderr)[:MAX]
    return f'{out}\n[exit code {r.returncode}; 0 = clean, 1 = findings, other = could not run]', r.returncode not in (0, 1)

def handle(m):
    mid, method = m.get('id'), m.get('method')
    if mid is None: return None   # notifications need no reply
    if method == 'initialize':
        v = (m.get('params') or {}).get('protocolVersion', '2024-11-05')
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'protocolVersion': v, 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'skills-as-systems-checks', 'version': '1.0.0'}}}
    if method == 'ping': return {'jsonrpc': '2.0', 'id': mid, 'result': {}}
    if method == 'tools/list':
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'tools': [{k: v for k, v in t.items() if k != 'build'} for t in TOOLS]}}
    if method == 'tools/call':
        p = m.get('params') or {}; text, err = run_tool(p.get('name'), p.get('arguments') or {})
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'content': [{'type': 'text', 'text': text}], 'isError': err}}
    return {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32601, 'message': f'method not found: {method}'}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: m = json.loads(line)
        except ValueError: print(json.dumps({'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'parse error'}}), flush=True); continue
        resp = handle(m)
        if resp is not None: print(json.dumps(resp), flush=True)
if __name__ == '__main__': main()
