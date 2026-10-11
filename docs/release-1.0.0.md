# Collection 1.0.0 release receipt

Date: 2026-08-15

## Scope

- SITECRAFT 0.3.0
- FOUNDRY 0.2.0
- Claude Code collection plugin 1.0.0

## Tested

- Official `skills-ref` validation: both canonical skills valid.
- Repository structural and portability validation: passed.
- Clean temporary Codex project installation: passed.
- Clean temporary Claude Code project installation: passed.
- SITECRAFT dependency-free regression suite: 22 tests passed.
- FOUNDRY dependency-free regression suite: 14 tests passed.
- FOUNDRY deterministic scenario evaluation: 22 positive routes, 6 negative routes, 16 adversarial cases, and 4 artifact corruption gates passed.
- Claude Code 2.1.232 `plugin validate`: passed for the marketplace manifest.
- Claude Code 2.1.232 clean local marketplace add and plugin installation: passed; the isolated plugin cache contained SITECRAFT and FOUNDRY at collection version 1.0.0.
- Claude Code 2.1.232 public GitHub marketplace add and plugin installation: passed over HTTPS from `makiaveli1/skills-as-systems`; the isolated plugin cache contained exactly SITECRAFT and FOUNDRY at collection version 1.0.0.
- GitHub Actions validation on Linux with Python 3.12: passed, including official Agent Skills validation, clean installs, both package suites, and the FOUNDRY scenario evaluator.

## Observed package state

- SITECRAFT canonical resource payload: approximately 669 KiB of file content.
- FOUNDRY canonical resource payload: approximately 227 KiB of file content.
- No canonical package contains a repository README, browser profile, generated build, node dependency tree, active MCP configuration, credential, or machine-specific user path.

## Inferred

- The standard skill directories should be discoverable by current Codex and Claude Code versions that implement the documented Agent Skills locations.

## Unverified at release-candidate stage

- Model-level implicit activation across every Codex and Claude model/version.
- Behavioral quality across the complete representative scenario catalog.
- Windows-specific host execution beyond path-neutral code and temporary directory tests.
- Real browser, audio, deployment, production security, and performance claims, which remain task-specific.

## Release state

- Final Git diff and secret/privacy audit: complete.
- Public GitHub repository creation and reviewed commit push: complete.
- Live repository links and public marketplace source: confirmed.
- Public Claude Code marketplace installation: observed directly against the reduced public repository.
- GitHub Actions validation: passed; the documentation-only release receipt update must receive the same check before the `v1.0.0` tag is created.
