#!/usr/bin/env python3
"""fantasyau1.1 progress tracker and dashboard renderer.

Subcommands:
  init <book_dir> --universe U --series S --title T --number N --chapters 20
      Write a fresh progress.json into <book_dir>, per
      pen-names/fantasyau1.1/seats/progress.schema.json.

  update <book_dir> NN
      Fill chapter NN of <book_dir>/progress.json from whatever seat reports
      are actually filed on disk: author-reports/chNN-report.md,
      editor-verdicts/chNN-verdict.md (+ -recheck.md + -verification.md +
      -fight-audit.md), reader-reports/chNN-reader-A.md/-B.md, and
      LOOP_STATE.md's Chapter status table. A file that does not exist
      contributes nothing -- the corresponding field is left null (or, for a
      whole missing seat, the whole sub-object is left null/omitted). Nothing
      is ever invented to fill a gap.

      Every parser here is defensive: it also has to read the 1.0 harness's
      single-track editor-verdict format (a bare "DEFECTS" section, no
      "PULL" track) as well as the 1.1 two-track format.

  rollup <series_dir>
      Read <series_dir>/series.json ({"universe":..., "series":...,
      "books": [<book_dir>, ...]}), load every listed book's progress.json,
      and write <series_dir>/series-progress.json with per-book means. If
      <series_dir>/../universe.json lists series directories, also write
      <series_dir>/../universe-progress.json one level up.

  render <book_dir|series_dir|universe_dir> --out <html>
      Render one self-contained HTML dashboard (inline CSS/JS/SVG, no
      external requests) with four tabs -- Universe, Series, Book, Chapter --
      for whichever level of directory is given. Recomputes every aggregate
      on the fly from the raw progress.json files so it never depends on a
      stale rollup. Missing data renders as an em dash; nothing is fabricated.

Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape as _h
from pathlib import Path
from typing import Any

PEN_NAME = "fantasyau1.1"

CHAPTER_STATUSES = [
    "PENDING", "DRAFTING", "EDITING", "READING", "VERIFYING",
    "REPAIRING", "RECHECKING", "SCENE_CLOSED", "BLOCKED",
]
VERDICT_ENUM = ["PASS", "PASS_WITH_FINDINGS", "STRUCTURAL_HOLD"]
SEVERITIES = ["BLOCKER", "HIGH", "MEDIUM", "LOW"]
PULL_SEVERITIES = ["STRUCTURAL", "MEDIUM", "LOW"]

WORD_NUMBERS = {
    "no": 0, "none": 0, "zero": 0,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_SEATS_WORD_TO_NUM = {"two": 2, "three": 3, "four": 4, "five": 5}
_SEATS_ORDINAL_TO_NUM = {"second": 2, "third": 3, "fourth": 4, "fifth": 5}


def _parse_seats_used(*texts: str | None) -> int | None:
    """How many seat invocations (author draft plus any repair-seat
    continuation after a session limit) produced this chapter's filed
    text. Parsed from whichever of the given texts (the author report,
    the LOOP_STATE chapter-status row) name a seat count explicitly:
    "two seats", "second seat", "2nd seat", "seat 2", "Two fable seats"
    -> 2; "three seats" -> 3; etc. Never defaults -- a chapter that says
    nothing about seat count returns None, so the field stays unset
    (renders as the dashboard's em dash) rather than inventing the
    single-seat baseline.

    "seat" (singular) plus a bare cardinal word ("one seat") is
    deliberately NOT matched: this fixture's own canon uses "a seat" /
    "one seat" as an in-story bureaucratic-office term (Ch9/15/19: "the
    seated list... one seat", "a seat is one seat"), and that reads
    nothing like a model-invocation count. The plural "seats" is required
    for the cardinal-word form, which real seat-count language always
    uses ("Two fable seats", "two-seat draft" -> counted via the digit-
    labeled "Seat 1"/"Seat 2" form below instead); numbered or ordinal
    seat labels ("seat 2", "2nd seat", "second seat") stay unambiguous on
    their own regardless of plurality."""
    combined = "\n".join(t for t in texts if t)
    if not combined:
        return None

    candidates: list[int] = []
    for m in re.finditer(r"\b(two|three|four|five)\s+(?:fable\s+)?seats\b", combined, re.IGNORECASE):
        candidates.append(_SEATS_WORD_TO_NUM[m.group(1).lower()])
    for m in re.finditer(r"\b(second|third|fourth|fifth)\s+seat\b", combined, re.IGNORECASE):
        candidates.append(_SEATS_ORDINAL_TO_NUM[m.group(1).lower()])
    for m in re.finditer(r"\b(\d+)(?:st|nd|rd|th)\s+seat\b", combined, re.IGNORECASE):
        candidates.append(int(m.group(1)))
    for m in re.finditer(r"\bseat\s*#?(\d+)\b", combined, re.IGNORECASE):
        candidates.append(int(m.group(1)))

    return max(candidates) if candidates else None


# --------------------------------------------------------------------------
# small IO helpers
# --------------------------------------------------------------------------

def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_number(s: str) -> float:
    return float(s.replace(",", ""))


def fail(msg: str) -> "NoReturn":
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    book_dir = Path(args.book_dir)
    out_path = book_dir / "progress.json"
    if out_path.exists() and not args.force:
        fail(f"{out_path} already exists (pass --force to overwrite)")

    chapters = [
        {"n": n, "title": "", "status": "PENDING"}
        for n in range(1, args.chapters + 1)
    ]
    data = {
        "pen_name": PEN_NAME,
        "universe": args.universe,
        "series": args.series,
        "book": {
            "slug": book_dir.name,
            "title": args.title,
            "number": args.number,
            "target_chapters": args.chapters,
            "status": "DRAFTING",
        },
        "chapters": chapters,
    }
    write_json(out_path, data)
    print(f"PROGRESS_INIT={out_path}")
    print(f"book={args.title!r} chapters={args.chapters}")
    return 0


# --------------------------------------------------------------------------
# update — per-source parsers
# --------------------------------------------------------------------------

def _prune_none(d: dict) -> dict:
    """Drop keys whose value is None, so we never write a null into a field
    the schema declares non-nullable. Callers that want an explicit null
    (reader_a/reader_b/fight, which the schema allows to be null) set that
    key directly on the parent dict instead of routing it through here."""
    return {k: v for k, v in d.items() if v is not None}


def parse_author_report(text: str) -> dict:
    out: dict[str, Any] = {}

    words = target = None

    m = re.search(r"([\d,]+)\s*words?\b[^.\n]{0,80}?against a target of\s*([\d,]+)", text, re.IGNORECASE)
    if m:
        words, target = parse_number(m.group(1)), parse_number(m.group(2))
    if words is None:
        # Bounded lookahead (not "no periods") because these sentences
        # legitimately contain one, e.g. "... by wc -w. Delta vs 4,750: ...".
        m = re.search(r"([\d,]+)\s*\(filed\)[\s\S]{0,120}?Delta vs\.?\s*\$?([\d,]+)", text, re.IGNORECASE)
        if m:
            words, target = parse_number(m.group(1)), parse_number(m.group(2))
    if words is None:
        m = re.search(r"Word count:\s*([\d,]+)\s*by\s*`?wc -w`?[\s\S]{0,120}?Delta vs\.?\s*\$?([\d,]+)", text, re.IGNORECASE)
        if m:
            words, target = parse_number(m.group(1)), parse_number(m.group(2))
    if words is None:
        m = re.search(r"After:\s*([\d,]+)", text)
        if m:
            words = parse_number(m.group(1))
            band = re.search(r"band\s+of\s*([\d,]+)\s*[–\-]\s*([\d,]+)", text)
            if band:
                target = round((parse_number(band.group(1)) + parse_number(band.group(2))) / 2)
    if words is None:
        m = re.search(r"([\d,]+)\s*words\b", text, re.IGNORECASE)
        if m:
            words = parse_number(m.group(1))

    if words is not None:
        out["words"] = int(words)
    if target is not None:
        out["target"] = int(target)
    if words is not None and target:
        delta_pct = round((words - target) / target * 100, 1)
        out["delta_pct"] = delta_pct
        out["in_band"] = abs(delta_pct) <= 5.0

    # seats_used: parsed from the report text alone here; cmd_update also
    # checks the LOOP_STATE chapter-status row (via _parse_seats_used) and
    # fills this in from there if the report itself is silent. Never
    # defaulted to 1 -- an unparseable chapter leaves the field unset.
    seats = _parse_seats_used(text)
    if seats is not None:
        out["seats_used"] = seats

    # humor beats claimed — 1.1 concept ("Humor beats: N"); absent from 1.0
    # reports, so this stays unset for those.
    m = re.search(r"Humor beats?:?\s*(\d+)", text, re.IGNORECASE)
    if m:
        out["humor_beats_claimed"] = int(m.group(1))

    m = re.search(r"\bCOLD\s+CHAPTER\b", text, re.IGNORECASE)
    if m:
        out["cold"] = True

    m = re.search(r"Action item:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["action_item"] = m.group(1).strip()

    m = re.search(r"Hook line:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["hook_line"] = m.group(1).strip()
    m = re.search(r"Want line:\s*(.+)", text, re.IGNORECASE)
    if m:
        out["want_line"] = m.group(1).strip()

    # names minted — "## N. Names minted" section's first non-blank line,
    # which always opens with a bold count ("**None.**", "**One: JESSOP**",
    # "**Two:** ...", or a bare "**3**").
    m = re.search(r"^##\s*\d+\.\s*Names minted.*$", text, re.MULTILINE)
    if m:
        rest = text[m.end():]
        for line in rest.splitlines():
            if line.strip():
                bm = re.match(r"\*\*([A-Za-z0-9]+)", line.strip())
                if bm:
                    token = bm.group(1).lower()
                    if token in WORD_NUMBERS:
                        out["names_minted"] = WORD_NUMBERS[token]
                    elif token.isdigit():
                        out["names_minted"] = int(token)
                break

    return _prune_none(out)


def _extract_section(text: str, start_pat: str, end_pats: list[str]) -> str | None:
    """Return the text between a line matching start_pat and the next line
    matching any of end_pats (or end of file). None if start_pat is absent."""
    start_re = re.compile(start_pat, re.MULTILINE)
    m = start_re.search(text)
    if not m:
        return None
    rest = text[m.end():]
    end_re = re.compile("|".join(f"(?:{p})" for p in end_pats), re.MULTILINE)
    em = end_re.search(rest)
    return rest[: em.start()] if em else rest


def _count_numbered_severities(block: str, severities: list[str]) -> dict[str, int]:
    """Count each numbered finding's severity. The severity word is usually
    bare ("1. MEDIUM — ...") but some filed verdicts bold it inside the
    numbered item ("1. **BLOCKER — ...**"), so an optional leading '**' (or
    other light markdown) is tolerated before the word."""
    counts = {s: 0 for s in severities}
    for line in block.splitlines():
        m = re.match(r"^\s*\d+\.\s*[*_]{0,2}\s*([A-Z]+)\b", line)
        if m and m.group(1) in counts:
            counts[m.group(1)] += 1
    return counts


def parse_editor_verdict_file(text: str) -> dict:
    """Parse one editor-verdicts/chNN-verdict*.md file (either 1.0
    single-track or 1.1 two-track) into {"verdict", "defects", ["pull"]}."""
    out: dict[str, Any] = {}
    m = re.search(r"^VERDICT:\s*(\S+)", text, re.MULTILINE)
    if m:
        token = m.group(1).strip().rstrip(".:,")
        if token in VERDICT_ENUM:
            out["verdict"] = token

    defects_block = _extract_section(text, r"^DEFECTS\b.*$", [r"^PULL:\s*$", r"^CONCERNS\b.*$"])
    if defects_block is not None:
        out["defects"] = _count_numbered_severities(defects_block, SEVERITIES)

    if re.search(r"^PULL:\s*$", text, re.MULTILINE):
        pull_block = _extract_section(text, r"^PULL:\s*$", [r"^CONCERNS\b.*$"])
        pull: dict[str, Any] = {}
        findings_block = _extract_section(pull_block or "", r"^Findings:\s*$", [r"\Z"]) if pull_block else None
        if findings_block is not None:
            pull.update(_count_numbered_severities(findings_block, PULL_SEVERITIES))
        if pull_block:
            hm = re.search(r"Humor beats?:\s*(\d+)", pull_block, re.IGNORECASE)
            if hm:
                pull["humor_beats_counted"] = int(hm.group(1))
            # "Hook: none" / "no" / "not present" / "absent" / "no want" all
            # say the same thing (no hook landed) in slightly different
            # filed phrasings -- all must read as hook_pass=False, not just
            # the bare "none"/"no" the old regex caught (which let "not
            # present" and "absent" fall through as a false True).
            hook_absent = r"(?:none|no|not\s+present|absent|no\s+want)\b"
            if re.search(r"^Hook:\s*" + hook_absent, pull_block, re.IGNORECASE | re.MULTILINE):
                pull["hook_pass"] = False
            elif re.search(r"^Hook:\s*(?!" + hook_absent + r")\S", pull_block, re.IGNORECASE | re.MULTILINE):
                pull["hook_pass"] = True
            if re.search(r"^Action:\s*(?:yes|delivered)\b", pull_block, re.IGNORECASE | re.MULTILINE):
                pull["action_pass"] = True
            elif re.search(r"^Action:\s*(?:no|not delivered)\b", pull_block, re.IGNORECASE | re.MULTILINE):
                pull["action_pass"] = False
        if pull:
            out["pull"] = pull

    return out


def parse_verification(text: str) -> dict:
    """Defensive parse of the VERIFICATION summary line. Real filed files
    vary in phrasing (see progress.py module docstring); an UPGRADED count
    is folded into 'confirmed' (schema has no separate bucket for it), a
    DOWNGRADED count — bare or 'CONFIRMED-DOWNGRADED' — goes to 'downgraded'."""
    out: dict[str, int] = {}
    m = re.search(r"^VERIFICATION:(.*)$", text, re.MULTILINE)
    if not m:
        return out
    line = m.group(1)

    confirmed = sum(int(n) for n in re.findall(r"(\d+)\s+CONFIRMED\b(?!-)", line))
    confirmed += sum(int(n) for n in re.findall(r"(\d+)\s+CONFIRMED-UPGRADED\b", line))
    confirmed += sum(int(n) for n in re.findall(r"(\d+)\s+UPGRADED\b", line))
    downgraded = sum(int(n) for n in re.findall(r"(\d+)\s+(?:CONFIRMED-)?DOWNGRADED\b", line))
    rejected = sum(int(n) for n in re.findall(r"(\d+)\s+REJECTED\b", line))
    new = sum(int(n) for n in re.findall(r"(\d+)\s+MISSED-BLOCKERS?\b", line))

    out["confirmed"] = confirmed
    out["downgraded"] = downgraded
    out["rejected"] = rejected
    out["new"] = new
    return out


def parse_adjudication_words(text: str) -> dict:
    """Fallback for a chNN-verification.md that carries no 'VERIFICATION:'
    summary line at all -- an orchestrator adjudication made without
    dispatching a verifier seat (Book 2's ch19/ch20: "no verifier seat
    dispatched", ruled by precedent instead), recorded as bare
    CONFIRMED/DOWNGRADED/REJECTED verdict words in prose (ch19's
    "**Adjudication:** CONFIRMED by precedent...") or in an adjudication
    table (ch20's "| # | Editor | Adjudication | Evidence |", a row
    sometimes carrying more than one verdict word, e.g. "PARTLY CONFIRMED
    / PARTLY REJECTED"). Counts every ALL-CAPS, case-sensitive occurrence
    of the three words -- deliberately not case-insensitive, so it does
    not pick up ordinary lowercase prose use of "confirmed". Returns {}
    (stays absent) if none of the three words appear at all."""
    confirmed = len(re.findall(r"\bCONFIRMED\b", text))
    downgraded = len(re.findall(r"\bDOWNGRADED\b", text))
    rejected = len(re.findall(r"\bREJECTED\b", text))
    if not (confirmed or downgraded or rejected):
        return {}
    return {"confirmed": confirmed, "downgraded": downgraded, "rejected": rejected, "new": 0}


def parse_loop_state_row(text: str, nn: int) -> dict:
    """Parse the '## Chapter status' table row for chapter nn:
    | Ch | Title | Words | Phase | Verdict | Repair cycle |
    "verdict_cell" (the row's own Verdict column, raw) is returned for the
    caller to scan for a seat-count mention (e.g. "Two fable seats", "2nd
    seat") -- it is a parsing input, not a field written to progress.json."""
    out: dict[str, Any] = {}
    pat = re.compile(
        r"^\|\s*0*" + str(nn) + r"\s*\|\s*([^|]+?)\s*\|\s*[\d,]*\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*(\d+)\s*\|\s*$",
        re.MULTILINE,
    )
    m = pat.search(text)
    if not m:
        return out
    title, phase_cell, verdict_cell, repair_cycles = m.group(1), m.group(2), m.group(3), m.group(4)
    title = re.sub(r"\*+", "", title).strip()
    if title:
        out["title"] = title
    sm = re.match(r"([A-Z_]+)", phase_cell.strip())
    if sm and sm.group(1) in CHAPTER_STATUSES:
        out["status"] = sm.group(1)
    out["repair_cycles"] = int(repair_cycles)
    if verdict_cell:
        out["verdict_cell"] = verdict_cell
    return out


def _nonempty_or_none(items: list) -> str | None:
    return None if not items else "\n".join(items)


def parse_reader_report(text: str) -> dict:
    out: dict[str, Any] = {}
    m = re.search(r"^PULL:\s*\[?([1-5])\]?", text, re.MULTILINE)
    if m:
        out["pull"] = int(m.group(1))
    m = re.search(r"^WOULD I READ THE NEXT CHAPTER:\s*\[?(yes|probably|no)\]?", text, re.MULTILINE | re.IGNORECASE)
    if m:
        out["would_continue"] = m.group(1).lower()

    def count_section(header: str, none_words: tuple[str, ...]) -> int | None:
        block = _extract_section(
            text,
            rf"^{header}:.*$",
            [r"^WHAT I DID NOT UNDERSTAND:", r"^WHERE I SKIMMED:", r"^WHERE I LAUGHED OR SMILED:",
             r"^WHO TALKS THE SAME:", r"^WHAT I WANT TO HAPPEN NEXT:", r"^THE ONE THING I WOULD CHANGE:",
             r"^BEST MOMENT:", r"\Z"],
        )
        if block is None:
            return None
        stripped = block.strip()
        if not stripped:
            return None
        if any(re.fullmatch(w + r"\.?", stripped, re.IGNORECASE) for w in none_words):
            return 0
        items = re.findall(r"^\s*\d+\.", block, re.MULTILINE)
        return len(items) if items else None

    v = count_section("WHAT I DID NOT UNDERSTAND", ("nothing",))
    if v is not None:
        out["confusions"] = v
    v = count_section("WHERE I SKIMMED", ("nowhere", "none"))
    if v is not None:
        out["skims"] = v
    v = count_section("WHERE I LAUGHED OR SMILED", ("nowhere", "none"))
    if v is not None:
        out["laughs"] = v

    same_block = _extract_section(
        text, r"^WHO TALKS THE SAME:.*$",
        [r"^WHAT I WANT TO HAPPEN NEXT:", r"^THE ONE THING I WOULD CHANGE:", r"^BEST MOMENT:", r"\Z"],
    )
    if same_block is not None:
        stripped = same_block.strip()
        if re.fullmatch(r"(none|nobody)\.?", stripped, re.IGNORECASE):
            out["same_voice_pairs"] = 0

    m = re.search(r"^THE ONE THING I WOULD CHANGE:\s*(.+)", text, re.MULTILINE)
    if m:
        out["one_change"] = m.group(1).strip()
    m = re.search(r"^BEST MOMENT:\s*(.+)", text, re.MULTILINE)
    if m:
        out["best_moment"] = m.group(1).strip()

    return _prune_none(out)


def parse_fight_audit(text: str) -> dict:
    out: dict[str, Any] = {}
    rows = re.findall(r"^\|\s*\d+\s+[^|]+\|\s*(Pass|Fail)\s*\|", text, re.MULTILINE | re.IGNORECASE)
    if rows:
        out["gates_passed"] = sum(1 for r in rows if r.strip().lower() == "pass")
        out["of"] = 8

    inj_block = _extract_section(text, r"^.*NEW INJURIES.*$", [r"^[A-Z].*PARAGRAPH", r"^FINDINGS", r"\Z"])
    if inj_block is not None:
        stripped = inj_block.strip()
        if re.fullmatch(r"(none)\.?", stripped, re.IGNORECASE):
            out["new_injuries"] = 0
        else:
            items = re.findall(r"^\s*[-\d].*\S", inj_block, re.MULTILINE)
            if items:
                out["new_injuries"] = len(items)

    env_row = re.search(r"^\|\s*16\s+Environmental[^|]*\|[^|]*\|(.*)\|\s*$", text, re.MULTILINE)
    if env_row:
        out["terrain_beats"] = len(re.findall(r'"[^"]+"', env_row.group(1)))

    fairness = re.search(r"^.*FAIRNESS.*$", text, re.MULTILINE)
    if fairness:
        tail = text[fairness.end(): fairness.end() + 400]
        if re.search(r"\bFAIL\b", tail):
            out["fairness_pass"] = False
        elif re.search(r"\bPASS\b", tail):
            out["fairness_pass"] = True

    return _prune_none(out)


# --------------------------------------------------------------------------
# update — orchestration
# --------------------------------------------------------------------------

def cmd_update(args: argparse.Namespace) -> int:
    book_dir = Path(args.book_dir)
    nn = args.nn
    progress_path = book_dir / "progress.json"
    if not progress_path.is_file():
        fail(f"{progress_path} does not exist — run `init` first")
    data = load_json(progress_path)

    chapters = data.setdefault("chapters", [])
    chapter = next((c for c in chapters if c.get("n") == nn), None)
    if chapter is None:
        target = data.get("book", {}).get("target_chapters")
        fail(
            f"chapter {nn} is not in progress.json's chapter list "
            f"(target_chapters={target}) — re-run init with a larger --chapters, or check NN"
        )

    nn_str = f"{nn:02d}"
    found: list[str] = []
    missing: list[str] = []

    def note(label: str, ok: bool) -> None:
        (found if ok else missing).append(label)

    # --- author report
    report_path = book_dir / "author-reports" / f"ch{nn_str}-report.md"
    report_text = read_text(report_path)
    note("author-report", report_text is not None)
    if report_text is not None:
        author = chapter.get("author", {})
        # seats_used is re-derived fresh on every update (report, then the
        # LOOP_STATE fallback below) -- drop whatever a prior run wrote so
        # a stale fabricated value (e.g. the old default of 1) can never
        # survive an update that no longer supports it.
        author.pop("seats_used", None)
        author.update(parse_author_report(report_text))
        chapter["author"] = author

    # --- editor verdict + recheck
    verdict_path = book_dir / "editor-verdicts" / f"ch{nn_str}-verdict.md"
    recheck_path = book_dir / "editor-verdicts" / f"ch{nn_str}-verdict-recheck.md"
    verdict_text = read_text(verdict_path)
    recheck_text = read_text(recheck_path)
    note("editor-verdict", verdict_text is not None)
    note("editor-recheck", recheck_text is not None)
    if verdict_text is not None or recheck_text is not None:
        editor = chapter.get("editor", {})
        if verdict_text is not None:
            editor.update(parse_editor_verdict_file(verdict_text))
        if recheck_text is not None:
            recheck_parsed = parse_editor_verdict_file(recheck_text)
            editor["recheck"] = recheck_parsed.get("verdict")
        else:
            editor.setdefault("recheck", None)
        chapter["editor"] = editor

    # --- verifier
    verification_path = book_dir / "editor-verdicts" / f"ch{nn_str}-verification.md"
    verification_text = read_text(verification_path)
    note("verification", verification_text is not None)
    if verification_text is not None:
        verifier = parse_verification(verification_text)
        if not verifier:
            # No "VERIFICATION:" line -- try the orchestrator-adjudication
            # fallback (a file with no verifier seat dispatched, ruled by
            # precedent instead; ch19/ch20 in the fixture).
            verifier = parse_adjudication_words(verification_text)
        if verifier:
            chapter["verifier"] = verifier

    # --- readers
    for persona, key in (("A", "reader_a"), ("B", "reader_b")):
        rpath = book_dir / "reader-reports" / f"ch{nn_str}-reader-{persona}.md"
        rtext = read_text(rpath)
        note(f"reader-{persona}", rtext is not None)
        chapter[key] = parse_reader_report(rtext) if rtext is not None else None

    # --- fight audit
    fight_path = book_dir / "editor-verdicts" / f"ch{nn_str}-fight-audit.md"
    fight_text = read_text(fight_path)
    note("fight-audit", fight_text is not None)
    chapter["fight"] = parse_fight_audit(fight_text) if fight_text is not None else None

    # --- LOOP_STATE (status, title, repair cycles)
    loop_state_text = read_text(book_dir / "LOOP_STATE.md")
    note("LOOP_STATE.md", loop_state_text is not None)
    if loop_state_text is not None:
        row = parse_loop_state_row(loop_state_text, nn)
        if "title" in row:
            chapter["title"] = row["title"]
        if "status" in row:
            chapter["status"] = row["status"]
        if "repair_cycles" in row:
            repair = chapter.get("repair", {})
            repair["cycles"] = row["repair_cycles"]
            chapter["repair"] = repair
        # seats_used cross-source fallback: the author report may be silent
        # on seat count even when the LOOP_STATE row names it (e.g. "10
        # repairs (fable, 2nd seat after a session limit)"). Only fills in
        # when the author report did not already resolve it -- never
        # overrides a report-derived value.
        author = chapter.get("author") or {}
        if author.get("seats_used") is None and row.get("verdict_cell"):
            seats = _parse_seats_used(row["verdict_cell"])
            if seats is not None:
                author["seats_used"] = seats
                chapter["author"] = author

    write_json(progress_path, data)
    print(f"PROGRESS_UPDATED={progress_path} chapter={nn_str}")
    print(f"sources_found={','.join(found) or 'none'}")
    print(f"sources_missing={','.join(missing) or 'none'}")
    return 0


# --------------------------------------------------------------------------
# rollup
# --------------------------------------------------------------------------

def _mean(values: list[float]) -> float | None:
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def aggregate_book(book: dict) -> dict:
    """Compute the on-the-fly per-book rollup means used by both `rollup`
    and `render`."""
    chapters = book.get("chapters", [])
    reader_a_pulls = [c.get("reader_a", {}).get("pull") if c.get("reader_a") else None for c in chapters]
    reader_b_pulls = [c.get("reader_b", {}).get("pull") if c.get("reader_b") else None for c in chapters]
    defects_per_ch = []
    pull_findings_per_ch = []
    verdict_dist = {v: 0 for v in VERDICT_ENUM}
    humor_beats = []
    fight_ratios = []
    repair_cycles = []
    words = []

    for c in chapters:
        editor = c.get("editor") or {}
        if editor.get("verdict") in verdict_dist:
            verdict_dist[editor["verdict"]] += 1
        defects = editor.get("defects")
        if defects:
            defects_per_ch.append(sum(defects.get(s, 0) for s in SEVERITIES))
        pull = editor.get("pull")
        if pull:
            pull_findings_per_ch.append(sum(pull.get(s, 0) for s in PULL_SEVERITIES))
        author = c.get("author") or {}
        # 1.1.1 moves humor counting out of the drafter's self-report. Prefer
        # the editor's measured count; retain the author field as a legacy
        # fallback for 1.0/early-1.1 reports.
        if pull and pull.get("humor_beats_counted") is not None:
            humor_beats.append(pull["humor_beats_counted"])
        elif author.get("humor_beats_claimed") is not None:
            humor_beats.append(author["humor_beats_claimed"])
        if author.get("words") is not None:
            words.append(author["words"])
        fight = c.get("fight")
        if fight and fight.get("gates_passed") is not None and fight.get("of"):
            fight_ratios.append(fight["gates_passed"] / fight["of"])
        repair = c.get("repair")
        if repair and repair.get("cycles") is not None:
            repair_cycles.append(repair["cycles"])

    chapters_closed = sum(1 for c in chapters if c.get("status") == "SCENE_CLOSED")

    return {
        "slug": book.get("book", {}).get("slug"),
        "title": book.get("book", {}).get("title"),
        "number": book.get("book", {}).get("number"),
        "status": book.get("book", {}).get("status"),
        "chapters_closed": chapters_closed,
        "chapters_total": len(chapters),
        "reader_pull_a_mean": _mean(reader_a_pulls),
        "reader_pull_b_mean": _mean(reader_b_pulls),
        "editor_first_pass_verdict_distribution": verdict_dist,
        "defects_per_chapter_mean": _mean(defects_per_ch),
        "pull_findings_per_chapter_mean": _mean(pull_findings_per_ch),
        "humor_beats_per_chapter_mean": _mean(humor_beats),
        "fight_gates_mean": _mean(fight_ratios),
        "repair_cycles_mean": _mean(repair_cycles),
        "words_total": sum(words) if words else None,
        "words_mean_per_chapter": _mean(words),
        "reader_pull_a_series": reader_a_pulls,
        "reader_pull_b_series": reader_b_pulls,
        "defects_series": defects_per_ch,
    }


def _load_books(book_dirs: list[str]) -> list[dict]:
    books = []
    for b in book_dirs:
        p = Path(b) / "progress.json"
        if not p.is_file():
            print(f"WARN: no progress.json in {b} — skipping", file=sys.stderr)
            continue
        book = load_json(p)
        book["_dir"] = str(Path(b))
        books.append(book)
    return books


def aggregate_series(series_json: dict) -> dict:
    books = _load_books(series_json.get("books", []))
    book_rollups = [aggregate_book(b) for b in books]
    return {
        "universe": series_json.get("universe"),
        "series": series_json.get("series"),
        "books": book_rollups,
    }


def cmd_rollup(args: argparse.Namespace) -> int:
    series_dir = Path(args.series_dir)
    series_json_path = series_dir / "series.json"
    if not series_json_path.is_file():
        fail(f"{series_json_path} does not exist")
    series_json = load_json(series_json_path)
    for key in ("universe", "series", "books"):
        if key not in series_json:
            fail(f"{series_json_path} is missing required key {key!r}")

    series_rollup = aggregate_series(series_json)
    out_path = series_dir / "series-progress.json"
    write_json(out_path, series_rollup)
    print(f"SERIES_ROLLUP={out_path}")
    print(f"books={len(series_rollup['books'])}")

    universe_json_path = series_dir.parent / "universe.json"
    if universe_json_path.is_file():
        universe_json = load_json(universe_json_path)
        series_list = []
        for s in universe_json.get("series", []):
            s_dir = Path(s)
            s_json_path = s_dir / "series.json"
            if not s_json_path.is_file():
                print(f"WARN: no series.json in {s} — skipping", file=sys.stderr)
                continue
            series_list.append(aggregate_series(load_json(s_json_path)))
        universe_rollup = {
            "universe": universe_json.get("universe"),
            "series": series_list,
        }
        universe_out = series_dir.parent / "universe-progress.json"
        write_json(universe_out, universe_rollup)
        print(f"UNIVERSE_ROLLUP={universe_out}")
    return 0


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------

def svg_sparkline(values: list[float | None], width: int = 140, height: int = 28,
                   kind: str = "line", y_max: float | None = None) -> str:
    """A minimal inline SVG sparkline. None values are gaps: for 'line' the
    segment through a gap is simply not drawn; for 'bar' a gap renders as a
    zero-height bar. Purely decorative trend indicator, not a precise chart."""
    clean = [v for v in values if v is not None]
    if not clean:
        return '<svg class="spark" width="{}" height="{}" role="img" aria-label="no data"></svg>'.format(width, height)
    vmax = y_max if y_max is not None else max(clean)
    vmax = vmax if vmax > 0 else 1
    n = len(values)
    step = width / max(n - 1, 1)

    if kind == "bar":
        bw = max(width / n - 2, 1)
        bars = []
        for i, v in enumerate(values):
            h = 0 if v is None else max((v / vmax) * (height - 2), 1 if v > 0 else 0)
            x = i * (width / n) + 1
            y = height - h
            bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" class="spark-bar"/>')
        return f'<svg class="spark" width="{width}" height="{height}" role="img" aria-label="sparkline">{"".join(bars)}</svg>'

    points = []
    segments = []
    current: list[str] = []
    for i, v in enumerate(values):
        x = i * step
        if v is None:
            if len(current) > 1:
                segments.append(current)
            current = []
            continue
        y = height - (v / vmax) * (height - 4) - 2
        current.append(f"{x:.1f},{y:.1f}")
        points.append((x, y))
    if len(current) > 1:
        segments.append(current)
    polylines = "".join(f'<polyline points="{" ".join(seg)}" class="spark-line"/>' for seg in segments)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" class="spark-dot"/>' for x, y in points)
    return f'<svg class="spark" width="{width}" height="{height}" role="img" aria-label="sparkline">{polylines}{dots}</svg>'


def _cell(v: Any) -> str:
    if v is None or v == "":
        return "—"
    return _h(str(v))


def render_chapter_detail(c: dict) -> str:
    author = c.get("author") or {}
    editor = c.get("editor") or {}
    verifier = c.get("verifier") or {}
    fight = c.get("fight")
    repair = c.get("repair") or {}
    reader_a = c.get("reader_a")
    reader_b = c.get("reader_b")

    def kv_table(d: dict | None, empty_note: str) -> str:
        if not d:
            return f"<p class='muted'>{_h(empty_note)}</p>"
        rows = "".join(f"<tr><th>{_h(k)}</th><td>{_cell(v)}</td></tr>" for k, v in d.items())
        return f"<table class='kv'>{rows}</table>"

    return f"""
    <details class="chapter-detail">
      <summary>Ch {c.get('n')}: {_h(c.get('title') or '(untitled)')} — <span class="status status-{_h(c.get('status','PENDING'))}">{_h(c.get('status','PENDING'))}</span></summary>
      <div class="detail-grid">
        <section><h4>Author</h4>{kv_table(author, 'No author-reports/chNN-report.md filed.')}</section>
        <section><h4>Editor</h4>{kv_table(editor, 'No editor-verdicts/chNN-verdict.md filed.')}</section>
        <section><h4>Verifier</h4>{kv_table(verifier, 'No editor-verdicts/chNN-verification.md filed.')}</section>
        <section><h4>Reader A</h4>{kv_table(reader_a, 'No reader-reports/chNN-reader-A.md filed.')}</section>
        <section><h4>Reader B</h4>{kv_table(reader_b, 'No reader-reports/chNN-reader-B.md filed.')}</section>
        <section><h4>Fight audit</h4>{kv_table(fight, 'Not a set-piece chapter, or no fight-audit filed.')}</section>
        <section><h4>Repair</h4>{kv_table(repair, 'No repair cycle recorded.')}</section>
      </div>
    </details>"""


def render_chapter_details(book: dict) -> str:
    chapters = book.get("chapters", [])
    return "".join(render_chapter_detail(c) for c in chapters) or "<p class='muted'>No chapters.</p>"


def render_book_summary(book: dict) -> str:
    """The Book tab's content: sparklines + the per-chapter summary table.
    Chapter-level drill-down (the <details> blocks) lives in the Chapter
    tab instead (render_chapter_details), so the two tabs are not
    duplicates of each other."""
    chapters = book.get("chapters", [])
    rows = []
    for c in chapters:
        author = c.get("author") or {}
        editor = c.get("editor") or {}
        defects = editor.get("defects") or {}
        pull = editor.get("pull") or {}
        reader_a = c.get("reader_a") or {}
        reader_b = c.get("reader_b") or {}
        fight = c.get("fight") or {}
        repair = c.get("repair") or {}
        defects_str = "/".join(str(defects.get(s, 0)) for s in SEVERITIES) if editor.get("defects") else "—"
        pull_str = "/".join(str(pull.get(s, 0)) for s in PULL_SEVERITIES) if editor.get("pull") else "—"
        fight_str = f"{fight.get('gates_passed')}/{fight.get('of')}" if fight.get("gates_passed") is not None else "—"
        repair_str = c.get("repair", {}).get("cycles") if c.get("repair") else None
        rows.append(f"""
        <tr>
          <td>{_cell(c.get('n'))}</td>
          <td>{_cell(c.get('title'))}</td>
          <td>{_cell(author.get('words'))}</td>
          <td>{_cell(author.get('delta_pct'))}</td>
          <td>{_cell(pull.get('humor_beats_counted') if pull.get('humor_beats_counted') is not None else author.get('humor_beats_claimed'))}</td>
          <td>{_cell(author.get('action_item'))}</td>
          <td>{_cell(editor.get('verdict'))}</td>
          <td>{_cell(defects_str)} <span class="muted">(B/H/M/L)</span></td>
          <td>{_cell(pull_str)} <span class="muted">(S/M/L)</span></td>
          <td>{_cell(reader_a.get('pull'))}</td>
          <td>{_cell(reader_a.get('would_continue'))}</td>
          <td>{_cell(reader_a.get('confusions'))}</td>
          <td>{_cell(reader_a.get('laughs'))}</td>
          <td>{_cell(reader_b.get('pull'))}</td>
          <td>{_cell(reader_b.get('would_continue'))}</td>
          <td>{_cell(reader_b.get('confusions'))}</td>
          <td>{_cell(reader_b.get('laughs'))}</td>
          <td>{_cell(fight_str)}</td>
          <td>{_cell(repair_str)}</td>
          <td><span class="status status-{_h(c.get('status','PENDING'))}">{_cell(c.get('status'))}</span></td>
        </tr>""")

    agg = aggregate_book(book)
    pull_avg_series = []
    for a, b in zip(agg["reader_pull_a_series"], agg["reader_pull_b_series"]):
        vals = [v for v in (a, b) if v is not None]
        pull_avg_series.append(sum(vals) / len(vals) if vals else None)

    spark_pull = svg_sparkline(pull_avg_series, kind="line", y_max=5)
    spark_defects = svg_sparkline(agg["defects_series"], kind="bar")

    return f"""
    <div class="sparks-row">
      <div class="spark-card"><div class="spark-label">Reader pull (A/B avg) across chapters</div>{spark_pull}</div>
      <div class="spark-card"><div class="spark-label">Defects across chapters</div>{spark_defects}</div>
    </div>
    <div class="table-scroll">
    <table class="book-table">
      <thead><tr>
        <th>Ch</th><th>Title</th>
        <th>Words</th><th>Δ%</th><th>Humor</th><th>Action</th>
        <th>Editor</th><th>Defects</th><th>Pull findings</th>
        <th>A pull</th><th>A continue</th><th>A confuse</th><th>A laugh</th>
        <th>B pull</th><th>B continue</th><th>B confuse</th><th>B laugh</th>
        <th>Fight</th><th>Repair cyc.</th><th>Status</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>
    """


def render_series_table(series_rollup: dict, books_raw: list[dict]) -> str:
    rows = []
    defects_means = []
    for b in series_rollup["books"]:
        defects_means.append(b["defects_per_chapter_mean"])
        rows.append(f"""
        <tr>
          <td>{_cell(b['number'])}</td>
          <td>{_cell(b['title'])}</td>
          <td>{_cell(b['status'])}</td>
          <td>{_cell(b['chapters_closed'])}/{_cell(b['chapters_total'])}</td>
          <td>{_cell(b['reader_pull_a_mean'])}</td>
          <td>{_cell(b['reader_pull_b_mean'])}</td>
          <td>{_cell(b['defects_per_chapter_mean'])}</td>
          <td>{_cell(b['pull_findings_per_chapter_mean'])}</td>
          <td>{_cell(b['humor_beats_per_chapter_mean'])}</td>
          <td>{_cell(b['fight_gates_mean'])}</td>
          <td>{_cell(b['repair_cycles_mean'])}</td>
          <td>{_cell(b['words_total'])}</td>
        </tr>""")
    spark = svg_sparkline(defects_means, kind="bar")
    return f"""
    <div class="sparks-row"><div class="spark-card"><div class="spark-label">Defects/chapter mean, per book</div>{spark}</div></div>
    <div class="table-scroll">
    <table class="book-table">
      <thead><tr>
        <th>#</th><th>Title</th><th>Status</th><th>Chapters</th>
        <th>Pull A</th><th>Pull B</th><th>Defects/ch</th><th>Pull findings/ch</th>
        <th>Humor/ch</th><th>Fight gates</th><th>Repair cyc.</th><th>Words</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>
    <h3>Book detail</h3>
    {"".join(f"<details><summary>{_h(b.get('book',{}).get('title') or b.get('book',{}).get('slug',''))}</summary>{render_book_summary(b)}</details>" for b in books_raw)}
    """


def render_universe_table(universe_rollup: dict, series_raw: list[tuple[dict, list[dict]]]) -> str:
    rows = []
    for s in universe_rollup["series"]:
        book_count = len(s["books"])
        closed = sum(b["chapters_closed"] for b in s["books"])
        total = sum(b["chapters_total"] for b in s["books"])
        rows.append(f"""
        <tr>
          <td>{_cell(s.get('series'))}</td>
          <td>{_cell(book_count)}</td>
          <td>{closed}/{total}</td>
        </tr>""")
    return f"""
    <div class="table-scroll">
    <table class="book-table">
      <thead><tr><th>Series</th><th>Books</th><th>Chapters closed</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>
    <h3>Series detail</h3>
    {"".join(f"<details><summary>{_h(sr.get('series') or '')}</summary>{render_series_table(sr, books)}</details>" for sr, books in series_raw)}
    """


CSS = """
:root {
  --font-display: "Newsreader", Georgia, "Times New Roman", serif;
  --font-body: "IBM Plex Sans", -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
body { font-family: var(--font-body); font-size: 14px; line-height: 1.5; }
h1, h2, h3 { font-family: var(--font-display); font-weight: 600; letter-spacing: -0.01em; text-wrap: balance; }
h1 { font-size: 2rem; } h2 { font-size: 1.4rem; } h3 { font-size: 1.1rem; }
table, td, .num { font-variant-numeric: tabular-nums; }
code, .mono { font-family: var(--font-mono); font-size: 0.92em; }
.tab-btn { font-family: var(--font-body); letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.78rem; }
:root {
  --bg: #f7f6f3; --panel: #ffffff; --text: #1c1b19; --muted: #6b6960;
  --border: #e4e1da; --accent: #7a5c3e; --accent-bg: #f0e9df;
  --pass: #2f6b3a; --pwf: #9a7a1f; --hold: #a13b3b; --pending: #8a8577;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #171613; --panel: #211f1b; --text: #ece8e0; --muted: #a29c8d;
    --border: #38352c; --accent: #d6b98a; --accent-bg: #2c2721;
    --pass: #6fbf7a; --pwf: #e0bf5a; --hold: #e07a7a; --pending: #8a8577;
  }
}
:root[data-theme="dark"] {
  --bg: #171613; --panel: #211f1b; --text: #ece8e0; --muted: #a29c8d;
  --border: #38352c; --accent: #d6b98a; --accent-bg: #2c2721;
  --pass: #6fbf7a; --pwf: #e0bf5a; --hold: #e07a7a; --pending: #8a8577;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 24px; }
h1 { font-size: 20px; margin: 0 0 4px; }
h1 .sub { color: var(--muted); font-weight: 400; font-size: 14px; }
h3 { font-size: 15px; margin: 24px 0 8px; }
h4 { font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin: 0 0 4px; }
.tabs { display: flex; gap: 4px; margin: 16px 0; border-bottom: 1px solid var(--border); }
.tab-btn { background: none; border: none; padding: 8px 14px; font-size: 13px; color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; }
.tab-btn.active { color: var(--text); border-bottom-color: var(--accent); font-weight: 600; }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.table-scroll { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }
table.book-table { border-collapse: collapse; width: 100%; min-width: 720px; font-size: 12.5px; background: var(--panel); }
table.book-table th, table.book-table td { padding: 6px 8px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }
table.book-table thead th { background: var(--accent-bg); position: sticky; top: 0; }
table.kv { border-collapse: collapse; font-size: 12.5px; margin-bottom: 8px; }
table.kv th { text-align: left; color: var(--muted); font-weight: 500; padding: 2px 10px 2px 0; vertical-align: top; }
table.kv td { padding: 2px 0; }
.muted { color: var(--muted); }
.status { padding: 1px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.status-SCENE_CLOSED { background: color-mix(in srgb, var(--pass) 18%, transparent); color: var(--pass); }
.status-PENDING { background: color-mix(in srgb, var(--pending) 18%, transparent); color: var(--pending); }
.status-BLOCKED { background: color-mix(in srgb, var(--hold) 18%, transparent); color: var(--hold); }
.sparks-row { display: flex; gap: 16px; margin: 12px 0; flex-wrap: wrap; }
.spark-card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; }
.spark-label { font-size: 11px; color: var(--muted); margin-bottom: 4px; }
svg.spark { display: block; }
.spark-line { fill: none; stroke: var(--accent); stroke-width: 1.5; }
.spark-dot { fill: var(--accent); }
.spark-bar { fill: var(--accent); }
details.chapter-detail { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; margin: 8px 0; padding: 8px 12px; }
details.chapter-detail summary { cursor: pointer; font-weight: 600; }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 10px; }
footer { margin-top: 32px; color: var(--muted); font-size: 11px; }
"""

JS = """
document.querySelectorAll('.tab-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
    document.querySelectorAll('.tab-panel').forEach(function (p) { p.hidden = true; p.classList.remove('active'); });
    btn.classList.add('active');
    var panel = document.getElementById('tab-' + btn.dataset.tab);
    panel.hidden = false;
    panel.classList.add('active');
  });
});
"""


def _build_fragment_parts(
    title: str, universe_panel: str, series_panel: str, book_panel: str, chapter_panel: str
) -> tuple[str, str]:
    """Split the dashboard into (head_bits, body_bits): head_bits is the
    <title> + <style> pair; body_bits is everything that belongs in
    <body>. Shared by build_html (the --fragment output) and
    build_full_document (the default, doctype-wrapped output) so the two
    never drift apart."""
    head_bits = f"""<title>{_h(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>"""
    body_bits = f"""<h1>{_h(title)} <span class="sub">fantasyau1.1 progress dashboard</span></h1>
<div class="tabs">
  <button class="tab-btn active" data-tab="universe">Universe</button>
  <button class="tab-btn" data-tab="series">Series</button>
  <button class="tab-btn" data-tab="book">Book</button>
  <button class="tab-btn" data-tab="chapter">Chapter</button>
</div>
<div class="tab-panel active" id="tab-universe">{universe_panel}</div>
<div class="tab-panel" id="tab-series" hidden>{series_panel}</div>
<div class="tab-panel" id="tab-book" hidden>{book_panel}</div>
<div class="tab-panel" id="tab-chapter" hidden>{chapter_panel}</div>
<footer>Generated by progress.py. Nothing on this page is hand-typed; every figure comes from a filed seat report. A dash (—) means no report has been filed for that field yet.</footer>
<script>{JS}</script>
"""
    return head_bits, body_bits


def build_html(title: str, universe_panel: str, series_panel: str, book_panel: str, chapter_panel: str) -> str:
    """Artifact-ready FRAGMENT: <title> and <style> first, then the body
    content -- no <!DOCTYPE>, <html>, <head>, or <body> tags. This is what
    `render --fragment` emits, for publishing through a wrapper that
    supplies its own skeleton."""
    head_bits, body_bits = _build_fragment_parts(title, universe_panel, series_panel, book_panel, chapter_panel)
    return f"{head_bits}\n{body_bits}"


def build_full_document(
    title: str, universe_panel: str, series_panel: str, book_panel: str, chapter_panel: str
) -> str:
    """Default `render` output: one complete, standalone HTML document
    (<!DOCTYPE html>, <html lang="en">, a <head> with charset + viewport
    meta plus the title/style, and a <body> with everything else)."""
    head_bits, body_bits = _build_fragment_parts(title, universe_panel, series_panel, book_panel, chapter_panel)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{head_bits}
</head>
<body>
{body_bits}</body>
</html>
"""


def cmd_render(args: argparse.Namespace) -> int:
    target = Path(args.target)
    out_path = Path(args.out)
    # --fragment emits the artifact-ready fragment (build_html); default
    # emits a full, standalone HTML document (build_full_document). Both
    # are built from the same _build_fragment_parts, so they never drift.
    renderer = build_html if getattr(args, "fragment", False) else build_full_document

    if (target / "progress.json").is_file():
        book = load_json(target / "progress.json")
        title = f"{book.get('book', {}).get('title', target.name)} — Book {book.get('book', {}).get('number', '?')}"

        # Synthesize a one-series, one-book rollup so the Universe/Series
        # tabs show real (if trivial) tables rather than a duplicate of the
        # Book tab -- each tab stays meaningfully distinct.
        series_rollup = {"universe": book.get("universe"), "series": book.get("series"), "books": [aggregate_book(book)]}
        universe_rollup = {"universe": book.get("universe"), "series": [series_rollup]}

        universe_panel = render_universe_table(universe_rollup, [(series_rollup, [book])])
        series_panel = render_series_table(series_rollup, [book])
        book_panel = render_book_summary(book)
        chapter_panel = render_chapter_details(book)
        html = renderer(title, universe_panel, series_panel, book_panel, chapter_panel)

    elif (target / "series.json").is_file():
        series_json = load_json(target / "series.json")
        series_rollup = aggregate_series(series_json)
        books_raw = _load_books(series_json.get("books", []))
        title = f"{series_rollup.get('series') or target.name} (series)"

        universe_rollup = {"universe": series_rollup.get("universe"), "series": [series_rollup]}
        universe_panel = render_universe_table(universe_rollup, [(series_rollup, books_raw)])
        series_panel = render_series_table(series_rollup, books_raw)
        first_book = books_raw[0] if books_raw else None
        book_panel = render_book_summary(first_book) if first_book else "<p class='muted'>No books.</p>"
        chapter_panel = render_chapter_details(first_book) if first_book else "<p class='muted'>No books.</p>"
        if first_book:
            book_panel = f"<p class='muted'>Showing book 1 of {len(books_raw)}: {_h(first_book.get('book',{}).get('title',''))}. See the Series tab's \"Book detail\" for the others.</p>" + book_panel
        html = renderer(title, universe_panel, series_panel, book_panel, chapter_panel)

    elif (target / "universe.json").is_file():
        universe_json = load_json(target / "universe.json")
        series_raw = []
        series_rollups = []
        for s in universe_json.get("series", []):
            s_dir = Path(s)
            s_json_path = s_dir / "series.json"
            if not s_json_path.is_file():
                continue
            s_json = load_json(s_json_path)
            rollup = aggregate_series(s_json)
            books_raw = _load_books(s_json.get("books", []))
            series_raw.append((rollup, books_raw))
            series_rollups.append(rollup)
        universe_rollup = {"universe": universe_json.get("universe"), "series": series_rollups}
        title = f"{universe_json.get('universe') or target.name} (universe)"

        universe_panel = render_universe_table(universe_rollup, series_raw)
        first_series_rollup, first_series_books = series_raw[0] if series_raw else (None, [])
        series_panel = render_series_table(first_series_rollup, first_series_books) if first_series_rollup else "<p class='muted'>No series.</p>"
        first_book = first_series_books[0] if first_series_books else None
        book_panel = render_book_summary(first_book) if first_book else "<p class='muted'>No books.</p>"
        chapter_panel = render_chapter_details(first_book) if first_book else "<p class='muted'>No books.</p>"
        if series_raw:
            series_panel = f"<p class='muted'>Showing series 1 of {len(series_raw)}: {_h(first_series_rollup.get('series') or '')}. See the Universe tab's \"Series detail\" for the others.</p>" + series_panel
        html = renderer(title, universe_panel, series_panel, book_panel, chapter_panel)

    else:
        fail(f"no progress.json, series.json, or universe.json found in {target}")
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"DASHBOARD_RENDERED={out_path}")
    print(f"bytes={out_path.stat().st_size}")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="progress.py",
        description="fantasyau1.1 progress tracker and dashboard renderer (stdlib only).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="write a fresh progress.json for a book")
    p_init.add_argument("book_dir")
    p_init.add_argument("--universe", required=True)
    p_init.add_argument("--series", required=True)
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--number", required=True, type=int)
    p_init.add_argument("--chapters", required=True, type=int)
    p_init.add_argument("--force", action="store_true", help="overwrite an existing progress.json")
    p_init.set_defaults(func=cmd_init)

    p_update = sub.add_parser("update", help="fill chapter NN from filed seat reports")
    p_update.add_argument("book_dir")
    p_update.add_argument("nn", type=int, metavar="NN")
    p_update.set_defaults(func=cmd_update)

    p_rollup = sub.add_parser("rollup", help="roll up a series (and, if listed, a universe)")
    p_rollup.add_argument("series_dir")
    p_rollup.set_defaults(func=cmd_rollup)

    p_render = sub.add_parser("render", help="render the self-contained HTML dashboard")
    p_render.add_argument("target", help="a book_dir, series_dir, or universe_dir")
    p_render.add_argument("--out", required=True)
    p_render.add_argument(
        "--fragment",
        action="store_true",
        help=(
            "emit the artifact-ready fragment only (title + style, then body "
            "content -- no doctype/html/head/body) for publishing through a "
            "wrapper that supplies its own skeleton. Default emits a full, "
            "standalone HTML document."
        ),
    )
    p_render.set_defaults(func=cmd_render)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
