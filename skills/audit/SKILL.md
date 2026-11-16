---
name: audit
description: "Audit academic and professional documents for guideline compliance, research logic, cross-section consistency, methodology fit, and claim-evidence alignment. Produces traceable findings and prioritized revision plans."
version: 1.2.0
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, OpenCode, Codex, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Audit

Audit the supplied document against applicable rules, evidence, and the internal logic of the work. **Guideline compliance and research quality are separate audit tracks.** A document can follow a campus template and still have a broken research argument. Read `../shared/workflow-contract.md`; reuse a completed profile or use `../shared/institution-profile.md` as a template.

## Principles

- Establish genre, purpose, scope, stage, research type, and inspection limits before judging.
- Current official program/faculty/university/journal/client rules outrank general convention. Record provenance and conflicts.
- Run two distinct tracks: (1) compliance with applicable rules; (2) academic coherence, methodological fit, and evidence validity.
- Every criterion receives **Pass**, **Needs work**, **Not applicable**, or **Not verifiable**. For research-coherence checks, use the operational statuses in `references/research-audit-schema.md`.
- Not applicable is not a failure; Not verifiable is not proof of non-compliance.
- Audit partial drafts only within their available scope. Run final-package checks only for final-readiness requests.
- Never claim inaccessible pages/files were inspected or claim formal approval/guaranteed grades.

## Workflow

1. Establish genre, purpose, program/level if relevant, research type, stage, target reader, available files, and audit depth.
2. Resolve rules from the guide/rubric/journal instructions. Record issuer, version, page/section, and conflicts. Presets are fallbacks only.
3. Inventory only accessible artifacts. Identify missing data, instruments, appendices, source documents, and previous drafts.
4. Load exactly one matching module: `references/genre-research.md`, `references/genre-article.md`, or `references/genre-internship-report.md`. For other reports, use universal checks and explain scope.
5. For thesis/research documents requiring cross-section analysis, read `references/research-coherence.md`. With shell access, prepare Markdown/DOCX using `scripts/prepare_research_audit.py`.
6. Read the complete `manuscript_numbered.md`, not only extracted anchors. Use `research_map.json` and `machine_findings.json` only as navigation/candidate signals.
7. Run distinct passes using `references/reviewer-protocol.md`: logic, consistency, methodology, evidence, and devil's advocate. Run sequentially when multi-agent support is unavailable; do not claim independent parallel agents ran if they did not.
8. Apply `references/gates.md` and dimensions RC01–RC10. A failed prerequisite blocks only dependent checks.
9. Verify sources by type using `references/reference-verification.md`. DOI resolution is required only when a DOI is assigned or claimed.
10. Consolidate duplicates by root cause. Validate every quote, location, status, and severity with `scripts/validate_research_audit.py` before presenting a research-audit report.
11. For revised drafts, use `references/revision-impact.md` when old and new versions are available.
12. Produce findings using `references/finding-report.md`.

## Research coherence

Trace the chain appropriate to the actual design:

**Problem/context → evidence/gap → research question → objective → theory/concepts → design/method → population/materials/data → instrument/procedure → analysis → result → discussion → conclusion → contribution/recommendation.**

Test whether the links are defensible, not merely whether headings exist. Look for questions the method cannot answer, objectives with no method/result, theory that is never operationalized, instruments that do not measure stated constructs, changing samples/scopes, results interpreted beyond the analysis, conclusions that answer different questions, and stale information after revision.

Do not force one-to-one counts between questions, objectives, and conclusions. Adapt checks to quantitative, qualitative, mixed-methods, system-development, machine-learning, and review designs.

## Severity

- **Critical:** central conclusion or integrity claim is demonstrably invalid or fundamentally contradicted.
- **Major:** research question, design, measurement, analysis, or evidence chain is materially broken.
- **Moderate:** consequential but bounded inconsistency, omission, or unsupported interpretation.
- **Minor:** local clarification or presentation improvement.

Severity describes impact, not certainty. Critical requires confirmed evidence and high confidence; potential issues cannot be critical or major. Check for innocent explanations before escalating.

## Required output

1. Overall status and scope inspected.
2. Applicability summary, including Not applicable and Not verifiable.
3. Research Coherence Matrix showing each element, its location, dependencies, evidence, and status.
4. Findings with ID, severity, certainty, exact quote, location, related sections, reasoning, impact, basis, correction, and missing evidence.
5. Reviewer synthesis: consensus, disagreement, root cause, and reviewer roles not run.
6. Missing/unverifiable items and traceability assessment.
7. Upstream-first revision plan.
8. Disclaimer: assistant review, not formal institutional/editorial approval.

## Integrity

Never invent sources, facts, respondents, page numbers, results, approvals, or guide rules. Never forge signatures/stamps or silently rewrite a document during audit. Similarity or machine-pattern signals are not proof of misconduct. An automated count mismatch is a candidate signal, not an academic contradiction by itself.

## References

- [Stage gates](references/gates.md)
- [Layered quality control](references/layered-qc.md)
- [Research coherence audit](references/research-coherence.md)
- [Specialist reviewer protocol](references/reviewer-protocol.md)
- [Research audit schema](references/research-audit-schema.md)
- [Revision impact review](references/revision-impact.md)
- [Reference verification](references/reference-verification.md)
- [Finding report](references/finding-report.md)
- [Research module](references/genre-research.md)
- [Article module](references/genre-article.md)
- [Internship report module](references/genre-internship-report.md)
