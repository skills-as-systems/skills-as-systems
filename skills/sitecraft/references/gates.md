# SITECRAFT gates (v2)

Each gate has a stop rule, a required artifact and one entry in the gate log (`assets/gate-log.template.json`, copy it to `gate-log.json` in the project at Gate 0). A gate is `pending`, `done`, `waived` (with the buyer's reason in `waiver`) or `blocked`. The log makes skipping visible. It does not stop a determined model from skipping; it is a checker, not a lock.

## Re-entry
On any return to the work, read `gate-log.json` first, say which gate you are at, then continue. At the end of every gate: run the checker if you can, update the log, name the next gate. State lives in the file so it survives compaction and restarts. `scripts/gate_log.py validate gate-log.json` checks the log (done needs evidence, waived needs a reason, no gate done while an earlier one is pending, level claims match capabilities); `gate_log.py report a.json b.json` shows where the run is and which gates were skipped, waived or blocked across runs.

## Gates
0. Intake. Fill `assets/PRODUCT.template.md` as PRODUCT.md (who, visitor jobs, constraints, voice). Stop until the buyer has answered or waived the open questions. Also record capabilities (shell, browser) and the level in the log.
1. Design sheet. Fill `assets/DESIGN.template.md` as DESIGN.md: tokens as roles, theme strategy, type, dials (density, motion, variance), quality bar, ban list, page overrides. The buyer approves it; log the approval quote and date. Libraries and examples propose; the buyer's sheet decides.
2. Direction. Show two structurally different layout sketches. The buyer picks one. Log the pick.
3. Build in slices. One slice at a time, each checked against the sheet before the next.
4. Shots. Desktop, mobile and 320px screenshots of every changed page and state. No browser: say "not verified: no browser" and mark the gate `blocked` or `waived`.
5. Fix loop. List defects, fix, re-shoot, compare. Cap at 3 rounds, then stop and ask the buyer ("stuck").
6. Critique. Score against the fixed rubric (`evaluation-rubric.md`), by a fresh reviewer when the host allows. Self-review is labelled as such.
7. Budget. Run `scripts/sitecraft_check.py` on the output (add `--ban` with the sheet's ban list). With `--sheet design-sheet.json` (format: `assets/design-sheet.example.json`) it also flags colours and fonts that are not on the sheet (errors) and spacing off the scale (warnings); alpha colours and `var()` uses are skipped. Record page weight, fallbacks for unsupported browsers, reduced motion and save-data, and any third-party script or telemetry and its licence.
   Optional Level 2.5: `scripts/render_check.py PAGE` renders in a real browser at 320, 390 and 1440 px (needs Playwright; axe-core via `--axe PATH`) and checks overflow, tap targets under 24px, focus after Tab, console errors and axe violations. If it cannot start it exits 3 "NOT RUN": report Level 2, not 2.5. It checks the page as loaded; it does not prove the site works for every user.
8. Release. Release record: what shipped, level reached, open defects, what was not verified. Print the Level report.

## Fast path
Small, reversible edits on an existing site with an approved sheet: skip gates 0 to 2 (log them `waived: existing sheet`), then do 3, 4, 7 and 8.

## Short commands (names a harness may map; the text works without them)
/shape = gates 0 to 2. /craft = gate 3. /shoot = gate 4. /critique = gate 6. /audit = gate 7. /polish and /harden (long text, wrapping, empty and error states, interrupted animation) = gate 5. /gate-check = read the log and report the next gate.

## Optional re-check by a fresh reviewer
Critique and verify may hand the artifacts to a fresh reviewer that re-enters with only those files. Opt-in, 3 rounds at most, report new findings only.
