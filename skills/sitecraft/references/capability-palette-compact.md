# Capability Palette — compact

Use this when a website may need consequential browser APIs, animation libraries, authored runtimes, canvas/GPU/3D, application frameworks, server capabilities, media systems, or several runtimes together.

## Keep two layers separate

**Runtime Capability Plan** — belongs to the website. Store material decisions in optional `implementation.capability_plan` in the Experience Contract.

**Host Capability Profile** — belongs to the current ChatGPT, Claude, Codex, generic MCP, CI, or other agent environment. Re-discover it after every handoff; never carry permissions between hosts.

For the host, mark project inspection, bounded writes/rollback, tests, preview, browser control, screenshots, recordings, media inspection, current-source research, persistence, specialist review, and deployment as `confirmed`, `unavailable`, or `unknown`.

## Runtime decision shape

For each consequential capability record:

- experience `need`;
- stable `capability_class`;
- replaceable `selected_route`;
- `reason` it earns its complexity;
- credible `rejected_routes`;
- `integration_boundary` and ownership;
- loading/lifecycle when relevant;
- `fallback`;
- material `risks`;
- `evidence_required`.

Do not create entries for ordinary CSS, every component, or trivial browser behaviour.

## Stable capability classes

Use the smallest durable class: `semantic-ui`, `layout-styling`, `interface-motion`, `scroll-timeline`, `navigation-transition`, `vector-runtime`, `canvas-2d`, `gpu-rendering`, `3d-scene`, `media-playback`, `application-rendering`, `client-state`, `server-data`, `realtime`, or `other` with explanation.

Exact tool names belong in `selected_route`, not in permanent schema fields. Verify current official documentation before relying on version-sensitive behaviour.

## Native-first, not native-only

Check the platform first, but choose a library, framework, authored runtime, renderer, media route, or service when it materially improves required capability, authoring control, coordination, performance, maintainability, accessibility, delivery, or team fit.

Ask: **what does this route make possible or substantially safer, clearer, faster, or more maintainable for this experience?**

Compare at least one credible alternative across experience fit, capability delta, integration cost, accessibility, performance, browser/device support, security/privacy, maintenance, and evidence.

Technology diversity is not creative diversity. The project-specific visual, narrative or interaction mechanism must come from the brief and Experience Contract before the runtime is chosen. Do not use a library as the reason to repeat a fashionable SITECRAFT motif or scene pattern.

## Multi-runtime ownership

Give each major concern one owner. Define who owns:

- DOM/canvas subtree;
- scrolling;
- animation clock/timeline;
- route/navigation state;
- application state;
- focus/keyboard and pointer/touch input;
- styles/tokens;
- data and mutations;
- media playback;
- render loop, resize/visibility lifecycle, and cleanup.

If systems cooperate, define the bridge explicitly: shared progress value, event, adapter, component boundary, asset handoff, or another small interface.

When several consequential runtimes interact, record this in optional `implementation.runtime_orchestration`: scoped ownership, explicit bridges, shared rules and prohibited conflicts. Ownership is scoped, so independent scenes may own independent render loops while the same concern in the same scope must have one owner.

Avoid competing smooth-scroll controllers, duplicate route managers or state stores, independent render loops that need one clock, or several systems transforming the same element without coordination.

## Fallback and evidence

Design the fallback as `equivalent`, `reduced`, `static`, or deliberately `unsupported` within the approved support promise. Reduced motion is a separate user preference and may require a calmer composition even when the runtime works technically.

Evidence follows the mechanism:

- DOM/layout → structural and responsive visual evidence;
- motion/scroll → temporal, interruption/reverse and reduced-motion evidence;
- vector runtime → asset/loading/state/fallback evidence;
- canvas/GPU/3D → device/browser fallback, resize/lifecycle, frame pacing, responsiveness and appropriate memory/energy observations;
- media → poster/failure/playback/visibility/loading/byte evidence;
- application/server boundary → route/history/loading/error/data/security evidence;
- realtime → reconnect/stale/order/conflict/failure evidence.

The Capability Plan declares what must be proved; the Evidence Contract records where it was actually proved. Carry material capability decision IDs into evidence rows and SITECRAFT Review scope/findings/floors when useful so a later reviewer or host can trace proof back to the exact planned decision without duplicating it.

## Route mesh

Frame sets outcomes and constraints → Map identifies surfaces/states needing capability → Compose defines visual mechanisms → Choreograph defines temporal/spatial behaviour → Build selects routes and boundaries → Observe gathers mechanism-specific evidence → Harden reconciles support, fallbacks, dependencies, security, performance and approval.

Small tasks may enter late; recover only the upstream facts needed for a safe decision.

## Portable handoff

Carry project identity/fingerprint when available, Experience Contract revision, Runtime Capability Plan, protected foundations, changed paths, verification receipts, existing evidence, blockers and next bounded action.

The receiving host re-discovers its Host Capability Profile and may use different execution tools without changing the intended website behaviour.

Never transfer hidden reasoning, private transcripts, secrets, temporary private URLs, or another host's permissions.

Use [capability-palette-and-orchestration.md](capability-palette-and-orchestration.md) for the full selection test, integration patterns, fallback model, evidence mapping, and AI-builder handoff guidance.
