#!/usr/bin/env python3
"""Promote critic-approved punctuation candidates into clean canonical sources."""

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


def collect_approvals(roots: list[Path]) -> list[Path]:
    approvals: list[Path] = []
    for root in roots:
        approvals.extend(root.rglob("*.punctuation-approval.json"))
    return sorted(set(approvals))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("approval_root", nargs="+", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    for approval_path in collect_approvals(args.approval_root):
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        source = Path(approval["source"])
        candidate = Path(approval["approvedCandidate"])
        repo = Path(approval["repoRoot"])
        result: dict[str, Any] = {
            "approval": str(approval_path),
            "source": str(source),
            "approvedEditCount": len(approval.get("approved", [])),
            "action": "skip",
            "reason": "",
        }
        if not result["approvedEditCount"]:
            result["reason"] = "critic approved no changes"
        elif not source.exists() or not candidate.exists():
            result["reason"] = "source or approved candidate is missing"
        elif sha256(source) != approval["sourceSha256"]:
            result["reason"] = "source changed after review"
        elif sha256(candidate) != approval["approvedSha256"]:
            result["reason"] = "approved candidate hash mismatch"
        else:
            source_text = source.read_text(encoding="utf-8")
            candidate_text = candidate.read_text(encoding="utf-8")
            valid, validation = REVIEW.punctuation_only(source_text, candidate_text)
            if not valid:
                result["reason"] = validation
            else:
                state = git_state(repo, source)
                if state:
                    result["reason"] = f"canonical source is not clean: {state}"
                elif args.apply:
                    source.write_text(candidate_text, encoding="utf-8")
                    result["action"] = "applied"
                    result["reason"] = validation
                    result["appliedSha256"] = approval["approvedSha256"]
                else:
                    result["action"] = "ready"
                    result["reason"] = validation
        results.append(result)

    summary = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "approvals": len(results),
        "ready": sum(item["action"] == "ready" for item in results),
        "applied": sum(item["action"] == "applied" for item in results),
        "skipped": sum(item["action"] == "skip" for item in results),
        "results": results,
    }
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(
        f"approvals={summary['approvals']} ready={summary['ready']} "
        f"applied={summary['applied']} skipped={summary['skipped']}"
    )
    for item in results:
        if item["approvedEditCount"] and item["action"] == "skip":
            print(f"SKIP {item['source']}: {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
