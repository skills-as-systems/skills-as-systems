# Collection 1.1.0 release receipt

Date: 2026-08-15

## Exact scope

- SITECRAFT 0.3.1
- FOUNDRY 0.2.1
- Claude Code collection plugin 1.1.0
- three paired Codex showcase benchmarks with baseline and skill conditions

## Changes

- SITECRAFT now distinguishes a compact working contract from a full durable
  Experience Contract, preventing small single-surface builds from generating
  schema-shaped paperwork without a continuity need.
- FOUNDRY packaging repairs now require the permanent regression to build,
  inspect, install, isolate, and exercise the incident-relevant artifact
  contracts.
- Public paired projects include frozen prompts, seeds, rubrics, final outputs,
  screenshots, blind review, deterministic evaluators, mutation checks, and
  machine-readable receipts.
- CI installs the official Agent Skills reference validator from pinned upstream
  commit `69ef37e9424c0a7ea9dd2293b559e43ec8176379`; `skills-ref` is not currently
  published on PyPI.

## TESTED locally

- SITECRAFT package validator: passed.
- SITECRAFT test suite: 22 tests passed.
- FOUNDRY package validator: passed with 25 references, 22 positive routing
  cases, and 17 adversarial evaluation cases.
- FOUNDRY test suite: 14 tests passed.
- FOUNDRY deterministic scenario evaluator: passed, including 6 negative routes
  and 4 artifact corruption gates; largest routed packet remained below its
  22,000-character ceiling.
- Official upstream `skills-ref` validation: both source packages and both fresh
  archive extractions passed.
- Clean-install smoke: Codex and Claude project layouts both passed with exact
  canonical package copies.
- Public benchmark validator: paired outputs, result receipts, privacy hygiene,
  and all deterministic reruns passed from their repository copies.
- TIDEGLASS browser evidence: Google Chrome through Playwright passed at
  1440×1000, 390×844, and 320×800, plus reduced-motion and declared pointer,
  keyboard, selected-state, invalid, submitting, success, failure, and no-network
  checks for both conditions.

## Benchmark results

| Showcase | Baseline | Skill condition | Supported conclusion |
| --- | ---: | ---: | --- |
| TIDEGLASS | 97.5/100 | 97/100 | One high-quality parity result; 0.5-point blind-review difference is not a general claim. |
| Ledgerbox | 100/100 | 100/100 | Correctness parity; FOUNDRY gathered wider crash and concurrency evidence. |
| Relaypack | 100/100 | 100/100 | Correctness parity; baseline carried broader permanent regression coverage. |

The paired work used SITECRAFT 0.3.0 and FOUNDRY 0.2.0. The findings informed
0.3.1 and 0.2.1, but the revisions are not retroactively credited with the old
outputs.

## Portable archives

- `sitecraft-0.3.1.zip` — SHA-256
  `dc5146a722f37b9238a887f03125a99b1d8f093d1e4456c01f9e0341a8c2adb1`
- `foundry-engineering-0.2.1.zip` — SHA-256
  `8e1f498274e3691c6cddb428db3a335203b73745703375decabafca436727be9`

Each archive was freshly extracted and passed its package suite plus the pinned
official Agent Skills reference validator.

## OBSERVED but not overclaimed

- Browser evidence is headless Chrome on this machine, not screen-reader,
  native-device, production, or cross-browser approval.
- The clean Claude directory layout and plugin JSON are validated; a live Claude
  Code CLI was not available in this task environment, so plugin marketplace
  installation was not rerun for 1.1.0.
- GitHub Actions is an external commit-level check; its live result is recorded on GitHub rather than predicted by this pre-push receipt.
- No package registry publication, deployment, production load, or security
  certification is claimed.
