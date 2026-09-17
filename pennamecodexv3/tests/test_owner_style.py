from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "scripts"))

from build_movement_prompt import build_movement_prompt  # noqa: E402
from owner_style import (  # noqa: E402
    OwnerStyleError,
    active_examples,
    active_protections,
    build_distillation_prompt,
    ingest,
    load_archive,
    normalize_pwa_event,
    select_examples,
    status,
    sync_github,
)
from validate import load_json, validate_instance  # noqa: E402


def event(
    event_id: str,
    *,
    event_type: str = "direct_edit",
    status_value: str = "applied",
    scope: str = "monroe_shared",
    reasons: list[str] | None = None,
    original: str = "He had chosen badly.",
    revised: str = "He had chosen poorly.",
    book_id: str = "kindling-book-01",
    series_id: str = "kindling",
    supersedes: str | None = None,
) -> dict:
    value = {
        "schemaVersion": "1.0",
        "eventId": event_id,
        "eventType": event_type,
        "createdAt": "2026-09-11T19:42:00Z",
        "actorRole": "owner",
        "repository": {
            "owner": "adobetoby-maker",
            "name": "kindling",
            "branch": "owner-edits/kindling-book-01",
        },
        "manuscript": {
            "bookId": book_id,
            "bookTitle": "Kindling",
            "seriesId": series_id,
            "chapterId": "chapter-02",
            "chapterNumber": 2,
            "chapterTitle": "What the Road Brought",
            "sourcePath": "books/book-01-hobbs-wall/manuscript/chapter-02.md",
            "resolvedSourcePath": "books/book-01-hobbs-wall/chapters/chapter-02.md",
            "baseCommit": "0123456789abcdef",
            "baseDocumentHash": "sha256:0123456789abcdef0123456789abcdef",
        },
        "selection": {
            "blockId": "chapter-02:p-37",
            "originalText": original,
            "contextBefore": "Toren replayed the decision.",
            "contextAfter": "There was no undoing it now.",
        },
        "result": {"revisedText": revised} if revised else {},
        "preference": {
            "reasonCodes": reasons or ["word_choice"],
            "ownerComment": "This is the word I would use.",
            "scopeHint": scope,
        },
        "protection": "owner_authored",
        "status": status_value,
    }
    if supersedes:
        value["supersedesEventId"] = supersedes
    return value


class OwnerEditSchemaTests(unittest.TestCase):
    def test_example_validates(self) -> None:
        schema = load_json(PACKAGE_ROOT / "contracts" / "owner-edit-event.schema.json")
        example = load_json(PACKAGE_ROOT / "templates" / "owner-edit-event.example.json")
        self.assertEqual([], validate_instance(example, schema))

    def test_schema_rejects_missing_source_identity(self) -> None:
        schema = load_json(PACKAGE_ROOT / "contracts" / "owner-edit-event.schema.json")
        broken = event("edit-missing-source")
        del broken["manuscript"]["baseDocumentHash"]
        errors = validate_instance(broken, schema)
        self.assertTrue(any("baseDocumentHash" in error for error in errors))

    def test_ingest_rejects_revision_request_without_instruction(self) -> None:
        broken = event(
            "request-without-instruction",
            event_type="revision_request",
            status_value="pending",
            revised="",
        )
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OwnerStyleError, "requires result.instruction"):
                ingest(Path(directory) / "owner-style", [broken])

    def test_deployed_pwa_event_is_adapted_without_losing_prose(self) -> None:
        flat = {
            "schemaVersion": "1",
            "eventId": "pwa-edit-0001",
            "eventType": "direct_edit",
            "createdAt": "2026-09-11T19:42:00Z",
            "actorRole": "owner",
            "supersedesEventId": None,
            "requestEventId": None,
            "repository": {
                "owner": "adobetoby-maker",
                "name": "kindling",
                "branch": "owner-edits/kindling-book-01",
            },
            "bookId": "kindling-book-01",
            "bookTitle": "Kindling",
            "seriesId": "kindling",
            "chapterId": "chapter-02",
            "chapterNumber": 2,
            "chapterTitle": "What the Road Brought",
            "sourcePath": "books/book-01/manuscript/chapter-02.md",
            "resolvedSourcePath": "books/book-01/chapters/chapter-02.md",
            "baseCommit": "0123456789abcdef",
            "baseDocumentHash": "sha256:0123456789abcdef",
            "blockId": "chapter-02:p-37",
            "startOffset": None,
            "endOffset": None,
            "originalText": "He had chosen badly.",
            "contextBefore": "Toren replayed the decision.",
            "contextAfter": "There was no undoing it now.",
            "pageHint": 3,
            "revisedText": "He had chosen poorly.",
            "revisionInstruction": None,
            "reasonCodes": ["word_choice"],
            "ownerComment": "This is the word I would use.",
            "scopeHint": "paragraph",
            "protectionStatus": "unprotected",
            "eventStatus": "synced",
        }
        normalized = normalize_pwa_event(flat)
        self.assertEqual("1.0", normalized["schemaVersion"])
        self.assertEqual("He had chosen poorly.", normalized["result"]["revisedText"])
        self.assertEqual("unclassified", normalized["preference"]["scopeHint"])
        self.assertEqual("owner_authored", normalized["protection"])
        self.assertEqual("applied", normalized["status"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "owner-style"
            self.assertEqual((1, 0), ingest(root, [flat]))
            self.assertEqual(1, status(root)["activeVoiceExamples"])


class OwnerStyleArchiveTests(unittest.TestCase):
    def test_ingest_is_idempotent_and_writes_event_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "owner-style"
            added, skipped = ingest(root, [event("edit-one")])
            self.assertEqual((1, 0), (added, skipped))
            added, skipped = ingest(root, [event("edit-one")])
            self.assertEqual((0, 1), (added, skipped))
            self.assertEqual(1, status(root)["activeVoiceExamples"])
            self.assertTrue(
                (root / "events" / "kindling-book-01" / "chapter-02" / "edit-one.json").is_file()
            )

    def test_duplicate_id_with_changed_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "owner-style"
            ingest(root, [event("edit-one")])
            changed = event("edit-one", revised="He chose with poor judgment.")
            with self.assertRaisesRegex(OwnerStyleError, "different content"):
                ingest(root, [changed])

    def test_revert_removes_positive_pair_from_active_examples(self) -> None:
        original = event("edit-one")
        reverted = event(
            "revert-one",
            event_type="revert",
            original="He had chosen poorly.",
            revised="",
            supersedes="edit-one",
        )
        self.assertEqual([], active_examples([original, reverted]))

    def test_mechanical_and_canon_only_edits_do_not_train_voice(self) -> None:
        typo = event("edit-typo", reasons=["typo_or_punctuation"])
        canon = event("edit-canon", reasons=["continuity", "canon_or_fact"])
        voice = event("edit-voice", reasons=["sentence_load"])
        self.assertEqual(["edit-voice"], [row["eventId"] for row in active_examples([typo, canon, voice])])

    def test_unprotect_releases_locked_passage_without_erasing_history(self) -> None:
        locked = event("protect-one", event_type="protect", revised="")
        locked["protection"] = "locked"
        unlocked = event(
            "unprotect-one",
            event_type="unprotect",
            original=locked["selection"]["originalText"],
            revised="",
            supersedes="protect-one",
        )
        self.assertEqual([], active_protections([locked, unlocked]))

    def test_github_sync_uses_commit_cursor_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = base / "pwa"
            event_path = repo / "edits" / "events" / "book" / "chapter" / "event.json"
            event_path.parent.mkdir(parents=True)
            flat = {
                "schemaVersion": "1",
                "eventId": "pwa-sync-0001",
                "eventType": "direct_edit",
                "createdAt": "2026-09-11T19:42:00Z",
                "actorRole": "owner",
                "supersedesEventId": None,
                "requestEventId": None,
                "repository": {"owner": "owner", "name": "book", "branch": "owner-edits/book"},
                "bookId": "book",
                "bookTitle": "Book",
                "seriesId": "series",
                "chapterId": "chapter",
                "chapterNumber": 1,
                "chapterTitle": "Chapter",
                "sourcePath": "chapter.md",
                "resolvedSourcePath": "chapter.md",
                "baseCommit": "0123456789abcdef",
                "baseDocumentHash": "sha256:0123456789abcdef",
                "blockId": "chapter:p-1",
                "startOffset": None,
                "endOffset": None,
                "originalText": "He chose badly.",
                "contextBefore": "",
                "contextAfter": "",
                "pageHint": 0,
                "revisedText": "He chose poorly.",
                "revisionInstruction": None,
                "reasonCodes": ["word_choice"],
                "ownerComment": None,
                "scopeHint": "paragraph",
                "protectionStatus": "unprotected",
                "eventStatus": "synced",
            }
            event_path.write_text(json.dumps(flat), encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(
                [
                    "git", "-C", str(repo), "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "-qm", "event",
                ],
                check=True,
            )
            root = base / "owner-style"
            first = sync_github(root, repo, "HEAD", fetch=False)
            second = sync_github(root, repo, "HEAD", fetch=False)
            self.assertEqual(1, first["added"])
            self.assertEqual(0, second["added"])
            self.assertEqual(0, second["filesExamined"])
            self.assertEqual(1, status(root)["activeVoiceExamples"])

    def test_selection_respects_scope_and_book(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "owner-style"
            ingest(
                root,
                [
                    event("shared"),
                    event("fantasy", scope="fantasy"),
                    event("scifi", scope="science_fiction"),
                    event("same-book", scope="unclassified"),
                    event("other-book", scope="book", book_id="other-book"),
                ],
            )
            selected = select_examples(
                root, "fantasy", book_id="kindling-book-01", series_id="kindling", limit=10
            )
            self.assertEqual(
                {"shared", "fantasy", "same-book"},
                {row["eventId"] for row in selected},
            )

    def test_explicit_voice_example_can_approve_unchanged_prose(self) -> None:
        favorite = event(
            "favorite-one",
            event_type="voice_example",
            original="The door knew his hand before he touched it.",
            revised="The door knew his hand before he touched it.",
        )
        examples = active_examples([favorite])
        self.assertEqual(1, len(examples))
        self.assertEqual("explicit", examples[0]["signal"])

    def test_explicit_endorsement_replaces_inferred_copy_as_evidence(self) -> None:
        direct = event("direct-one")
        favorite = event("favorite-one", event_type="voice_example")
        favorite["requestEventId"] = "direct-one"
        examples = active_examples([direct, favorite])
        self.assertEqual(["favorite-one"], [row["eventId"] for row in examples])


class OwnerStylePromptTests(unittest.TestCase):
    def test_movement_prompt_includes_approved_voice_and_selected_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            book = base / "book"
            book.mkdir()
            packet = book / "MOVEMENT.md"
            packet.write_text("# Movement\n\nA fight tests Toren's judgment.", encoding="utf-8")
            owner_root = base / "owner-style"
            owner_root.mkdir()
            (owner_root / "OWNER_VOICE.md").write_text(
                "# Monroe Jackson — Owner Voice\n\nPrefer a cleaner sentence.",
                encoding="utf-8",
            )
            ingest(owner_root, [event("edit-one")])
            prompt = build_movement_prompt(
                "fantasy",
                packet,
                book,
                ["chapter 2=learning"],
                owner_style_root=owner_root,
                book_id="kindling-book-01",
                series_id="kindling",
            )
            self.assertIn("OWNER VOICE — APPROVED", prompt)
            self.assertIn("Prefer a cleaner sentence", prompt)
            self.assertIn("OWNER EDIT EXAMPLES — SELECTED", prompt)
            self.assertIn("He had chosen poorly", prompt)
            self.assertLess(prompt.index("OWNER VOICE — APPROVED"), prompt.index("ACTION ASSIGNMENTS"))

    def test_control_prompt_can_exclude_owner_style(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            packet = book / "MOVEMENT.md"
            packet.write_text("# Movement", encoding="utf-8")
            prompt = build_movement_prompt(
                "scifi", packet, book, [], owner_style_root=None
            )
            self.assertNotIn("OWNER VOICE — APPROVED", prompt)
            self.assertNotIn("OWNER EDIT EXAMPLES — SELECTED", prompt)

    def test_packet_ids_select_unclassified_book_examples(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            book = base / "not-the-pwa-id"
            book.mkdir()
            packet = book / "MOVEMENT.md"
            packet.write_text(
                "# Movement\n\n- PWA book ID: kindling-book-01\n- Series ID: kindling\n",
                encoding="utf-8",
            )
            owner_root = base / "owner-style"
            owner_root.mkdir()
            ingest(owner_root, [event("same-book", scope="unclassified")])
            prompt = build_movement_prompt(
                "fantasy", packet, book, [], owner_style_root=owner_root
            )
            self.assertIn("same-book", prompt)

    def test_distillation_is_a_candidate_not_an_automatic_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "owner-style"
            root.mkdir()
            approved = "# Monroe Jackson — Owner Voice\n\nKeep this approved text."
            (root / "OWNER_VOICE.md").write_text(approved, encoding="utf-8")
            ingest(root, [event("edit-one")])
            prompt = build_distillation_prompt(root)
            self.assertIn("reviewable candidate", prompt)
            self.assertIn("MODEL ORIGINAL", prompt)
            self.assertIn("OWNER REVISION", prompt)
            self.assertEqual(approved, (root / "OWNER_VOICE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
