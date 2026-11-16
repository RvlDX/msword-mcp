# Campus presets

A preset is a filled set of the 14 variables from the outline skill plus the export variables (margins, font, spacing, cover). A preset never replaces the guide. When a preset and the user guide disagree, the guide wins and the difference is flagged.

## Preset file shape

Presets live in `shared/presets/` as YAML files, one per campus or per national standard. The file name is the preset id, for example `generic.yml` or `ui-skripsi.yml`. Fields follow the example in `shared/presets/generic.yml`.

Required fields: preset id, name, description, margins (top, bottom, left, right), font family and size, line spacing, heading chapter prefix and number format, cover settings. Optional fields: abstract languages and word limit, citation style, chapter count, table and figure numbering style, similarity limit.

## Presets bundled here

- `generic.yml`: national standard, margins 4, 4, 3, 3 cm, Times New Roman 12, double spacing. Use when the campus has no preset and no guide file yet. Mark every value `[CHECK: campus guide]`.

## Full preset sets in the source repos

This repo bundles only the generic preset. The full sets live in the repos this work adapts, all MIT licensed. Copy a preset file from there when the campus is needed, verify it against the current guide, and add it here with its source noted.

- proposal-skripsi-skill by Bima Januri: 28 campus JSON presets (UGM, UI, UNY, ITB, IPB, UNAIR, UB, ITS, UNDIP, Unpad, Unhas, Telkom, BINUS, UMY, UII, UAD, UMS, Udinus, UMM, UMB, Gunadarma, UPN Veteran, Budi Luhur, UMN, generic, custom). Each preset records its provenance (official or convention).
- rangka by Bryan Kwandou: sourced notes for 22 Indonesian campuses (UI, UGM, ITB, ITS, Unhas, UNM, UMI, UIN Alauddin, IPB, and more) in `references/campus-*.md`, plus the UAJM FTI guides in full.
- laporan-generator by muadzhdz: YAML presets (skripsi-4433 national standard, UI, UGM, ITB, ITS, IPB, UB, Unpad, Undip, Unair, Unhas, Telkom, and journal presets).

## How to add a preset

1. Copy the closest existing preset or start from `generic.yml`.
2. Fill every field from the campus guide, with the guide page or section noted in a comment.
3. Mark any field that is faculty or program decided as `[CHECK the faculty guide]`.
4. Add one line to the list above with the campus name and the source.
5. Run `scripts/validate_package.py` before committing.

## Sources and credit

Preset design adapted from proposal-skripsi-skill by Bima Januri (MIT), rangka by Bryan Kwandou (MIT), and laporan-generator by muadzhdz (MIT).
