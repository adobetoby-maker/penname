from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

from build_movement_prompt import build_movement_prompt  # noqa: E402
from build_showrunner_prompt import build_showrunner_prompt  # noqa: E402


class ShowrunnerTests(unittest.TestCase):
    def test_package_is_1_2_0(self) -> None:
        self.assertEqual("1.2.0", (PACKAGE_ROOT / "VERSION").read_text().strip())

    def test_showrunner_prompt_is_deterministic_and_loop_based(self) -> None:
        first = build_showrunner_prompt("A city remembers its dead.", "fantasy", "not selected")
        second = build_showrunner_prompt("A city remembers its dead.", "fantasy", "not selected")
        self.assertEqual(first, second)
        self.assertIn("Sonnet showrunner session", first)
        self.assertIn("NOW", first)
        self.assertIn("NEXT", first)
        self.assertIn("HORIZON", first)
        self.assertIn("POSSIBLE", first)
        self.assertIn("learning-deception", first)
        self.assertIn("Do not write manuscript prose", first)

    def test_installed_action_manifest_resolves_every_layer(self) -> None:
        manifest = json.loads(
            (PACKAGE_ROOT / "craft" / "action-layers" / "manifest.json").read_text()
        )
        for layers in manifest["stacks"].values():
            for layer in layers:
                self.assertTrue(
                    (PACKAGE_ROOT / "craft" / "action-layers" / f"{layer}.md").is_file()
                )


class LightMovementTests(unittest.TestCase):
    def test_compiler_loads_only_assigned_layers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = root / "MOVEMENT-001.md"
            packet.write_text("# Movement 1\n\nDraft chapters 1-4.", encoding="utf-8")
            prompt = build_movement_prompt(
                "fantasy",
                Path("MOVEMENT-001.md"),
                root,
                ["chapter 2=learning-deception"],
            )
        self.assertIn("Monroe Jackson — Fantasy Light 1.2.0", prompt)
        self.assertIn("ACTION LAYER — CORE", prompt)
        self.assertIn("ACTION LAYER — LEARNING", prompt)
        self.assertIn("ACTION LAYER — MISDIRECTION", prompt)
        self.assertIn("ACTION LAYER — KINETIC", prompt)
        self.assertNotIn("ACTION LAYER — ARSENAL", prompt)
        self.assertNotIn("ACTION LAYER — HIGH_STAKES", prompt)
        self.assertNotIn("41 craft principles", prompt)

    def test_compiler_rejects_unknown_stack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = root / "MOVEMENT.md"
            packet.write_text("# Movement", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown action stack"):
                build_movement_prompt(
                    "scifi", packet, root, ["climax=everything-everywhere"]
                )

    def test_packet_cannot_escape_book_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "escapes book root"):
                build_movement_prompt("fantasy", Path("../outside.md"), root, [])


if __name__ == "__main__":
    unittest.main()
