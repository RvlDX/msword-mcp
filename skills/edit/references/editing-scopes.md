# Editing scopes

When the user asks to check or revise existing text, use the narrowest scope that fits the request and say which scope is used. Ask which scope the user wants when the request is unclear.

| Scope | May change | Must not change |
|---|---|---|
| Correction | Typos, punctuation, spelling | Wording, claims, structure, facts, numbers, citations |
| Editing | Grammar, clarity, flow, sentence structure | Facts, numbers, claims, citations, terminology, the author voice |
| Rewriting | Section structure, sentence wording, paragraph order | Facts, numbers, claims, citations. Flag any claim that cannot be kept |
| Writing | New prose from the user material | Nothing invented. Every missing fact is `[NEED: ...]`, every unverified fact is `[CHECK: ...]` |

## Rules for every scope

- Never change a number, a date, a name, a quote, or a citation. If a number looks wrong, flag it and ask, never fix it silently.
- Never change a term the field defines, a variable name, or a formula.
- Never change a direct quote, a work title, an institution name, or an interview quote. See references/keep-it.md.
- When the scope is Correction or Editing, the output is the corrected text plus a short table of what changed and where. The user must be able to see every change.
- When the scope is Rewriting, keep the paragraph count close to the original unless the user asks for a restructure, and report which claims were kept, moved, or flagged.
- When the scope is Writing, attach the traceability note: which identified issue or objective the section supports and where it connects next.

## Sources and credit

Adapted from the change-boundary table in naskah-id by nothinx (MIT).
