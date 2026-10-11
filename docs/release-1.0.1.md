# Collection 1.0.1 release receipt

Date: 2026-08-15

## Scope

- SITECRAFT 0.3.0
- FOUNDRY 0.2.0
- Claude Code collection plugin 1.0.1

## Corrections and improvements

- Public authorship, ownership, copyright, and Git attribution use **MAKIAVELI** only.
- The repository README now leads with one-prompt and one-line installation paths.
- Codex and standalone Claude installs from a checkout accept `install.py codex|claude`.
- SITECRAFT, FOUNDRY, architecture, and portability documents now begin with a plain-language quick start.
- The portable skill doctrine remains provider-neutral and unchanged by the onboarding simplification.

## Local release evidence

- Tracked files and filenames contain only the intended public skill material and attribution.
- Official Agent Skills validation passes for both canonical packages.
- Repository validation, clean-install smoke tests, 22 SITECRAFT tests, and 14 FOUNDRY tests pass.
- FOUNDRY's evaluator passes 22 positive, 6 negative, 16 adversarial, and 4 mutation-gate cases.
- Claude Code 2.1.232 accepts the marketplace and plugin manifests and installs exactly the two intended skills at plugin version 1.0.1.

## Public release evidence

- A fresh public clone installs SITECRAFT and FOUNDRY into a clean Codex project with the short installer form.
- Claude Code 2.1.232 adds `makiaveli1/skills-as-systems` as a marketplace and installs exactly those two skills at plugin version 1.0.1.
- [GitHub Actions run 31878388283](https://github.com/makiaveli1/skills-as-systems/actions/runs/31878388283) passed on the clean public root commit.
- Both release archives pass their package regression suites, FOUNDRY scenario evaluation, and official Agent Skills validation after fresh extraction.
- Attribution and privacy scans pass across the repository, installed copies, plugin cache, and extracted archives.
- `sitecraft-0.3.0.zip`: `95554a9d7ad12fcdd7115af4a2b913bf4c8afe118c6d9243d7351a9b9bb5bdc9`
- `foundry-engineering-0.2.0.zip`: `935aa3388c6eb661a1c0e5e6c960c4feb4b2a373ad531bc90f6c677efb27f9d5`

## Evidence boundary

A successful installation proves package delivery and discovery layout. It does not prove every model version will route identically or that every task-specific browser, deployment, security, or performance claim has been observed.
