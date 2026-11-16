---
name: draft
description: "Draft academic and professional document sections from the user's own notes, data, documents, outline, and verified sources. Supports research chapters, articles, internship reports, and technical reports with evidence-first safeguards."
version: 1.2.0
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, OpenCode, Codex, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Draft

Read `../shared/workflow-contract.md` before substantive work. Reuse a completed task profile from the project; treat `../shared/institution-profile.md` as a template, not as verified rules.

Start from a finished outline. If none exists, use `outline` first. Follow the approved structure and do not silently change it. Route by genre: use `references/article-manuscript.md` for journal/conference manuscripts; use chapter references only for thesis, proposal, dissertation, or a guide-based chapter report. Never force Chapter I to V onto an article.

## Evidence discipline

Classify factual material using shared labels E (evidence), C (citation), A (analysis), P (proposal), and U (unknown). Never present a proposal as an existing implementation. Use `[NEED: ...]` for missing evidence and `[CHECK: ...]` for unverified material.

Evidence may include direct observation, authorized records, source files, datasets, interview/observation notes, official documents, and verified literature. Student recollection may guide questions but needs confirmation for exact dates, figures, roles, or processes. Assumptions are not facts.

## Workflow

1. Confirm the genre, document stage, outline, and required output.
2. Inventory guide, draft, notes, data, references, diagrams, and other available artifacts. State what has and has not been inspected.
3. Create a terminology list and keep terminology and author point of view consistent.
4. Draft one section or chapter at a time using its specific reference. Complete a section check before moving to the next.
5. Verify citations, numbers, quotes, and data while drafting, not only at the end.
6. Distinguish current state from proposed state and planned work from completed work.
7. Report unresolved `[NEED: ...]` and `[CHECK: ...]`, traceability to the outline, and the next step.
8. Run `audit` before describing a final package as ready for review or submission.

## Method paths

Select the actual design: quantitative, qualitative, mixed methods, R&D/prototyping, document study, conceptual argument, or another justified approach. Do not force hypotheses, experiments, sampling, or survey assumptions onto work that does not use them. Dataset statistics must be calculated from supplied data. Never quote, code, count, or report results that do not exist in the source material.

## Integrity

Never invent data, respondents, sources, numbers, tests, results, implementation/deployment status, or approvals. Refuse ghostwriting intended to be submitted as the student's independent work and requests to disguise AI output as the user's own work. Never forge signatures, stamps, assessments, letters, attendance, or consultation records.

## References

- `references/chapter1-introduction.md` through `references/chapter5-conclusions.md`: chapter-based research/report drafting.
- `references/export.md`: Markdown, DOCX, PDF, and citation export.
- `references/article-manuscript.md`: journal and conference manuscripts.
