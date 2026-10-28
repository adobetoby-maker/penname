#!/usr/bin/env python3
"""Sentence-variance metrics for a fantasyau1.1 chapter manuscript.

Reads one chapter file and prints a JSON report of narration-only sentence
metrics: total words, a narration sentence-length histogram, the chapter-wide
rate of <=12-word sentences, the diagnostic count of 120-word narration windows
that never dip to a <=12-word sentence,
consecutive "chained sentence" runs longer than 2, uses of " for " as a
conjunction, a define-by-negation count, and the em dash count.

Dialogue (any text inside double quotes) is excluded from every narration
metric -- it is extracted, counted, and then discarded before the sentence
work begins. The word count field ("words") is the whole-file word count
(title, narration, and dialogue), matching the "wc -w" figure used
elsewhere in the harness; every other field is narration-only.

A "chained sentence" is one sentence containing at least two clause joins of
the shape ", and" or ", for" (i.e. >= 3 clauses total). " for " counted as a
conjunction is the heuristic: a ", for " followed by a clause (a lowercase
word starting the next clause, not "for" introducing a plain noun phrase
object like "waited for supper").

Usage: variance.py <chapter.md>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Any span in double quotes is treated as dialogue and stripped before
# narration metrics run. DOTALL so a quote that wraps a line break is still
# treated as one span rather than leaking the closing quote into narration.
QUOTE_RE = re.compile(r'"[^"]*"', re.DOTALL)

# Sentence boundary: a run of . ! or ? followed by whitespace. Deliberately
# naive (no abbreviation table) -- this is a craft heuristic, not a parser.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

WORD_RE = re.compile(r"[A-Za-z0-9'’-]+")

# A single clause join: ", and" or ", for" (case-insensitive, comma required
# so a sentence-initial "And" or a plain "for" object doesn't count).
CLAUSE_JOIN_RE = re.compile(r",\s+(?:and|for)\b", re.IGNORECASE)

# " for " used as a conjunction (heuristic): a comma, "for", then a clause --
# approximated as "for" followed by a personal pronoun or "the"/"a"/"it"
# plus a verb-shaped continuation, which is the commonest causal-for shape
# ("he went, for the light was failing"). This deliberately undercounts
# rather than flags every object-of-preposition "for".
FOR_CONJUNCTION_RE = re.compile(
    r",\s+for\s+(?:he|she|it|they|I|we|you|the|a|an|his|her|their|its)\b",
    re.IGNORECASE,
)

# Define-by-negation shapes (Charter-style "not X but Y" / "no X, only Y" /
# flat "was not" / "did not ... it was" constructions).
NEGATION_PATTERNS = [
    re.compile(r"\bnot\s+\w+(?:\s+\w+){0,4}\s+but\b", re.IGNORECASE),
    re.compile(r"\bno\s+\w+(?:\s+\w+){0,3},\s+only\b", re.IGNORECASE),
    re.compile(r"\bwas\s+not\b", re.IGNORECASE),
    re.compile(r"\bdid\s+not\b.{0,60}?\bit\s+was\b", re.IGNORECASE | re.DOTALL),
]

# The real em dash character only. A bare "--" is not counted: this corpus
# uses "---" as a markdown section-break rule between scenes, and counting
# it as an em dash would overcount on every multi-scene chapter.
EM_DASH_RE = re.compile(r"—")

WINDOW_SIZE = 120
SHORT_SENTENCE_MAX = 12
CHAINED_RUN_THRESHOLD = 2


def strip_title_line(text: str) -> str:
    """Drop a leading '# Chapter N -- Title' line if present."""
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        return "\n".join(lines[1:])
    return text


def word_count(s: str) -> int:
    return len(WORD_RE.findall(s))


def split_narration_and_dialogue(body: str) -> tuple[str, list[str]]:
    dialogue_spans = QUOTE_RE.findall(body)
    narration = QUOTE_RE.sub(" ", body)
    return narration, dialogue_spans


def split_sentences(narration: str) -> list[str]:
    flat = re.sub(r"\s+", " ", narration).strip()
    if not flat:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(flat) if s.strip()]


def bucket_for(n: int, width: int = 5) -> str:
    lo = (n // width) * width
    hi = lo + width - 1
    return f"{lo}-{hi}"


def histogram_of(lengths: list[int]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for n in lengths:
        b = bucket_for(n)
        hist[b] = hist.get(b, 0) + 1
    return dict(sorted(hist.items(), key=lambda kv: int(kv[0].split("-")[0])))


def count_windows_missing_short_sentence(lengths: list[int]) -> tuple[int, int]:
    """Slide a running window over narration sentences by word count; every
    time the running total reaches WINDOW_SIZE words, close the window and
    check whether it contained a sentence of SHORT_SENTENCE_MAX words or
    fewer. Returns (windows_missing_short, windows_total)."""
    total_windows = 0
    missing = 0
    window_words = 0
    window_has_short = False
    for n in lengths:
        window_words += n
        if n <= SHORT_SENTENCE_MAX:
            window_has_short = True
        if window_words >= WINDOW_SIZE:
            total_windows += 1
            if not window_has_short:
                missing += 1
            window_words = 0
            window_has_short = False
    return missing, total_windows


def count_chained_runs(sentences: list[str]) -> tuple[int, int]:
    """A sentence is 'chained' if it has >=2 clause joins (>=3 clauses). A
    run is a maximal sequence of consecutive chained sentences. Returns
    (runs_over_threshold, longest_run)."""
    flags = [len(CLAUSE_JOIN_RE.findall(s)) >= 2 for s in sentences]
    runs_over = 0
    longest = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            longest = max(longest, current)
        else:
            if current > CHAINED_RUN_THRESHOLD:
                runs_over += 1
            current = 0
    if current > CHAINED_RUN_THRESHOLD:
        runs_over += 1
    return runs_over, longest


def count_negation(narration: str) -> int:
    return sum(len(pat.findall(narration)) for pat in NEGATION_PATTERNS)


def analyze(text: str, path: str) -> dict:
    body = strip_title_line(text)
    narration, dialogue_spans = split_narration_and_dialogue(body)
    sentences = split_sentences(narration)
    lengths = [word_count(s) for s in sentences]

    missing, total_windows = count_windows_missing_short_sentence(lengths)
    runs_over, longest_run = count_chained_runs(sentences)

    narration_words = sum(lengths)
    short_sentences = sum(1 for n in lengths if n <= SHORT_SENTENCE_MAX)

    return {
        "file": path,
        "words": word_count(text),
        "narration_words": narration_words,
        "narration_sentences": len(sentences),
        "dialogue_spans_excluded": len(dialogue_spans),
        "narration_sentence_length_histogram": histogram_of(lengths),
        "short_sentences_12w_or_less": short_sentences,
        "short_sentences_per_1000_narration_words": round(
            short_sentences * 1000 / narration_words, 2
        ) if narration_words else 0.0,
        "windows_120w_total": total_windows,
        "windows_120w_missing_short_sentence": missing,
        "chained_sentence_runs_over_2": runs_over,
        "longest_chained_run": longest_run,
        "for_as_conjunction_count": len(FOR_CONJUNCTION_RE.findall(narration)),
        "define_by_negation_count": count_negation(narration),
        "em_dash_count": len(EM_DASH_RE.findall(text)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sentence-variance metrics for a fantasyau1.1 chapter (JSON to stdout)."
    )
    parser.add_argument("chapter", type=Path, help="path to a chNN-*.md manuscript file")
    args = parser.parse_args()

    if not args.chapter.exists():
        print(f"FATAL: no such file: {args.chapter}", file=sys.stderr)
        return 1
    if not args.chapter.is_file():
        print(f"FATAL: not a file: {args.chapter}", file=sys.stderr)
        return 1

    text = args.chapter.read_text(encoding="utf-8")
    result = analyze(text, str(args.chapter))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
