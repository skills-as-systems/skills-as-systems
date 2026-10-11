#!/usr/bin/env python3
"""Gate-log validator and report, shared by SITECRAFT and FOUNDRY. stdlib only, no network.
  gate_log.py validate gate-log.json            # is the log honest and consistent?
  gate_log.py report gate-log.json [more.json]  # where is the run, which gates were skipped, waived or blocked
  gate_log.py cross-check SITECRAFT-LOG FOUNDRY-LOG  # a change touching UI and backend: are both sides done and linked?
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

def last_gate(log): return log['gates'][-1]

def cmd_cross_check(a, b):
    """A change that touches UI and backend carries two logs, linked by run_id in each log's "linked" block:
    {"linked": {"peer_skill": "foundry-engineering", "peer_run_id": "...", "experience_contract": "...", "change_contract": "..."}}.
    'Done' for the whole change needs the SITECRAFT release gate AND the FOUNDRY claim gate both done (not waived without reason)."""
    la, lb = load(a), load(b); pr = []
    for name, log in (('SITECRAFT log', la), ('FOUNDRY log', lb)):
        pr += [f'{name}: {x}' for x in problems(log)]
    if la.get('skill') != 'sitecraft': pr.append(f'first log is not a sitecraft log (skill={la.get("skill")!r})')
    if lb.get('skill') != 'foundry-engineering': pr.append(f'second log is not a foundry-engineering log (skill={lb.get("skill")!r})')
    for name, me, other in (('SITECRAFT', la, lb), ('FOUNDRY', lb, la)):
        ln = me.get('linked') or {}
        if not me.get('run_id') or not other.get('run_id'): pr.append('both logs need a run_id to be linked'); break
        if ln.get('peer_run_id') != other.get('run_id'): pr.append(f'{name} log does not link to the other log (linked.peer_run_id must equal its run_id)')
    if not pr:
        for name, log, gid in (('SITECRAFT', la, None), ('FOUNDRY', lb, None)):
            g = last_gate(log)
            if g.get('status') not in ('done', 'waived'): pr.append(f'{name}: last gate {g["gate"]} ({g.get("name", "")}) is {g.get("status")}, so the change is not done')
        fa = next((g for g in lb['gates'] if g.get('name') == 'claims'), None)
        if not fa or fa.get('status') != 'done': pr.append('FOUNDRY: the claims gate (receipt) is not done; screenshots alone do not cover the backend')
        sa = next((g for g in la['gates'] if g.get('name') == 'shots'), None)
        if not sa or sa.get('status') != 'done': pr.append('SITECRAFT: the shots gate is not done; a receipt alone does not cover the UI')
    for x in pr: print('PROBLEM:', x)
    if pr: return 1
    print(f'ok: both sides done and linked. Lowest level claimed: {min(la["level"], lb["level"])}'); return 0

def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c')
    v = sp.add_parser('validate'); v.add_argument('file')
    r = sp.add_parser('report'); r.add_argument('files', nargs='+')
    x = sp.add_parser('cross-check'); x.add_argument('sitecraft_log'); x.add_argument('foundry_log')
    n = ap.parse_args()
    if n.c == 'validate': sys.exit(cmd_validate(n.file))
    if n.c == 'cross-check': sys.exit(cmd_cross_check(n.sitecraft_log, n.foundry_log))
    if n.c == 'report': sys.exit(cmd_report(n.files))
    ap.print_usage(); sys.exit(2)
if __name__ == '__main__': main()
