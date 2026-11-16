---
name: outline
description: "Build and check outlines for research, journal articles, internship reports, and other academic or professional documents. Adapts structure to the applicable guide, identifies the core gap or purpose, checks traceability, and proposes titles last when appropriate."
version: 1.2.0
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, OpenCode, Codex, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Outline

Read `../shared/workflow-contract.md` before substantive work. Treat `../shared/institution-profile.md` as a task-profile template, not official campus data. Reuse a completed profile from the current project when available.

## Workflow

1. Classify purpose, genre, reader, discipline, stage, and available material.
2. If a campus or venue is named, inspect its current guide. For campus structure, use `references/guide-adapter.md` and record provenance for each applicable variable. Without a guide, use defaults only with `[CHECK: ...]` labels.
3. Build a core map: desired state/expectation, current state/evidence, gap or purpose, reader, central claim, proof/material, and intended contribution/action.
4. Choose the correct genre module: `references/genre-research.md` for research; `references/genre-report.md` for internship/KP/PKL reports; `references/genre-article.md` for journal/conference manuscripts. For other professional reports, structure around purpose and evidence rather than assuming a placement report.
5. For every section, state its job, key content, evidence/source required, and expected length or scope.
6. Run `references/checklist.md` and report Pass, Waiting for data, or Fail. Repair structural failures before presenting a final outline.
7. Generate title options only after the structure and central claim are coherent. List unresolved `[NEED: ...]` and `[CHECK: ...]` items.

## Rules

- Never invent facts, sources, quotes, figures, respondents, or rules. Use `[NEED: ...]` for missing user material and `[CHECK: ...]` for unverified details.
- Citations must come from supplied or verified sources. Do not guess bibliographic metadata.
- Do not force a five-chapter thesis structure onto an article, study note, or non-chapter report.
- Every question, promise, or claim must connect to a section and supporting evidence. Every section must serve the document purpose.
- Ask at most one essential question before starting; otherwise proceed with explicit placeholders.
- The outline skill produces structure and reasoning, not a full submission written in place of the student.

## References

- `references/guide-adapter.md`: campus authority order and structure variables.
- `references/checklist.md`: universal and genre checks.
- `references/genre-research.md`: research outline.
- `references/genre-report.md`: internship/KP/PKL report outline.
- `references/genre-article.md`: journal/conference article outline.
