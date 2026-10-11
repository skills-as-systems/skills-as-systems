# FOUNDRY gates (v2)

Each gate has a stop rule, a required artifact and one entry in the gate log (`assets/gate-log.template.json`, copy to `gate-log.json` at G0). Status is `pending`, `done`, `waived` (reason in `waiver`, from the owner) or `blocked`. The log makes skipping visible. It is a checker, not a lock.

## Re-entry
On any return, read `gate-log.json` first, say which gate you are at, continue. At the end of every gate update the log and name the next gate. State lives in the file so it survives compaction and restarts. `scripts/gate_log.py validate gate-log.json` checks the log (done needs evidence, waived needs a reason, no gate done while an earlier one is pending, level claims match capabilities); `gate_log.py report a.json b.json` shows where the run is and which gates were skipped, waived or blocked across runs.

## Gates
- G0 Intake. Repo root, branch, dirty state, and what can run (tests, shell, browser, sub-agents). Read the constitution (`assets/constitution-template.md`) if the repo has one. Record the level.
- G1 Map. System map from entry points, call paths and tests. Mark each documentation claim confirmed or stale. Read code, not docs.
- G2 Contract. No edit before the owner approves the Change Contract: objective, invariants, out-of-bounds list, expected diff size, verification plan, recovery, and a task list of small steps with exact paths and expected output. Approval is section by section; log the owner's approval quote and date. The contract cites the constitution rules it relies on.
- G3 Isolate. Branch or worktree, clean baseline run recorded. Never on the owner's main working copy.
- G4 Root cause (bugs). Fill `assets/root-cause-record-template.md` before any fix: symptom, proximate cause, root cause, contributing conditions.
- G5 Red first. Show a regression test failing for the right reason before the fix (`scripts/foundry_check.py testrun --expect-fail`). Prototype, generated code and config may be waived with the owner's reason in `waiver`.
- G6 Green and wider. New test passes, then focused tests, then the wider suite; save each run's output as evidence. A run that executed 0 tests never counts (`foundry_check.py testrun`). If the suite cannot run here, record a verification gap, do not claim.
  Also run `foundry_check.py test-weakening --base <baseline>` on the diff: it flags removed assertions, added skip/xfail/only, trivially true checks, deleted test files and rewritten snapshots. Any hit fails the receipt unless the contract names it and the owner approved (`--allow-weakening "reason"`, copy the reason into the receipt).
- G7 Two-stage review. For services, run the backend pass in [backend quality](backend-quality.md) as part of stage 2. Stage 1: does the diff match the contract (spec compliance)? Stage 2: quality and risk (behaviour, compatibility, security, migration, concurrency). Use a fresh reviewer where the host allows, else mark it self-review. Output one verdict:
  Before the verdict run `foundry_check.py scope-drift --base <baseline> --contract contract.json`: it compares the changed paths with `surfaces.allowed`, `affected` and `forbidden`, and flags lockfile, CI config and test-file changes that the contract does not name. Both checks are heuristics on a diff, not locks; a moved or renamed assertion can slip past.
  - Ship: no open findings above LOW.
  - Revise: fixable findings; list them and the fix.
  - Block: a safety, data-loss, security or contract breach; stop and tell the owner.
- G8 Claim check. Every completion statement is labelled TESTED, OBSERVED, INFERRED or UNVERIFIED and tied to a check in the Verification Receipt. Run `foundry_check.py receipt`.
- G9 Checkpoint. Continuation record so the work can resume.

## Consistency check (before G8)
Compare contract, task list and receipt: every contract objective has a task, every task has evidence, every receipt claim maps to a contract item, nothing in the diff is outside the contract. Rate each finding CRITICAL, HIGH, MEDIUM or LOW. Any CRITICAL blocks G8.

## Fast path
Trivial, reversible edit: G2 notes only (still approved), G6 focused tests, G8.

## Quick commands (names a harness may map; the text works without them)
/map = G1. /contract = G2. /red = G5. /verify = G6 and G8. /review = G7. /checkpoint = G9. /gate-check = read the log and report the next gate.

## UI and backend together
When one change touches both skills, link the two gate logs and finish both. See [cross-skill](cross-skill.md).
