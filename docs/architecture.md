# Architecture: skills as systems

## The short version

A Skills as Systems package has six simple responsibilities:

```text
route → understand → contract → act → verify → continue
```

- **Route:** activate for the right task and load only relevant knowledge.
- **Understand:** inspect the real project, constraints, and current behavior first.
- **Contract:** state the intended outcome, invariants, boundaries, risks, and proof plan.
- **Act:** make the smallest coherent intervention.
- **Verify:** match claims to evidence and challenge plausible-looking failure.
- **Continue:** leave compact, exact state another worker can resume.

Everything else in this document explains how the packages make those responsibilities portable and testable.

## Purpose

Skills as Systems is an architecture for turning domain judgment into portable, testable agent behavior.

The goal is not to make a model follow more instructions. It is to help a capable model decide:

- when a body of expertise applies;
- what it must understand before acting;
- which specialist knowledge is relevant now;
- which artifact owns the current decision;
- what failure would look like;
- what evidence can support the final claim;
- what another host or worker needs to continue safely.

This architecture is used by SITECRAFT and FOUNDRY. Their domains differ, but the systems share the same structural responsibilities.

## The eight layers

### 1. Discovery metadata

The host normally sees `name` and `description` before it sees the full skill. That makes the description a router, not marketing copy.

A strong description:

- begins with the situations in which the skill should be used;
- uses the vocabulary users naturally put in requests;
- distinguishes adjacent skills;
- stays compact enough to survive host startup budgets;
- never implies capabilities or permissions the host may not have.

The canonical frontmatter uses only the portable Agent Skills fields needed by both Codex and Claude Code. Host-only invocation controls and tool pre-approvals stay outside it.

### 2. Compact doctrine

Doctrine is the small set of principles that should remain true across routes.

It is not a style guide. It resolves recurring tensions:

- SITECRAFT: purpose before surface; visual evidence differs from code correctness.
- FOUNDRY: understand first; evidence before confidence; preserve existing behavior deliberately.

Doctrine belongs in `SKILL.md` because the host must have it whenever the skill is active.

### 3. Director or operating loop

Each skill has one thin orchestration responsibility:

- SITECRAFT routes Frame, Map, Compose, Choreograph, Build, Observe, and Harden.
- FOUNDRY routes engineering modes and applies its target-understand-contract-intervene-verify-challenge-close loop.

The director does not contain every specialist answer. It decides what needs answering and who or what owns the answer.

### 4. Progressive specialist knowledge

References are capability pages, not chapters in a compulsory textbook.

The loading pattern is:

```text
metadata → compact core → route or compact reference → specialist depth → project evidence
```

Good reference boundaries follow decisions:

- a compact tells the agent what to notice and when to go deeper;
- a deep reference supplies the specialist method;
- an atlas is loaded by heading or bounded packet rather than in full;
- references do not restate the entire core;
- a reference must earn its context through a distinct decision or failure boundary.

This is both a context optimization and a quality mechanism. Irrelevant knowledge can create confident but inappropriate work.

### 5. Canonical artifacts

Substantial work needs a stable owner that survives revisions and host changes.

| Skill | Canonical artifact | Responsibility |
| --- | --- | --- |
| SITECRAFT | Experience Contract | Experience intent, visual grammar, behavior, responsive rules, assets, implementation, evidence, and release boundaries |
| FOUNDRY | Change Contract | Existing and desired behavior, invariants, allowed and forbidden surfaces, risk, verification, and recovery |

Artifacts are optional for trivial work and valuable for risky, shared, resumable, or multi-stage work. They are not paperwork quotas.

The authority rule is consistent: generated output, reviews, councils, builders, and handoffs can propose changes to the artifact; none silently replaces it.

### 6. Evidence and failure tests

The skills define evidence by claim, not by ceremony.

Examples:

- a screenshot can support a visual-state claim but not keyboard accessibility;
- a unit test can support focused behavior but not a live deployment;
- a benchmark without a baseline cannot prove improvement;
- another worker's report is information, not fresh system state.

Failure tests veto plausible-looking output. They target common agent failures such as premature production, hidden scope expansion, default solutions, weakened tests, invented capabilities, fake completion, and unsupported release claims.

### 7. Continuity

Long work should not depend on a giant Markdown handoff or recursively summarized transcript.

A continuation record carries only durable working truth:

- objective and current state;
- established findings and their evidence;
- changed or approved surfaces;
- important invariants;
- unresolved issues and dependencies;
- exact references;
- next eligible action;
- fresh-state checks required before resuming.

It carries no hidden reasoning, secret, private transcript, or transferred permission.

### 8. Optional host enhancement

The skill discovers the host's capabilities at runtime. A host may add:

- file inspection and guarded editing;
- schema or script execution;
- browser, audio, image, or runtime observation;
- research and connected tools;
- durable state and collaboration;
- provider integrations;
- richer interface metadata.

These capabilities do not change the canonical doctrine. Missing capability becomes a named evidence gap or a bounded handoff.

## Authority and truth

The skills use domain-specific authority orders, but share one rule: current reality outranks stale prose.

A useful general order is:

1. current user intent and explicit authority;
2. current observable project, artifact, runtime, or supplied source;
3. approved contracts and compatibility promises;
4. relevant repository, historical, or domain evidence;
5. current official specifications and primary sources;
6. bounded professional inference;
7. generic preference.

The skill's text is not automatically the highest authority. It can be wrong, outdated, or irrelevant to a project-local constraint.

## Context budgets as architecture

Context efficiency is not achieved by making every skill shallow. It is achieved by separating stable operating knowledge from conditional specialist depth.

The packages use four practical budgets:

- **discovery budget:** a short name and front-loaded description;
- **activation budget:** a compact `SKILL.md`, below host compaction and Agent Skills recommendations;
- **decision budget:** a small route-specific packet;
- **evidence budget:** exact project files, artifacts, outputs, and observations needed for the decision.

No skill should load all references merely because they exist.

## Contracts without bureaucracy

A contract is justified when it prevents one of these failures:

- several passes are changing the same outcome;
- upstream decisions can make downstream work stale;
- approval scope matters;
- compatibility or rollback matters;
- evidence must be associated with exact claims;
- another worker or host must continue;
- private and public knowledge must remain separate.

For a small reversible task, the same fields can remain in working notes. The artifact exists to reduce ambiguity, not to create forms.

## Evaluation as product behavior

Validation is layered:

1. **Structural:** specification, metadata, paths, budgets, schemas, package hygiene.
2. **Routing:** positive activation, negative exclusion, bounded specialist selection.
3. **Artifact:** valid examples plus invalid mutations that fail for the intended reason.
4. **Adversarial:** plausible shortcuts, fake evidence, authority leakage, privacy leakage, and compatibility drift.
5. **Scenario:** representative end-to-end tasks across modes.
6. **Host:** clean installation and, where available, real Codex or Claude activation.

A structural pass does not prove that a model will use the skill well. A scenario pass on one model does not prove universal behavior. The receipt should name the layer actually tested.

## Learning without doctrine drift

The skills distinguish:

- project-local convention;
- environment quirk;
- verified reusable pattern;
- failure pattern;
- framework, domain, or provider-specific lesson;
- candidate change to public doctrine.

Promotion requires evidence, scope, counterexample risk, and review. One successful project does not rewrite the public skill.

## Anti-patterns

The architecture resists:

- one giant prompt;
- one workflow for every task;
- host or framework lock-in hidden inside doctrine;
- deeply chained references;
- duplicate canonical state;
- reviews that become authority by verbosity;
- automatic tool permission in skill metadata;
- private project material in public packages;
- tests that prove only that the test was weakened;
- release claims broader than the observed evidence;
- learning based on one anecdote;
- handoffs that contain transcripts instead of state.

## Maintenance test

Before adding a component, ask:

1. Which real failure does this prevent?
2. Why can an existing owner not handle it?
3. When should it load?
4. What context and maintenance cost does it add?
5. What positive and negative case proves the routing?
6. What mutation or adversarial case proves the rule?
7. Is it portable doctrine, domain depth, project-local knowledge, or a host adapter?
8. How can it be removed or revised without breaking canonical state?

If those questions have no concrete answers, the addition is probably not ready.
