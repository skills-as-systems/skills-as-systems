# Premium craft: what separates "works" from "feels finished"

Premium is not decoration. It is restraint, consistency and care in the places people touch. Use this at gate 3 (build), gate 5 (fix loop) and gate 6 (critique). Every item is something an agent can look at and fix. The buyer's design sheet wins when it disagrees with this page.

## The premium pass (run after the first working build)
1. One focal point per screen. Squint at the 390px and 1440px shots: if three things compete, demote two (size, weight, colour, space).
2. Spacing from one scale. Use only the sheet's spacing steps. Group related things closer than unrelated things (proximity does more than borders). Generous space around the primary action and the headline.
3. Type that holds together. At most two families (often one). A fixed size scale (for example 14, 16, 20, 28, 40, 56). Body 16px or more, line height 1.5 to 1.7, line length 45 to 75 characters. Headings tighter (1.1 to 1.25). No more than three weights.
4. Colour with roles. Neutral surfaces, one accent for the primary action, semantic colours only for state. Check contrast (the checker does this). Avoid pure black on pure white for long text; avoid decorative gradients unless the sheet asks for them.
5. Every state designed. Hover, focus (visible), active, disabled, loading, empty, error, success. A page with only the happy state feels unfinished. Use `/harden` for long text, wrapping, empty and error, and interrupted animation.
6. Motion with purpose. 150 to 300ms, ease-out for entrances, nothing that blocks reading, no animation on every element. Honour `prefers-reduced-motion`. Motion shows cause and effect, it does not decorate.
7. Consistent details. One radius scale, one shadow scale, one icon style and stroke width, aligned edges, consistent button heights, optical alignment of icons and text.
8. Real content. No lorem ipsum, no "Click here", no generic stock claims. Specific verbs on buttons ("Book a tasting", not "Submit"). Real numbers, names, prices. If content is missing, mark it as a placeholder for the buyer, do not invent facts.
9. Stable and fast to the eye. No layout shift (set image sizes), fonts with fallbacks and `font-display`, images sized and compressed, skeletons for slow parts. A page that jumps feels cheap.
10. Touch and keyboard. Targets at least 44px where you can (24px is the minimum the checker enforces), logical tab order, visible focus, forms with labels and helpful errors.

## Common cheap tells (fix on sight)
Centered everything, equal-weight card grids with no hierarchy, three-column feature rows with generic icons, gradient text, glassmorphism everywhere, pill buttons of five sizes, shadows that differ on every card, emoji as icons, walls of grey text, placeholder-only form labels.

## How to decide, not guess
Show two options when taste is the question (gate 2 sketches). Ask the buyer for one reference site they love and one they hate, and write what you see in each as tokens and rules in the design sheet. Library ideas propose; the sheet decides.

## Evidence
Say what you checked: screenshots at 320, 390 and 1440px, the checker output (and `render_check.py` if it ran), and what you did not check (real devices, real users). "Premium" is a judgement; the evidence is the list above, shown.
