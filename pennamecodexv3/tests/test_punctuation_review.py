import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "punctuation_review.py"
SPEC = importlib.util.spec_from_file_location("punctuation_review", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PunctuationReviewTests(unittest.TestCase):
    def test_accepts_punctuation_and_capitalization_only(self):
        original = "He stopped, and then he listened."
        edited = "He stopped. And then he listened."
        valid, _ = MODULE.punctuation_only(original, edited)
        self.assertTrue(valid)

    def test_accepts_paragraph_break_without_word_change(self):
        original = "He stopped. Then she spoke."
        edited = "He stopped.\n\nThen she spoke."
        valid, _ = MODULE.punctuation_only(original, edited)
        self.assertTrue(valid)

    def test_rejects_added_word(self):
        valid, reason = MODULE.punctuation_only("He stopped.", "He finally stopped.")
        self.assertFalse(valid)
        self.assertIn("word sequence changed", reason)

    def test_rejects_removed_word(self):
        valid, reason = MODULE.punctuation_only("He finally stopped.", "He stopped.")
        self.assertFalse(valid)
        self.assertIn("word sequence changed", reason)

    def test_rejects_reordered_words(self):
        valid, reason = MODULE.punctuation_only("She saw him.", "She him saw.")
        self.assertFalse(valid)
        self.assertIn("word sequence changed", reason)

    def test_rejects_lost_emphasis_marker(self):
        valid, reason = MODULE.punctuation_only("It was *hers*.", "It was hers.")
        self.assertFalse(valid)
        self.assertIn("Markdown marker", reason)

    def test_rejects_changed_heading_marker(self):
        valid, reason = MODULE.punctuation_only("# Chapter One", "Chapter One")
        self.assertFalse(valid)
        self.assertIn("Markdown marker", reason)

    def test_rejects_changed_scene_break(self):
        valid, reason = MODULE.punctuation_only("Before.\n\n---\n\nAfter.", "Before.\n\n—\n\nAfter.")
        self.assertFalse(valid)
        self.assertIn("scene-break", reason)

    def test_split_join_round_trip_is_exact(self):
        source = "# Title\n\nFirst paragraph.\n\nSecond paragraph.\n"
        paragraphs, separators = MODULE.split_document(source)
        self.assertEqual(source, MODULE.join_document(paragraphs, separators))

    def test_preserves_spacing_around_existing_em_dash(self):
        original = "It was — it wasn't even hard."
        edited = "It was—it wasn't even hard."
        self.assertEqual(
            original,
            MODULE.preserve_existing_em_dash_spacing(original, edited),
        )

    def test_preserves_closed_interruption_dash(self):
        original = '"I told you—" She stopped.'
        edited = '"I told you — " She stopped.'
        self.assertEqual(
            original,
            MODULE.preserve_existing_em_dash_spacing(original, edited),
        )


if __name__ == "__main__":
    unittest.main()
