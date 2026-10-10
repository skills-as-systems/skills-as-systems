# Capability Palette and orchestration

SITECRAFT chooses technology from the experience, not the other way around. Use this reference when a project may combine browser-native features, animation libraries, authored motion runtimes, canvas or GPU rendering, 3D, application frameworks, server features, generated media, or several of these together.

The purpose is not to maintain a catalogue of fashionable tools. The purpose is to make technical choices explicit, replaceable, testable, and portable across agent harnesses.

## Two capability layers

Keep these separate.

### Runtime Capability Plan

The Runtime Capability Plan belongs to the website or web application. It records what the experience needs and how that need will be implemented.

Store substantial decisions in `implementation.capability_plan` in the Experience Contract.

Each decision should answer:

- What experience or product need exists?
- Which stable capability class does it belong to?
- Which route or runtime was selected?
- Why does that route earn its complexity?
- Which credible alternatives were rejected and why?
- Where does the selected runtime integrate with the rest of the experience?
- What happens when it cannot run or should not run?
- What evidence is required before the decision is accepted?

The selected route is intentionally a free string. A current project may choose a browser API, a framework, a library, a hosted service, or a small custom implementation. Future tools should be able to replace it without changing the meaning of the capability class.

### Host Capability Profile

The Host Capability Profile belongs to the current ChatGPT, Claude, Codex, generic MCP, CI, or other agent environment. It records what this host can actually inspect, change, run, observe, persist, or release now.

Do not store host permissions as website requirements. Re-discover them when work moves to another host.

For substantial execution, classify these as `confirmed`, `unavailable`, or `unknown`:

- project/file inspection;
- bounded file modification and rollback;
- build, lint, type, unit, integration, or package-script execution;
- preview-server control;
- visible or headless browser control;
- screenshot capture and inspection;
- temporal recording and inspection;
- image/video/media inspection;
- current official-source research;
- project-state persistence and continuation;
- specialist or parallel review;
- deployment or publishing authority.

A host may be able to implement a capability without being able to verify it visually. Another host may be able to observe it without having write access. SITECRAFT must degrade honestly rather than inventing capability.

## Stable capability classes

Use the smallest class that describes the need. These classes are deliberately broader and more durable than product names:

- `semantic-ui` — native document structure, controls, forms, focus, disclosure and accessible interaction;
- `layout-styling` — layout, typography, responsive composition, masks, filters, blending and visual styling;
- `interface-motion` — local state transitions, feedback, choreography and timeline control;
- `scroll-timeline` — progress linked to document, element or viewport travel;
- `navigation-transition` — continuity across routes, documents, views or application states;
- `vector-runtime` — authored vector animation or interactive state-machine artwork;
- `canvas-2d` — custom 2D raster drawing or simulation that does not belong in the DOM;
- `gpu-rendering` — shader, particle, procedural, compute or other GPU-driven rendering;
- `3d-scene` — cameras, geometry, materials, lighting and spatial interaction;
- `media-playback` — image sequences, audio, video, alpha video, streaming or synchronized media;
- `application-rendering` — framework or rendering architecture for routes, components, server/client boundaries or hydration;
- `client-state` — sustained local application state beyond simple native-control behaviour;
- `server-data` — privileged data, mutations, server rendering, caching or server-only integrations;
- `realtime` — live collaborative, streaming, socket or event-driven state;
- `other` — a genuine capability that does not fit the stable set; explain it clearly.

Do not create a new class merely because a new library exists.

## Native-first is a baseline, not a veto

Start by checking whether the platform already provides the required behaviour with acceptable quality, support and maintenance cost. This keeps simple experiences simple.

Choose a library, framework or specialized runtime when it materially improves one or more of these:

- capability that would otherwise be impractical to build;
- authoring quality or designer control;
- temporal or spatial coordination;
- rendering performance;
- tested cross-browser behaviour;
- application architecture and state management;
- maintainability for the actual team;
- accessibility or input handling;
- delivery workflow, tooling or asset pipeline.

Do not reject a strong library merely because native code could theoretically reproduce it. Do not add a library merely because it makes a familiar effect convenient.

The question is: **what does this route make possible or substantially safer, clearer, faster, or more maintainable for this experience?**

## Selection test

Before accepting a non-trivial runtime, compare at least one credible alternative. Check:

1. **Experience fit** — does it directly serve the intended visual, interaction, content or product behaviour?
2. **Capability delta** — what does it add beyond the simpler route?
3. **Integration cost** — bundle/runtime weight, setup, lifecycle, style assumptions, build tooling and coordination cost.
4. **Accessibility** — semantic fallback, keyboard/focus behaviour, reduced motion, input alternatives and assistive-technology impact.
5. **Performance** — loading, main-thread work, GPU/decoder cost, memory, energy, responsiveness and low-end-device behaviour appropriate to the mechanism.
6. **Support** — target engines/devices and what progressive enhancement or fallback is needed.
7. **Security and privacy** — third-party code, remote services, privileged data, supply-chain and public/private boundaries.
8. **Maintenance** — ownership, versioning, upgrade path, skill availability and removal cost.
9. **Evidence** — what must be observed to prove the chosen route actually works.

When exact library or platform behaviour could have changed, verify current official documentation before implementation. Keep temporal product facts out of the durable capability classes.

## Creative distinction before capability

Technology diversity is not creative diversity. A site does not become original because it combines several libraries, renderers or media types.

Before choosing a consequential runtime, identify the project-specific visual, narrative or interaction mechanism it serves. That mechanism should already be traceable to the brief, Experience Contract, visual grammar, motion argument, content structure or approved asset system. The runtime is an implementation route for that mechanism, not the source of the concept.

Reject a capability choice when its main justification is equivalent to "this library makes a fashionable effect easy." Repeated SITECRAFT motifs, scene sequences, hero structures or signature effects should be treated as warning signs even when implemented with different technologies. Prefer a quieter or simpler route when it expresses the project's own character more clearly.

## Integration boundaries

Creative stacks become fragile when several runtimes believe they own the same concern. For every selected route, define its boundary.

Useful boundaries include:

- DOM subtree or canvas/container ownership;
- scroll ownership;
- timeline/clock ownership;
- animation state ownership;
- application state ownership;
- route/navigation ownership;
- focus and keyboard ownership;
- pointer/touch/gesture ownership;
- design-token and style ownership;
- data-fetch and mutation ownership;
- media loading and playback ownership;
- render-loop creation and cleanup;
- resize and visibility lifecycle;
- disposal of GPU, observer, listener and media resources.

Prefer one owner per concern. If two systems must cooperate, state the bridge explicitly: shared progress value, custom event, framework adapter, component boundary, asset handoff, or another small interface.

Avoid two independent smooth-scroll controllers, competing requestAnimationFrame loops, duplicate route managers, conflicting state stores, or several libraries transforming the same element without an explicit coordinator.

### Runtime orchestration record

When more than one consequential runtime interacts on the same surface or concern, add `implementation.runtime_orchestration` to the Experience Contract.

Use it to record:

- `mode` — whether special coordination is unnecessary, one significant runtime dominates, or several runtimes require coordination;
- `ownership` — one owner for a named concern within a named scope, with optional links back to Capability Plan decision IDs;
- `bridges` — the explicit interface between layers, such as an event, progress value, component boundary, asset handoff, adapter or URL/state synchronization;
- `shared_rules` — design, accessibility, performance, lifecycle and support rules every runtime must obey;
- `prohibited_conflicts` — project-specific combinations that must not appear.

Ownership is scoped deliberately. Two isolated canvases may each own their own render loop; two systems may not both own the same render loop in the same scene. Likewise, a timeline library may coordinate one authored chapter while CSS owns unrelated local hover/focus feedback.

The orchestration record is not a package inventory. Record only consequential ownership and bridges that could become ambiguous or fragile.

## Composition patterns

A mixed technology stack is valid when the boundaries are clean. Examples of the pattern, not prescriptions:

- semantic DOM owns content and accessibility while a GPU canvas owns a decorative or spatial scene behind it;
- an authored vector runtime owns one interactive character while normal DOM controls own navigation and forms;
- a timeline library coordinates a complex chapter while CSS handles local hover and focus feedback;
- a server-rendered framework owns routes and data while isolated client components own genuinely interactive islands;
- generated video supplies living atmosphere while live HTML owns the message and controls.

The visual system and Experience Contract remain the authority across all runtimes. Do not allow each technology to invent a separate design language.

## Fallback contract

A fallback is part of the design, not an error page added later.

For every capability that is essential or expensive, define the fallback level:

- **equivalent** — same task and information through a simpler mechanism;
- **reduced** — same core outcome with less motion, fidelity or interaction;
- **static** — approved still composition or semantic state;
- **unsupported** — deliberately outside the support promise, with an understandable message or alternate path where appropriate.

Reduced motion is not automatically the same as technical fallback. A WebGL scene might run technically while still requiring a calmer reduced-motion composition.

## Evidence follows the mechanism

Add evidence because of the selected capability, not because a generic checklist says so.

Examples:

- DOM/layout work needs structural and responsive visual evidence;
- motion and scroll timelines need temporal evidence, interruption/reverse behaviour and reduced-motion evidence;
- vector runtimes need loading, state, accessibility/fallback and asset-lineage evidence;
- canvas/GPU/3D need device/browser fallback, resize/context-loss behaviour where relevant, frame pacing, responsiveness and appropriate memory/energy observations;
- media needs poster/failure/playback/visibility/network and byte-budget evidence;
- application/server boundaries need route/history/loading/error/data/security evidence;
- realtime systems need reconnect, stale state, ordering, conflict and failure evidence.

The Capability Plan should point to the evidence required; the Evidence Contract records the actual matrix and receipts. When a capability decision is consequential, carry its decision ID into relevant evidence rows and SITECRAFT Review scope/findings/floors/repair steps so proof remains traceable back to the plan without copying the decision text.

For `coordinated_multi_runtime` work, test the bridges as first-class behaviour. Collect evidence that the named owner actually remains authoritative, that state/progress handoffs work in both normal and interrupted paths, and that route changes, unmounts, hidden tabs, reduced motion or scene exit do not leave duplicate listeners, animation clocks, render loops, media playback or stale state behind. A set of individually working runtimes is not proof that the orchestration works.

## Route mesh

The seven SITECRAFT routes are not separate departments. They pass decisions forward:

- **Frame** defines audience, outcome, support promise, constraints and acceptable complexity.
- **Map** identifies which surfaces and states actually need special capabilities.
- **Compose** defines the visual mechanisms and which content must remain live, semantic, static or media-led.
- **Choreograph** defines temporal, spatial and interaction behaviour before selecting a motion runtime.
- **Build** turns those needs into the Runtime Capability Plan and exact implementation boundaries.
- **Observe** collects evidence specific to the selected mechanisms and records failures without changing the contract silently.
- **Harden** checks whether dependencies, fallbacks, support, security, performance and evidence justify the final support promise.

A small repair may enter at Build or Observe. Do not force every task through all routes. When it enters late, recover the minimum upstream facts needed for a safe decision.

## Builder and agent handoff

Carry the decision, not one provider's hidden working state.

A portable handoff should contain:

- project identity and exact-state fingerprint when available;
- Experience Contract revision;
- current Runtime Capability Plan;
- protected foundations and change boundary;
- relevant files/components and changed paths;
- tests and verification receipts;
- visual, temporal, accessibility, performance and security evidence that actually exists;
- known blockers and unverified states;
- next bounded action;
- intended receiving host when known.

On receipt, the next host re-discovers its Host Capability Profile and chooses how to execute the same contract. It may use different tools without changing the website's intended behaviour.

Do not transfer hidden reasoning, raw private transcripts, secrets, stale temporary URLs, or permissions granted to another host.

## AI-builder translation

When handing work to a code-generating builder, include only the capability decisions relevant to the current pass. Tell the builder:

- what capability it is implementing;
- which existing layer owns surrounding behaviour;
- selected route and reason;
- what must not be replaced;
- fallback and responsive/reduced-motion behaviour;
- acceptance criteria;
- evidence to collect after implementation.

Do not dump the entire Capability Plan into every prompt. Progressive disclosure applies to technical decisions too.

## Anti-bloat rule

A Capability Plan is optional. Use it when a choice is consequential: new runtime, framework boundary, specialized rendering, significant third party, cross-runtime coordination, material performance risk, or support/fallback implication.

Do not create entries for ordinary CSS declarations, every component, every package already owned by the project, or trivial browser behaviour.

The plan exists to make difficult technical choices portable and reviewable, not to create paperwork.
