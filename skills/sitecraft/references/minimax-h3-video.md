# MiniMax H3 Video — Sitecraft Production Guide

Use MiniMax H3 when its multimodal reference handling, native audio, 2K output, or video-to-video/reference-driven generation is a good fit for the site experience.

Do not make H3 a hard dependency of Sitecraft. Treat it as one optional generation transport alongside Kling and other video tools.

## Current verified H3 capability profile

MiniMax's official H3 tooling documents:
- model: `MiniMax-H3`
- 2K output
- duration: integer 4–15 seconds
- prompt: up to 7000 characters
- first-frame + optional last-frame mode
- mixed reference mode with image/video/audio inputs
- up to 9 reference images
- up to 3 reference videos
- up to 3 reference audios
- at most 12 mixed reference items total
- native synchronized audio

Frame mode and mixed-reference mode are separate. Reference audio requires at least one reference image or video.

## Transport routing

Use this order:

1. **H3-capable official MCP, if capability-probed and actually available.** The existence of the MiniMax MCP is not enough; the exposed tool/model must explicitly support `MiniMax-H3`.
2. **Official `mmx` CLI H3 path**, if installed/configured. The current official CLI includes an H3-specific workflow.
3. **Prompt/export-only mode** when neither transport is available.

Do not silently install/update the MiniMax CLI or configure credentials unless the user requested setup.

Never route an H3 request through Kling, and never alter or substitute the independent Kling route to make H3 work.

## Credential and paid-task safety

For the official H3 CLI path:
- use a compatible Pay-as-you-go/Credit API key, not an OAuth/Token Plan credential when the official H3 tool says those are unsupported
- reuse securely stored credentials
- never print literal API keys in prompts, logs, handoffs, or shell commands
- avoid duplicate paid generation submissions
- once a task ID exists, recovery operates on that task rather than creating another one
- do not interpret a local polling/download problem as evidence that generation must be resubmitted

## Reference-role mapping

Assign every reference one job before generation:

```text
reference image 1 -> character identity / product identity
reference image 2 -> environment or key pose
reference video 1 -> motion/camera rhythm
reference audio 1 -> dialogue/voice/rhythm/ambience
```

When identity matters, use the Character Identity Board as the master identity reference and state which derived views are supplied to H3.

## Prompt structure

For a simple one-shot clip:
1. output spec
2. subject/reference roles
3. chronological action
4. environment/light
5. camera
6. look/pacing
7. audio
8. hard continuity/negative constraints

For two or more ordered storyboard references, use a two-level timeline:
- master timeline: one contiguous range per shot/reference
- micro-timeline: establish -> prepare -> execute -> settle/hold

The locked end state of shot N must match the initial state of shot N+1.

## H3 + interactive generated motion

H3 can generate the continuous source motion, but browser interactivity still comes from the Interactive Generated Motion pipeline:

H3 clip -> frame QA/cleanup -> trim/deduplicate/compress -> deterministic web asset -> scroll/pointer/drag/touch/state mapping.

Do not call H3 at interaction time.

## Failure rules

- validation failure before task creation: correct only the invalid field
- authentication/billing/safety rejection: stop and report; do not silently rewrite or resubmit
- task created but polling interrupted: preserve task ID; do not create a replacement
- download failure after success: retry retrieval of the same result, not generation
- model capability unavailable through an MCP: fall back to the official configured H3 transport, not to an unrelated model without telling the user

## Acceptance test

A Sitecraft H3 integration is ready only when:
- transport/model capability was actually detected
- the request uses `MiniMax-H3` explicitly
- references are role-mapped and within limits
- identity/continuity constraints are present when needed
- secrets are absent from artifacts and logs
- paid-task duplication protections are documented/enforced
- output provenance records model, transport, prompt, references, task ID when available, and final asset path
- Kling regression tests remain unchanged and green
