# Levels and second-agent review

## Level report (print at the start of every run)
Before step 1, state which level this run can honestly reach:
- Level 2 (Checked): you can run the bundled scripts. Try `py -3`, `python`, `python3` (Windows) or `python3`, `python` (Mac/Linux). Run `scripts/foundry_check.py --help` once to prove it.
- Level 1 (Paper): you cannot run scripts. Follow the same gates and artifacts by hand. Every claim that needs a checker is labelled UNVERIFIED (not run), and the final receipt says "Level 1: checks not executed".
- Level 3 (Full): Level 2 plus an enforcer add-on that you have seen block or log a step in this session. Never claim Level 3 on faith.
Never report a higher level than you proved. Write the level into the gate log.

## Second-agent review (optional, recommended before "passed")
`scripts/foundry_check.py review-packet receipt.json --out DIR` builds a packet (receipt, contract, evidence, changed files) with no builder reasoning. Give it to a fresh agent. It re-runs at least one check and writes review.json with its own id. A receipt may say "passed" only when that review agrees; otherwise the verdict stays "self_reviewed_only". The person coordinating decides when to stop; never tell the reviewer what answer to give.
