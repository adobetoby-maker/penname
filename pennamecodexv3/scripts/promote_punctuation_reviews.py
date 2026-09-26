#!/usr/bin/env python3
"""Promote validated punctuation candidates into clean canonical manuscript files."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).with_name("punctuation_review.py")
SPEC = importlib.util.spec_from_file_location("punctuation_review", SCRIPT)
assert SPEC and SPEC.loader
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_state(repo: Path, source: Path) -> str:
    relative = source.resolve().relative_to(repo.resolve())
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--", str(relative)],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def collect_reports(roots: list[Path]) -> list[Path]:
    reports: list[Path] = []
    for root in roots:
        reports.extend(root.rglob("*.punctuation-review.json"))
    return sorted(set(reports))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_root", nargs="+", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    for report_path in collect_reports(args.result_root):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        source = Path(report["source"])
        candidate = Path(report["candidate"])
        repo = Path(report["repoRoot"])
        result: dict[str, Any] = {
            "report": str(report_path),
            "source": str(source),
            "acceptedEditCount": int(report["acceptedEditCount"]),
            "action": "skip",
            "reason": "",
        }
        if not result["acceptedEditCount"]:
            result["reason"] = "review made no safe change"
        elif not source.exists() or not candidate.exists():
            result["reason"] = "source or candidate is missing"
        elif sha256(source) != report["sourceSha256"]:
            result["reason"] = "source changed after review"
        elif sha256(candidate) != report["candidateSha256"]:
            result["reason"] = "candidate hash mismatch"
        else:
            source_text = source.read_text(encoding="utf-8")
            candidate_text = candidate.read_text(encoding="utf-8")
            valid, validation = REVIEW.punctuation_only(
                source_text,
                candidate_text,
            )
            if not valid:
                result["reason"] = validation
            else:
                candidate_text = REVIEW.preserve_existing_em_dash_spacing(
                    source_text,
                    candidate_text,
                )
                result["houseStyleSpacingRestored"] = (
                    candidate_text != candidate.read_text(encoding="utf-8")
                )
                state = git_state(repo, source)
                if state:
                    result["reason"] = f"canonical source is not clean: {state}"
                elif args.apply:
                    source.write_text(candidate_text, encoding="utf-8")
                    result["action"] = "applied"
                    result["reason"] = validation
                    result["appliedSha256"] = hashlib.sha256(
                        candidate_text.encode("utf-8")
                    ).hexdigest()
                else:
                    result["action"] = "ready"
                    result["reason"] = validation
        results.append(result)

    summary = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "reports": len(results),
        "ready": sum(item["action"] == "ready" for item in results),
        "applied": sum(item["action"] == "applied" for item in results),
        "skipped": sum(item["action"] == "skip" for item in results),
        "results": results,
    }
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        f"reports={summary['reports']} ready={summary['ready']} "
        f"applied={summary['applied']} skipped={summary['skipped']}"
    )
    for item in results:
        if item["acceptedEditCount"] and item["action"] == "skip":
            print(f"SKIP {item['source']}: {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
