# Harness matrix

What has been run, and what has not. A cell says TESTED only when someone ran it and the result is recorded here. Everything else says UNTESTED, even where it should work.

Last updated: 11 October 2026. Evidence for TESTED cells is the repository's CI (`.github/workflows/validate.yml`) and the test files named below.

## Matrix

| Harness | Install from the repository | Skill is discovered by the real harness | Checkers run through a shell | Checkers run through the MCP server |
| --- | --- | --- | --- | --- |
| Codex | TESTED: clean install into a temporary project (`scripts/smoke_install.py`) | UNTESTED | TESTED: scripts run in CI with Python 3.12 (harness-independent) | UNTESTED in a real Codex session |
| Claude Code | TESTED: clean install into a temporary project (`scripts/smoke_install.py`) | UNTESTED | TESTED: same scripts, harness-independent | UNTESTED in a real Claude Code session |
| Any other harness that reads Agent Skills folders | UNTESTED: copy `skills/<name>/` into its skill folder with `scripts/install.py --target` | UNTESTED | UNTESTED in that harness | UNTESTED |
| Any harness with no skill support | Not applicable: paste `SKILL.md` and the needed references into the prompt | UNTESTED | UNTESTED | UNTESTED |

What "TESTED" covers in the install column: the installed `SKILL.md` and `VERSION` files match the source. It does not show that the harness then loads the skill.

## What is tested without a real harness

- `tests/mcp/test_mcp_server.py` talks to the MCP server with a scripted JSON-RPC client: handshake, tool list, checker findings, clean runs, missing arguments, unknown tool, unknown method, and an argument that tries to inject a shell command. It does not use a real MCP client.
- The checker scripts have their own tests (`skills/*/tests/`), run in CI.

## Per-harness notes

### Codex

- Install: `python3 scripts/install.py codex` (user scope) or the commands in the README.
- Discovery: Codex reads skills from `.agents/skills`. This repository carries that folder with relative links. UNTESTED in a live session.
- Checkers: run the scripts under `skills/<name>/scripts/` from the shell, or register the MCP server (see below).

### Claude Code

- Install: the plugin commands in the README, or `python3 scripts/install.py claude`. Only the second route is covered by the smoke test; the plugin marketplace route is UNTESTED.
- Checkers: shell scripts, or the MCP server.

### Other harnesses

- The skills are plain Agent Skills folders. Copy them to the harness's skill location, or paste the text. Whether a given harness picks them up is UNTESTED here.
- If the harness supports MCP over stdio, point it at `python3 integrations/mcp/skills_as_systems_mcp.py`. See `integrations/mcp/README.md`.

## MCP server

Command: `python3 integrations/mcp/skills_as_systems_mcp.py`. It exposes the checkers as tools. These are checkers, not locks: a harness can still ignore the result.

## How a cell moves to TESTED

Run it in the real harness, save what you saw (version of the harness, the prompt, the output), and change the cell in the same commit as the evidence. If a later release breaks it, change the cell back.
