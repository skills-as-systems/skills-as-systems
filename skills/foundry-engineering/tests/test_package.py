#!/usr/bin/env python3
"""Regression, mutation, routing, and portability tests for FOUNDRY."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_artifact import validate_bundle, validate_file, validate_value  # noqa: E402
from validate_skill import validate as validate_skill  # noqa: E402


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


class FoundryPackageTests(unittest.TestCase):
    """Keep package contracts executable rather than merely aspirational."""

    def test_complete_package_validator(self) -> None:
        self.assertEqual(validate_skill(), [])

    def test_examples_validate_as_a_bundle(self) -> None:
        paths = [
            ROOT / "examples/system-map-example.json",
            ROOT / "examples/change-contract-example.json",
            ROOT / "examples/verification-receipt-example.json",
            ROOT / "examples/continuation-record-example.json",
        ]
        loaded = []
        for path in paths:
            errors, value = validate_file(path)
            self.assertEqual(errors, [], msg=f"{path.name}: {errors}")
            self.assertIsNotNone(value)
            loaded.append((path, value))
        self.assertEqual(validate_bundle(loaded), [])

    def test_system_map_rejects_unknown_behaviour_owner(self) -> None:
        value = load_json("examples/system-map-example.json")
        value["behavioural_paths"][0]["owner"] = "invented-owner"
        errors = validate_value(value)
        self.assertTrue(any("unknown owner" in error for error in errors), errors)

    def test_system_map_rejects_stale_action_sufficiency(self) -> None:
        value = load_json("examples/system-map-example.json")
        value["captured_state"]["freshness"] = "stale"
        errors = validate_value(value)
        self.assertTrue(any("sufficient_for_action" in error for error in errors), errors)

    def test_change_contract_rejects_dangling_risk_reference(self) -> None:
        value = load_json("examples/change-contract-example.json")
        value["verification_plan"][0]["risk_ids"] = ["risk-invented"]
        errors = validate_value(value)
        self.assertTrue(any("unknown risk" in error for error in errors), errors)

    def test_change_contract_cannot_claim_permissions(self) -> None:
        value = load_json("examples/change-contract-example.json")
        value["authority"]["permissions_carried_by_contract"] = True
        errors = validate_value(value)
        self.assertTrue(any("cannot carry permissions" in error for error in errors), errors)

    def test_tested_claim_requires_passing_evidence(self) -> None:
        value = load_json("examples/verification-receipt-example.json")
        value["claims"][0]["evidence_ids"] = []
        errors = validate_value(value)
        self.assertTrue(any("lacks evidence" in error for error in errors), errors)

        failed_evidence = load_json("examples/verification-receipt-example.json")
        failed_evidence["checks"][0]["outcome"] = "failed"
        errors = validate_value(failed_evidence)
        self.assertTrue(any("non-passing evidence" in error for error in errors), errors)

    def test_passed_verdict_rejects_unverified_claim(self) -> None:
        value = load_json("examples/verification-receipt-example.json")
        value["verdict"] = "passed"
        errors = validate_value(value)
        self.assertTrue(any("UNVERIFIED" in error for error in errors), errors)

    def test_continuation_rejects_permissions_and_dangling_dependency(self) -> None:
        value = load_json("examples/continuation-record-example.json")
        value["safety"]["permissions_carried_over"] = True
        value["next_eligible_work"][0]["dependency_ids"] = ["dependency-missing"]
        errors = validate_value(value)
        self.assertTrue(any("prohibited state" in error for error in errors), errors)
        self.assertTrue(any("unknown dependency" in error for error in errors), errors)

    def test_bundle_rejects_project_drift_and_missing_planned_claim(self) -> None:
        system_map = load_json("examples/system-map-example.json")
        contract = load_json("examples/change-contract-example.json")
        receipt = load_json("examples/verification-receipt-example.json")
        continuation = load_json("examples/continuation-record-example.json")
        contract["project_ref"] = "wrong-project"
        receipt["claims"] = [
            claim for claim in receipt["claims"] if claim["claim_id"] != "claim-timeout-flag"
        ]
        values = [
            (Path("system-map"), system_map),
            (Path("contract"), contract),
            (Path("receipt"), receipt),
            (Path("continuation"), continuation),
        ]
        errors = validate_bundle(values)
        self.assertTrue(any("System Map" in error for error in errors), errors)
        self.assertTrue(any("misses planned claims" in error for error in errors), errors)

    def test_routing_scenarios_are_bounded_and_resolvable(self) -> None:
        cases = load_json("tests/routing-cases.json")
        references = {path.stem for path in (ROOT / "references").glob("*.md")}
        for case in cases:
            with self.subTest(case=case["id"]):
                required = case["required_references"]
                self.assertLessEqual(len(required), case["max_references"])
                self.assertLessEqual(case["max_references"], 7)
                self.assertTrue(set(required).issubset(references))
                self.assertTrue(case["must_not"])
                routed_chars = sum(
                    len((ROOT / "references" / f"{reference}.md").read_text(encoding="utf-8-sig"))
                    for reference in required
                )
                self.assertLessEqual(routed_chars, 22_000)

    def test_adversarial_scenarios_define_evidence_and_vetoes(self) -> None:
        evaluation = load_json("tests/evaluation-cases.json")
        cases = evaluation["cases"]
        self.assertGreaterEqual(len(cases), evaluation["coverage_requirements"]["minimum_cases"])
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["expected_behaviour"])
                self.assertTrue(case["required_evidence"])
                self.assertTrue(case["failure_vetoes"])


    def test_artifact_mutation_does_not_change_source_example(self) -> None:
        original = load_json("examples/change-contract-example.json")
        mutated = copy.deepcopy(original)
        mutated["objective"]["outcome"] = "different"
        self.assertNotEqual(mutated, original)
        self.assertEqual(
            load_json("examples/change-contract-example.json")["objective"]["outcome"],
            original["objective"]["outcome"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
