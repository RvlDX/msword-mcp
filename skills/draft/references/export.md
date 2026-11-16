# Export

Produce Markdown first, then convert. Never present an export as final until the `audit` skill passes it.

## Markdown to DOCX with Pandoc

Convert with Pandoc and a campus template. The template variables come from the filled preset in `shared/campus-presets.md` or from the preset file in `shared/presets/`.

- Page: A4, margins from the preset (the national standard is top 4 cm, bottom 3 cm, left 4 cm, right 3 cm).
- Font: Times New Roman 12 for the body, from the preset when it differs.
- Spacing: double spacing for the body, single spacing inside tables and figures, from the preset when it differs.
- Headings: chapter number and title centered, capital letters, size 14, bold. Subchapter titles start with a capital letter, size 12, bold.
- Page numbers: front matter in small Roman numerals centered at the bottom, main body in Arabic numerals starting at 1 on the first page of Chapter I, first page of each chapter centered at the bottom and other pages at the top right.
- Figure titles below the figure, centered. Table titles above the table, centered. Figures and tables numbered by chapter, for example Figure III.1.

Check the DOCX after conversion: headings, numbering, and captions survive the conversion. Fix the Markdown source and convert again, never hand-edit the DOCX and call it the source.

## PDF with Typst

When the campus template supports it, compile the same Markdown source to PDF with Typst. Use the same preset variables for margins, font, and spacing. The Markdown source stays the single source of truth. Never maintain two separate sources for DOCX and PDF.

## Citation export

Export the bibliography to BibTeX or RIS on request. Verify every exported entry against the verified reference list first. Never export an entry with guessed metadata.

## Sources and credit

Export workflow adapted from laporan-generator by muadzhdz (MIT) and the document assembly guidance in proposal-skripsi-skill by Bima Januri (MIT).
