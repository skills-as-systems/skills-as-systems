# Skills as Systems

[![Validate](https://github.com/skills-as-systems/skills-as-systems/actions/workflows/validate.yml/badge.svg)](https://github.com/skills-as-systems/skills-as-systems/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

I'm Gbemi Akadiri, and I made these two portable Agent Skills.

- **SITECRAFT** is my skill for planning, designing, building, repairing, auditing, and releasing web experiences.
- **FOUNDRY** is my skill for understanding, changing, debugging, reviewing, testing, and recovering software systems.

> A skill should not be a giant prompt. It should be a small, testable operating system for judgment.

Both skills follow the open [Agent Skills specification](https://agentskills.io/specification). I built them so they don't need Codex, Claude Code, or any particular model provider.

## Install in under a minute

### Easiest: ask your agent

Paste this into a capable coding agent:

```text
Install SITECRAFT and FOUNDRY from https://github.com/skills-as-systems/skills-as-systems for this harness at user scope. Prefer the harness's native skill or plugin installer. Otherwise clone the repository and use its portable installer. Verify that both skills are discoverable, report their exact installed paths, and tell me whether a reload or restart is needed. Do not add tool permissions or configure external services.
```

### Codex

Paste this into Codex:

```text
$skill-installer Install sitecraft and foundry-engineering from https://github.com/skills-as-systems/skills-as-systems for my user account. Verify both appear in the skill picker or /skills, report their installed paths, and tell me if Codex needs a restart.
```

Or use one terminal line:

```bash
git clone --depth 1 https://github.com/skills-as-systems/skills-as-systems.git && python3 skills-as-systems/scripts/install.py codex
```

Codex loads user skills from `$HOME/.agents/skills`. See the official [Codex skills documentation](https://developers.openai.com/codex/skills/).

### Claude Code

Use one terminal line:

```bash
claude plugin marketplace add skills-as-systems/skills-as-systems && claude plugin install skills-as-systems@skills-as-systems
```

Or paste this into Claude Code:

```text
Add skills-as-systems/skills-as-systems as a plugin marketplace, install the skills-as-systems plugin, reload plugins if requested, and verify that sitecraft and foundry-engineering are available.
```

See the official [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).

### Another Agent Skills host

Ask the agent to copy either complete directory from `skills/` into its configured skill location. Keep the directory name unchanged. For a local checkout, you can also run:

```bash
python3 scripts/install.py --target /path/to/your/skills
```

For project-only installation, advanced replacement, symlink, and removal guidance, see [Portability and installation](docs/portability.md).

## Use the skills

### SITECRAFT

Codex:

```text
$sitecraft Build this product brief into a distinctive responsive website, then verify the important states.
```

Claude Code plugin:

```text
/skills-as-systems:sitecraft Audit this website's visual hierarchy, responsiveness, accessibility, and release evidence.
```

### FOUNDRY

Codex:

```text
$foundry-engineering Map this unfamiliar repository, trace the failing behavior, make the smallest safe fix, and prove it works.
```

Claude Code plugin:

```text
/skills-as-systems:foundry-engineering Review this change for behavioral, compatibility, security, and migration risk.
```

Capable hosts can also activate either skill automatically when the request matches its description.

## Choose the right skill

| Skill | Version | Use it for | Central artifact |
| --- | ---: | --- | --- |
| [SITECRAFT](docs/sitecraft.md) | 0.3.1 | Websites, web applications, responsive experience, visual systems, interaction, accessibility, and release evidence | Experience Contract |
| [FOUNDRY](docs/foundry.md) | 0.2.1 | Codebase understanding, implementation, debugging, testing, review, architecture, migrations, reliability, security, and performance | Change Contract |

Use both when a task changes a web experience and the software system behind it.

## What makes these different

I split each skill into six jobs that ordinary prompts tend to mix together:

1. **Route:** decide whether the skill applies and which part is needed.
2. **Understand:** inspect the real project or problem before producing work.
3. **Contract:** record what should change, what must remain true, and what owns the decision.
4. **Act:** make the smallest coherent intervention.
5. **Verify:** match every completion claim to appropriate evidence.
6. **Continue:** leave compact state another agent or human can safely resume.

I only load the detailed specialist references when they're needed. My failure tests aim at plausible-looking mistakes such as unnecessary rewrites, guessed capabilities, weakened tests, unsupported visual claims, and fake completion.

I also wrote two small checkers that run without a network: `sitecraft_check.py` for pages and `foundry_check.py` for test runs and receipts. They catch things like low-contrast text, missing alt text, an empty test run counted as a pass, and a receipt that claims more than its evidence shows. They only help when the agent actually runs them. They're checkers, not locks.

[The architecture](docs/architecture.md) has the complete model, and [the evaluation guide](docs/evaluation.md) covers what the test suite does and doesn't prove.

## See the work, including the inconvenient results

I've included the frozen prompts, seeds, final projects, screenshots,
deterministic evaluators, blind review, and machine-readable receipts from fresh
paired Codex runs.

| Showcase | Baseline | With skill | Honest result |
| --- | ---: | ---: | --- |
| [TIDEGLASS web experience](benchmarks/sitecraft-tideglass/) | 97.5 | 97 | High-quality parity; baseline led by 0.5 in one blind review. |
| [Ledgerbox transaction repair](benchmarks/foundry-ledger-repair/) | 100 | 100 | Correctness parity; FOUNDRY collected wider crash/concurrency evidence. |
| [Relaypack artifact repair](benchmarks/foundry-relaypack-boundary/) | 100 | 100 | Correctness parity; baseline carried broader permanent regression coverage. |

![SITECRAFT TIDEGLASS desktop output](benchmarks/sitecraft-tideglass/evidence/with-sitecraft/desktop-1440x1000.png)

These examples aren't a leaderboard, and they don't prove the skills help everywhere. They
show how I test skills without hiding a strong baseline. The first findings led
me to make the SITECRAFT artifacts smaller and strengthen the FOUNDRY package regressions. The
[benchmark method and limitations](benchmarks/) are written up there.

## Portable core, optional adapters

The canonical packages live under `skills/`. Their doctrine and references are provider-neutral.

- `agents/openai.yaml` adds optional Codex presentation metadata.
- `.claude-plugin/` packages both skills for Claude Code distribution.

None of these files give permission to use tools, write files, deploy, spend money, or access accounts. The receiving host and user remain the authority.

## Validate the repository

Run the complete repository checks:

```bash
python3 scripts/validate_repository.py && python3 scripts/smoke_install.py
```

GitHub Actions also validates both packages, the installer, routing fixtures, and clean Codex and Claude directory layouts on every push.

## Repository map

```text
skills/                 Portable skill packages
.agents/skills/         Codex project-discovery links
.claude-plugin/         Claude Code marketplace metadata
docs/                   Architecture, evaluation, and portability guides
benchmarks/              Paired projects, frozen prompts, evaluators, and evidence
evaluations/            Cross-skill routing fixtures
scripts/                Safe installer and repository validation
```

## Contributing and security

I'd like contributions to make a skill more correct, portable, discriminating, verifiable, or context-efficient. See [CONTRIBUTING.md](CONTRIBUTING.md).

Report security problems using [SECURITY.md](SECURITY.md). Do not publish credentials, private project data, or production artifacts in an issue.

## License

Copyright 2026 **Gbemi Akadiri**.

Licensed under the [Apache License 2.0](LICENSE).
