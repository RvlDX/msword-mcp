# Adapting the outline to any campus guide

This skill does not store every campus guide. That is impossible and it would go stale fast. What it stores is an adaptation procedure: the few variables that really change an outline, and how to fill them from the guide the user has.

Authority order: program guide beats faculty guide, faculty guide beats university guide, university guide beats supervisor habit, supervisor habit beats general convention, general convention beats this file. When two rules clash, the one on the left wins, and the difference is stated openly.

## Adaptation steps

1. If the user gives a guide file (PDF or DOCX), read it and fill the variable table below. Done. Never guess anything written in it.
2. If there is no file, use the most common Indonesian defaults (column "Default"), mark every risky item `[CHECK: campus guide]`, and continue. Never stop the work only because the guide is not there yet.
3. If the campus has a preset in `shared/campus-presets.md`, read that preset first. Fill variables from the preset only for rules stated as university-wide. Variables the preset marks as faculty or program decided stay `[CHECK the faculty guide]` until the user names the faculty.
4. If the guide is in a foreign language, read it in its original language, fill the 14 variables with a short quote plus page or article number from the guide (original language, then a working translation in parentheses), and use the section names exactly as the guide writes them. Use IMRaD as the default shape for campuses outside Indonesia.
5. If two guides conflict (university guide versus program template, old edition versus new edition, text versus an appendix example in the same guide), apply the authority order above, state both wordings, and mark `[CHECK: ...]`. Never pick silently.
6. If there is no guide at all and the campus is unknown, use the defaults, write one line "This outline uses the general defaults because the campus guide is not available yet" above the variable table, and make "upload or name the guide" the first item in the closing block.

Every variable value shown to the user carries its source: `guide (p. n)`, `preset`, or `default [CHECK]`. A value with no source must never appear.

## The 14 variables

| # | Variable | Default (most common in Indonesia) | If different, the consequence |
|---|---|---|---|
| 1 | Chapter count | 5 | 4 chapters (results, discussion, and closing merged) or 6 chapters (discussion separate) |
| 2 | Location of problem statement, objectives, benefits, scope | parallel subchapters in Chapter I | some guides put them inside the Background |
| 3 | Chapter II name | Literature Review | Theoretical Framework, Theoretical Basis, or Chapter II theory plus Chapter III conceptual framework |
| 4 | Thinking or conceptual framework | diagram in Chapter I or at the end of Chapter II | its location moves, subchapter numbers shift |
| 5 | Results and discussion | one chapter | split into two chapters |
| 6 | Subchapter numbering | 1.1, 1.1.1 (tiered Arabic) | A., 1., a. (style of many PTKIN and law programs) |
| 7 | Maximum depth | 4 levels | some allow 3 |
| 8 | Citation style | author-year | APA 7, IEEE (engineering), Vancouver (health), Chicago (history) |
| 9 | Abstract | Indonesian plus English | some add a regional language or Arabic, word limit 150 to 300 |
| 10 | Special front matter | approval page, originality statement | thesis usage guide, dedication, transliteration (PTKIN), motto |
| 11 | Table and figure numbering | one series for the whole document | per chapter (Table 2.1) |
| 12 | Mandatory output | journal manuscript | published article, poster, intellectual property registration, product |
| 13 | Writing systematics | stated at the end of Chapter I | some guides forbid it |
| 14 | Similarity limit | none | a threshold (for example 25 percent), affects how to quote |

Fill this table at the start of the work and show the filled table to the user before the outline. That makes the difference with their own template visible, not a surprise at supervision.

## Known patterns in Indonesia

This is a rough map to guide guesses, not a replacement for the guide. Always `[CHECK: campus guide]`.

- Engineering and informatics: engineering research is common, Chapter III holds design (UML or ERD), Chapter IV holds implementation plus testing, citation is IEEE or author-year, the output is a system.
- Economics and management: quantitative dominates, operational definitions of variables are mandatory, classic assumption tests, Chapter IV holds hypothesis tests, APA.
- Education: classroom action research with cycles, R and D (ADDIE, 4D, Borg and Gall), instruments plus expert validation.
- Health and nursing: ethical clearance is mandatory, theory framework and concept framework are separate, operational definitions, Vancouver.
- Law: normative juridical versus empirical, primary, secondary, and tertiary legal materials replace population and sample, letter numbering, footnotes.
- PTKIN (UIN, IAIN, STAIN): Arab-Latin transliteration in the front matter, three-language abstract sometimes.
- Social and qualitative communication: paradigm and approach are stated, triangulation, data validity (credibility, transferability, dependability, confirmability).
- Vocational and D3 to D4: applied final project reports, weight on process and product, not on theoretical novelty.

Local terms often met: KKP, KP, PKL, Magang, MBKM means internship. Usulan Penelitian, Proposal, Pra-proposal means the early final-project stage. Seminar Judul, Seminar Proposal, Sempro. Seminar Hasil, Semhas. Sidang, Ujian Komprehensif, Munaqasyah (PTKIN) means the final exam. Skripsi, Tugas Akhir, Karya Tulis Ilmiah (KTI, D3 health).

## Adaptation checks

| Code | Check |
|---|---|
| A1 | 14 variables filled, from the guide when there is one |
| A2 | Every uncertain item marked `[CHECK: campus guide]` |
| A3 | Differences with the template the user brought are stated |
| A4 | Local terms used as the campus uses them (KKP versus KP versus PKL) |
| A5 | Citation style consistent across the outline |
| A6 | No campus rule invented |
| A7 | Every variable value carries its source (guide plus page, preset, or default [CHECK]) |
| A8 | Foreign guide: section names used in the guide original language, conflicts stated |

## Sources and credit

Adapted from guide-adapter.md in rangka by Bryan Kwandou (MIT).
