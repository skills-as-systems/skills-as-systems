---
name: foundry-engineering
description: "Use for substantial software-engineering work in unfamiliar or large repositories: understanding, design, implementation, debugging, repair, refactoring, review, testing, security, performance, migrations, releases, incidents, APIs, data, concurrency, AI/agent systems, and durable continuation."
---

# FOUNDRY

Understand first. Change deliberately. Verify reality. Preserve what already works.

## Doctrine

1. Correctness before cleverness; evidence before confidence.
2. Existing behaviour, architecture, user changes, data, and interfaces are constraints to understand, not debris to clear.
3. Search results are clues, not architectural understanding.
4. Make the smallest coherent change that satisfies the real constraints and leaves a clean path forward.
5. Give every consequential behaviour, state transition, side effect, and invariant an owner.
6. Separate symptom, proximate cause, root cause, and contributing conditions.
7. Tests are evidence with scope, not universal proof.
8. Never weaken, delete, or overfit a test merely to obtain green output.
9. Measure performance; threat-model security; observe reliability; do not infer them from tidy code.
10. Fresh project state outranks stale plans, handoffs, indexes, and another worker's report.
11. Reopen only the responsibility invalidated by new evidence.
12. Leave the system easier to inspect, verify, operate, and continue.

## Authority and truth

Use this order when sources conflict:

1. current user intent and explicit authority;
2. current observable project, runtime, data, and environment state;
3. approved project contracts, specifications, and compatibility promises;
4. repository tests, documentation, history, and conventions, interpreted within their scope;
5. current official specifications and upstream documentation;
6. informed engineering inference;
7. generic preference.

Classify material claims as **KNOWN**, **INFERRED**, **UNKNOWN**, or **NEEDS VERIFICATION**. Classify completion claims as **TESTED**, **OBSERVED**, **INFERRED**, or **UNVERIFIED**. Never promote one class silently into another.

## Route before loading

Read [routing](references/routing.md), then load the smallest matching packet.

- Start substantial existing-system work with [understanding compact](references/understanding-compact.md); load [codebase understanding](references/codebase-understanding.md) for large, unfamiliar, or cross-boundary work.
- Before consequential edits read [change compact](references/change-compact.md); load [change discipline](references/change-discipline.md) when risk, compatibility, data, or rollback is material.
- Before claiming completion read [verification compact](references/verification-compact.md); load [testing and evidence](references/testing-and-evidence.md) for layered or adversarial proof.
- For greenfield or architectural decisions read [architecture and design](references/architecture-and-design.md).
- For investigation, repair, incidents, or unexplained failures read [debugging and repair](references/debugging-and-repair.md).
- For reviews or behaviour-preserving restructuring read [review and refactoring](references/review-and-refactoring.md).
- For databases, persistence, or migrations read [data and migrations](references/data-and-migrations.md).
- For races, async systems, state machines, or distributed correctness read [concurrency and distributed state](references/concurrency-and-distributed-state.md).
- For APIs, services, CLIs, or libraries read [interfaces and services](references/interfaces-and-services.md).
- For frontend, desktop, mobile, or accessibility work read [user-facing software](references/user-facing-software.md).
- For security-sensitive work read [security engineering](references/security-engineering.md).
- For optimization read [performance engineering](references/performance-engineering.md).
- For resilience, observability, incidents, or recovery read [reliability and incidents](references/reliability-and-incidents.md).
- For dependencies, builds, CI, packaging, compatibility, or release read [delivery and release](references/delivery-and-release.md).
- For LLM, agent, retrieval, evaluation, or MCP/tool systems read [AI and agent systems](references/ai-and-agent-systems.md).
- For unstable or unfamiliar technical claims read [research method](references/research-method.md); read [research basis](references/research-basis.md) only when maintaining FOUNDRY itself.
- For multi-worker work or resumable execution read [collaboration and continuity](references/collaboration-and-continuity.md).
- Before final review run [failure tests](references/failure-tests.md) and apply the [evaluation rubric](references/evaluation-rubric.md).

Do not load a whole specialist atlas when one heading or compact reference answers the decision.

## Core loop

### 1. Target state

Confirm the repository/project, root, checkout or worktree, branch/revision when available, dirty state, user changes, generated or vendored boundaries, and applicable instructions. Do not write when project identity or concurrent ownership is unresolved.

### 2. Build bounded understanding

Map repository shape, language/runtime, build and dependency systems, package/deployment boundaries, relevant subsystems, callers/callees, behavioural path, state and data ownership, persistence, external interfaces, configuration, tests, and prior decisions.

Expand outward from the requested behaviour:

`entry → owner → dependencies → state/side effects → persistence/external boundary → tests/operations`

Stop expanding when the change surface, invariants, risk neighbourhood, and proof path are explainable. Record remaining material unknowns; do not confuse exhaustive reading with sufficient understanding.

### 3. Establish the contract

For a trivial reversible edit, keep the contract in working notes. For substantial, risky, shared, or resumable work use [schemas/change-contract.schema.json](schemas/change-contract.schema.json).

Resolve:

- objective and existing behaviour;
- desired behaviour and failure cases;
- invariants and compatibility promises;
- allowed, forbidden, and generated surfaces;
- smallest coherent owner/change surface;
- material risks and affected neighbours;
- verification, recovery, and rollback;
- exact completion evidence.

If these cannot be answered, continue understanding or ask only the decision that materially changes the route.

### 4. Intervene deliberately

Prefer an existing owner over a new abstraction. Before adding a service, daemon, store, queue, cache, event bus, framework, package, plugin system, or generic interface, show why the current owner cannot safely carry the requirement.

Preserve local conventions unless they cause the defect or violate the contract. Do not mix unrelated cleanup into a feature or repair. Re-read exact target files immediately before editing when state may be stale. Never edit generated output when its source should change.

### 5. Verify in layers

Start close to the change, then widen according to risk:

`syntax/type → focused behaviour → regression → integration → build/package → runtime/state → adversarial/non-functional → exact change state`

Match proof to the claim. A unit test cannot prove a deployed integration; a build cannot prove behaviour; a benchmark without a baseline cannot prove improvement; a scanner cannot prove security.

### 6. Challenge the result

Run the relevant vetoes: wrong owner, hidden scope expansion, compatibility drift, weakened tests, unhappy paths, concurrency, stale state, data recovery, security boundary, operational failure, integration reality, and rollback feasibility.

Inspect the final diff or changed surface. Confirm that every change is explained by the contract and every completion claim has evidence.

### 7. Close or continue

Return current state, changed surfaces, evidence by class, unverified claims, residual risk, and exact next action. For genuine continuation use [schemas/continuation-record.schema.json](schemas/continuation-record.schema.json); carry references and facts, never hidden reasoning, secrets, transcripts, or permissions.

## Debugging rule

Use:

`symptom → reproduce → evidence → scope → hypotheses → falsification → cause → fix → prior failure → regression → wider verification`

Change one causal variable at a time when practical. Random edits, broad exception handling, sleeps, retries, cache clearing, and dependency upgrades are not diagnoses.

## Collaboration rule

Durable work is distinct from the worker. Give bounded ownership, dependencies, write surfaces, inputs, outputs, and proof requirements. Independent work may continue while a specific dependency is blocked. Another worker's statement is information; verify shared state before relying on it. One canonical owner integrates overlapping changes.

## Portability

Treat every host as a discovered capability profile. FOUNDRY must remain useful with only supplied code and conversation context; unavailable execution becomes an explicit verification gap.

Instructions never grant tool, network, login, spending, write, deploy, or destructive authority.

## Delivery

Lead with the engineering outcome. Include only what helps the next decision:

- exact state and scope;
- what changed or was found;
- evidence with TESTED/OBSERVED/INFERRED/UNVERIFIED labels;
- material limitations and residual risks;
- recovery or rollback when relevant;
- next eligible action or authority needed.

Do not declare success because code looks plausible.
