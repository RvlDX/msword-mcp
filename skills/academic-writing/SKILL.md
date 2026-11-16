---
name: academic-writing
description: "Route and coordinate Indonesian academic writing tasks across outline, draft, edit, and audit. Identify genre, applicable campus or journal rules, evidence, and the smallest suitable workflow. Use for end-to-end academic writing help or choosing the right specialist skill."
version: 1.2.0
license: MIT
compatibility: "Hermes, CodeBuddy, Claude Code, OpenCode, Codex, and any agent that reads the Agent Skills format."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Academic Writing Workflow

Act as the workflow coordinator. Read `../shared/workflow-contract.md` before routing. Treat `../shared/institution-profile.md` as a template; reuse a completed task profile from the current project when available.

## Classify

Identify intent (outline/draft/edit/audit/combined), genre, purpose, discipline, program/level when applicable, institution or venue when supplied, target reader, available guide and material, document stage, and requested output. Do not infer missing official rules. Continue with uncertainty labels when possible and ask at most one essential question.

## Route to the smallest skill set

| Request | Route |
|---|---|
| Build, restructure, or check an outline | `outline` |
| Draft a section from user material | `draft` |
| Correct or revise existing text | `edit` |
| Inspect requirements, evidence, citations, or readiness | `audit` |
| Review research logic, cross-chapter consistency, methodology fit, or claim-evidence alignment | `audit` |
| End-to-end work explicitly requested | `outline` → `draft` → `edit` → `audit`, skipping completed or irrelevant stages |

## Genre routing

- Research thesis/proposal/dissertation: research structure and only the methodology path actually used.
- Journal/conference article: target venue instructions first; IMRaD only when suitable.
- Internship/KP/PKL: placement-specific checks only for an actual placement report and only when required by the current guide.
- Technical/professional report: structure follows purpose and evidence; do not assume an internship.
- Study notes: explanatory structure, not thesis compliance gates.

If genre is ambiguous, state the working assumption and proceed where safe.

## Handoff

Use the shared handoff contract. Preserve task profile, guide provenance, inspected artifacts, evidence labels, completed checks, blockers, and next step. Never claim another skill ran unless its output is available. Never ask the user to repeat known information.

## Integrity

Never invent data, references, respondents, results, DOI metadata, approvals, or institutional rules. Distinguish existing state from proposals. Preserve facts and author voice during editing. Do not promise grades, detector outcomes, similarity scores, or formal approval.

## Specialist entrypoints

- `../outline/SKILL.md`
- `../draft/SKILL.md`
- `../edit/SKILL.md`
- `../audit/SKILL.md`

Load only relevant specialist instructions and their required references.

## Updater

The installed dispatcher folder ships its own updater at `scripts/update.py` (standard library only). From the installed dispatcher folder, `python scripts/update.py version` shows the installed version, `check-update` compares it with the latest GitHub Release without changing files, `update` downloads that release, validates it, backs the current family up outside the skills directory, and replaces it, and `rollback` restores the latest backup. There is no automatic update. A v1.0.0 installation does not have the updater yet: install v1.1.0 once with the installer first, then use the updater for later versions.
