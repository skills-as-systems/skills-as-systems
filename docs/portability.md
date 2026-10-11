# Portability: one core, discovered hosts

## Quick installation

### Ask the receiving agent

```text
Install SITECRAFT and FOUNDRY from https://github.com/skills-as-systems/skills-as-systems for this harness. Prefer its native skill or plugin installer; otherwise use the repository's portable installer. Verify both skills are discoverable and report the exact installed paths. Do not add permissions or external integrations.
```

### Codex user install

```bash
git clone --depth 1 https://github.com/skills-as-systems/skills-as-systems.git && python3 skills-as-systems/scripts/install.py codex
```

### Claude Code plugin install

```bash
claude plugin marketplace add skills-as-systems/skills-as-systems && claude plugin install skills-as-systems@skills-as-systems
```

### Existing checkout

```bash
python3 scripts/install.py codex
python3 scripts/install.py claude
python3 scripts/install.py --target /custom/skill/root
```

The first two commands install both skills at user scope. Use the advanced options below only when you need project scope, one skill, a custom target, replacement, or symlinks.

## Portable by construction

The canonical packages under `skills/` use the open Agent Skills shape:

```text
skill-name/
├── SKILL.md
├── references/
├── assets/
├── schemas/
├── scripts/
├── examples/
└── tests/
```

Only `SKILL.md` is required by the standard. The additional resources provide progressive depth, reusable artifacts, and validation.

The portable core assumes only that a capable agent can read the supplied text. It does not assume:

- a particular model or provider;
- shell access;
- Python execution;
- a browser, audio, image, or runtime tool;
- network access;
- a logged-in account;
- permission to write or publish;

When a capability is missing, the skill reports the resulting limitation and can produce a bounded packet for another host or human.

## Canonical versus adapter material

The repository separates three concerns:

| Concern | Location | Rule |
| --- | --- | --- |
| Portable doctrine and references | `skills/<name>/` | No provider-only authority or invocation behavior |
| Codex interface metadata | `skills/<name>/agents/openai.yaml` | Presentation and invocation policy only |
| Claude distribution | `.claude-plugin/` | Marketplace and plugin packaging only |

Repository documentation, release notes, development fixtures, captures, generated sites, browser profiles, and private workspaces stay outside canonical skill directories.

## Codex

Codex discovers skills from `.agents/skills` at user or project scope. The repository supports both approaches:

- `.agents/skills/` contains relative links for use while working in this repository;
- `scripts/install.py --host codex` copies canonical packages into a user or project skill directory;
- every package contains optional `agents/openai.yaml` metadata for display name, concise description, default prompt, and safe implicit activation.

The canonical `SKILL.md` descriptions are front-loaded because Codex may shorten descriptions when the initial skill catalog approaches its context budget.

No skill declares that a tool is allowed. Codex permissions remain Codex and user policy.

## Claude Code

Claude Code can discover standalone skills from `~/.claude/skills` or `.claude/skills`, and it can distribute them through plugins.

This repository is a single marketplace plugin containing both canonical skill directories. The wrapper does not duplicate their instructions.

The canonical frontmatter avoids Claude-only fields such as invocation disabling, forked context, argument hints, and pre-approved tools. Those fields can be useful for a host-specific skill, but placing them in the shared core would change behavior elsewhere.

The compact cores also stay below Claude's recommended `SKILL.md` size and compaction boundaries. Deep references load only when needed.

## Generic Agent Skills hosts

Copy a complete directory from `skills/` into the host's configured skill location. The package name must remain the same as the frontmatter `name`.

If the host does not understand `agents/openai.yaml`, it can ignore it. The operating instructions remain in `SKILL.md` and relative resources.

## Installer behavior

The dependency-free installer supports:

```text
python3 scripts/install.py codex
python3 scripts/install.py claude --scope project --project /path/to/project
python3 scripts/install.py --target /custom/skill/root --skill sitecraft
```

Safety behavior:

- the default mode copies files, which works across operating systems;
- it installs only known skill directories;
- it refuses to replace an existing target by default;
- `--replace` moves the existing skill to a timestamped sibling backup before installation;
- `--dry-run` prints the exact plan without writing;
- `--mode symlink` is available for local development;
- it never edits host settings, installs plugins, configures MCP, or authenticates providers.

## Updating

For marketplace installs, use Claude Code's marketplace update flow.

For copied installs:

1. fetch or download the new repository version;
2. inspect release changes;
3. run the repository validation;
4. reinstall with `--replace` to retain a recoverable backup;
5. restart or reload the receiving host if required.

Do not merge two package versions by copying individual reference files. Schemas, examples, validators, and routing manifests evolve together.

## Removing

Remove only the exact installed skill directory from the host's configured skill root. If `--replace` created a backup, it remains beside the installed directory until the user intentionally removes it.

The installer does not provide an uninstall command because deletion policy belongs to the user and host.

## Host evidence

Compatibility claims have scope:

- **structural:** the package matches the documented host directory and metadata shape;
- **installation smoke:** a clean temporary Codex or Claude directory receives complete packages;
- **plugin validation:** Claude Code accepts the marketplace/plugin metadata;
- **activation:** the host discovers and invokes the intended skill;
- **behavioral:** the host uses the correct route and produces compliant work.

This repository automates the first two. Plugin and behavioral tests should be recorded against the exact host and version used.

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [Codex skills](https://developers.openai.com/codex/skills/)
- [Claude Code skills](https://code.claude.com/docs/en/slash-commands)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
