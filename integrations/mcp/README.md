# MCP server for the checkers

A small stdio MCP server that exposes the SITECRAFT and FOUNDRY checkers as tools. It uses only the Python standard library and makes no network calls.

Run it with: `python3 integrations/mcp/skills_as_systems_mcp.py`

Point your harness's MCP config at that command. The server speaks newline-delimited JSON-RPC over stdin and stdout.

## Tools

| Tool | Runs |
|---|---|
| `sitecraft_check` | `sitecraft_check.py` on a file or folder |
| `foundry_testrun` | `foundry_check.py testrun` |
| `foundry_receipt` | `foundry_check.py receipt` |
| `foundry_test_weakening` | `foundry_check.py test-weakening` |
| `foundry_scope_drift` | `foundry_check.py scope-drift` |
| `gate_log_validate` | `gate_log.py validate` |
| `gate_log_cross_check` | `gate_log.py cross-check` |
| `design_propose` | `design_search.py propose` (proposals only; the buyer approves the sheet) |

Each tool returns the checker's own output plus its exit code (0 clean, 1 findings, anything else means it could not run). Findings are results, not tool errors.

## What it does not do

- It runs only the bundled scripts with the paths you give it, never a shell.
- These are checkers, not locks. A harness can still ignore the result.
- Tested here with a scripted JSON-RPC client (`tests/mcp/test_mcp_server.py`). Not yet tested inside a real MCP client: see the harness matrix for status.
