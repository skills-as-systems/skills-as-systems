# Platform and browser portability

SITECRAFT must separate a support promise from evidence collected in one environment. A standards-based implementation may be expected to work broadly, but a macOS Safari pass does not prove Windows Chromium, Linux Firefox, another input method, or another assistive-technology stack.

## Three layers

Treat portability as three related layers:

1. **Portable core** — the Experience Contract, HTML, CSS, JavaScript, assets, tests, prompts, and review logic that should not depend on one operating system or harness.
2. **Host adapter** — the available file, browser, screenshot, recording, test, and deployment tools for the current environment.
3. **Evidence environment** — the exact operating system, architecture, browser and engine, viewport, input modes, assistive technology, motion preference, capture provider, build identity, and evidence date actually observed.

A host adapter may change. The portable core and approval rules must remain understandable without it.

## Support promise versus evidence

Record the intended browser and platform promise in `implementation.browser_support`. Record actual observations in `evidence_contract.environment_matrix` and the workspace platform-evidence matrix.

Use these evidence states:

- `planned` — required by the support promise but not yet observed;
- `partial` — some required views or interactions were observed;
- `passed` — the declared checks passed for this exact environment and build;
- `failed` — a named check failed;
- `unsupported` — the project deliberately does not support this environment;
- `not_required` — the environment is outside the approved scope.

Never convert `planned` or standards-based expectation into `passed`.

## Choose the matrix from the real audience

Do not test operating systems by habit. Derive the matrix from audience, analytics when trustworthy, organisational policy, device constraints, browser-support promise, accessibility needs, deployment risk, and the experience’s technical mechanisms.

A broad public-web promise normally needs evidence across more than one browser engine. A business application may need a narrower managed-browser matrix. A WebKit-specific feature needs an explicit fallback or a scoped support promise.

At minimum, consider:

- macOS with a WebKit browser when Apple desktop users are in scope;
- Windows with a Chromium browser when general desktop or managed-enterprise use is in scope;
- Linux with Chromium or Firefox when Linux desktop users, kiosks, development environments, or open-platform support are in scope;
- Firefox or another non-Chromium engine when the public support promise is broader than Chromium;
- mobile operating systems and real touch input when mobile use is material.

This is a planning matrix, not proof that every row was executed.

## Portable files, paths, and commands

For reusable SITECRAFT assets and helpers:

- use project-relative paths and language-native path APIs such as Python `pathlib`;
- do not hard-code a user home directory, drive letter, path separator, temporary directory, application bundle, or browser binary;
- do not assume paths are case-sensitive or case-insensitive;
- avoid filenames that depend on characters or reserved names that are invalid on another target system;
- write UTF-8 deliberately and tolerate normal line-ending differences;
- do not require Bash, PowerShell, AppleScript, or another shell for the portable core;
- expose package scripts or language-level entry points, then let each host adapter choose the safe command form;
- treat symlinks, executable bits, file permissions, quarantine, firewall prompts, localhost binding, and port availability as environment-specific;
- never store administrator credentials or bypass a local permission prompt.

Platform-specific instructions belong in a labelled adapter or evidence note, not in the provider-neutral contract.

## Browser and engine coverage

Record both browser name and rendering engine because different branded browsers may share an engine. For every required environment, test only the views, states, inputs, and mechanisms that matter to the contract.

Pay particular attention to:

- layout, font metrics, native form controls, focus rendering, scrolling, viewport units, sticky positioning, media decoding, and colour management;
- feature-detected progressive APIs and their fallback;
- keyboard conventions and browser preferences that change how links or controls receive focus;
- reduced-motion, forced colours, high contrast, zoom, text spacing, pointer, touch, and assistive technology;
- video, canvas, WebGL, WebGPU, SVG, Lottie, Rive, View Transitions, or other mechanisms whose support and performance vary by engine or device.

Do not repair an engine-specific problem by breaking the semantic fallback or another required environment.

## Capture and browser adapters

SITECRAFT may use Playwright, WebDriver, browser developer tools, a CI browser service, operating-system capture APIs, or manual evidence. None is mandatory to the skill.

For each capture or automation route, record:

- provider and version when known;
- browser and engine;
- operating system and architecture;
- whether the browser was headless, visible, emulated, remote, containerised, or native;
- viewport and device-pixel ratio;
- input method and motion or accessibility preferences;
- exact build identity;
- known limitations, such as an inability to keep the correct foreground window in a desktop recording.

A screenshot provider proves only the frame it captured. A browser automation provider proves only the interactions it executed. Neither proves another operating system.

## When another operating system is unavailable

Do not block useful work merely because every machine is not present. Instead:

1. keep portable structural and schema checks running locally;
2. add planned matrix rows for missing environments;
3. create a bounded manual, remote-browser, virtual-machine, CI, or collaborator test packet;
4. distinguish simulated path or parser tests from real browser execution;
5. narrow the support promise or keep release blocked when the missing environment is material.

A compatibility simulation can find obvious path and encoding defects. It cannot become a real Windows, Linux, macOS, browser-engine, touch, or assistive-technology receipt.

## Cross-platform release rule

Before calling a broad support promise verified:

- every required environment row is `passed`, `not_required`, or explicitly accepted as a bounded risk by the owner;
- failures have a named consequence and repair or support decision;
- screenshots, recordings, keyboard, accessibility, performance, and security evidence are scoped to their exact environment;
- implementation changes after a receipt stale the affected rows;
- the final approval names the tested matrix and exclusions.

Use `assets/platform-evidence-matrix.csv` for a simple portable ledger. Keep environment-specific raw evidence outside the distributable skill package.