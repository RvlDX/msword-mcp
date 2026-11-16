---
name: edit
description: "Edit Indonesian academic prose and other scholarly writing while preserving facts, claims, citations, disciplinary terminology, and author voice. Supports correction, editing, rewriting, and drafting from user material."
version: 1.2.0
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, OpenCode, Codex, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Edit

Read `../shared/workflow-contract.md` before substantive work. Reuse the current task's terminology list and completed institution profile where available. The institution profile is a template, not an official source.

Start from user-provided text. If no text exists, route to `draft`.

## Editing scopes

| Scope | May change | Must preserve |
|---|---|---|
| Correction | Typos, punctuation, spelling | Wording, facts, claims, structure, numbers, citations |
| Editing | Grammar, clarity, flow, sentence structure | Facts, numbers, claims, citations, terminology, author voice |
| Rewriting | Sentence/paragraph order and wording | Facts, numbers, claims, citations; flag unsupported claims |
| Writing | New prose from user material | No invented facts; missing/unverified items are marked |

When unclear, use the narrowest scope (Correction) and state that choice. Ask one question only when scope materially affects the result.

## Workflow

1. Read the text and determine the requested scope.
2. Check applicable language rules (EYD V/KBBI for Indonesian) using `references/eyd-kbbi.md`.
3. Check mechanical writing patterns in `references/ai-patterns.md`. Patterns are signals, not proof of AI authorship or misconduct.
4. Check `references/keep-it.md` to avoid damaging legitimate field conventions, technical terms, hedging, quotations, and author voice.
5. Check terminology and cross-section consistency.
6. Return revised text plus a change report with location, issue, and correction. Never rewrite silently.

## Boundaries

Never change numbers, dates, names, direct quotations, source metadata, formulas, variable names, or citations without explicit verified basis. Never promise plagiarism/AI-detector scores, and never edit to evade detectors or conceal AI authorship. A pattern signal alone is not evidence of misconduct.

## References

- `references/editing-scopes.md`: scope boundaries.
- `references/eyd-kbbi.md`: Indonesian language rules.
- `references/ai-patterns.md`: patterns to improve clarity.
- `references/keep-it.md`: legitimate conventions to preserve.
