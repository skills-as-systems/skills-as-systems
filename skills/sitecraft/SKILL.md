---
name: sitecraft
description: Use for planning, designing, building, repairing, auditing, or hardening websites and web apps when visual coherence, responsive behaviour, accessibility, motion, implementation, performance, privacy, or release evidence matters.
---

# SITECRAFT

Build coherent working experiences, not generic sections with effects.

## Core

- Purpose before surface; structure before decoration.
- One job per screen/state; one explainable visual grammar.
- Motion explains change, orientation, feedback, or deliberate narrative.
- Responsive design means intentional compositions.
- Code correctness is not visual approval; evidence supports every claim.
- Version approved foundations; public builds exclude private/debug material.
- Prefer the simplest architecture that preserves the experience.
- Generated media needs bounded roles/references, fallbacks, budgets, and hard floors.
- Derive each site's devices from its brief.

Routes: **Frame**, **Map**, **Compose**, **Choreograph**, **Build**, **Observe**, **Harden**. Modes: **Sketch**, **Make**, **Repair**, **Audit**, **Evolve**. Use only what the task needs. For work spanning more than one route, or when routing is unclear, read [interaction and routing](references/interaction-and-routing.md) before loading deeper material.

## Authority + references

For substantial work, [schemas/experience-contract.schema.json](schemas/experience-contract.schema.json) is authoritative. Brainstorms, builder output, reviews, and handoffs never replace it silently. A full contract file is not mandatory for every build: bounded single-surface work should use the compact contract threshold in [interaction and routing](references/interaction-and-routing.md) and must not create schema-shaped paperwork without a durability need. Use `continuity_system` only for genuine shared continuity.

Load only matching material. Start with [architecture](references/architecture-maintenance-compact.md), [routing](references/interaction-and-routing.md), [visual](references/visual-system.md), [evidence](references/evidence-and-qa.md), [harness](references/harness-integration.md), or [handoff](references/handoff-and-continuity.md). Compacts: [images](references/generated-image-production-compact.md), [video](references/generated-video-production-compact.md), [motion](references/motion-design-and-graphics-compact.md), [capabilities](references/capability-palette-compact.md). Specialized routes: [character identity boards](references/character-identity-board.md), [Creative DNA reference analysis](references/creative-dna-reference-analysis.md), [interactive generated motion](references/interactive-generated-motion.md), [MiniMax H3](references/minimax-h3-video.md).

## Work

Inspect current project/context, approved assets, prior decisions, and confirmed host capabilities first. Resolve only consequential unknowns. Map real tasks, states, recovery, and orientation before styling.

Choose one dominant visual idea. Translate references through this project's hierarchy, tokens, components, responsive/accessibility rules, performance budget, and code conventions. Never let a reference become a second design system.

Use `visual_grammar.creative_distinction` only when distinction matters; otherwise **do not invent novelty to fill a form**. If direction is genuinely open, `visual_grammar.direction_selection` compares at least two structurally different arguments; use `not_needed` when direction is already strong.

Use `image_system`, `video_system`, and `asset_lineage` only when needed. When a recurring person, character, avatar, mascot, or identity-sensitive subject must survive across several assets, approve one identity master before dependent generations. When a reference is supplied mainly for its feel, extract and recombine its Creative DNA instead of copying its surface. Generated video defines first/last frame, continuity, fallback, hard floors, attempt/spend limits, and evidence before paid execution. H3 and Kling remain optional independent provider routes; never substitute one silently for the other.

Every animation needs purpose/fallback. Substantial motion defines handoffs, interruption, responsive transformation, performance, reduced-motion/static equivalents, and evidence. Avoid scroll hijacking and uncontrolled perpetual motion.

Inspect before modifying; respect project conventions/user changes. Record consequential implementation choices in `implementation.capability_plan`; use `implementation.runtime_orchestration` where major runtimes share ownership. Keep changes bounded with acceptance, evidence, and rollback.

## Review + release

Builds do not prove visuals; screenshots do not prove interaction; recordings do not prove accessibility. Start with blocking floors and observed defects. Self/fresh-context reviews are not independent; automated checks prove only stated scope.

Begin with ordinary evidence. Escalate to logs/traces/profiles/runtime/media/frame inspection only for an unexplained real defect or deeper proof need; stop when cause/proof is clear. Never claim evidence not observed.

Before release verify declared accessibility, performance, public/private separation, security, support promises, rollback, and human approval. Missing required evidence means not production-ready.

## Portability

Keep product Runtime Capability Plan separate from temporary Host Capability Profile; re-discover after handoff. When capability is missing, name the semantic need first. The host may use native capability, plan a reviewed extension/plugin, hand off the bounded task, or return a portable packet. Planning grants no network/login/provider/spend/write/deploy authority.

For H3 or other external generation, discover the live model/tool capability before claiming support and preserve paid-task identity across handoff so a reconnect never creates a duplicate generation.

Handoffs carry compact contract/build/capability/continuity pointers, never hidden reasoning, transcripts, secrets, or assumed permissions. Validate Contract + Review + Handoff together when they describe one state.

One success never creates doctrine. Promote `sitecraft-learning-candidate` only after contrasting/stronger external evidence plus explicit `approved_for_promotion`; preserve its source.

## Delivery

Return the smallest useful package: current state, relevant rules, bounded work, changed paths, evidence/findings, unresolved risks, exact next approval/release condition, and Handoff only when needed. Do not emit a full Experience Contract merely to demonstrate compliance. Explain consequential decisions simply.

## Level report (print at the start of every run)
Before step 1, state which level this run can honestly reach:
- Level 2 (Checked): you can run the bundled scripts. Try `py -3`, `python`, `python3` (Windows) or `python3`, `python` (Mac/Linux). Run `scripts/sitecraft_check.py --help` once to prove it.
- Level 1 (Paper): you cannot run scripts. Follow the same gates and artifacts by hand. Every claim that needs a checker is labelled UNVERIFIED (not run), and the final receipt says "Level 1: checks not executed".
- Level 3 (Full): Level 2 plus an enforcer add-on that you have seen block or log a step in this session. Never claim Level 3 on faith.
Never report a higher level than you proved. Write the level into the gate log.

## Gates
Work in gates 0 to 8 with a gate log; on every return read it first. Details, fast path and commands: [gates](references/gates.md). Templates: `assets/PRODUCT.template.md`, `assets/DESIGN.template.md`, `assets/gate-log.template.json`.
