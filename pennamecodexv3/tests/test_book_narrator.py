from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts/book_narrator.py"
SPEC = importlib.util.spec_from_file_location("book_narrator", SCRIPT)
assert SPEC and SPEC.loader
BOOK_NARRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOK_NARRATOR)


class BookNarratorTests(unittest.TestCase):
    def test_chapter_range(self) -> None:
        self.assertEqual(BOOK_NARRATOR.parse_chapters("1-3,5"), [1, 2, 3, 5])

    def test_prepared_copy_is_word_locked(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.md"
            prepared = root / "prepared.md"
            source.write_text("# Chapter 1\n\nIt ran, and it fell.\n", encoding="utf-8")
            prepared.write_text("# Chapter 1\n\nIt ran. And it fell.\n", encoding="utf-8")
            passed, _ = BOOK_NARRATOR.validate_prepared(source, prepared)
            self.assertTrue(passed)

    def test_clarity_review_requires_complete_coverage_and_routes_writing(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.md"
            review = root / "clarity.jsonl"
            source.write_text(
                "# Chapter 1\n\nThe first thought ran on.\n\nIt pointed at him.\n",
                encoding="utf-8",
            )
            items = [
                {
                    "paragraph": 1,
                    "status": "clean",
                    "onePassComprehension": True,
                    "issue": "",
                    "reason": "Meaning lands once.",
                    "preparedText": "The first thought ran on.",
                    "alternatePreparedText": None,
                    "cadenceImpact": "none",
                    "ownerDecision": "not-required",
                    "suggestedWritingRevision": None,
                    "returnToWritingMonroe": False,
                },
                {
                    "paragraph": 2,
                    "status": "writing-change-needed",
                    "onePassComprehension": False,
                    "issue": "The pronoun has two possible referents.",
                    "reason": "Punctuation cannot identify the intended person.",
                    "preparedText": "It pointed at him.",
                    "alternatePreparedText": None,
                    "cadenceImpact": "material",
                    "ownerDecision": "pending",
                    "suggestedWritingRevision": "Name the intended referent.",
                    "returnToWritingMonroe": True,
                },
            ]
            review.write_text(
                "".join(json.dumps(item) + "\n" for item in items), encoding="utf-8"
            )
            passed, note, blockers = BOOK_NARRATOR.validate_clarity(source, review)
            self.assertFalse(passed)
            self.assertEqual(blockers, 1)
            self.assertIn("coverage complete", note)

    def test_material_punctuation_choice_blocks_until_owner_decides(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.md"
            review = root / "clarity.jsonl"
            sentence = "Then the edges came, and they came fast, and they arrived straight."
            source.write_text(f"# Chapter 1\n\n{sentence}\n", encoding="utf-8")
            item = {
                "paragraph": 1,
                "status": "performance-choice",
                "onePassComprehension": True,
                "issue": "A full stop creates a materially different landing.",
                "reason": "Both scores are clear but produce different performances.",
                "preparedText": sentence,
                "alternatePreparedText": "Then the edges came—and they came fast. And they arrived straight.",
                "cadenceImpact": "material",
                "ownerDecision": "pending",
                "suggestedWritingRevision": None,
                "returnToWritingMonroe": False,
            }
            review.write_text(json.dumps(item) + "\n", encoding="utf-8")
            passed, _, blockers = BOOK_NARRATOR.validate_clarity(source, review)
            self.assertFalse(passed)
            self.assertEqual(blockers, 1)

            item["ownerDecision"] = "use-alternate"
            review.write_text(json.dumps(item) + "\n", encoding="utf-8")
            passed, _, blockers = BOOK_NARRATOR.validate_clarity(source, review)
            self.assertTrue(passed)
            self.assertEqual(blockers, 0)

    def test_context_supported_punctuation_correction_may_change_cadence(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.md"
            review = root / "clarity.jsonl"
            sentence = "Then the edges came, and they came fast, and they arrived straight."
            source.write_text(f"# Chapter 1\n\n{sentence}\n", encoding="utf-8")
            item = {
                "paragraph": 1,
                "status": "punctuation-correction",
                "onePassComprehension": True,
                "issue": "Run-on commas flatten two distinct actions.",
                "reason": "The surrounding scene establishes a restart before the final arrival.",
                "preparedText": "Then the edges came—and they came fast. And they arrived straight.",
                "alternatePreparedText": None,
                "cadenceImpact": "material",
                "ownerDecision": "not-required",
                "suggestedWritingRevision": None,
                "returnToWritingMonroe": False,
            }
            review.write_text(json.dumps(item) + "\n", encoding="utf-8")
            passed, _, blockers = BOOK_NARRATOR.validate_clarity(source, review)
            self.assertTrue(passed)
            self.assertEqual(blockers, 0)


if __name__ == "__main__":
    unittest.main()
