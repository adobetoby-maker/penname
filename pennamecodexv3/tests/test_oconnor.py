from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_oconnor_prompt as compiler


class OConnorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "brief.md").write_text("- PWA book id: example\n\nA rescue changes trust.\n")

    def args(self, mode="movement", *extra):
        args = [mode, "--root", str(self.root), "--author", "opus"]
        if mode == "movement":
            args += ["--packet", "brief.md", "--owner-style-root", str(self.root / "owner")]
        return compiler.parser().parse_args(args + list(extra))

    def test_open_range_full_chapter_destinations_and_determinism(self):
        for count in (6, 8, 12):
            args = self.args("movement", "--start", "9", "--count", str(count))
            text = compiler.compile_prompt(args)
            self.assertEqual(text, compiler.compile_prompt(args))
            paths = [line for line in text.splitlines() if line.startswith("manuscript/chapter-")]
            self.assertEqual(paths, [f"manuscript/chapter-{i:02d}.md" for i in range(9, 9 + count)])
            self.assertNotIn("OPTIONAL ACTION LAYER", text)
            self.assertIn("27.7%", text)
            self.assertNotIn("Touren", text)

    def test_opus_is_default_and_fable_is_explicit_comparison(self):
        default = compiler.parser().parse_args(
            ["movement", "--root", str(self.root), "--packet", "brief.md",
             "--owner-style-root", str(self.root / "owner")])
        self.assertEqual("opus", default.author)
        self.assertEqual(8, default.count)
        self.assertIn("Requested manuscript author: opus", compiler.compile_prompt(default))
        args = self.args()
        args.author = "fable"
        self.assertIn("Requested manuscript author: fable", compiler.compile_prompt(args))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.args("movement", "--count", "x")

    def test_power_layer_has_no_other_book_lore(self):
        text = compiler.compile_prompt(self.args("movement", "--action", "trial=learning-power"))
        self.assertIn("OPTIONAL ACTION LAYER — POWER_DISCOVERY", text)
        self.assertIn("OPTIONAL ACTION LAYER — LEARNING", text)
        self.assertNotIn("IRON_PRINCE_EXPANSION", text)
        self.assertNotIn("Toren", text)

    def test_bad_stack_and_escaped_inputs_rejected(self):
        for extra in [("--action", "trial=unknown"), ("--packet", "../outside.md"),
                      ("--chapter-dir", "../outside"), ("--context", "../outside.md")]:
            with self.assertRaises(ValueError):
                compiler.compile_prompt(self.args("movement", *extra))

    def test_existing_manuscript_is_not_a_new_draft(self):
        (self.root / "manuscript").mkdir()
        chapter = self.root / "manuscript/chapter-01.md"
        chapter.write_text("Owner's current edition")
        with self.assertRaisesRegex(ValueError, "already exist"):
            compiler.compile_prompt(self.args())
        self.assertEqual(chapter.read_text(), "Owner's current edition")

    def test_review_contains_all_files_in_order_without_author_brief(self):
        for number in range(1, 9):
            (self.root / f"{number}.md").write_text(f"Unique chapter {number}.")
        args = self.args("review", *[part for n in range(1, 9) for part in ("--chapter", f"{n}.md")])
        text = compiler.compile_prompt(args)
        locations = [text.index(f"Unique chapter {n}.") for n in range(1, 9)]
        self.assertEqual(locations, sorted(locations))
        self.assertNotIn("## AUTHOR PROFILE", text)
        self.assertNotIn("## STRUCTURAL FORMULA", text)
        self.assertNotIn("Requested manuscript author", text)
        self.assertNotIn("27.7%", text)
        args.chapter.append(Path("1.md"))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            compiler.compile_prompt(args)

    def test_owner_protections_are_book_scoped_and_exact(self):
        protections = [{"bookId": "example", "protectedText": "Leave this EXACT."},
                       {"bookId": "other", "protectedText": "Unrelated secret."}]
        with patch.object(compiler, "active_protections", return_value=protections):
            text = compiler.compile_prompt(self.args())
        self.assertIn("Leave this EXACT.", text)
        self.assertNotIn("Unrelated secret.", text)

    def test_plan_does_not_inject_existing_story(self):
        text = compiler.compile_prompt(self.args("plan", "--idea", "A city floats.",
                                                 "--owner-style-root", str(self.root / "owner")))
        self.assertIn("A city floats.", text)
        self.assertNotIn("Glory Realm", text)

    def test_output_refuses_overwrite(self):
        path = self.root / "prompt.md"
        path.write_text("preserve me")
        argv = ["compiler", "movement", "--root", str(self.root), "--author", "opus",
                "--packet", "brief.md", "--output", str(path),
                "--owner-style-root", str(self.root / "owner")]
        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                compiler.main()
        self.assertEqual(path.read_text(), "preserve me")

    def test_source_craft_sections_preserved_verbatim_in_plan_and_movement(self):
        import re
        raw = compiler.FORMULA_SOURCE.read_text()
        sections = re.split(r"(?=^## [1-9]\. )", raw, flags=re.MULTILINE)
        chosen = [s.strip() for s in sections if re.match(r"## [2345689]\. ", s)]
        self.assertEqual(len(chosen), 7)
        for args in (self.args(), self.args("plan", "--idea", "Test premise",
                                         "--owner-style-root", str(self.root / "owner"))):
            prompt = compiler.compile_prompt(args)
            for section in chosen:
                self.assertIn(section, prompt)
            self.assertNotIn("## 1. Why", prompt)
            self.assertNotIn("## 7. What", prompt)

    def test_formula_export_and_editorial_review(self):
        export = compiler.compile_prompt(compiler.parser().parse_args(["formula"]))
        self.assertIn("Source SHA-256:", export)
        for value in ("14.6", "27.7%", "3.3%", "26.8", "72.3", "6.8", "~87%", "~58"):
            self.assertIn(value, export)
        (self.root / "1.md").write_text("Manuscript to review.")
        reviewed = compiler.compile_prompt(self.args("review", "--chapter", "1.md", "--formula-check"))
        self.assertIn(export.strip(), reviewed)
        self.assertIn("UNMEASURED", reviewed)

    def test_closing_gesture_cap_is_in_plan_movement_and_review_census(self):
        clause = "A closing gesture is a device"
        plan = compiler.compile_prompt(self.args("plan", "--idea", "A city floats.",
                                                 "--owner-style-root", str(self.root / "owner")))
        movement = compiler.compile_prompt(self.args("movement"))
        for text in (plan, movement):
            self.assertEqual(1, text.count(clause))
            self.assertIn("is not a closing gesture and is not capped", " ".join(text.split()))
        (self.root / "1.md").write_text("Manuscript to review.")
        review = compiler.compile_prompt(self.args("review", "--chapter", "1.md"))
        self.assertIn('"closing gestures"', review)
        self.assertIn("more than one of the book's biggest beats", " ".join(review.split()))
        formula = compiler.compile_prompt(self.args("review", "--chapter", "1.md", "--formula-check"))
        self.assertIn('"closing gestures"', formula)

    def test_source_structure_change_is_not_silently_ignored(self):
        broken = self.root / "formula.md"
        broken.write_text("## 2. Only one section\n")
        with patch.object(compiler, "FORMULA_SOURCE", broken):
            with self.assertRaisesRegex(ValueError, "source sections"):
                compiler.numerical_formula()


if __name__ == "__main__":
    unittest.main()
