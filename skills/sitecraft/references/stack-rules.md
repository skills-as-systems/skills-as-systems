# Stack rule sets (load only the one that matches)

Detect the stack from the files (package.json, config files, imports) and follow its conventions. Do not migrate a site to a new stack unless the contract says so.

## Plain HTML and CSS
Semantic landmarks (header, nav, main, footer), one h1, CSS custom properties for the sheet's tokens in `:root`, mobile-first media queries, `clamp()` for fluid type, logical properties where useful, no framework unless asked. Keep CSS in one file per concern; avoid `!important`.

## React (Vite or similar)
Components small and named for what they show. Tokens as CSS variables or a theme object loaded once; no hard-coded colours in components. Handle loading, empty and error in every data component. Keys on lists, labels on inputs, buttons for actions and links for navigation. Do not store derived data in state. Lazy-load heavy routes.

## Tailwind
Put the sheet's tokens in the Tailwind config (colors, fontFamily, spacing) and use them. No arbitrary values (`[13px]`, `#abc`) unless the sheet lacks a token; then add the token. Extract repeated class groups into components, not `@apply` piles. Use `focus-visible:` and `motion-reduce:` variants.

## Next.js
Server components by default; client components only where interactivity needs them. Use `next/image` with sizes and `next/font` for fonts. Metadata per page. Loading and error boundaries per route segment. No secrets in client bundles (only `NEXT_PUBLIC_` values are public).

## Whatever the stack
Run `scripts/sitecraft_check.py` on the built HTML/CSS (or the rendered output) and `render_check.py` if a browser is available. Say which stack rules you applied and which you could not verify.
