#!/usr/bin/env python3
"""Validate the portable SITECRAFT skill package without modifying it."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MUTABLE_WORKSPACE_PARTS = {"build", "dist", ".cache"}
FORBIDDEN_TOP_LEVEL_WORKSPACES = {"forward-tests", "captures", "evidence"}

REQUIRED_FILES = {
    "SKILL.md",
    "VERSION",
    "pyproject.toml",
    "agents/openai.yaml",
    "schemas/experience-contract.schema.json",
    "schemas/sitecraft-review.schema.json",
    "schemas/sitecraft-handoff.schema.json",
    "assets/experience-contract-template.json",
    "assets/sitecraft-review-template.json",
    "assets/handoff-packet-template.json",
    "assets/ai-builder-work-packet.md",
    "assets/image-generation-pack.md",
    "assets/video-generation-pack.md",
    "assets/asset-ledger.csv",
    "assets/reference-role-map.csv",
    "assets/evidence-matrix.csv",
    "assets/platform-evidence-matrix.csv",
    "assets/decision-log.csv",
    "examples/experience-contract-example.json",
    "examples/sitecraft-review-example.json",
    "examples/handoff-packet-example.json",
    "tests/routing-cases.json",
    "tests/negative-routing-cases.json",
    "tests/artifact-threshold-cases.json",
    "references/experience-contract.md",
    "references/interaction-and-routing.md",
    "references/experience-mapping.md",
    "references/content-and-discoverability.md",
    "references/research-and-reference-analysis.md",
    "references/visual-system.md",
    "references/asset-and-media-pipeline.md",
    "references/generated-image-production-compact.md",
    "references/generated-image-production.md",
    "references/generated-video-production-compact.md",
    "references/generated-video-production.md",
    "references/responsive-layout.md",
    "references/motion-and-interaction.md",
    "references/motion-design-and-graphics-compact.md",
    "references/motion-design-and-graphics.md",
    "references/accessibility.md",
    "references/performance.md",
    "references/ai-builder-translation.md",
    "references/implementation-routing.md",
    "references/capability-palette-compact.md",
    "references/capability-palette-and-orchestration.md",
    "references/evidence-and-qa.md",
    "references/security-and-boundaries.md",
    "references/harness-integration.md",
    "references/handoff-and-continuity.md",
    "references/platform-portability-compact.md",
    "references/platform-and-browser-portability.md",
    "references/tutorial-pattern-study.md",
    "references/animated-reference-build-compact.md",
    "references/release-audit-compact.md",
    "references/failure-tests.md",
    "references/evaluation-rubric.md",
    "references/research-basis.md",
    "references/character-identity-board.md",
    "references/creative-dna-reference-analysis.md",
    "references/interactive-generated-motion.md",
    "references/minimax-h3-video.md",
    "scripts/create_workspace.py",
    "scripts/validate_artifact.py",
    "tests/test_new_reference_modules.py",
    "run_tests.py",
}


class ValidationError(Exception):
    pass


def load_json(relative: str) -> Any:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON: {relative}: {exc}") from exc


def resolve_selector(selector: str) -> Path:
    base = selector.split("#", 1)[0]
    return ROOT / base


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValidationError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValidationError("SKILL.md frontmatter is not closed")
    block = text[4:end]
    values: dict[str, str] = {}
    for raw_line in block.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            raise ValidationError(f"Malformed frontmatter line: {raw_line!r}")
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_required_files(errors: list[str]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")


def validate_skill_md(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8-sig")
    try:
        frontmatter = parse_skill_frontmatter(text)
    except ValidationError as exc:
        errors.append(str(exc))
        return

    if set(frontmatter) != {"name", "description"}:
        errors.append("SKILL.md frontmatter must contain only name and description")
    if frontmatter.get("name") != "sitecraft":
        errors.append("SKILL.md name must be sitecraft")
    description = frontmatter.get("description", "")
    if len(description) < 80:
        errors.append("SKILL.md description is too short to route reliably")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds the 500-line progressive-disclosure limit")

    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in link or link.startswith("#"):
            continue
        if not resolve_selector(link).exists():
            errors.append(f"Broken SKILL.md link: {link}")

    banned = ["database migration contract", "native mobile release plan"]
    for phrase in banned:
        if phrase.lower() in text.lower():
            errors.append(f"Inherited domain phrase found in SKILL.md: {phrase}")


def validate_openai_yaml(errors: list[str]) -> None:
    path = ROOT / "agents/openai.yaml"
    text = path.read_text(encoding="utf-8-sig")
    required_fragments = [
        'display_name: "SITECRAFT"',
        'default_prompt: "Use $sitecraft',
        "allow_implicit_invocation: true",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(f"agents/openai.yaml missing: {fragment}")

    match = re.search(r'short_description:\s*"([^"]+)"', text)
    if not match:
        errors.append("agents/openai.yaml lacks a quoted short_description")
    elif not 25 <= len(match.group(1)) <= 64:
        errors.append("agents/openai.yaml short_description must be 25-64 characters")

    stray = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("openai.yaml")
        if path != ROOT / "agents/openai.yaml"
    ]
    if stray:
        errors.append(f"Stray openai.yaml files: {', '.join(sorted(stray))}")


def validate_version_metadata(errors: list[str]) -> None:
    version_path = ROOT / "VERSION"
    if version_path.is_file() and version_path.read_text(encoding="utf-8-sig").strip() != "0.3.1":
        errors.append("VERSION must be 0.3.1")

    pyproject_path = ROOT / "pyproject.toml"
    if pyproject_path.is_file():
        text = pyproject_path.read_text(encoding="utf-8-sig")
        required_fragments = [
            'name = "sitecraft-skill"',
            'version = "0.3.1"',
            'test_entry = "run_tests.py"',
        ]
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"pyproject.toml missing: {fragment}")


def validate_json_artifacts(errors: list[str]) -> None:
    json_paths = [
        "schemas/experience-contract.schema.json",
        "schemas/sitecraft-review.schema.json",
        "schemas/sitecraft-handoff.schema.json",
        "assets/experience-contract-template.json",
        "assets/sitecraft-review-template.json",
        "assets/handoff-packet-template.json",
        "examples/experience-contract-example.json",
        "examples/sitecraft-review-example.json",
        "examples/handoff-packet-example.json",
        "tests/routing-cases.json",
        "tests/negative-routing-cases.json",
        "tests/artifact-threshold-cases.json",
    ]
    artifacts: dict[str, Any] = {}
    for relative in json_paths:
        try:
            artifacts[relative] = load_json(relative)
        except ValidationError as exc:
            errors.append(str(exc))

    if len(artifacts) != len(json_paths):
        return

    schema = artifacts["schemas/experience-contract.schema.json"]
    required = set(schema.get("required", []))

    template_relative = "assets/experience-contract-template.json"
    template_missing = required.difference(artifacts[template_relative])
    if template_missing:
        errors.append(f"{template_relative} missing required keys: {sorted(template_missing)}")

    example_relative = "examples/experience-contract-example.json"
    try:
        import jsonschema  # type: ignore
    except ImportError:
        example_missing = required.difference(artifacts[example_relative])
        if example_missing:
            errors.append(f"{example_relative} missing required keys: {sorted(example_missing)}")
    else:
        try:
            jsonschema.Draft202012Validator(schema).validate(artifacts[example_relative])
        except jsonschema.ValidationError as exc:
            location = "/".join(str(item) for item in exc.absolute_path)
            errors.append(f"Schema validation failed for {example_relative} at {location}: {exc.message}")

    review_schema = artifacts["schemas/sitecraft-review.schema.json"]
    review_required = set(review_schema.get("required", []))
    review_template_relative = "assets/sitecraft-review-template.json"
    review_template_missing = review_required.difference(artifacts[review_template_relative])
    if review_template_missing:
        errors.append(
            f"{review_template_relative} missing required keys: {sorted(review_template_missing)}"
        )

    review_example_relative = "examples/sitecraft-review-example.json"
    try:
        import jsonschema  # type: ignore
    except ImportError:
        review_example_missing = review_required.difference(artifacts[review_example_relative])
        if review_example_missing:
            errors.append(
                f"{review_example_relative} missing required keys: {sorted(review_example_missing)}"
            )
    else:
        try:
            jsonschema.Draft202012Validator(review_schema).validate(
                artifacts[review_example_relative]
            )
        except jsonschema.ValidationError as exc:
            location = "/".join(str(item) for item in exc.absolute_path)
            errors.append(
                f"Schema validation failed for {review_example_relative} at {location}: {exc.message}"
            )

    handoff_schema = artifacts["schemas/sitecraft-handoff.schema.json"]
    handoff_required = set(handoff_schema.get("required", []))
    handoff_template_relative = "assets/handoff-packet-template.json"
    handoff_template_missing = handoff_required.difference(artifacts[handoff_template_relative])
    if handoff_template_missing:
        errors.append(
            f"{handoff_template_relative} missing required keys: {sorted(handoff_template_missing)}"
        )

    handoff_example_relative = "examples/handoff-packet-example.json"
    try:
        import jsonschema  # type: ignore
    except ImportError:
        handoff_example_missing = handoff_required.difference(artifacts[handoff_example_relative])
        if handoff_example_missing:
            errors.append(
                f"{handoff_example_relative} missing required keys: {sorted(handoff_example_missing)}"
            )
    else:
        try:
            jsonschema.Draft202012Validator(handoff_schema).validate(
                artifacts[handoff_example_relative]
            )
        except jsonschema.ValidationError as exc:
            location = "/".join(str(item) for item in exc.absolute_path)
            errors.append(
                f"Schema validation failed for {handoff_example_relative} at {location}: {exc.message}"
            )

    routing = artifacts["tests/routing-cases.json"]
    if not isinstance(routing, list) or len(routing) < 8:
        errors.append("tests/routing-cases.json must contain at least eight cases")
    else:
        ids: set[str] = set()
        for case in routing:
            case_id = case.get("id")
            if not case_id or case_id in ids:
                errors.append(f"Invalid or duplicate routing case id: {case_id!r}")
            ids.add(case_id)
            if not case.get("routes") or not case.get("required_references"):
                errors.append(f"Routing case lacks route/reference expectations: {case_id}")

    negative_routing = artifacts["tests/negative-routing-cases.json"]
    if not isinstance(negative_routing, list) or len(negative_routing) < 5:
        errors.append("tests/negative-routing-cases.json must contain at least five cases")
    else:
        negative_ids: set[str] = set()
        for case in negative_routing:
            case_id = case.get("id")
            if not case_id or case_id in negative_ids:
                errors.append(f"Invalid or duplicate negative routing case id: {case_id!r}")
            negative_ids.add(case_id)
            if case.get("expected") != "exclude_sitecraft" or not case.get("reason_contains"):
                errors.append(f"Negative routing case lacks exclusion expectation: {case_id}")

    artifact_cases = artifacts["tests/artifact-threshold-cases.json"]
    allowed_artifact_routes = {
        "compact_working_contract",
        "full_experience_contract",
        "update_existing_contract",
    }
    if not isinstance(artifact_cases, list) or len(artifact_cases) < 4:
        errors.append("tests/artifact-threshold-cases.json must contain at least four cases")
    else:
        artifact_ids: set[str] = set()
        observed_routes: set[str] = set()
        for case in artifact_cases:
            case_id = case.get("id")
            route = case.get("expected")
            if not case_id or case_id in artifact_ids:
                errors.append(f"Invalid or duplicate artifact-threshold case id: {case_id!r}")
            artifact_ids.add(case_id)
            observed_routes.add(route)
            if route not in allowed_artifact_routes or not case.get("reason"):
                errors.append(f"Invalid artifact-threshold expectation: {case_id}")
        if observed_routes != allowed_artifact_routes:
            errors.append("Artifact-threshold cases must cover compact, full, and existing-contract routes")


def validate_workspace_isolation(errors: list[str]) -> None:
    for name in sorted(FORBIDDEN_TOP_LEVEL_WORKSPACES):
        candidate = ROOT / name
        if candidate.exists():
            errors.append(
                f"Mutable workspace must not live at skill root: {name}; use build/forward-tests or a sibling project"
            )


def validate_platform_portability(errors: list[str]) -> None:
    machine_path_patterns = [
        re.compile("/" + "Users" + r"/[A-Za-z0-9._-]+/"),
        re.compile("/" + "home" + r"/[A-Za-z0-9._-]+/"),
        re.compile(r"[A-Za-z]:" + r"\\Users\\" + r"[^\\\s]+\\"),
    ]
    text_suffixes = {".md", ".json", ".yaml", ".yml", ".py", ".toml", ".csv"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        relative_path = path.relative_to(ROOT)
        if any(part.casefold() in MUTABLE_WORKSPACE_PARTS for part in relative_path.parts):
            continue
        text = path.read_text(encoding="utf-8-sig")
        for pattern in machine_path_patterns:
            if pattern.search(text):
                errors.append(
                    f"Machine-specific user path found in distributable file: {relative_path.as_posix()}"
                )
                break

    portable_python = [ROOT / "scripts" / "create_workspace.py", ROOT / "scripts" / "validate_artifact.py", ROOT / "scripts" / "validate_skill.py"]
    forbidden_process_fragments = ["shell" + "=True", "os." + "system("]
    for path in portable_python:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for fragment in forbidden_process_fragments:
            if fragment in text:
                errors.append(
                    f"Portable helper must not depend on an implicit shell: {path.relative_to(ROOT).as_posix()} contains {fragment}"
                )


def validate_no_placeholders(errors: list[str]) -> None:
    allowed_placeholder_files = {
        "assets/experience-contract-template.json",
        "assets/sitecraft-review-template.json",
        "assets/ai-builder-work-packet.md",
        "scripts/validate_skill.py",
    }
    forbidden_tokens = ["TODO", "TBD", "database migration contract"]
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml", ".py"}:
            continue
        relative_path = path.relative_to(ROOT)
        if any(part.casefold() in MUTABLE_WORKSPACE_PARTS for part in relative_path.parts):
            continue
        relative = relative_path.as_posix()
        if relative in allowed_placeholder_files:
            continue
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden_tokens:
            if token.lower() in text.lower():
                errors.append(f"Placeholder or inherited token {token!r} in {relative}")


def validate() -> list[str]:
    errors: list[str] = []
    validate_required_files(errors)
    if (ROOT / "SKILL.md").is_file():
        validate_skill_md(errors)
    if (ROOT / "agents/openai.yaml").is_file():
        validate_openai_yaml(errors)
    validate_version_metadata(errors)
    validate_json_artifacts(errors)
    validate_workspace_isolation(errors)
    validate_platform_portability(errors)
    validate_no_placeholders(errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("SITECRAFT validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SITECRAFT validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
