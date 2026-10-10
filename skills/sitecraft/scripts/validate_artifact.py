#!/usr/bin/env python3
"""Validate a SITECRAFT JSON artifact against a bundled schema."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "experience-contract": ROOT / "schemas" / "experience-contract.schema.json",
    "review": ROOT / "schemas" / "sitecraft-review.schema.json",
    "handoff": ROOT / "schemas" / "sitecraft-handoff.schema.json",
    "video-generation-workflow": ROOT / "schemas" / "video-generation-workflow.schema.json",
    "learning-candidate": ROOT / "schemas" / "learning-candidate.schema.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def limited_validate(instance: dict, schema: dict) -> list[str]:
    """Standard-library fallback for top-level contract integrity."""
    errors: list[str] = []
    if not isinstance(instance, dict):
        return ["Artifact root must be a JSON object"]
    required = set(schema.get("required", []))
    missing = sorted(required.difference(instance))
    if missing:
        errors.append(f"Missing required top-level keys: {missing}")

    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in instance or not isinstance(rules, dict):
            continue
        if "const" in rules and instance[key] != rules["const"]:
            errors.append(f"{key} must equal {rules['const']!r}")
        if "enum" in rules and instance[key] not in rules["enum"]:
            errors.append(f"{key} must be one of {rules['enum']!r}")
    return errors


def experience_contract_semantic_errors(instance: Any) -> list[str]:
    """Enforce cross-runtime ownership and asset traceability without optional dependencies."""
    if not isinstance(instance, dict):
        return []

    errors: list[str] = []
    implementation = instance.get("implementation")
    decision_ids: set[str] = set()
    capability_routes: set[str] = set()

    if isinstance(implementation, dict):
        capability_plan = implementation.get("capability_plan")
        if isinstance(capability_plan, list):
            for index, item in enumerate(capability_plan):
                if not isinstance(item, dict):
                    continue
                decision_id = item.get("id")
                if not isinstance(decision_id, str) or not decision_id.strip():
                    continue
                decision_id = decision_id.strip()
                if decision_id in decision_ids:
                    errors.append(
                        f"/implementation/capability_plan/{index}/id duplicates capability decision {decision_id!r}"
                    )
                decision_ids.add(decision_id)
                selected_route = item.get("selected_route")
                if isinstance(selected_route, str) and selected_route.strip():
                    capability_routes.add(" ".join(selected_route.split()).casefold())

        orchestration = implementation.get("runtime_orchestration")
        if isinstance(orchestration, dict):
            mode = orchestration.get("mode")
            ownership = orchestration.get("ownership")
            bridges = orchestration.get("bridges")
            if mode == "coordinated_multi_runtime" and (
                not isinstance(ownership, list) or not ownership
            ):
                errors.append(
                    "/implementation/runtime_orchestration/ownership must identify at least one scoped owner for coordinated_multi_runtime"
                )

            seen_ownership: dict[tuple[str, str], tuple[int, str]] = {}
            if isinstance(ownership, list):
                for index, item in enumerate(ownership):
                    if not isinstance(item, dict):
                        continue
                    concern = str(item.get("concern") or "").strip().casefold()
                    scope = " ".join(str(item.get("scope") or "").split()).strip().casefold()
                    owner = " ".join(str(item.get("owner") or "").split()).strip()
                    if concern and scope:
                        key = (concern, scope)
                        previous = seen_ownership.get(key)
                        if previous is not None:
                            previous_index, previous_owner = previous
                            errors.append(
                                f"/implementation/runtime_orchestration/ownership/{index} conflicts with ownership/{previous_index}: "
                                f"{concern!r} in scope {scope!r} already belongs to {previous_owner!r}"
                            )
                        else:
                            seen_ownership[key] = (index, owner)
                    related = item.get("related_decision_ids")
                    if isinstance(related, list):
                        for decision_id in related:
                            if (
                                isinstance(decision_id, str)
                                and decision_id.strip()
                                and decision_id.strip() not in decision_ids
                            ):
                                errors.append(
                                    f"/implementation/runtime_orchestration/ownership/{index}/related_decision_ids references unknown capability decision {decision_id.strip()!r}"
                                )

            if isinstance(bridges, list):
                for index, item in enumerate(bridges):
                    if not isinstance(item, dict):
                        continue
                    related = item.get("related_decision_ids")
                    if isinstance(related, list):
                        for decision_id in related:
                            if (
                                isinstance(decision_id, str)
                                and decision_id.strip()
                                and decision_id.strip() not in decision_ids
                            ):
                                errors.append(
                                    f"/implementation/runtime_orchestration/bridges/{index}/related_decision_ids references unknown capability decision {decision_id.strip()!r}"
                                )

    visual_grammar = instance.get("visual_grammar")
    if isinstance(visual_grammar, dict):
        distinction = visual_grammar.get("creative_distinction")
        if isinstance(distinction, dict):
            valid_intents = {"task_specific", "brand_distinctive", "expressive_flagship"}
            if distinction.get("intent") not in valid_intents:
                errors.append(
                    "/visual_grammar/creative_distinction/intent must describe task_specific, brand_distinctive, or expressive_flagship work"
                )

            project_drivers = distinction.get("project_drivers")
            if not isinstance(project_drivers, list) or not any(
                isinstance(item, str) and item.strip() for item in project_drivers
            ):
                errors.append(
                    "/visual_grammar/creative_distinction/project_drivers must contain at least one concrete project driver"
                )

            mechanisms = distinction.get("mechanisms")
            if not isinstance(mechanisms, list) or not mechanisms:
                errors.append(
                    "/visual_grammar/creative_distinction/mechanisms must contain at least one project-specific design mechanism"
                )
            else:
                seen_mechanism_ids: dict[str, int] = {}
                seen_mechanisms: dict[str, int] = {}
                tool_only_labels = {
                    "css",
                    "waapi",
                    "web animations api",
                    "view transitions",
                    "gsap",
                    "framer motion",
                    "rive",
                    "lottie",
                    "dotlottie",
                    "svg",
                    "canvas",
                    "webgl",
                    "webgpu",
                    "three.js",
                    "threejs",
                    "react",
                    "next.js",
                    "nextjs",
                    "vue",
                    "svelte",
                    "video",
                    "generated video",
                    "3d",
                }
                for index, item in enumerate(mechanisms):
                    if not isinstance(item, dict):
                        continue
                    mechanism_id = " ".join(str(item.get("mechanism_id") or "").split()).strip()
                    mechanism_text = " ".join(str(item.get("mechanism") or "").split()).strip()
                    project_reason = " ".join(str(item.get("project_reason") or "").split()).strip()
                    surfaces = item.get("surfaces")
                    must_not_become = item.get("must_not_become")

                    if not mechanism_id:
                        errors.append(
                            f"/visual_grammar/creative_distinction/mechanisms/{index}/mechanism_id must be non-empty"
                        )
                    else:
                        normalized_id = mechanism_id.casefold()
                        previous = seen_mechanism_ids.get(normalized_id)
                        if previous is not None:
                            errors.append(
                                f"/visual_grammar/creative_distinction/mechanisms/{index}/mechanism_id duplicates mechanisms/{previous} ID {mechanism_id!r}"
                            )
                        else:
                            seen_mechanism_ids[normalized_id] = index

                    if not mechanism_text:
                        errors.append(
                            f"/visual_grammar/creative_distinction/mechanisms/{index}/mechanism must describe the design mechanism"
                        )
                    else:
                        normalized_mechanism = mechanism_text.casefold().strip(" .:_-")
                        previous = seen_mechanisms.get(normalized_mechanism)
                        if previous is not None:
                            errors.append(
                                f"/visual_grammar/creative_distinction/mechanisms/{index}/mechanism duplicates mechanisms/{previous} rather than adding a distinct mechanism"
                            )
                        else:
                            seen_mechanisms[normalized_mechanism] = index
                        if normalized_mechanism in tool_only_labels or normalized_mechanism in capability_routes:
                            errors.append(
                                f"/visual_grammar/creative_distinction/mechanisms/{index}/mechanism cannot be only an implementation route or tool name; describe what the project-specific design mechanism does instead"
                            )

                    if not project_reason:
                        errors.append(
                            f"/visual_grammar/creative_distinction/mechanisms/{index}/project_reason must explain why this mechanism belongs to this project"
                        )
                    if not isinstance(surfaces, list) or not any(
                        isinstance(surface, str) and surface.strip() for surface in surfaces
                    ):
                        errors.append(
                            f"/visual_grammar/creative_distinction/mechanisms/{index}/surfaces must identify where the mechanism is actually used"
                        )
                    if not isinstance(must_not_become, list) or not any(
                        isinstance(rule, str) and rule.strip() for rule in must_not_become
                    ):
                        errors.append(
                            f"/visual_grammar/creative_distinction/mechanisms/{index}/must_not_become must contain at least one drift guard"
                        )

            anti_repetition = distinction.get("anti_repetition_rules")
            if not isinstance(anti_repetition, list) or not any(
                isinstance(item, str) and item.strip() for item in anti_repetition
            ):
                errors.append(
                    "/visual_grammar/creative_distinction/anti_repetition_rules must contain at least one project-specific anti-repetition rule"
                )

        direction_selection = visual_grammar.get("direction_selection")
        if isinstance(direction_selection, dict):
            mode = direction_selection.get("mode")
            directions = direction_selection.get("directions")
            selected_id = direction_selection.get("selected_id")
            direction_ids: set[str] = set()
            structural_differences: set[str] = set()
            if isinstance(directions, list):
                for index, item in enumerate(directions):
                    if not isinstance(item, dict):
                        continue
                    direction_id = " ".join(str(item.get("id") or "").split()).strip()
                    structural_difference = " ".join(
                        str(item.get("structural_difference") or "").split()
                    ).strip()
                    if direction_id:
                        normalized_id = direction_id.casefold()
                        if normalized_id in direction_ids:
                            errors.append(
                                f"/visual_grammar/direction_selection/directions/{index}/id duplicates direction ID {direction_id!r}"
                            )
                        direction_ids.add(normalized_id)
                    if structural_difference:
                        normalized_difference = structural_difference.casefold()
                        if normalized_difference in structural_differences:
                            errors.append(
                                f"/visual_grammar/direction_selection/directions/{index}/structural_difference repeats another direction instead of describing a structurally different route"
                            )
                        structural_differences.add(normalized_difference)

            direction_count = len(directions) if isinstance(directions, list) else 0
            if mode in {"exploring", "converged"} and direction_count < 2:
                errors.append(
                    "/visual_grammar/direction_selection/directions must contain at least two structurally different directions while mode is exploring or converged"
                )
            if mode == "exploring" and selected_id is not None:
                errors.append(
                    "/visual_grammar/direction_selection/selected_id must be null while directions are still being explored"
                )
            if mode == "converged":
                normalized_selected = (
                    " ".join(selected_id.split()).casefold()
                    if isinstance(selected_id, str) and selected_id.strip()
                    else ""
                )
                if not normalized_selected or normalized_selected not in direction_ids:
                    errors.append(
                        "/visual_grammar/direction_selection/selected_id must name one declared direction after convergence"
                    )
            if mode == "not_needed" and selected_id is not None:
                errors.append(
                    "/visual_grammar/direction_selection/selected_id must be null when deliberate divergence is not needed"
                )

    surfaces: dict[str, set[str]] = {}
    experience_map = instance.get("experience_map")
    if isinstance(experience_map, dict):
        surface_items = experience_map.get("surfaces")
        if isinstance(surface_items, list):
            for item in surface_items:
                if not isinstance(item, dict):
                    continue
                surface_id = str(item.get("id") or "").strip()
                if not surface_id:
                    continue
                states = item.get("states")
                surfaces[surface_id] = {
                    str(state).strip()
                    for state in states
                    if isinstance(state, str) and state.strip()
                } if isinstance(states, list) else set()

    continuity = instance.get("continuity_system")
    if isinstance(continuity, dict):
        anchor_ids: set[str] = set()
        dimension_ids: set[str] = set()

        def validate_continuity_targets(values: Any, pointer: str) -> None:
            if not isinstance(values, list):
                return
            for target in values:
                if not isinstance(target, str):
                    continue
                target = target.strip()
                if target.startswith("surface:"):
                    surface_id = target.split(":", 1)[1]
                    if surface_id not in surfaces:
                        errors.append(f"{pointer} references unknown surface {surface_id!r}")
                elif target.startswith("state:"):
                    parts = target.split(":", 2)
                    if len(parts) != 3 or parts[1] not in surfaces or parts[2] not in surfaces.get(parts[1], set()):
                        errors.append(f"{pointer} references unknown state target {target!r}")

        anchors = continuity.get("anchors")
        if isinstance(anchors, list):
            for index, item in enumerate(anchors):
                if not isinstance(item, dict):
                    continue
                anchor_id = str(item.get("id") or "").strip()
                if anchor_id:
                    if anchor_id in anchor_ids:
                        errors.append(
                            f"/continuity_system/anchors/{index}/id duplicates continuity anchor {anchor_id!r}"
                        )
                    anchor_ids.add(anchor_id)
                validate_continuity_targets(
                    item.get("applies_to"),
                    f"/continuity_system/anchors/{index}/applies_to",
                )

        dimensions = continuity.get("state_dimensions")
        if isinstance(dimensions, list):
            for index, item in enumerate(dimensions):
                if not isinstance(item, dict):
                    continue
                dimension_id = str(item.get("id") or "").strip()
                if dimension_id:
                    if dimension_id in dimension_ids:
                        errors.append(
                            f"/continuity_system/state_dimensions/{index}/id duplicates state dimension {dimension_id!r}"
                        )
                    dimension_ids.add(dimension_id)
                validate_continuity_targets(
                    item.get("applies_to"),
                    f"/continuity_system/state_dimensions/{index}/applies_to",
                )

    lineage = instance.get("asset_lineage")
    if not isinstance(lineage, dict):
        return errors
    records = lineage.get("records")
    if not isinstance(records, list):
        return errors

    asset_ids: set[str] = set()
    record_by_id: dict[str, dict[str, Any]] = {}
    record_index: dict[str, int] = {}
    ledger_declared = isinstance(lineage.get("ledger_path"), str) and bool(
        str(lineage.get("ledger_path") or "").strip()
    )

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        asset_id = record.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            continue
        asset_id = asset_id.strip()
        if asset_id in asset_ids:
            errors.append(
                f"/asset_lineage/records/{index}/asset_id duplicates asset ID {asset_id!r}"
            )
        else:
            asset_ids.add(asset_id)
            record_by_id[asset_id] = record
            record_index[asset_id] = index
        declared_systems = record.get("declared_systems")
        if ledger_declared and (
            not isinstance(declared_systems, list) or "asset_ledger" not in declared_systems
        ):
            errors.append(
                f"/asset_lineage/records/{index}/declared_systems must include 'asset_ledger' while ledger_path is declared"
            )

    parent_graph: dict[str, list[str]] = {asset_id: [] for asset_id in asset_ids}
    for asset_id, record in record_by_id.items():
        index = record_index[asset_id]
        parents = record.get("parent_asset_ids")
        references = record.get("reference_asset_ids")
        parent_ids = [
            item.strip()
            for item in parents
            if isinstance(item, str) and item.strip()
        ] if isinstance(parents, list) else []
        reference_ids = [
            item.strip()
            for item in references
            if isinstance(item, str) and item.strip()
        ] if isinstance(references, list) else []

        overlap = sorted(set(parent_ids).intersection(reference_ids))
        if overlap:
            errors.append(
                f"/asset_lineage/records/{index} cannot treat the same asset IDs as both direct parents and references: {overlap!r}"
            )

        for field_name, related_ids in (
            ("parent_asset_ids", parent_ids),
            ("reference_asset_ids", reference_ids),
        ):
            for related_id in related_ids:
                if related_id == asset_id:
                    errors.append(
                        f"/asset_lineage/records/{index}/{field_name} cannot reference the asset itself {asset_id!r}"
                    )
                elif related_id not in asset_ids:
                    errors.append(
                        f"/asset_lineage/records/{index}/{field_name} references unknown asset ID {related_id!r}"
                    )
        parent_graph[asset_id] = [item for item in parent_ids if item in asset_ids]

        capability_ids = record.get("capability_decision_ids")
        if isinstance(capability_ids, list):
            for decision_id in capability_ids:
                if (
                    isinstance(decision_id, str)
                    and decision_id.strip()
                    and decision_id.strip() not in decision_ids
                ):
                    errors.append(
                        f"/asset_lineage/records/{index}/capability_decision_ids references unknown capability decision {decision_id.strip()!r}"
                    )

    visited: set[str] = set()
    cycle_signatures: set[tuple[str, ...]] = set()

    def visit_asset(asset_id: str, path: list[str]) -> None:
        if asset_id in path:
            start = path.index(asset_id)
            cycle = path[start:] + [asset_id]
            signature = tuple(sorted(set(cycle)))
            if signature not in cycle_signatures:
                cycle_signatures.add(signature)
                errors.append(
                    "/asset_lineage contains a direct-derivation cycle: "
                    + " -> ".join(cycle)
                )
            return
        if asset_id in visited:
            return
        for parent_id in parent_graph.get(asset_id, []):
            visit_asset(parent_id, path + [asset_id])
        visited.add(asset_id)

    for asset_id in sorted(asset_ids):
        visit_asset(asset_id, [])

    def require_asset(asset_id: Any, system: str, pointer: str) -> None:
        if not isinstance(asset_id, str) or not asset_id.strip():
            return
        stable_id = asset_id.strip()
        record = record_by_id.get(stable_id)
        if record is None:
            errors.append(f"{pointer} references asset ID {stable_id!r} missing from /asset_lineage/records")
            return
        declared_systems = record.get("declared_systems")
        if not isinstance(declared_systems, list) or system not in declared_systems:
            errors.append(
                f"{pointer} references asset ID {stable_id!r}, but its lineage record does not declare {system!r}"
            )

    image_system = instance.get("image_system")
    if isinstance(image_system, dict):
        asset_roles = image_system.get("asset_roles")
        if isinstance(asset_roles, list):
            for index, item in enumerate(asset_roles):
                if isinstance(item, dict):
                    require_asset(
                        item.get("id"),
                        "image_system",
                        f"/image_system/asset_roles/{index}/id",
                    )
        generation_routes = image_system.get("generation_routes")
        if isinstance(generation_routes, list):
            for index, item in enumerate(generation_routes):
                if isinstance(item, dict):
                    require_asset(
                        item.get("asset_id"),
                        "image_system",
                        f"/image_system/generation_routes/{index}/asset_id",
                    )

        reference_role_ids: set[str] = set()
        reference_roles = image_system.get("reference_roles")
        if isinstance(reference_roles, list):
            for index, item in enumerate(reference_roles):
                if not isinstance(item, dict):
                    continue
                reference_id = item.get("reference_id")
                if not isinstance(reference_id, str) or not reference_id.strip():
                    continue
                reference_id = reference_id.strip()
                if reference_id in reference_role_ids:
                    errors.append(
                        f"/image_system/reference_roles/{index}/reference_id duplicates reference ID {reference_id!r}"
                    )
                reference_role_ids.add(reference_id)

        production_jobs = image_system.get("production_jobs")
        if isinstance(production_jobs, list):
            job_ids: set[str] = set()
            job_output_assets: dict[str, int] = {}
            job_graph: dict[str, list[str]] = {}
            job_index_by_id: dict[str, int] = {}

            for index, item in enumerate(production_jobs):
                if not isinstance(item, dict):
                    continue
                pointer = f"/image_system/production_jobs/{index}"
                job_id = item.get("job_id")
                stable_job_id = job_id.strip() if isinstance(job_id, str) else ""
                if stable_job_id:
                    if stable_job_id in job_ids:
                        errors.append(f"{pointer}/job_id duplicates production job {stable_job_id!r}")
                    else:
                        job_ids.add(stable_job_id)
                        job_index_by_id[stable_job_id] = index

                output_asset = item.get("asset_id")
                stable_output = output_asset.strip() if isinstance(output_asset, str) else ""
                if stable_output:
                    require_asset(stable_output, "image_system", f"{pointer}/asset_id")
                    previous = job_output_assets.get(stable_output)
                    if previous is not None:
                        errors.append(
                            f"{pointer}/asset_id duplicates production output asset {stable_output!r} from production_jobs/{previous}; one distinct asset requires one job"
                        )
                    else:
                        job_output_assets[stable_output] = index

                dependencies = item.get("depends_on_job_ids")
                dependency_ids = [
                    value.strip()
                    for value in dependencies
                    if isinstance(value, str) and value.strip()
                ] if isinstance(dependencies, list) else []
                job_graph[stable_job_id] = dependency_ids if stable_job_id else []

                sources = item.get("source_asset_ids")
                source_ids = [
                    value.strip()
                    for value in sources
                    if isinstance(value, str) and value.strip()
                ] if isinstance(sources, list) else []
                for source_id in source_ids:
                    require_asset(source_id, "image_system", f"{pointer}/source_asset_ids")
                    if stable_output and source_id == stable_output:
                        errors.append(
                            f"{pointer}/source_asset_ids cannot use the output asset itself {stable_output!r} as its edit source"
                        )

                required_approved = item.get("required_approved_asset_ids")
                required_ids = [
                    value.strip()
                    for value in required_approved
                    if isinstance(value, str) and value.strip()
                ] if isinstance(required_approved, list) else []
                for required_id in required_ids:
                    require_asset(
                        required_id,
                        "image_system",
                        f"{pointer}/required_approved_asset_ids",
                    )

                references = item.get("reference_ids")
                production_reference_ids = [
                    value.strip()
                    for value in references
                    if isinstance(value, str) and value.strip()
                ] if isinstance(references, list) else []
                for reference_id in production_reference_ids:
                    if reference_id not in reference_role_ids:
                        errors.append(
                            f"{pointer}/reference_ids references unknown image reference role {reference_id!r}"
                        )

                intent = item.get("intent")
                if intent == "edit" and not source_ids:
                    errors.append(f"{pointer}/source_asset_ids must name at least one edit source when intent is 'edit'")
                if intent == "generate" and source_ids:
                    errors.append(
                        f"{pointer}/source_asset_ids must be empty when intent is 'generate'; use reference_ids for bounded influence or change the job intent to 'edit' when an existing image must be modified"
                    )

                if intent == "edit" and stable_output:
                    output_record = record_by_id.get(stable_output)
                    parent_ids = output_record.get("parent_asset_ids") if isinstance(output_record, dict) else None
                    declared_parents = {
                        value.strip()
                        for value in parent_ids
                        if isinstance(value, str) and value.strip()
                    } if isinstance(parent_ids, list) else set()
                    for source_id in source_ids:
                        if source_id not in declared_parents:
                            errors.append(
                                f"{pointer}/source_asset_ids declares edit source {source_id!r}, but asset lineage for {stable_output!r} does not list it as a direct parent"
                            )

            for index, item in enumerate(production_jobs):
                if not isinstance(item, dict):
                    continue
                pointer = f"/image_system/production_jobs/{index}"
                job_id = item.get("job_id")
                stable_job_id = job_id.strip() if isinstance(job_id, str) else ""
                dependencies = item.get("depends_on_job_ids")
                dependency_ids = [
                    value.strip()
                    for value in dependencies
                    if isinstance(value, str) and value.strip()
                ] if isinstance(dependencies, list) else []
                for dependency_id in dependency_ids:
                    if dependency_id == stable_job_id and stable_job_id:
                        errors.append(f"{pointer}/depends_on_job_ids cannot depend on itself {stable_job_id!r}")
                    elif dependency_id not in job_ids:
                        errors.append(
                            f"{pointer}/depends_on_job_ids references unknown production job {dependency_id!r}"
                        )

            visited_jobs: set[str] = set()
            job_cycles: set[tuple[str, ...]] = set()

            def visit_job(job_id: str, path: list[str]) -> None:
                if job_id in path:
                    start = path.index(job_id)
                    cycle = path[start:] + [job_id]
                    signature = tuple(sorted(set(cycle)))
                    if signature not in job_cycles:
                        job_cycles.add(signature)
                        errors.append(
                            "/image_system/production_jobs contains a dependency cycle: "
                            + " -> ".join(cycle)
                        )
                    return
                if job_id in visited_jobs:
                    return
                for dependency_id in job_graph.get(job_id, []):
                    if dependency_id in job_ids:
                        visit_job(dependency_id, path + [job_id])
                visited_jobs.add(job_id)

            for job_id in sorted(job_ids):
                visit_job(job_id, [])

    video_system = instance.get("video_system")
    if isinstance(video_system, dict):
        asset_roles = video_system.get("asset_roles")
        if isinstance(asset_roles, list):
            for index, item in enumerate(asset_roles):
                if not isinstance(item, dict):
                    continue
                require_asset(
                    item.get("id"),
                    "video_system",
                    f"/video_system/asset_roles/{index}/id",
                )
                require_asset(
                    item.get("poster_asset_id"),
                    "video_system",
                    f"/video_system/asset_roles/{index}/poster_asset_id",
                )
                require_asset(
                    item.get("fallback_asset_id"),
                    "video_system",
                    f"/video_system/asset_roles/{index}/fallback_asset_id",
                )
                capability_id = item.get("capability_decision_id")
                if (
                    isinstance(capability_id, str)
                    and capability_id.strip()
                    and capability_id.strip() not in decision_ids
                ):
                    errors.append(
                        f"/video_system/asset_roles/{index}/capability_decision_id references unknown capability decision {capability_id.strip()!r}"
                    )

    motion_system = instance.get("motion_system")
    if isinstance(motion_system, dict):
        delivery_routes = motion_system.get("delivery_routes")
        if isinstance(delivery_routes, list):
            for index, item in enumerate(delivery_routes):
                if not isinstance(item, dict):
                    continue
                require_asset(
                    item.get("asset_id"),
                    "motion_system",
                    f"/motion_system/delivery_routes/{index}/asset_id",
                )
                require_asset(
                    item.get("fallback_asset_id"),
                    "motion_system",
                    f"/motion_system/delivery_routes/{index}/fallback_asset_id",
                )

    return errors


def learning_candidate_semantic_errors(instance: Any) -> list[str]:
    """Keep project learning local until it has real contrasting support and promotion authority."""
    if not isinstance(instance, dict):
        return []

    errors: list[str] = []
    status = instance.get("status")
    contrast = instance.get("contrast_evidence")
    external = instance.get("external_evidence")
    has_contrast = isinstance(contrast, list) and any(
        isinstance(item, str) and item.strip() for item in contrast
    )
    has_external = isinstance(external, list) and any(
        isinstance(item, str) and item.strip() for item in external
    )

    if status in {"contrasted", "promoted"} and not (has_contrast or has_external):
        errors.append(
            "/status cannot be contrasted or promoted until contrast_evidence or stronger external_evidence exists"
        )
    if status == "promoted":
        if instance.get("user_verdict") != "approved_for_promotion":
            errors.append(
                "/user_verdict must be 'approved_for_promotion' before a candidate becomes core doctrine"
            )
        promotion_target = instance.get("promotion_target")
        if not isinstance(promotion_target, str) or not promotion_target.strip():
            errors.append(
                "/promotion_target must name the bounded core destination before status is 'promoted'"
            )

    return errors


def sitecraft_review_semantic_errors(instance: Any) -> list[str]:
    """Prevent review provenance from overstating independence."""
    if not isinstance(instance, dict):
        return []

    errors: list[str] = []
    provenance = instance.get("review_provenance")
    if not isinstance(provenance, list):
        return errors

    expected_pairs = {
        "self_review": ("same_context", "not_independent"),
        "fresh_context_review": ("same_actor_fresh_context", "fresh_context_only"),
        "independent_agent_review": ("separate_actor", "independent"),
        "human_owner_review": ("human_owner", "human_authority"),
        "automated_evidence_check": ("automated_system", "automated_check"),
    }
    seen_ids: set[str] = set()
    for index, item in enumerate(provenance):
        if not isinstance(item, dict):
            continue
        review_id = str(item.get("id") or "").strip()
        if review_id:
            if review_id in seen_ids:
                errors.append(
                    f"/review_provenance/{index}/id duplicates review provenance ID {review_id!r}"
                )
            seen_ids.add(review_id)
        kind = item.get("kind")
        expected = expected_pairs.get(kind)
        if expected is None:
            continue
        expected_relation, expected_independence = expected
        if item.get("build_relation") != expected_relation:
            errors.append(
                f"/review_provenance/{index}/build_relation must be {expected_relation!r} for {kind!r}"
            )
        if item.get("independence") != expected_independence:
            errors.append(
                f"/review_provenance/{index}/independence must be {expected_independence!r} for {kind!r}"
            )

    return errors


def sitecraft_handoff_semantic_errors(instance: Any) -> list[str]:
    """Enforce portable handoff coordination and non-transferable authority without optional dependencies."""
    if not isinstance(instance, dict):
        return []

    errors: list[str] = []
    execution = instance.get("execution")
    if not isinstance(execution, dict) or execution.get(
        "receiving_host_must_rediscover_capabilities"
    ) is not True:
        errors.append(
            "/execution/receiving_host_must_rediscover_capabilities must be true"
        )

    safety = instance.get("safety")
    if not isinstance(safety, dict):
        errors.append("/safety must be present")
    else:
        for key in [
            "contains_hidden_reasoning",
            "contains_private_transcript",
            "contains_secrets",
            "permissions_carried_over",
        ]:
            if safety.get(key) is not False:
                errors.append(f"/safety/{key} must be false")

    coordination = instance.get("coordination")
    if not isinstance(coordination, dict):
        return errors + ["/coordination must be present for a safe handoff"]

    if coordination.get("receiving_host_must_confirm_checkout_before_write") is not True:
        errors.append(
            "/coordination/receiving_host_must_confirm_checkout_before_write must be true"
        )

    workspace_mode = coordination.get("workspace_mode")
    checkout_status = coordination.get("checkout_status")
    current_owner = coordination.get("current_owner")
    receiver_write_policy = coordination.get("receiver_write_policy")
    checkout_reference = coordination.get("checkout_reference")
    receipts = coordination.get("coordination_receipts")
    state = instance.get("state")
    blockers = state.get("blockers") if isinstance(state, dict) else None

    if workspace_mode == "isolated":
        if checkout_status != "not_shared":
            errors.append(
                "/coordination/checkout_status must be 'not_shared' when workspace_mode is 'isolated'"
            )
        if current_owner not in {None, ""}:
            errors.append(
                "/coordination/current_owner must be null for an isolated workspace"
            )
        if receiver_write_policy != "allowed_after_revalidation":
            errors.append(
                "/coordination/receiver_write_policy must be 'allowed_after_revalidation' for an isolated workspace"
            )
    elif workspace_mode == "unknown":
        if checkout_status != "revalidate_required":
            errors.append(
                "/coordination/checkout_status must be 'revalidate_required' when workspace ownership is unknown"
            )
        if receiver_write_policy != "read_only_until_handoff":
            errors.append(
                "/coordination/receiver_write_policy must remain 'read_only_until_handoff' while workspace ownership is unknown"
            )
    elif workspace_mode == "shared":
        if not isinstance(checkout_reference, str) or not checkout_reference.strip():
            errors.append(
                "/coordination/checkout_reference must identify the shared checkout"
            )
        if checkout_status == "free":
            if current_owner not in {None, ""}:
                errors.append(
                    "/coordination/current_owner must be null when a shared checkout is free"
                )
            if receiver_write_policy != "allowed_after_revalidation":
                errors.append(
                    "/coordination/receiver_write_policy must be 'allowed_after_revalidation' when a shared checkout is explicitly free"
                )
            if not isinstance(receipts, list) or not any(
                isinstance(item, str) and item.strip() for item in receipts
            ):
                errors.append(
                    "/coordination/coordination_receipts must contain an explicit release/handoff receipt before a shared checkout can be marked free"
                )
        elif checkout_status == "reserved":
            if not isinstance(current_owner, str) or not current_owner.strip():
                errors.append(
                    "/coordination/current_owner must name the current owner while a shared checkout is reserved"
                )
            if receiver_write_policy != "read_only_until_handoff":
                errors.append(
                    "/coordination/receiver_write_policy must be 'read_only_until_handoff' while a shared checkout is reserved"
                )
        elif checkout_status == "blocked":
            if receiver_write_policy != "blocked":
                errors.append(
                    "/coordination/receiver_write_policy must be 'blocked' when checkout_status is 'blocked'"
                )
            if not isinstance(blockers, list) or not any(
                isinstance(item, str) and item.strip() for item in blockers
            ):
                errors.append(
                    "/state/blockers must explain why a blocked shared checkout cannot proceed"
                )
        elif checkout_status == "revalidate_required":
            if receiver_write_policy != "read_only_until_handoff":
                errors.append(
                    "/coordination/receiver_write_policy must remain 'read_only_until_handoff' while a shared checkout requires revalidation"
                )
        else:
            errors.append(
                "/coordination/checkout_status cannot be 'not_shared' for a shared workspace"
            )
    else:
        errors.append(
            "/coordination/workspace_mode must be isolated, shared, or unknown"
        )

    return errors


def video_generation_workflow_semantic_errors(instance: Any) -> list[str]:
    """Enforce critical generated-video gates even without jsonschema installed."""
    if not isinstance(instance, dict):
        return []
    errors: list[str] = []
    readiness = instance.get("generation_readiness")
    asset_plan = instance.get("asset_plan")
    inspection = instance.get("provider_inspection")
    stage_state = instance.get("stage_state")

    if (
        instance.get("route_decision") == "generated_video"
        and isinstance(readiness, dict)
        and readiness.get("ready") is True
    ):
        required_true = [
            (asset_plan, "host_can_inspect_result", "/asset_plan/host_can_inspect_result"),
            (asset_plan, "prompt_ready", "/asset_plan/prompt_ready"),
            (asset_plan, "references_ready", "/asset_plan/references_ready"),
            (inspection, "catalogue_discovered", "/provider_inspection/catalogue_discovered"),
            (inspection, "current_source_used", "/provider_inspection/current_source_used"),
            (inspection, "model_requirements_known", "/provider_inspection/model_requirements_known"),
            (readiness, "provider_model_frozen", "/generation_readiness/provider_model_frozen"),
            (readiness, "settings_checked_against_contract", "/generation_readiness/settings_checked_against_contract"),
        ]
        for container, key, pointer in required_true:
            if not isinstance(container, dict) or container.get(key) is not True:
                errors.append(f"{pointer} must be true before generation readiness can be declared")
        if not isinstance(inspection, dict) or not isinstance(inspection.get("provider"), str) or not inspection["provider"].strip():
            errors.append("/provider_inspection/provider must name the inspected provider before generation readiness")
        if not isinstance(inspection, dict) or not isinstance(inspection.get("model"), str) or not inspection["model"].strip():
            errors.append("/provider_inspection/model must name the inspected model before generation readiness")
        settings_summary = inspection.get("settings_summary") if isinstance(inspection, dict) else None
        if not isinstance(settings_summary, list) or not any(isinstance(item, str) and item.strip() for item in settings_summary):
            errors.append("/provider_inspection/settings_summary must record at least one current model/setting fact before generation readiness")
        if not isinstance(inspection, dict) or inspection.get("generation_performed_during_inspection") is not False:
            errors.append(
                "/provider_inspection/generation_performed_during_inspection must be false before generation readiness can be declared"
            )
        if isinstance(stage_state, dict):
            if stage_state.get("asset_plan") not in {"passed", "warnings"}:
                errors.append("/stage_state/asset_plan must be passed or warnings before generation readiness")
            if stage_state.get("provider_inspection") not in {"passed", "warnings"}:
                errors.append("/stage_state/provider_inspection must be passed or warnings before generation readiness")

    review = instance.get("review_delivery")
    if isinstance(review, dict) and review.get("decision") == "accepted":
        for key in [
            "actual_artifact_inspected",
            "hard_floors_passed",
            "delivery_verified",
            "responsive_delivery_verified",
            "performance_budget_verified",
            "media_accessibility_verified",
            "reduced_motion_verified",
        ]:
            if review.get(key) is not True:
                errors.append(f"/review_delivery/{key} must be true before an artifact can be accepted")
        artifact_reference = review.get("artifact_reference")
        if not isinstance(artifact_reference, str) or not artifact_reference.strip():
            errors.append("/review_delivery/artifact_reference must identify the inspected artifact before acceptance")
        evidence_refs = review.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not any(isinstance(item, str) and item.strip() for item in evidence_refs):
            errors.append("/review_delivery/evidence_refs must contain at least one concrete evidence reference before acceptance")
        if review.get("owner_approval") not in {"approved", "not_required"}:
            errors.append(
                "/review_delivery/owner_approval must be approved or not_required before an artifact can be accepted"
            )
    return errors


def split_csv_ids(value: Any) -> list[str]:
    """Parse semicolon-separated stable IDs used by SITECRAFT CSV artifacts."""
    if not isinstance(value, str):
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def load_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = [str(field or "").strip() for field in (reader.fieldnames or [])]
        rows = [
            {str(key or "").strip(): str(value or "").strip() for key, value in row.items()}
            for row in reader
        ]
    return rows, fields


def validate_traceability_bundle(
    contract_path: Path,
    ledger_path: Path,
    evidence_path: Path,
) -> list[str]:
    """Cross-check consequential asset lineage across contract, ledger and evidence CSVs."""
    contract = load_json(contract_path)
    if not isinstance(contract, dict):
        return ["Traceability contract root must be a JSON object"]

    errors: list[str] = []
    lineage = contract.get("asset_lineage")
    if not isinstance(lineage, dict):
        return ["/asset_lineage is required for traceability-bundle validation"]
    records = lineage.get("records")
    if not isinstance(records, list):
        return ["/asset_lineage/records must be an array for traceability-bundle validation"]

    contract_assets: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        asset_id = record.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            continue
        stable_id = asset_id.strip()
        if stable_id in contract_assets:
            errors.append(
                f"/asset_lineage/records/{index}/asset_id duplicates asset ID {stable_id!r}"
            )
        else:
            contract_assets[stable_id] = record

    implementation = contract.get("implementation")
    decision_ids: set[str] = set()
    if isinstance(implementation, dict):
        plan = implementation.get("capability_plan")
        if isinstance(plan, list):
            for item in plan:
                if isinstance(item, dict):
                    decision_id = item.get("id")
                    if isinstance(decision_id, str) and decision_id.strip():
                        decision_ids.add(decision_id.strip())

    ledger_rows, ledger_fields = load_csv_rows(ledger_path)
    ledger_required = {
        "asset_id",
        "lineage_stage",
        "parent_asset_ids",
        "reference_asset_ids",
        "capability_decision_ids",
        "evidence_ids",
        "approval_state",
    }
    missing_ledger_fields = sorted(ledger_required.difference(ledger_fields))
    if missing_ledger_fields:
        errors.append(
            "Asset ledger is missing required traceability columns: "
            + ", ".join(missing_ledger_fields)
        )

    evidence_rows, evidence_fields = load_csv_rows(evidence_path)
    evidence_required = {
        "evidence_id",
        "contract_revision",
        "capability_decision_ids",
        "asset_ids",
    }
    missing_evidence_fields = sorted(evidence_required.difference(evidence_fields))
    if missing_evidence_fields:
        errors.append(
            "Evidence matrix is missing required traceability columns: "
            + ", ".join(missing_evidence_fields)
        )

    expected_contract_revision = str(contract.get("revision") or "").strip()
    evidence_by_id: dict[str, dict[str, str]] = {}
    for index, row in enumerate(evidence_rows, start=2):
        evidence_id = row.get("evidence_id", "").strip()
        if not evidence_id:
            continue
        if "contract_revision" in evidence_fields:
            evidence_revision = row.get("contract_revision", "").strip()
            if evidence_revision != expected_contract_revision:
                errors.append(
                    f"Evidence matrix row {index} contract revision disagrees with Experience Contract: "
                    f"contract={expected_contract_revision!r}, evidence={evidence_revision!r}"
                )
        if evidence_id in evidence_by_id:
            errors.append(
                f"Evidence matrix row {index} duplicates evidence ID {evidence_id!r}"
            )
        else:
            evidence_by_id[evidence_id] = row
        for asset_id in split_csv_ids(row.get("asset_ids", "")):
            if asset_id not in contract_assets:
                errors.append(
                    f"Evidence matrix row {index} references unknown lineage asset ID {asset_id!r}"
                )
        for decision_id in split_csv_ids(row.get("capability_decision_ids", "")):
            if decision_id not in decision_ids:
                errors.append(
                    f"Evidence matrix row {index} references unknown capability decision {decision_id!r}"
                )

    ledger_by_id: dict[str, dict[str, str]] = {}
    for index, row in enumerate(ledger_rows, start=2):
        asset_id = row.get("asset_id", "").strip()
        if not asset_id:
            continue
        if asset_id in ledger_by_id:
            errors.append(f"Asset ledger row {index} duplicates asset ID {asset_id!r}")
        else:
            ledger_by_id[asset_id] = row

        for field_name in ("parent_asset_ids", "reference_asset_ids"):
            for related_id in split_csv_ids(row.get(field_name, "")):
                if related_id not in contract_assets:
                    errors.append(
                        f"Asset ledger row {index} {field_name} references unknown lineage asset ID {related_id!r}"
                    )
        for decision_id in split_csv_ids(row.get("capability_decision_ids", "")):
            if decision_id not in decision_ids:
                errors.append(
                    f"Asset ledger row {index} references unknown capability decision {decision_id!r}"
                )
        for evidence_id in split_csv_ids(row.get("evidence_ids", "")):
            if evidence_id not in evidence_by_id:
                errors.append(
                    f"Asset ledger row {index} references unknown evidence ID {evidence_id!r}"
                )

    for asset_id, record in contract_assets.items():
        row = ledger_by_id.get(asset_id)
        if row is None:
            errors.append(
                f"Lineage asset {asset_id!r} is missing from the supplied asset ledger"
            )
            continue

        expected_parents = {
            item.strip()
            for item in record.get("parent_asset_ids", [])
            if isinstance(item, str) and item.strip()
        }
        actual_parents = set(split_csv_ids(row.get("parent_asset_ids", "")))
        if actual_parents != expected_parents:
            errors.append(
                f"Asset {asset_id!r} parent_asset_ids disagree between contract and ledger: "
                f"contract={sorted(expected_parents)!r}, ledger={sorted(actual_parents)!r}"
            )

        expected_references = {
            item.strip()
            for item in record.get("reference_asset_ids", [])
            if isinstance(item, str) and item.strip()
        }
        actual_references = set(split_csv_ids(row.get("reference_asset_ids", "")))
        if actual_references != expected_references:
            errors.append(
                f"Asset {asset_id!r} reference_asset_ids disagree between contract and ledger: "
                f"contract={sorted(expected_references)!r}, ledger={sorted(actual_references)!r}"
            )

        expected_stage = str(record.get("stage") or "").strip()
        actual_stage = row.get("lineage_stage", "").strip()
        if expected_stage and actual_stage != expected_stage:
            errors.append(
                f"Asset {asset_id!r} lineage stage disagrees between contract and ledger: "
                f"contract={expected_stage!r}, ledger={actual_stage!r}"
            )

        expected_approval = str(record.get("approval_state") or "").strip()
        actual_approval = row.get("approval_state", "").strip()
        if expected_approval and actual_approval != expected_approval:
            errors.append(
                f"Asset {asset_id!r} approval state disagrees between contract and ledger: "
                f"contract={expected_approval!r}, ledger={actual_approval!r}"
            )

        expected_decisions = {
            item.strip()
            for item in record.get("capability_decision_ids", [])
            if isinstance(item, str) and item.strip()
        }
        actual_decisions = set(split_csv_ids(row.get("capability_decision_ids", "")))
        if actual_decisions != expected_decisions:
            errors.append(
                f"Asset {asset_id!r} capability_decision_ids disagree between contract and ledger: "
                f"contract={sorted(expected_decisions)!r}, ledger={sorted(actual_decisions)!r}"
            )

        expected_evidence = {
            item.strip()
            for item in record.get("evidence_refs", [])
            if isinstance(item, str) and item.strip()
        }
        actual_evidence = set(split_csv_ids(row.get("evidence_ids", "")))
        missing_from_ledger = sorted(expected_evidence.difference(actual_evidence))
        if missing_from_ledger:
            errors.append(
                f"Asset {asset_id!r} contract evidence refs are missing from ledger evidence_ids: {missing_from_ledger!r}"
            )
        for evidence_id in expected_evidence:
            if evidence_id not in evidence_by_id:
                errors.append(
                    f"Asset {asset_id!r} contract references unknown evidence ID {evidence_id!r}"
                )

    return errors


def validate_continuation_bundle(
    contract_path: Path,
    review_path: Path,
    handoff_path: Path,
) -> list[str]:
    """Cross-check project, revision and capability continuity across core SITECRAFT artifacts."""
    contract = load_json(contract_path)
    review = load_json(review_path)
    handoff = load_json(handoff_path)

    errors: list[str] = []
    if not isinstance(contract, dict):
        errors.append("Continuation contract root must be a JSON object")
    if not isinstance(review, dict):
        errors.append("Continuation review root must be a JSON object")
    if not isinstance(handoff, dict):
        errors.append("Continuation handoff root must be a JSON object")
    if errors:
        return errors

    contract_project = str(contract.get("project") or "").strip()
    review_project = str(review.get("project") or "").strip()
    handoff_project_block = handoff.get("project")
    handoff_project = (
        str(handoff_project_block.get("name") or "").strip()
        if isinstance(handoff_project_block, dict)
        else ""
    )
    if contract_project and review_project != contract_project:
        errors.append(
            "Review project identity disagrees with Experience Contract: "
            f"contract={contract_project!r}, review={review_project!r}"
        )
    if contract_project and handoff_project != contract_project:
        errors.append(
            "Handoff project identity disagrees with Experience Contract: "
            f"contract={contract_project!r}, handoff={handoff_project!r}"
        )

    contract_revision = contract.get("revision")
    review_revision = review.get("contract_revision")
    handoff_contract = handoff.get("contract")
    handoff_revision = (
        handoff_contract.get("revision")
        if isinstance(handoff_contract, dict)
        else None
    )
    if review_revision != contract_revision:
        errors.append(
            "Review contract_revision disagrees with Experience Contract revision: "
            f"contract={contract_revision!r}, review={review_revision!r}"
        )
    if handoff_revision != contract_revision:
        errors.append(
            "Handoff contract revision disagrees with Experience Contract revision: "
            f"contract={contract_revision!r}, handoff={handoff_revision!r}"
        )

    contract_status = str(contract.get("status") or "").strip()
    handoff_status = (
        str(handoff_contract.get("status") or "").strip()
        if isinstance(handoff_contract, dict)
        else ""
    )
    if contract_status and handoff_status != contract_status:
        errors.append(
            "Handoff contract status disagrees with Experience Contract status: "
            f"contract={contract_status!r}, handoff={handoff_status!r}"
        )

    capability_ids: set[str] = set()
    implementation = contract.get("implementation")
    if isinstance(implementation, dict):
        capability_plan = implementation.get("capability_plan")
        if isinstance(capability_plan, list):
            for item in capability_plan:
                if not isinstance(item, dict):
                    continue
                decision_id = item.get("id")
                if isinstance(decision_id, str) and decision_id.strip():
                    capability_ids.add(decision_id.strip())

    capability_scope = review.get("capability_scope")
    reviewed_ids: set[str] = set()
    unreviewed_ids: set[str] = set()
    if isinstance(capability_scope, dict):
        reviewed_ids = {
            item.strip()
            for item in capability_scope.get("reviewed_ids", [])
            if isinstance(item, str) and item.strip()
        }
        unreviewed_ids = {
            item.strip()
            for item in capability_scope.get("unreviewed_ids", [])
            if isinstance(item, str) and item.strip()
        }
    overlap = sorted(reviewed_ids.intersection(unreviewed_ids))
    if overlap:
        errors.append(
            "Review capability_scope lists capability decisions as both reviewed and unreviewed: "
            + ", ".join(overlap)
        )
    review_ids = reviewed_ids.union(unreviewed_ids)
    unknown_review_ids = sorted(review_ids.difference(capability_ids))
    if unknown_review_ids:
        errors.append(
            "Review capability_scope references unknown Experience Contract capability decisions: "
            + ", ".join(unknown_review_ids)
        )
    missing_review_ids = sorted(capability_ids.difference(review_ids))
    if missing_review_ids:
        errors.append(
            "Review capability_scope does not account for Experience Contract capability decisions: "
            + ", ".join(missing_review_ids)
        )

    handoff_ids: set[str] = set()
    if isinstance(handoff_contract, dict):
        handoff_ids = {
            item.strip()
            for item in handoff_contract.get("capability_decision_ids", [])
            if isinstance(item, str) and item.strip()
        }
    unknown_handoff_ids = sorted(handoff_ids.difference(capability_ids))
    if unknown_handoff_ids:
        errors.append(
            "Handoff references unknown Experience Contract capability decisions: "
            + ", ".join(unknown_handoff_ids)
        )

    continuity = contract.get("continuity_system")
    continuity_anchor_ids: set[str] = set()
    continuity_dimension_ids: set[str] = set()
    if isinstance(continuity, dict):
        anchors = continuity.get("anchors")
        if isinstance(anchors, list):
            continuity_anchor_ids = {
                str(item.get("id") or "").strip()
                for item in anchors
                if isinstance(item, dict) and str(item.get("id") or "").strip()
            }
        dimensions = continuity.get("state_dimensions")
        if isinstance(dimensions, list):
            continuity_dimension_ids = {
                str(item.get("id") or "").strip()
                for item in dimensions
                if isinstance(item, dict) and str(item.get("id") or "").strip()
            }

    if isinstance(handoff_contract, dict):
        handoff_anchor_ids = {
            item.strip()
            for item in handoff_contract.get("continuity_anchor_ids", [])
            if isinstance(item, str) and item.strip()
        }
        handoff_dimension_ids = {
            item.strip()
            for item in handoff_contract.get("continuity_state_dimension_ids", [])
            if isinstance(item, str) and item.strip()
        }
        unknown_anchor_ids = sorted(handoff_anchor_ids.difference(continuity_anchor_ids))
        if unknown_anchor_ids:
            errors.append(
                "Handoff references unknown Experience Contract continuity anchors: "
                + ", ".join(unknown_anchor_ids)
            )
        unknown_dimension_ids = sorted(
            handoff_dimension_ids.difference(continuity_dimension_ids)
        )
        if unknown_dimension_ids:
            errors.append(
                "Handoff references unknown Experience Contract continuity state dimensions: "
                + ", ".join(unknown_dimension_ids)
            )

    return errors


def validate(instance_path: Path, schema_path: Path) -> tuple[list[str], bool]:
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    if schema_path.name == "video-generation-workflow.schema.json":
        semantic_errors = video_generation_workflow_semantic_errors(instance)
    elif schema_path.name == "experience-contract.schema.json":
        semantic_errors = experience_contract_semantic_errors(instance)
    elif schema_path.name == "sitecraft-review.schema.json":
        semantic_errors = sitecraft_review_semantic_errors(instance)
    elif schema_path.name == "sitecraft-handoff.schema.json":
        semantic_errors = sitecraft_handoff_semantic_errors(instance)
    elif schema_path.name == "learning-candidate.schema.json":
        semantic_errors = learning_candidate_semantic_errors(instance)
    else:
        semantic_errors = []
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return limited_validate(instance, schema) + semantic_errors, True

    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append(f"{location}: {error.message}")
    errors.extend(error for error in semantic_errors if error not in errors)
    return errors, False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument(
        "--kind",
        choices=sorted(SCHEMAS),
        required=True,
        help="Bundled SITECRAFT schema to use",
    )
    parser.add_argument(
        "--asset-ledger",
        type=Path,
        default=None,
        help="Optional asset ledger CSV for Experience Contract traceability validation",
    )
    parser.add_argument(
        "--evidence-matrix",
        type=Path,
        default=None,
        help="Optional evidence matrix CSV for Experience Contract traceability validation",
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=None,
        help="Optional SITECRAFT Review to cross-check with an Experience Contract and Handoff Packet",
    )
    parser.add_argument(
        "--handoff",
        type=Path,
        default=None,
        help="Optional Handoff Packet to cross-check with an Experience Contract and SITECRAFT Review",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact = args.artifact.expanduser().resolve()
    schema = SCHEMAS[args.kind]
    ledger_arg = args.asset_ledger
    evidence_arg = args.evidence_matrix
    review_arg = args.review
    handoff_arg = args.handoff

    if (ledger_arg is None) != (evidence_arg is None):
        print(
            "Traceability validation requires both --asset-ledger and --evidence-matrix together.",
            file=sys.stderr,
        )
        return 2
    if ledger_arg is not None and args.kind != "experience-contract":
        print(
            "--asset-ledger and --evidence-matrix are only valid with --kind experience-contract.",
            file=sys.stderr,
        )
        return 2
    if (review_arg is None) != (handoff_arg is None):
        print(
            "Continuation validation requires both --review and --handoff together.",
            file=sys.stderr,
        )
        return 2
    if review_arg is not None and args.kind != "experience-contract":
        print(
            "--review and --handoff are only valid with --kind experience-contract.",
            file=sys.stderr,
        )
        return 2

    try:
        errors, limited = validate(artifact, schema)
        if ledger_arg is not None and evidence_arg is not None:
            errors.extend(
                validate_traceability_bundle(
                    artifact,
                    ledger_arg.expanduser().resolve(),
                    evidence_arg.expanduser().resolve(),
                )
            )
        if review_arg is not None and handoff_arg is not None:
            errors.extend(
                validate_continuation_bundle(
                    artifact,
                    review_arg.expanduser().resolve(),
                    handoff_arg.expanduser().resolve(),
                )
            )
    except (OSError, json.JSONDecodeError, csv.Error) as exc:
        print(f"Validation failed to run: {exc}", file=sys.stderr)
        return 2

    if errors:
        print(f"SITECRAFT {args.kind} validation failed:")
        for error in errors:
            print(f"- {error}")
        if limited:
            print(
                "Note: jsonschema is not installed; SITECRAFT standard-library structural and semantic gates were still applied."
            )
        return 1

    if limited:
        print(
            f"SITECRAFT {args.kind} passed standard-library structural and semantic validation. "
            "Install jsonschema or use a full JSON Schema validator for Draft 2020-12 schema validation."
        )
    else:
        print(f"SITECRAFT {args.kind} validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
