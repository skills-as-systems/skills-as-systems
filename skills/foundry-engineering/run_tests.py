#!/usr/bin/env python3
"""Test entry point for the FOUNDRY package tests."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

TEST_FILE = Path(__file__).resolve().parent / "tests" / "test_package.py"
SPEC = importlib.util.spec_from_file_location("foundry_package_tests", TEST_FILE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {TEST_FILE}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FoundryPackageTests = MODULE.FoundryPackageTests

if __name__ == "__main__":
    unittest.main(verbosity=2)
