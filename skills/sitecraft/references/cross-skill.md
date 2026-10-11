# Changes that touch both the UI and the backend

Use SITECRAFT for the interface and FOUNDRY for the code behind it, each with its own gate log. The same text is in FOUNDRY's `references/cross-skill.md`.

1. Give each log a `run_id` and a `linked` block pointing at the other: `"linked": {"peer_run_id": "<other run_id>", "experience_contract": "<id or path>", "change_contract": "<id or path>"}`.
2. The Experience Contract (what the visitor must be able to do) and the Change Contract (what code may change, what must not break) name each other. Every visitor job that needs a backend change is a contract objective on the FOUNDRY side. Every backend change that a visitor can see is a slice on the SITECRAFT side.
3. "Done" for the whole change needs both: SITECRAFT's `shots` gate (screenshots of every changed page and state) and FOUNDRY's `claims` gate (a receipt with labelled claims), plus each log's last gate done or waived with a reason. Screenshots do not prove the API works; a receipt does not prove the page looks right.
4. Check with `python3 scripts/gate_log.py cross-check sitecraft-gate-log.json foundry-gate-log.json`. It checks both logs, the link, the two gates and reports the lowest level claimed. It is a checker, not a lock.
5. If one side cannot run here (no browser, no tests), say "not verified: <what>" in that log; do not mark the gate done.
