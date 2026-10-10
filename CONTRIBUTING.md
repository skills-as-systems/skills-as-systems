# Contributing

Thank you for helping improve Skills as Systems.

The quality bar is not “more instructions.” A contribution should make a skill more discriminating, more correct, more portable, more verifiable, or more context-efficient.

## Before proposing a change

Identify the failure or opportunity precisely:

- What real task does the current skill mishandle?
- Is the problem routing, doctrine, workflow, specialist knowledge, evidence, continuity, or host integration?
- Can an existing reference or owner absorb the improvement?
- What must remain unchanged?
- What positive, negative, adversarial, or mutation case would prevent regression?

Prefer the smallest coherent intervention. Do not add a new reference, schema, script, route, or abstraction unless it has a distinct job.

## Architectural rules

1. Keep the canonical skill provider-neutral.
2. Keep `SKILL.md` below 500 lines and comfortably below 5,000 tokens.
3. Front-load accurate activation terms in `description`.
4. Use relative, direct references from `SKILL.md`.
5. Load compact material before deep specialist material.
6. Keep repository documentation outside `skills/<name>/`.
7. Do not add host-only frontmatter or pre-approved tools to the canonical core.
8. A skill never grants file, network, credential, spending, deployment, or destructive authority.
9. Add evidence and failure cases for consequential doctrine.
10. Keep private projects, artists, reviewers, credentials, transcripts, and generated workspaces out of the repository.

## Domain boundaries

### SITECRAFT

Do not introduce a house style, framework dependency, or provider dependency. A new technique must serve an experience need and include accessibility, responsive, performance, fallback, and evidence implications when relevant.

### FOUNDRY

Do not turn a framework preference into universal engineering doctrine. A new practice must state its applicability, failure boundary, compatibility impact, and verification path.

## Validation

Run:

```text
python3 scripts/validate_repository.py
python3 scripts/smoke_install.py
python3 skills/sitecraft/run_tests.py
python3 skills/foundry-engineering/run_tests.py
```

If the change affects routing, add or update positive and negative cases. If it changes a schema or invariant, add a mutation that fails for the intended reason. If it changes host packaging, test both Codex and Claude directory layouts.

## Pull requests

Explain:

- the observed problem;
- the smallest chosen change;
- changed surfaces;
- evidence collected;
- compatibility or migration impact;
- remaining uncertainty.

Do not claim live host, browser, audio, security, performance, or deployment verification unless it was actually performed.
