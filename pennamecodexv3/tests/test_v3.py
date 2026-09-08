from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

from build_prompt import build_prompt, within_root  # noqa: E402
from advance_loop import advance  # noqa: E402
from validate import load_json, validate_instance  # noqa: E402


class SchemaTests(unittest.TestCase):
    CASES = (
        ("scene-packet.schema.json", "scene-packet.example.json"),
        ("author-report.schema.json", "author-report.example.json"),
        ("editor-report.schema.json", "editor-report.example.json"),
        ("verification-report.schema.json", "verification-report.example.json"),
        ("loop-state.schema.json", "loop-state.example.json"),
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

    def test_editor_report_cannot_skip_all_gates(self) -> None:
        schema = load_json(PACKAGE_ROOT / "contracts" / "editor-report.schema.json")
        report = load_json(PACKAGE_ROOT / "templates" / "editor-report.example.json")
        report["gate_results"] = []
        errors = validate_instance(report, schema)
        self.assertTrue(any("fewer than 1 items" in error for error in errors))

    def test_editor_finding_cannot_be_born_verified(self) -> None:
        schema = load_json(PACKAGE_ROOT / "contracts" / "editor-report.schema.json")
        report = load_json(PACKAGE_ROOT / "templates" / "editor-report.example.json")
        report["findings"][0]["status"] = "VERIFIED"
        errors = validate_instance(report, schema)
        self.assertTrue(any("expected constant 'PROPOSED'" in error for error in errors))


class PromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.book_root = PACKAGE_ROOT / "examples" / "minimal-book"
        self.packet = self.book_root / "packets" / "scene-001.json"

    def test_author_prompt_is_deterministic(self) -> None:
        first = build_prompt("author", self.packet, self.book_root)
        second = build_prompt("author", self.packet, self.book_root)
        self.assertEqual(first, second)

    def test_author_gets_voice_but_not_editor_module_gates(self) -> None:
        prompt = build_prompt("author", self.packet, self.book_root)
        self.assertIn("SHARED POSITIVE VOICE", prompt)
        self.assertIn("PEN NAME VOICE — Monroe Jackson — Fantasy v1.1.1", prompt)
        self.assertIn("Growth is earned", prompt)
        self.assertNotIn("PEN NAME VOICE — Science Fiction Author B", prompt)
        self.assertNotIn("## Editor gates", prompt)
        self.assertNotIn("Positions and movement remain sufficiently legible", prompt)

    def test_editor_requires_the_declared_draft(self) -> None:
        packet = PACKAGE_ROOT / "templates" / "scene-packet.example.json"
        with self.assertRaises(FileNotFoundError):
            build_prompt("editor", packet, PACKAGE_ROOT)

    def test_context_path_cannot_escape_book_root(self) -> None:
        with self.assertRaises(ValueError):
            within_root(PACKAGE_ROOT, "../../outside.md")

    def test_minimal_dock_builds_all_role_prompts(self) -> None:
        book_root = self.book_root
        packet = self.packet
        author_prompt = build_prompt("author", packet, book_root)
        editor_prompt = build_prompt("editor", packet, book_root)
        verifier_prompt = build_prompt(
            "verifier", packet, book_root, Path("reports/scene-001-editor.json")
        )
        self.assertIn("CONTEXT — approved canon", author_prompt)
        self.assertIn("CONTEXT — name registry", author_prompt)
        self.assertNotIn("## Editor gates", author_prompt)
        self.assertIn("## Editor gates", editor_prompt)
        self.assertIn("MANUSCRIPT — drafts/scene-001.md", editor_prompt)
        self.assertIn("AUTHOR REPORT — reports/scene-001-author.json", editor_prompt)
        self.assertIn("word_target_state=OUTSIDE_TARGET", editor_prompt)
        self.assertIn("MANUSCRIPT — drafts/scene-001.md", verifier_prompt)
        self.assertIn("EDITOR REPORT —", verifier_prompt)

    def test_science_fiction_profile_requires_its_default_modules(self) -> None:
        packet = load_json(self.packet)
        packet["pen_name"] = "science-fiction-author-b"
        packet["modules"] = ["hard-science"]
        with tempfile.TemporaryDirectory() as directory:
            temp_packet = Path(directory) / "packet.json"
            temp_packet.write_text(json.dumps(packet), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "moral-choice"):
                build_prompt("author", temp_packet, self.book_root)

    def test_science_fiction_profile_compiles_without_influence_names(self) -> None:
        packet = load_json(self.packet)
        packet["pen_name"] = "science-fiction-author-b"
        packet["modules"] = ["hard-science", "moral-choice"]
        with tempfile.TemporaryDirectory() as directory:
            temp_packet = Path(directory) / "packet.json"
            temp_packet.write_text(json.dumps(packet), encoding="utf-8")
            prompt = build_prompt("author", temp_packet, self.book_root)
        self.assertIn("PEN NAME VOICE — Monroe Jackson — Science Fiction v1.1.1", prompt)
        self.assertIn("SELECTED MODULE — HARD-SCIENCE", prompt)
        self.assertIn("SELECTED MODULE — MORAL-CHOICE", prompt)
        for influence_name in ("Orson Scott Card", "Andy Weir", "Brandon Sanderson"):
            self.assertNotIn(influence_name, prompt)


class CompletionLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_json(PACKAGE_ROOT / "templates" / "loop-state.example.json")
        self.state["scenes_total"] = 1

    def test_scene_can_close_and_reach_voice_selection(self) -> None:
        advance(self.state, "start_scene", "scene-001", None, "")
        advance(self.state, "packet_validated", None, None, "")
        advance(self.state, "author_done", None, None, "")
        advance(self.state, "editor_pass", None, None, "")
        advance(self.state, "scope_audit", None, None, "")
        advance(self.state, "scope_pass", None, None, "")
        advance(self.state, "audio_audition_ready", None, None, "")
        self.assertEqual("AWAITING_VOICE_SELECTION", self.state["phase"])
        self.assertIsNotNone(self.state["human_gate"])
        advance(self.state, "voice_selected", None, None, "selected narrator A")
        self.assertEqual("COMPLETE", self.state["phase"])

    def test_same_defect_surviving_three_cycles_blocks(self) -> None:
        advance(self.state, "start_scene", "scene-001", None, "")
        advance(self.state, "packet_validated", None, None, "")
        advance(self.state, "author_done", None, None, "")
        for cycle in range(3):
            advance(self.state, "editor_findings", None, None, "")
            advance(self.state, "verification_repair", None, "same-finding", "")
            if cycle < 2:
                advance(self.state, "repair_done", None, None, "")
        self.assertEqual("BLOCKED", self.state["phase"])
        self.assertIn("same verified defect", self.state["blocker"])

    def test_book_cannot_pass_scope_audit_with_open_scenes(self) -> None:
        self.state["phase"] = "SCOPE_AUDIT"
        with self.assertRaisesRegex(ValueError, "scenes remain open"):
            advance(self.state, "scope_pass", None, None, "")

    def test_scope_repair_returns_to_scope_audit(self) -> None:
        self.state["phase"] = "SCOPE_AUDIT"
        self.state["scenes_closed"] = 1
        advance(self.state, "scope_findings", None, "book-finding", "")
        self.assertEqual("REPAIRING", self.state["phase"])
        advance(self.state, "repair_done", None, None, "")
        self.assertEqual("SCOPE_AUDIT", self.state["phase"])


if __name__ == "__main__":
    unittest.main()
