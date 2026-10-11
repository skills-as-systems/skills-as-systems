# Evaluation and release evidence

## Evaluation philosophy

Skill quality is behavioral. A package can have valid YAML and still route badly, load too much, invent authority, or reward plausible-looking failure.

The suite therefore uses several independent layers. Each layer supports different claims.

## Gate 1: package integrity

Repository validation checks:

- required files and canonical directory names;
- Agent Skills frontmatter and description length;
- compact-core line and approximate token budgets;
- direct relative link integrity;
- package versions and host metadata;
- absence of repository-only READMEs inside skill packages;
- absence of generated builds, browser profiles, logs, caches, credentials, and machine-specific paths;
- package size ceilings;
- Claude marketplace and plugin structure;
- Codex project-discovery links.

This proves structural readiness, not task quality.

## Gate 2: skill-specific regression suites

### SITECRAFT

The suite exercises contracts, cross-artifact drift, portable workspace creation, image and video production graphs, responsive/platform evidence, capability ownership, handoff authority, learning promotion, and provider-neutral routing.

Important negative properties include:

- builds do not prove visuals;
- screenshots do not prove interaction or accessibility;
- generated media providers are optional;
- public packages do not contain active provider configuration;
- host capabilities do not become experience requirements;
- handoffs carry no permissions, secrets, or hidden reasoning.

### FOUNDRY

The suite exercises system maps, change contracts, verification receipts, continuation records, routing scenarios, project identity, evidence classes, dependency links, carried authority, and invalid mutations.

Important adversarial properties include:

- coding before understanding;
- weakening tests to get green output;
- generated-file edits;
- version and environment assumptions;
- fake performance and security claims;
- broad exception swallowing;
- unsafe migrations and concurrency neglect;
- completion claims wider than the evidence.

## Gate 3: routing

Routing tests operate at two levels:

1. **skill activation:** which of SITECRAFT or FOUNDRY should activate;
2. **internal paging:** which compact and specialist references should load.

Cases include:

- clear positive triggers;
- explicit negative requests;
- adjacent-domain ambiguity;
- multi-skill tasks;
- negated keywords;
- provider names that must not broaden generic routes;
- large tasks that should load compacts before deep atlases.

Automated routing data checks structure and expected boundaries. Model-level activation remains a host evaluation because different hosts use different retrieval systems.

## Gate 4: artifact mutations

A valid example is necessary but weak: it can pass while the validator ignores important fields.

Mutation tests deliberately introduce invalid states, including:

- mismatched project or contract identity;
- a passing verdict with unverified required claims;
- dangling evidence, risk, dependency, or capability references;
- a continuation record that carries permissions;
- stale downstream state after an upstream decision changes;
- unsupported cultural certainty or reviewer scope;
- missing rollback or recovery information where required.

The test passes only when the invalid artifact fails for the intended reason.

## Gate 5: clean installation

`scripts/smoke_install.py` creates temporary projects and installs both skills into:

- Codex project scope: `.agents/skills/<name>`;
- Claude Code project scope: `.claude/skills/<name>`.

It then verifies package identity, file completeness, frontmatter names, and byte-for-byte `SKILL.md` equality with the source.

This is an installation-layout test. It does not claim a live Codex or Claude session invoked the skill.

## Gate 6: representative work

Release candidates should be exercised against tasks such as:

### SITECRAFT

- frame a new product experience from a sparse brief;
- repair a visually broken existing site without rewriting it;
- audit responsive behavior, accessibility, and release evidence;
- create a generated-media plan with fallbacks and spend boundaries;
- reject a visually impressive but incoherent or unverified result.

### FOUNDRY

- explain an unfamiliar repository and its behavioral path;
- add a small feature without an unnecessary rewrite;
- debug an environment-versus-code failure;
- repair a concurrency defect;
- perform a safe migration;
- review a risky change;
- recover from interrupted or concurrent work;
- catch green unit tests masking broken integration.

The receiving model and host version, supplied context, tools, exact prompt, output, evaluator, and evidence should be recorded.

## Gate 7: paired public showcases

The [`benchmarks/`](../benchmarks/) directory adds outcome-level checks with a
baseline condition and a skill condition. Each showcase freezes its seed,
prompt, rubric, and evaluator before the agents run; isolates the workspaces;
publishes final artifacts rather than private reasoning; and separates
deterministic checks from subjective review.

The first three runs produced parity rather than a universal uplift claim. That
is valid evidence. A benchmark is allowed to show that a strong current model
solves a bounded task without the skill. Findings may improve a skill, but the
new version is never retroactively credited with an older output.

Repeat conditions before generalizing. Model sampling, host capability, task
selection, evaluator coverage, and reviewer judgment all remain sources of
variance.

## Release receipt

A public release should state:

- package versions and commit;
- structural validator result;
- skill suite results;
- official Agent Skills validator result;
- clean-install smoke result;
- Claude plugin validation result when Claude Code is available;
- representative host/scenario results actually run;
- unverified platforms or behaviors;
- known compatibility and migration risks.

Never collapse these into “all tests passed.”

## What the current automated suite does not prove

It does not by itself prove:

- every Codex or Claude model will route identically;
- visual quality in a real browser;
- production security, performance, or reliability;
- absence of all legal, cultural, or operational risk.

Those claims require their own observations, reviewers, environments, and evidence.
