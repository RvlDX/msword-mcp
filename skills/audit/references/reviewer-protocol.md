# Specialist Reviewer Protocol

Use five separate review lenses. These are review roles, not an obligation to run five runtime agents. If the platform does not support multi-agent, run five sequential passes and do not claim independent agents ran in parallel.

## Roles

1. **Logic reviewer:** argument flow, gaps, premises, transitions, logical leaps, circular reasoning, and conclusions.
2. **Consistency reviewer:** terms, numbers, names, dates, periods, samples, variables, methods, tables/figures, abstract, and conclusions across sections.
3. **Methodology reviewer:** fit of questions to design, samples/materials, instruments, procedures, analysis, assumptions, and evaluation against the actual design.
4. **Evidence reviewer:** traceability of claims to sources/data, accuracy of quotes/tables/calculations, overclaim, and missing evidence.
5. **Devil's advocate:** alternative explanations, counterexamples, boundary conditions, confounders, weak assumptions, and cases that could defeat the interpretation. Do not invent objections.

## Protocol

1. Read the full manuscript before concluding.
2. Each reviewer records candidate findings with exact quote, location, related sections, reasoning, impact, and recommendation.
3. Merge comments that share a root cause; consensus is not proof of correctness.
4. Record disagreements and alternative explanations. If unresolved, lower certainty or mark not assessable.
5. Look for innocent explanations before assigning high severity.
6. Validate quotes and severity with `validate_research_audit.py`.
7. An audit must not silently edit the manuscript. Diagnosis comes before revision.

## Status and severity

- `confirmed`: directly supported by the manuscript/evidence submitted.
- `likely`: strong indication, but a reasonable explanation exists or an appendix is unavailable.
- `potential`: candidate needing checking, evidence not yet sufficient.
- `critical`: a central conclusion/integrity claim is demonstrably invalid or fundamentally contradicted.
- `major`: the question, design, measurement, analysis, or evidence chain is materially broken.
- `moderate`: consequential but bounded inconsistency, omission, or unsupported interpretation.
- `minor`: local clarification or presentation improvement.

Critical may only be confirmed with high confidence. Potential may not be critical or major. Missing input is not automatically a defect; use `not_assessable`.
