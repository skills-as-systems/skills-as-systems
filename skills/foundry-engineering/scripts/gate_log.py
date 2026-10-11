#!/usr/bin/env python3
"""Gate-log validator and report, shared by SITECRAFT and FOUNDRY. stdlib only, no network.
  gate_log.py validate gate-log.json            # is the log honest and consistent?
  gate_log.py report gate-log.json [more.json]  # where is the run, which gates were skipped, waived or blocked
Exit 0 ok, 1 problems, 2 usage. A checker, not a lock: it reads what the agent wrote and cannot know what it left out."""
import sys, json, argparse

STATUSES = ('pending', 'done', 'waived', 'blocked')

def load(path):
    log = json.load(open(path, encoding='utf-8-sig'))
    return log

def problems(log):
    p = []
    if not isinstance(log, dict) or not isinstance(log.get('gates'), list) or not log['gates']:
        return ['log has no "gates" list']
    lvl = log.get('level')
    if lvl not in (1, 2, 2.5, 3): p.append(f'level must be 1, 2, 2.5 or 3, got {lvl!r}')
    cap = log.get('capabilities') or {}
    if lvl in (2, 2.5, 3) and not cap.get('shell'): p.append(f'level {lvl} claimed but capabilities.shell is not true')
    if lvl == 3 and not cap.get('enforcer'): p.append('level 3 claimed but capabilities.enforcer is not true')
    seen = set(); first_pending = None
    for g in log['gates']:
        gid = g.get('gate'); st = g.get('status')
        if gid in seen: p.append(f'gate {gid}: listed twice')
        seen.add(gid)
        if st not in STATUSES: p.append(f'gate {gid}: unknown status {st!r}'); continue
        if st == 'done' and not str(g.get('evidence', '')).strip(): p.append(f'gate {gid}: done with no evidence')
        if st == 'waived' and not str(g.get('waiver', '')).strip(): p.append(f'gate {gid}: waived with no reason')
        if st == 'pending' and first_pending is None: first_pending = gid
        elif st in ('done', 'waived') and first_pending is not None:
            p.append(f'gate {gid}: {st} while earlier gate {first_pending} is still pending (skipped)')
    return p

def summary(log):
    gs = log['gates']; c = {s: [g['gate'] for g in gs if g.get('status') == s] for s in STATUSES}
    nxt = next((g for g in gs if g.get('status') in ('pending', 'blocked')), None)
    return c, nxt

def cmd_validate(path):
    log = load(path); pr = problems(log)
    for x in pr: print('PROBLEM:', x)
    if pr: return 1
    c, nxt = summary(log); print(f'ok: {len(c["done"])} done, {len(c["waived"])} waived, {len(c["blocked"])} blocked, {len(c["pending"])} pending')
    return 0

def cmd_report(paths):
    agg = {}
    for path in paths:
        log = load(path); pr = problems(log); c, nxt = summary(log)
        print(f'{path}: skill={log.get("skill", "?")} level={log.get("level", "?")} run={log.get("run_id", "") or "-"}')
        print('  done: ' + (', '.join(map(str, c['done'])) or 'none'))
        if c['waived']: print('  waived: ' + ', '.join(map(str, c['waived'])))
        if c['blocked']: print('  blocked: ' + ', '.join(map(str, c['blocked'])))
        print('  next: ' + (f'gate {nxt["gate"]} ({nxt.get("name", "")}), status {nxt["status"]}' if nxt else 'none, all gates done or waived'))
        for x in pr: print('  PROBLEM:', x)
        for g in log['gates']:
            a = agg.setdefault(g['gate'], {s: 0 for s in STATUSES}); a[g.get('status', 'pending')] = a.get(g.get('status', 'pending'), 0) + 1
    if len(paths) > 1:
        print('across runs (gate: done/waived/blocked/pending):')
        for gid, a in agg.items(): print(f'  {gid}: {a["done"]}/{a["waived"]}/{a["blocked"]}/{a["pending"]}')
    return 0

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c')
    v = sp.add_parser('validate'); v.add_argument('file')
    r = sp.add_parser('report'); r.add_argument('files', nargs='+')
    n = ap.parse_args()
    if n.c == 'validate': sys.exit(cmd_validate(n.file))
    if n.c == 'report': sys.exit(cmd_report(n.files))
    ap.print_usage(); sys.exit(2)
if __name__ == '__main__': main()
