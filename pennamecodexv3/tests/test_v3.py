from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

from build_prompt import build_prompt, within_root  # noqa: E402
from validate import load_json, validate_instance  # noqa: E402


class SchemaTests(unittest.TestCase):
    CASES = (
        ("scene-packet.schema.json", "scene-packet.example.json"),
        ("author-report.schema.json", "author-report.example.json"),
        ("editor-report.schema.json", "editor-report.example.json"),
        ("run-record.schema.json", "run-record.example.json"),
    )

    def test_examples_validate(self) -> None:
        for schema_name, example_name in self.CASES:
            with self.subTest(example=example_name):
                schema = load_json(PACKAGE_ROOT / "contracts" / schema_name)
                instance = load_json(PACKAGE_ROOT / "templates" / example_name)
                self.assertEqual([], validate_instance(instance, schema))

    def test_scene_packet_rejects_unknown_fields(self) -> None:
        schema = load_json(PACKAGE_ROOT / "contracts" / "scene-packet.schema.json")
        packet = load_json(PACKAGE_ROOT / "templates" / "scene-packet.example.json")
        broken = copy.deepcopy(packet)
        broken["provider"] = "claude"
        errors = validate_instance(broken, schema)
        self.assertTrue(any("unexpected property 'provider'" in error for error in errors))


class PromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = PACKAGE_ROOT / "templates" / "scene-packet.example.json"

    def test_author_prompt_is_deterministic(self) -> None:
        first = build_prompt("author", self.packet, PACKAGE_ROOT)
        second = build_prompt("author", self.packet, PACKAGE_ROOT)
        self.assertEqual(first, second)

    def test_author_gets_voice_but_not_editor_module_gates(self) -> None:
        prompt = build_prompt("author", self.packet, PACKAGE_ROOT)
        self.assertIn("POSITIVE VOICE CHARTER", prompt)
        self.assertIn("Growth is earned", prompt)
        self.assertNotIn("## Editor gates", prompt)
        self.assertNotIn("Positions and movement remain sufficiently legible", prompt)

    def test_editor_requires_the_declared_draft(self) -> None:
        with self.assertRaises(FileNotFoundError):
            build_prompt("editor", self.packet, PACKAGE_ROOT)

    def test_context_path_cannot_escape_book_root(self) -> None:
        with self.assertRaises(ValueError):
            within_root(PACKAGE_ROOT, "../../outside.md")

    def test_minimal_dock_builds_both_role_prompts(self) -> None:
        book_root = PACKAGE_ROOT / "examples" / "minimal-book"
        packet = book_root / "packets" / "scene-001.json"
        author_prompt = build_prompt("author", packet, book_root)
        editor_prompt = build_prompt("editor", packet, book_root)
        self.assertIn("CONTEXT — approved canon", author_prompt)
        self.assertNotIn("## Editor gates", author_prompt)
        self.assertIn("## Editor gates", editor_prompt)
        self.assertIn("MANUSCRIPT — drafts/scene-001.md", editor_prompt)
        self.assertIn("AUTHOR REPORT — reports/scene-001-author.json", editor_prompt)


if __name__ == "__main__":
    unittest.main()
