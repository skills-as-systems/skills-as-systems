#!/usr/bin/env python3
"""Validate repository structure, portability, host metadata, and package hygiene."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EXPECTED_SKILLS = (
    "sitecraft",
    "foundry-engineering",
)
REPOSITORY_REQUIRED = (
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".github/workflows/validate.yml",
    "docs/architecture.md",
    "docs/portability.md",
    "docs/evaluation.md",
    "docs/sitecraft.md",
    "docs/foundry.md",
    "docs/release-1.0.0.md",
    "docs/release-1.0.1.md",
    "docs/release-1.1.0.md",
    "benchmarks/README.md",
    "benchmarks/sitecraft-tideglass/results.json",
    "benchmarks/foundry-ledger-repair/results.json",
    "benchmarks/foundry-relaypack-boundary/results.json",
    "evaluations/cross-skill-routing.json",
    "scripts/install.py",
    "scripts/smoke_install.py",
    "scripts/validate_benchmarks.py",
)
REPOSITORY_ONLY_NAMES = {
    "README.md",
    "ARCHITECTURE.md",
    "MIGRATION.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
}
BANNED_PARTS = {
    ".git",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "browser-profile",
    "browser_profiles",
    "captures",
}
TEXT_SUFFIXES = {
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".toml",
    ".csv",
    ".txt",
}
MACHINE_PATHS = (
    re.compile(r"(?<![A-Za-z0-9])/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"(?<![A-Za-z0-9])/home/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
)


def load_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")
        return None


def parse_frontmatter(text: str, relative: str, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        errors.append(f"{relative}: SKILL.md must start with YAML frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{relative}: unclosed YAML frontmatter")
        return {}
    values: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            errors.append(f"{relative}: malformed frontmatter line {raw!r}")
            continue
        key, value = raw.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def package_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def validate_skill(name: str, errors: list[str]) -> None:
    root = SKILLS_ROOT / name
    relative_root = root.relative_to(ROOT).as_posix()
    if not root.is_dir():
        errors.append(f"Missing skill directory: {relative_root}")
        return

    for filename in REPOSITORY_ONLY_NAMES:
        if (root / filename).exists():
            errors.append(f"Repository-only file inside canonical skill: {relative_root}/{filename}")

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        errors.append(f"Missing {relative_root}/SKILL.md")
        return
    text = skill_path.read_text(encoding="utf-8-sig")
    frontmatter = parse_frontmatter(text, relative_root, errors)
    if set(frontmatter) != {"name", "description"}:
        errors.append(f"{relative_root}: canonical frontmatter must contain only name and description")
    if frontmatter.get("name") != name:
        errors.append(f"{relative_root}: frontmatter name must match directory")
    description = frontmatter.get("description", "")
    if not description.startswith("Use "):
        errors.append(f"{relative_root}: description must front-load 'Use ...' activation language")
    if not 40 <= len(description) <= 1024:
        errors.append(f"{relative_root}: description length must be 40-1024 characters")
    if len(text.splitlines()) > 500:
        errors.append(f"{relative_root}: SKILL.md exceeds 500 lines")
    if len(text) > 20_000:
        errors.append(f"{relative_root}: SKILL.md exceeds the approximate 5,000-token ceiling")

    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in link or link.startswith("#"):
            continue
        raw_path = link.split("#", 1)[0]
        resolved = (root / raw_path).resolve(strict=False)
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative_root}: link escapes skill root: {link}")
            continue
        if not resolved.exists():
            errors.append(f"{relative_root}: broken SKILL.md link: {link}")

    version_path = root / "VERSION"
    version = version_path.read_text(encoding="utf-8-sig").strip() if version_path.is_file() else ""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"{relative_root}: missing or invalid VERSION")
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file():
        pyproject = pyproject_path.read_text(encoding="utf-8-sig")
        if f'version = "{version}"' not in pyproject:
            errors.append(f"{relative_root}: pyproject.toml version differs from VERSION")

    openai_path = root / "agents" / "openai.yaml"
    if not openai_path.is_file():
        errors.append(f"{relative_root}: missing agents/openai.yaml")
    else:
        openai_text = openai_path.read_text(encoding="utf-8-sig")
        match = re.search(r'short_description:\s*"([^"]+)"', openai_text)
        if not match or not 25 <= len(match.group(1)) <= 64:
            errors.append(f"{relative_root}: Codex short_description must be 25-64 characters")
        if "allow_implicit_invocation: true" not in openai_text:
            errors.append(f"{relative_root}: Codex metadata must explicitly allow safe implicit routing")

    total = package_size(root)
    if total > 8 * 1024 * 1024:
        errors.append(f"{relative_root}: package exceeds 8 MiB ({total} bytes)")

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in BANNED_PARTS for part in relative.parts):
            errors.append(f"{relative_root}: development debris: {relative.as_posix()}")
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            errors.append(f"{relative_root}: oversized individual file: {relative.as_posix()}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            errors.append(f"{relative_root}: non-UTF-8 text resource: {relative.as_posix()}")
            continue
        if any(pattern.search(content) for pattern in MACHINE_PATHS):
            errors.append(f"{relative_root}: machine-specific path in {relative.as_posix()}")
        if any(pattern.search(content) for pattern in SECRET_PATTERNS):
            errors.append(f"{relative_root}: possible secret in {relative.as_posix()}")


def validate_host_wrappers(errors: list[str]) -> None:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    plugin = load_json(plugin_path, errors)
    marketplace = load_json(marketplace_path, errors)
    if isinstance(plugin, dict):
        if plugin.get("name") != "skills-as-systems":
            errors.append("Claude plugin name must be skills-as-systems")
        if plugin.get("license") != "Apache-2.0":
            errors.append("Claude plugin must declare Apache-2.0")
        if not isinstance(plugin.get("author"), dict) or plugin["author"].get("name") != "MAKIAVELI":
            errors.append("Claude plugin author must be MAKIAVELI")
    if isinstance(marketplace, dict):
        if marketplace.get("name") != "skills-as-systems":
            errors.append("Claude marketplace name must be skills-as-systems")
        if not isinstance(marketplace.get("owner"), dict) or marketplace["owner"].get("name") != "MAKIAVELI":
            errors.append("Claude marketplace owner must be MAKIAVELI")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1:
            errors.append("Claude marketplace must expose one collection plugin")
        else:
            entry = plugins[0]
            if entry.get("name") != "skills-as-systems" or entry.get("source") != "./":
                errors.append("Claude marketplace plugin must point at the repository root")
            if isinstance(plugin, dict) and entry.get("version") != plugin.get("version"):
                errors.append("Claude marketplace and plugin versions differ")
            if not isinstance(entry.get("author"), dict) or entry["author"].get("name") != "MAKIAVELI":
                errors.append("Claude marketplace plugin author must be MAKIAVELI")

    if "Portable Agent Skills by **MAKIAVELI**." not in (ROOT / "README.md").read_text(
        encoding="utf-8-sig"
    ):
        errors.append("README public attribution must be MAKIAVELI")
    if "Copyright 2026 MAKIAVELI" not in (ROOT / "LICENSE").read_text(encoding="utf-8-sig"):
        errors.append("LICENSE copyright notice must be MAKIAVELI")

    for name in EXPECTED_SKILLS:
        link = ROOT / ".agents" / "skills" / name
        expected = (SKILLS_ROOT / name).resolve()
        if not link.is_symlink():
            errors.append(f"Codex project-discovery path is not a symlink: {link.relative_to(ROOT)}")
        elif link.resolve() != expected:
            errors.append(f"Codex project-discovery link targets the wrong package: {name}")


def validate_json_files(errors: list[str]) -> None:
    for path in ROOT.rglob("*.json"):
        if any(part == ".git" for part in path.parts):
            continue
        load_json(path, errors)


def validate_repository_doc_links(errors: list[str]) -> None:
    paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "SECURITY.md"]
    paths.extend(sorted((ROOT / "docs").glob("*.md")))
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#") or link.startswith("mailto:"):
                continue
            raw_path = link.split("#", 1)[0]
            if not (path.parent / raw_path).resolve(strict=False).exists():
                errors.append(
                    f"Broken repository documentation link in {path.relative_to(ROOT)}: {link}"
                )


def validate_cross_skill_routing(errors: list[str]) -> None:
    path = ROOT / "evaluations" / "cross-skill-routing.json"
    cases = load_json(path, errors)
    if not isinstance(cases, list) or len(cases) < 18:
        errors.append("Cross-skill routing evaluation must contain at least 18 cases")
        return
    known = set(EXPECTED_SKILLS)
    ids: set[str] = set()
    multi_skill = 0
    intentional_none = 0
    expected_counts = {name: 0 for name in EXPECTED_SKILLS}
    for case in cases:
        if not isinstance(case, dict):
            errors.append("Cross-skill routing cases must be objects")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            errors.append(f"Invalid or duplicate cross-skill routing id: {case_id!r}")
            continue
        ids.add(case_id)
        expected = case.get("expected_skills")
        forbidden = case.get("forbidden_skills")
        if not isinstance(expected, list) or not isinstance(forbidden, list):
            errors.append(f"{case_id}: expected_skills and forbidden_skills must be lists")
            continue
        expected_set = set(expected)
        forbidden_set = set(forbidden)
        if not expected_set.union(forbidden_set).issubset(known):
            errors.append(f"{case_id}: unknown skill in routing expectation")
        if expected_set.intersection(forbidden_set):
            errors.append(f"{case_id}: a skill cannot be both expected and forbidden")
        if not isinstance(case.get("request"), str) or not case["request"].strip():
            errors.append(f"{case_id}: missing request")
        if not isinstance(case.get("reason"), str) or len(case["reason"].strip()) < 30:
            errors.append(f"{case_id}: missing substantive routing reason")
        if len(expected_set) > 1:
            multi_skill += 1
        if not expected_set:
            intentional_none += 1
        for name in expected_set:
            expected_counts[name] += 1
    if multi_skill < 3:
        errors.append("Cross-skill routing evaluation needs at least three multi-skill cases")
    if intentional_none < 4:
        errors.append("Cross-skill routing evaluation needs at least four intentional no-skill cases")
    for name, count in expected_counts.items():
        if count < 3:
            errors.append(f"Cross-skill routing under-covers {name}: {count} expected cases")


def run_skills_ref(require: bool, errors: list[str]) -> None:
    command = shutil.which("agentskills") or shutil.which("skills-ref")
    if command is None:
        if require:
            errors.append("Official skills-ref validator is required but not installed")
        else:
            print("NOTE: skills-ref not installed; official validation skipped")
        return
    for name in EXPECTED_SKILLS:
        result = subprocess.run(
            [command, "validate", str(SKILLS_ROOT / name)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stdout + result.stderr).strip()
            errors.append(f"skills-ref rejected {name}: {details}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-skills-ref", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors: list[str] = []
    for relative in REPOSITORY_REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing repository file: {relative}")
    actual = tuple(sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()))
    if actual != tuple(sorted(EXPECTED_SKILLS)):
        errors.append(f"Unexpected canonical skill set: {actual}")
    for name in EXPECTED_SKILLS:
        validate_skill(name, errors)
    validate_host_wrappers(errors)
    validate_json_files(errors)
    validate_repository_doc_links(errors)
    validate_cross_skill_routing(errors)
    run_skills_ref(args.require_skills_ref, errors)
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    sizes = ", ".join(
        f"{name}={package_size(SKILLS_ROOT / name) / 1024:.0f} KiB" for name in EXPECTED_SKILLS
    )
    print(f"Repository validation passed ({sizes}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
