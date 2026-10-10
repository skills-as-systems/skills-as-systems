# Harness integration

SITECRAFT is portable. Treat every host as a capability profile, not as an identity or source of authority.

## Portable core

In any capable chat or agent environment, SITECRAFT can:

- frame the problem;
- create an Experience Contract;
- map surfaces and journeys;
- define visual and motion systems;
- produce implementation and AI-builder packets;
- write or review code supplied in context;
- create verification plans;
- report explicit unverified states.

It must not require a particular coding agent, or a particular AI builder to provide useful work.

## Capability negotiation

At the start of substantial execution, discover whether the host can:

- inspect local or connected files;
- modify files with review and rollback;
- run package scripts or tests;
- start a preview server;
- open a browser or local URL;
- capture screenshots;
- record interaction clips;
- inspect images and video;
- generate raster images when the project requires custom imagery;
- edit existing raster images while preserving named invariants;
- make required local or connected reference media actually available to a generator, rather than assuming a filesystem path is sufficient;
- inspect returned generated media at useful resolution;
- import or persist accepted generated media into the project workspace;
- browse current official sources;
- persist project state;
- use specialist reviews;
- deploy or publish.

Use only confirmed capabilities. Do not infer tool access from earlier conversations or from the name of the host.

## Two capability layers

Do not confuse what the website needs with what the current agent can do.

- The **Runtime Capability Plan** lives in the Experience Contract and records consequential implementation choices for the product: need, capability class, selected route, integration boundary, fallback, risks and evidence.
- The **Host Capability Profile** is temporary execution context for the current harness. Mark file inspection, bounded writes/rollback, tests, preview, browser control, screenshots, recordings, media inspection, authenticated media generation, paid-action authority/budget visibility, returned-media import, current-source research, persistence, specialist review and deployment as `confirmed`, `unavailable` or `unknown`.

Re-discover the Host Capability Profile after a handoff. For image production, distinguish at least generation, edit fidelity, reference-media loading, returned-image inspection and project import/persistence when those capabilities matter to the next job. A host that can read a local image path but cannot expose that image to its generator has not satisfied a reference-dependent image job. Do not store host permissions, temporary tool URLs or provider-specific authority in the Runtime Capability Plan. A new host may implement or verify the same contract through different tools. Read [capability-palette-and-orchestration.md](capability-palette-and-orchestration.md).

## Capability acquisition planning

SITECRAFT owns the semantic need, not the provider. When a required host capability is unavailable, first describe the missing capability and why the current bounded task needs it. Then let the current host decide whether it already has an equivalent native capability, can plan a reviewed extension/plugin route, should hand the task to another capable host, or should return a portable work packet instead.

Planning an acquisition route is not execution authority. It grants no network access, authentication, provider activation, spending, filesystem scope, deployment permission, or approval to change the Experience Contract. A host may produce a task-scoped route and data boundary, but SITECRAFT must not encode that route as permanent creative policy.

## Capability levels

### Advisory

No project or browser access. Produce contracts, maps, specifications, prompts, code snippets, and an evidence plan. Mark implementation and verification as not performed.

### Project-aware

Read project files and history. Produce codebase-grounded plans and patches. Do not claim rendered quality without visual evidence.

### Executing

Apply bounded changes and run declared checks. Record changed paths, outputs, failures, and rollback information.

### Observing

Capture or inspect screenshots and recordings. Tie findings to exact viewports, states, and builds.

### Release-capable

Review deployment configuration and execute approved release actions. Require exact-state verification and explicit human authority.

## Cross-host continuity

When moving work between ChatGPT, Claude, Codex, or another MCP host, carry:

- project identity and fingerprint;
- current Experience Contract revision;
- current Runtime Capability Plan and material integration boundaries;
- relevant continuity anchor/state IDs when later work must preserve them;
- approved and protected foundations;
- changed paths;
- current verification receipts;
- blockers;
- next bounded action;
- intended host;
- permission requirements that the receiving host must independently re-establish.

When continuity matters beyond one conversation, use the provider-neutral SITECRAFT Handoff Packet in [handoff-and-continuity.md](handoff-and-continuity.md). The packet points to the Experience Contract and material capability-decision IDs rather than duplicating them, and it always records that receiving-host capability discovery is required and permissions are not carried over. For a shared checkout, the packet must also carry explicit coordination state; a clean tree is not proof that another chat or agent has released ownership. The receiving host independently confirms both checkout ownership and local write capability before modifying shared project state.

Do not carry hidden reasoning, conversation transcripts, secrets, private temporary URLs, or assumed permissions.

## Operating-system and browser adapters

Treat macOS, Windows, Linux, mobile operating systems, browser engines, and capture providers as environment adapters around the portable core.

For each adapter:

- discover available browsers, automation, screenshot, recording, accessibility, and performance capabilities instead of assuming them;
- use project-relative paths and language-native path handling rather than a user home directory or one path separator;
- use package scripts or language entry points rather than embedding one shell dialect into the portable workflow;
- keep local permission prompts and administrator approval with the local user;
- record operating system, architecture, browser, engine, input mode, assistive technology, capture provider, viewport, build identity, and limitations;
- never generalise evidence from one adapter to another.

A macOS Safari receipt remains valuable, but it proves only that macOS Safari environment. Windows Chromium, Linux Firefox, touch, reduced motion, or another assistive-technology stack require their own row or an explicit unverified state. Use [platform-and-browser-portability.md](platform-and-browser-portability.md) and the workspace platform evidence matrix.

## Builder adapters

Platform-specific prompts may be created for v0, Lovable, Bolt, Replit, Cursor, Claude Code, Codex, or another builder. Keep adapters outside the canonical contract. Record:

- platform and model/version when known;
- project context supplied;
- files or references supplied;
- prompt;
- requested scope;
- output received;
- evidence and drift;
- follow-up repair.

## Mutable workspaces beside a skill

A staged skill workflow protects the exact skill package identity. Writing screenshots, recordings, generated sites, reviews, or other changing test material into the distributable skill resource tree can invalidate an active workflow even when `SKILL.md` is unchanged.

When a skill is also the active development project:

- keep distributable instructions, schemas, templates, tests, and stable examples in the skill package;
- keep mutable forward-test sites and evidence under a host-ignored project directory such as `build/forward-tests/` or in a separate sibling test project;
- confirm the host actually ignores that directory when calculating skill identity;
- never weaken package hashing merely to allow mutable evidence;
- restart a staged workflow after an intentional skill-package revision;
- record fixture identity separately from skill identity.

Fixtures under `build/`, `dist/`, and `.cache/` are not skill resources. SITECRAFT forward-test fixtures use `build/forward-tests/` so they stay inside the approved project.

## Tool failure

When a tool fails:

1. preserve the current project state;
2. report the failed action accurately;
3. retry only when the failure is plausibly transient and the action remains safe;
4. use a lower-capability fallback without pretending the action succeeded;
5. record what remains unverified.
