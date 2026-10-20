from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

from build_movement_prompt import build_movement_prompt, movement_chapters  # noqa: E402
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
            packet.write_text("# Movement 1\n\n- Chapter range: 1-8", encoding="utf-8")
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

    def test_validates_open_ended_ranges_of_six_or_more(self) -> None:
        for count in (6, 7, 8, 12, 20):
            with self.subTest(count=count):
                self.assertEqual(list(range(13, 13 + count)), movement_chapters(
                    f"- Chapter range: 13–{12 + count}"))

    def test_rejects_short_long_missing_and_invalid_ranges(self) -> None:
        for packet in ("- Chapter range: 1-3", "- Chapter range: 1-5",
                       "- Chapter range: 0-6",
                       "- Chapter range: 8-1", "# No range",
                       "- Chapter range: START-END", "- Chapter range: 1-6,9",
                       "- Chapter range: 1-6\n- Chapters: 7-12",
                       "# Brief\n\n## Sources\nRead chapters 1-8."):
            with self.subTest(packet=packet), self.assertRaises(ValueError):
                movement_chapters(packet)

    def test_short_owner_override_does_not_allow_invalid_range(self) -> None:
        self.assertEqual([5, 6, 7], movement_chapters(
            "- Chapter range: 5-7", allow_short_movement=True))
        for value in ("0-3", "5-1"):
            with self.assertRaises(ValueError):
                movement_chapters(f"- Chapter range: {value}", allow_short_movement=True)

    def test_existing_opening_brief_range_is_supported(self) -> None:
        self.assertEqual(list(range(13, 21)), movement_chapters(
            "# Callie\n- Book / movement: Callie, chapters 13–20.\n\n## Sources\nRead chapters 1–12."))

    def test_compiler_enforces_range_and_passes_exact_scope_to_author(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = root / "MOVEMENT.md"
            packet.write_text("- Chapter range: 21-28", encoding="utf-8")
            prompt = build_movement_prompt("fantasy", packet, root)
            self.assertIn("Draft chapters 21–28: 8 contiguous chapters", prompt)
            packet.write_text("- Chapter range: 21-24", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "six chapters or more"):
                build_movement_prompt("fantasy", packet, root)
            self.assertIn("Draft chapters 21–24: 4 contiguous chapters",
                          build_movement_prompt("fantasy", packet, root,
                                                allow_short_movement=True))


if __name__ == "__main__":
    unittest.main()
