# Shared workflow contract

This file defines common operating rules for the academic-writing skill family. It is not a campus guide or a substitute for genre-specific references.

## Routing

Use the smallest skill set that completes the request. `outline` builds structure; `draft` develops text from user material; `edit` improves existing prose without changing facts; `audit` checks requirements and evidence. Use `academic-writing` for multi-stage coordination. Do not invoke all skills by default.

| User intent | Skill | Optional next step |
|---|---|---|
| Plan or check structure | outline | draft |
| Develop prose from material | draft | edit, then audit |
| Improve existing prose | edit | audit when compliance is requested |
| Inspect compliance/readiness | audit | edit or draft for remediation |
| Coordinate end-to-end work | academic-writing | applicable specialist stages |

A language correction request is not a full audit. An audit does not authorize silent rewriting. A request for one section does not require drafting an entire document.

## Task identity

Identify only relevant details: genre, purpose, discipline, program/level when applicable, institution/faculty/venue when supplied, target reader, requested scope, available guide/rubric/template, source material, dataset, draft, document stage, and requested output.

Do not infer official rules, academic level, research design, or citation style from unrelated context. If information is missing but work can proceed, use `[NEED: ...]` or `[CHECK: ...]` and continue. Ask at most one essential question.

## Provenance and authority

Every institutional or venue rule must carry provenance: `guide (page/section)`, `preset`, `default [CHECK]`, or `user decision`. A preset is a fallback, never an authority over a current official guide. Record conflicting requirements rather than silently resolving them. For campus rules, use the authority order in `skills/outline/references/guide-adapter.md`.

## Shared evidence labels

| Label | Meaning |
|---|---|
| E | Empirical or operational fact supported by accessible evidence |
| C | Conceptual or literature claim supported by a verified source |
| A | Analysis or inference derived from E or C |
| P | Proposal, recommendation, or future-state design |
| U | Unknown or not yet verified |

Never promote U or P to E. Never invent sources, DOI, respondents, quotations, numbers, test results, implementation status, permissions, signatures, or institutional rules. Keep confidential material out unless the user has authority to use it.

## Handoff contract

When moving between skills, preserve: task/genre; applicable guide and provenance; artifacts actually inspected; evidence status; completed checks; unresolved `[NEED: ...]` and `[CHECK: ...]`; and next step. Do not claim that a skill ran unless its output is available in the current context or project files. Do not ask the user to repeat known information.

## Audit statuses

- **Pass:** requirement is supported and fulfilled.
- **Needs work:** evidence shows a defect.
- **Not applicable:** requirement does not belong to this genre or task.
- **Not verifiable:** available files/evidence cannot establish compliance.

Not applicable is not a failure. Not verifiable is not proof of non-compliance.

## Research record handoff

For multi-stage research, maintain `shared/research-record.md` (or a project-local copy) with research questions, design, terms, scope, evidence, decisions, cross-section dependencies, open issues, and next action. Never invent missing fields.

## Output discipline

Separate verified findings from recommendations. Cite exact guide pages and source metadata when available. Do not fabricate page numbers or imply that inaccessible files or sources were inspected.
