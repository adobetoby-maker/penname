# Role Contract — Finding Verifier

## Mission

Test proposed editorial findings against frozen evidence. You verify claims;
you do not improve prose and do not generate new findings while verifying an
existing batch.

The verifier may be a human, the orchestrator, a deterministic script, or a
model. Independence from the original editor is preferred for high-impact
findings.

## For each proposed finding

1. Confirm that cited files and locations exist at the run's recorded revision.
2. Confirm that the quoted draft evidence is accurate and sufficient.
3. For contradictions, confirm the comparison evidence and authority level.
4. For counts, repeat the count over the same declared scope.
5. Confirm the claimed reader consequence follows from the evidence.
6. Record `VERIFIED`, `REJECTED`, or `NEEDS_HUMAN_JUDGMENT`, with a concise
   reason, in a new verification report. Never mutate the editor report.

If evidence is unavailable, use `NEEDS_HUMAN_JUDGMENT` and identify the missing
artifact. Absence of evidence is not verification.

## Boundaries

- Do not rewrite the manuscript.
- Do not change severity merely because a repair seems easy or difficult.
- Do not convert a taste concern into a verified defect.
- Do not broaden the finding while verifying it; create a separate proposed
  finding during a later editorial pass if necessary.

## Output

Write exactly one report conforming to
`contracts/verification-report.schema.json` at the packet's declared
`output.verifier_report_path`. The manuscript, author report, editor report,
and frozen context are evidence only.
