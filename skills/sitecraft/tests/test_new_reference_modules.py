from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        raise AssertionError(f"missing {rel}")
    return path.read_text(encoding="utf-8")


class NewReferenceModuleTests(unittest.TestCase):
    def test_character_identity_board_contract(self):
        text = read("references/character-identity-board.md")
        for required in [
            "2:1", "RIGHT 25%", "LEFT 10%", "CENTER 65%", "exactly four",
            "top-down", "low-angle", "Acceptance test", "gpt-image-2",
            "execution surface",
        ]:
            self.assertIn(required, text)
        self.assertNotIn("input_fidelity", text)

    def test_creative_dna_contract(self):
        text = read("references/creative-dna-reference-analysis.md")
        for required in ["Extract", "Abstract", "Recombine", "Motion DNA", "DO NOT COPY", "PROOF NEEDED"]:
            self.assertIn(required, text)

    def test_interactive_generated_motion_contract(self):
        text = read("references/interactive-generated-motion.md")
        for required in [
            "scroll", "pointer", "drag", "device orientation", "requestAnimationFrame",
            "prefers-reduced-motion", "Two-dimensional input rule", "Alpha WebP", "chroma MP4",
        ]:
            self.assertIn(required, text)



    def test_provider_adapters_are_not_bundled_in_portable_core(self):
        self.assertFalse((ROOT / "integrations").exists())



if __name__ == "__main__":
    unittest.main(verbosity=2)
