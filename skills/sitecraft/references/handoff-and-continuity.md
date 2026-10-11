# Handoff and continuity

Use a SITECRAFT Handoff Packet when work must move between ChatGPT, Codex, Claude, an MCP host, a CI/review agent, another coding harness, or a later session that should not depend on conversation memory.

The packet is a compact pointer to authoritative project state. It must not become a second Experience Contract.

## Authority

The Experience Contract remains the source of truth for purpose, audience, visual system, behaviour, Runtime Capability Plan, support promise, evidence requirements and approval state.

The Handoff Packet records only what the receiving host needs to resume safely:

- project identity or workspace reference;
- Experience Contract reference and revision;
- exact build fingerprint when available;
- IDs of material Runtime Capability Plan decisions that matter next;
- IDs of material continuity anchors/state dimensions that matter next, when the Experience Contract defines them;
- current mode and routes;
- protected foundations and change boundary;
- source and intended receiving host labels;
- a short factual summary of what the source host could actually do;
- explicit workspace/checkout coordination state, including whether a shared checkout is free, reserved, blocked, or requires revalidation;
- changed paths;
- verification receipts and evidence references;
- blockers and explicitly unverified states;
- one next bounded action.

Use `schemas/sitecraft-handoff.schema.json` and `assets/handoff-packet-template.json`.

## No authority transfer

A handoff carries context, not permission.

The packet must always declare:

- `contains_hidden_reasoning: false`;
- `contains_private_transcript: false`;
- `contains_secrets: false`;
- `permissions_carried_over: false`;
- `receiving_host_must_rediscover_capabilities: true`;
- `receiving_host_must_confirm_checkout_before_write: true`.

Do not paste credentials, private temporary URLs, raw private conversations, administrator approvals, browser permission grants, deployment authority, or another host's write approval into the packet.

## Receiving-host procedure

Before acting, the receiving host should:

1. locate and read the referenced Experience Contract;
2. verify project identity and exact current state when tools allow;
3. compare the packet revision/fingerprint with the current project;
4. inspect `coordination` and independently confirm the shared checkout is still in the declared state before any write;
5. re-discover its own Host Capability Profile and local permissions;
6. inspect the material Runtime Capability Plan entries by ID;
7. inspect any carried continuity anchor/state-dimension IDs against the current `continuity_system`; if an ID disappeared or its authority changed, treat the affected continuation as stale instead of guessing;
8. when the next action is image production, inspect the current `image_system.production_jobs` and portable Image Generation Pack, then confirm every required reference/edit source is actually available to the receiving host's image generator and every declared approval dependency is still satisfied;
9. confirm protected foundations and change boundary;
10. check whether verification and coordination receipts are still current;
11. continue only the named next bounded action and only within the declared receiver write policy.

If the project changed after the packet was created, refresh the packet or clearly mark stale evidence. Do not force continuation from an obsolete state.

When a populated SITECRAFT Review is also present, validate the Experience Contract, Review, and Handoff Packet as one continuation bundle before resuming consequential work. Individual schema passes are insufficient because each file can be valid while describing a different project revision. The bundle check should confirm project identity, contract revision/status, Review capability coverage, and that Review/Handoff capability IDs exist in the current contract.

Portable validator example:

```text
python scripts/validate_artifact.py contracts/experience-contract.json --kind experience-contract --review reviews/sitecraft-review.json --handoff handoffs/sitecraft-handoff.json
```

## Source-host procedure

Create or refresh a packet only from observable project state. Keep summaries factual:

Good:

- `bridge regression suite passed for fingerprint abc123`;
- `desktop screenshot reviewed; touch input unverified`;
- `files X and Y changed`;
- `shared checkout explicitly released by the source host at the recorded fingerprint; receiver must revalidate before writing`;
- `next action: implement the approved navigation transition`.

Bad:

- hidden reasoning;
- a transcript dump;
- vague claims such as `everything is tested`;
- treating a clean tree as proof that no other chat or agent still owns a shared checkout;
- permissions that the next host has not granted;
- assumed tool access based on the receiving host's brand name.

## Capability continuity

Do not duplicate full capability decisions in the handoff. Use `contract.capability_decision_ids` to point at the current `implementation.capability_plan` entries in the Experience Contract.

This allows a receiving host to use different execution tools while preserving the same intended runtime architecture. For example, an implementation host may write the 3D integration while another host later captures browser evidence. The technical ownership boundary remains the same unless the Experience Contract is deliberately revised.

## Evidence continuity

A verification receipt is not universal proof. Keep each receipt tied to the build and environment that produced it.

When a new host cannot inspect a referenced screenshot, recording, browser session, or local artifact, preserve the reference but mark the corresponding review unverified in that host. Do not replace missing evidence with confidence language.

When implementation changes, stale affected evidence before handing off again.

## Packet lifetime

Refresh the packet when any of these materially changes:

- Experience Contract revision;
- build fingerprint or commit;
- protected foundation or change boundary;
- Runtime Capability Plan decision relevant to the next work;
- changed paths;
- shared-checkout ownership, reservation, release, blocker, or coordination receipt;
- verification status or blockers;
- next bounded action.

A packet can remain unchanged across a simple conversational handoff if the underlying project state has not changed.

## Portability

Use workspace-relative references where possible. Do not hard-code one user's home directory, one operating system path separator, one browser, or one shell into the portable packet.

Any host may generate or consume the same JSON using ordinary file or chat capabilities.
