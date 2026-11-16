"""Page layout, header/footer, spacing, bookmark, and watermark tools.

Cross-platform tools using python-docx for section-level and page-level operations.
"""

import json
import os
from typing import Optional

from docx import Document
from docx.shared import Pt, Inches, Cm, Mm, Emu
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

from word_document_server.utils.file_utils import check_file_writeable, ensure_docx_extension, get_file_lock


_ALIGN_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def _parse_unit_length(value: Optional[float], unit: str = "cm", fallback_inches: Optional[float] = None):
    """Convert a numeric value to a python-docx Length object based on metric or imperial unit."""
    if value is not None:
        u = unit.lower().strip()
        if u in ("cm", "centimeter", "centimeters"):
            return Cm(value), f"{value}cm"
        elif u in ("mm", "millimeter", "millimeters"):
            return Mm(value), f"{value}mm"
        elif u in ("pt", "point", "points"):
            return Pt(value), f"{value}pt"
        elif u in ("inch", "inches", "in"):
            return Inches(value), f"{value}in"
        else:
            return Cm(value), f"{value}cm"
    if fallback_inches is not None:
        return Inches(fallback_inches), f"{fallback_inches}in"
    return None, None


async def set_page_layout(
    filename: str,
    section_index: int = 0,
    orientation: str = None,
    margin_unit: str = "cm",
    margin_top: float = None,
    margin_bottom: float = None,
    margin_left: float = None,
    margin_right: float = None,
    page_width: float = None,
    page_height: float = None,
    columns: int = None,
    column_spacing_cm: float = None,
    page_width_inches: float = None,
    page_height_inches: float = None,
    margin_top_inches: float = None,
    margin_bottom_inches: float = None,
    margin_left_inches: float = None,
    margin_right_inches: float = None,
) -> str:
    """Set page layout for a document section supporting metric (cm, mm) and imperial (inch) units, plus multi-column layout.

    Args:
        filename: Path to the Word document.
        section_index: Section number (0-based). Default 0 = first section.
        orientation: "portrait" or "landscape".
        margin_unit: Unit for margins and dimensions: "cm", "mm", "inch", or "pt". Default "cm".
        margin_top: Top margin in specified unit (e.g. 4.0 for 4 cm).
        margin_bottom: Bottom margin in specified unit (e.g. 3.0 for 3 cm).
        margin_left: Left margin in specified unit (e.g. 4.0 for 4 cm).
        margin_right: Right margin in specified unit (e.g. 3.0 for 3 cm).
        page_width: Page width in specified unit (e.g. 21.0 for A4 cm).
        page_height: Page height in specified unit (e.g. 29.7 for A4 cm).
        columns: Number of text columns for this section (e.g. 2 for scientific/SINTA journals).
        column_spacing_cm: Spacing between columns in cm (default ~0.65 cm).
        page_width_inches: Page width in inches (legacy fallback).
        page_height_inches: Page height in inches (legacy fallback).
        margin_top_inches: Top margin in inches (legacy fallback).
        margin_bottom_inches: Bottom margin in inches (legacy fallback).
        margin_left_inches: Left margin in inches (legacy fallback).
        margin_right_inches: Right margin in inches (legacy fallback).
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            if section_index >= len(doc.sections):
                return f"Section {section_index} does not exist. Document has {len(doc.sections)} section(s)."

            section = doc.sections[section_index]
            changes = []

            if orientation is not None:
                if orientation.lower() == "landscape":
                    section.orientation = WD_ORIENT.LANDSCAPE
                    # Swap width/height if needed
                    if section.page_width < section.page_height:
                        section.page_width, section.page_height = section.page_height, section.page_width
                    changes.append("orientation=landscape")
                elif orientation.lower() == "portrait":
                    section.orientation = WD_ORIENT.PORTRAIT
                    if section.page_width > section.page_height:
                        section.page_width, section.page_height = section.page_height, section.page_width
                    changes.append("orientation=portrait")

            pw, pw_desc = _parse_unit_length(page_width, margin_unit, page_width_inches)
            if pw is not None:
                section.page_width = pw
                changes.append(f"width={pw_desc}")

            ph, ph_desc = _parse_unit_length(page_height, margin_unit, page_height_inches)
            if ph is not None:
                section.page_height = ph
                changes.append(f"height={ph_desc}")

            mt, mt_desc = _parse_unit_length(margin_top, margin_unit, margin_top_inches)
            if mt is not None:
                section.top_margin = mt
                changes.append(f"margin_top={mt_desc}")

            mb, mb_desc = _parse_unit_length(margin_bottom, margin_unit, margin_bottom_inches)
            if mb is not None:
                section.bottom_margin = mb
                changes.append(f"margin_bottom={mb_desc}")

            ml, ml_desc = _parse_unit_length(margin_left, margin_unit, margin_left_inches)
            if ml is not None:
                section.left_margin = ml
                changes.append(f"margin_left={ml_desc}")

            mr, mr_desc = _parse_unit_length(margin_right, margin_unit, margin_right_inches)
            if mr is not None:
                section.right_margin = mr
                changes.append(f"margin_right={mr_desc}")

            if columns is not None:
                cols_elem = section._sectPr.find(qn('w:cols'))
                if cols_elem is None:
                    cols_elem = OxmlElement('w:cols')
                    section._sectPr.append(cols_elem)
                cols_elem.set(qn('w:num'), str(columns))
                if column_spacing_cm is not None:
                    twips = int(column_spacing_cm * 567)
                    cols_elem.set(qn('w:space'), str(twips))
                changes.append(f"columns={columns}")

            doc.save(filename)
        return json.dumps({
            "success": True,
            "section": section_index,
            "changes": changes,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


async def add_header_footer(
    filename: str,
    section_index: int = 0,
    header_text: str = None,
    footer_text: str = None,
    header_alignment: str = "center",
    footer_alignment: str = "center",
) -> str:
    """Add header and/or footer text to a document section.

    Args:
        filename: Path to the Word document.
        section_index: Section number (0-based).
        header_text: Text to put in the header. None = don't change.
        footer_text: Text to put in the footer. None = don't change.
        header_alignment: "left", "center", "right", "justify".
        footer_alignment: "left", "center", "right", "justify".
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            if section_index >= len(doc.sections):
                return f"Section {section_index} does not exist."

            section = doc.sections[section_index]
            added = []

            if header_text is not None:
                header = section.header
                header.is_linked_to_previous = False
                # Clear existing and add new
                for p in header.paragraphs:
                    p.clear()
                p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
                p.text = header_text
                p.alignment = _ALIGN_MAP.get(header_alignment.lower(), WD_ALIGN_PARAGRAPH.CENTER)
                added.append("header")

            if footer_text is not None:
                footer = section.footer
                footer.is_linked_to_previous = False
                for p in footer.paragraphs:
                    p.clear()
                p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
                p.text = footer_text
                p.alignment = _ALIGN_MAP.get(footer_alignment.lower(), WD_ALIGN_PARAGRAPH.CENTER)
                added.append("footer")

            doc.save(filename)
        return json.dumps({"success": True, "added": added, "section": section_index})

    except Exception as e:
        return json.dumps({"error": str(e)})


def _add_field(paragraph, field_code: str):
    """Insert a Word field code (PAGE, NUMPAGES, etc.) into a paragraph."""
    run = paragraph.add_run()
    fld_char_begin = parse_xml(
        f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'
    )
    run._r.append(fld_char_begin)

    run2 = paragraph.add_run()
    instr = parse_xml(
        f'<w:instrText {nsdecls("w")} xml:space="preserve"> {field_code} </w:instrText>'
    )
    run2._r.append(instr)

    run3 = paragraph.add_run()
    fld_char_end = parse_xml(
        f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'
    )
    run3._r.append(fld_char_end)


def _parse_pos_str(pos_str: str):
    if not pos_str or pos_str.lower() in ("none", "null", "false"):
        return None, None
    parts = pos_str.lower().split("_")
    pos = parts[0]  # "header" or "footer"
    align = parts[1] if len(parts) > 1 else "center"
    return pos, align


def _apply_page_num_to_target(target, align_name: str, prefix: str, suffix: str, include_total: bool):
    target.is_linked_to_previous = False
    p = target.add_paragraph()
    p.alignment = _ALIGN_MAP.get(align_name.lower(), WD_ALIGN_PARAGRAPH.CENTER)
    if prefix:
        p.add_run(prefix)
    _add_field(p, "PAGE")
    if include_total:
        p.add_run(" / ")
        _add_field(p, "NUMPAGES")
    if suffix:
        p.add_run(suffix)


async def add_page_numbers(
    filename: str,
    section_index: int = 0,
    position: str = "footer",
    alignment: str = "center",
    prefix: str = "",
    suffix: str = "",
    include_total: bool = False,
    number_format: str = "decimal",
    restart_numbering: bool = False,
    start_at: int = 1,
    different_first_page: bool = False,
    first_page_position: str = "footer_center",
    subsequent_position: str = "header_right",
) -> str:
    """Add page numbers to a document supporting academic section numbering and different first page.

    Args:
        filename: Path to the Word document.
        section_index: Section number (0-based).
        position: "header" or "footer" (used when different_first_page is False).
        alignment: "left", "center", "right" (used when different_first_page is False).
        prefix: Text before page number (e.g. "Page ").
        suffix: Text after page number.
        include_total: If True, adds " of N" after the page number.
        number_format: "decimal", "lowerRoman", "upperRoman", "lowerLetter", "upperLetter".
        restart_numbering: If True, restart page numbering in this section.
        start_at: Starting page number if restart_numbering is True. Default 1.
        different_first_page: If True, enable different first page headers/footers for this section.
        first_page_position: Page number position on first page (e.g. "none", "footer_center", "footer_right").
        subsequent_position: Page number position on subsequent pages (e.g. "header_right", "footer_right").
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            if section_index >= len(doc.sections):
                return f"Section {section_index} does not exist."

            section = doc.sections[section_index]

            # Configure section page numbering in XML (<w:pgNumType>)
            sectPr = section._sectPr
            pgNumType = sectPr.find(qn('w:pgNumType'))
            if pgNumType is None:
                pgNumType = OxmlElement('w:pgNumType')
                sectPr.append(pgNumType)

            fmt_map = {
                "decimal": "decimal",
                "arabic": "decimal",
                "lowerroman": "lowerRoman",
                "upperroman": "upperRoman",
                "lower_roman": "lowerRoman",
                "upper_roman": "upperRoman",
                "roman": "lowerRoman",
                "lowerletter": "lowerLetter",
                "upperletter": "upperLetter",
            }
            fmt_val = fmt_map.get(str(number_format).lower(), str(number_format))
            pgNumType.set(qn('w:fmt'), fmt_val)

            if restart_numbering:
                pgNumType.set(qn('w:start'), str(start_at))
            elif qn('w:start') in pgNumType.attrib:
                del pgNumType.attrib[qn('w:start')]

            # Configure different first page
            if different_first_page:
                section.different_first_page_header_footer = True
                f_pos, f_align = _parse_pos_str(first_page_position)
                section.first_page_header.is_linked_to_previous = False
                section.first_page_footer.is_linked_to_previous = False
                if f_pos == "footer":
                    _apply_page_num_to_target(section.first_page_footer, f_align, prefix, suffix, include_total)
                elif f_pos == "header":
                    _apply_page_num_to_target(section.first_page_header, f_align, prefix, suffix, include_total)

                s_pos, s_align = _parse_pos_str(subsequent_position)
                section.header.is_linked_to_previous = False
                section.footer.is_linked_to_previous = False
                if s_pos == "header":
                    _apply_page_num_to_target(section.header, s_align, prefix, suffix, include_total)
                elif s_pos == "footer":
                    _apply_page_num_to_target(section.footer, s_align, prefix, suffix, include_total)
            else:
                target = section.header if position.lower() == "header" else section.footer
                _apply_page_num_to_target(target, alignment, prefix, suffix, include_total)

            doc.save(filename)
        return json.dumps({
            "success": True,
            "section_index": section_index,
            "number_format": number_format,
            "restart_numbering": restart_numbering,
            "start_at": start_at,
            "different_first_page": different_first_page,
            "position": position if not different_first_page else None,
            "first_page_position": first_page_position if different_first_page else None,
            "subsequent_position": subsequent_position if different_first_page else None,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


async def apply_document_preset(
    filename: str,
    preset: str = "indonesian_thesis",
) -> str:
    """Apply a complete document preset layout and section structure with 1 call.

    Presets:
    - 'indonesian_thesis' / 'academic': Kertas A4, margin 4-4-3-3 cm (Left 4, Top 4, Bottom 3, Right 3),
      Times New Roman 12 pt, spasi 1.5, setup 4 section otomatis (Cover tanpa nomor, Halaman Awal romawi i, ii di bawah tengah,
      Bab Isi arab 1, 2 beda halaman pertama (bawah tengah vs kanan atas), Daftar Pustaka arab lanjut).
    - 'business': Kertas A4, margin 2.54 cm (1 inch), Calibri 11 pt, spasi 1.15, nomor halaman kanan bawah.
    - 'legal': Kertas Legal/A4, margin 2.54 cm, Times New Roman 12 pt, spasi 2.0 (double), nomor halaman bawah tengah.
    - 'journal': Kertas A4, margin 2.0 cm, Times New Roman 10 pt, spasi 1.0.
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return json.dumps({"error": f"Document {filename} does not exist"})

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return json.dumps({"error": f"Cannot modify document: {err}"})

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            p_name = preset.lower().strip()

            if p_name in ("indonesian_thesis", "academic", "skripsi", "thesis"):
                # 1. Base Styles
                normal = doc.styles['Normal']
                normal.font.name = 'Times New Roman'
                normal.font.size = Pt(12)
                normal.paragraph_format.line_spacing = 1.5
                normal.paragraph_format.space_before = Pt(0)
                normal.paragraph_format.space_after = Pt(0)
                normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                normal.paragraph_format.first_line_indent = Cm(1.0)

                # Ensure 4 sections exist
                while len(doc.sections) < 4:
                    doc.add_section(WD_SECTION.NEW_PAGE)

                # Configure each section
                for idx, sec in enumerate(doc.sections):
                    sec.page_width = Cm(21.0)
                    sec.page_height = Cm(29.7)
                    sec.top_margin = Cm(4.0)
                    sec.left_margin = Cm(4.0)
                    sec.bottom_margin = Cm(3.0)
                    sec.right_margin = Cm(3.0)

                # Section 0: Cover (no page number)
                sec0 = doc.sections[0]
                sec0.different_first_page_header_footer = True
                sec0.header.is_linked_to_previous = False
                sec0.footer.is_linked_to_previous = False
                sec0.first_page_header.is_linked_to_previous = False
                sec0.first_page_footer.is_linked_to_previous = False

                # Section 1: Halaman Awal (lowerRoman, bottom center)
                sec1 = doc.sections[1]
                sectPr1 = sec1._sectPr
                pg1 = sectPr1.find(qn('w:pgNumType'))
                if pg1 is None:
                    pg1 = OxmlElement('w:pgNumType')
                    sectPr1.append(pg1)
                pg1.set(qn('w:fmt'), 'lowerRoman')
                pg1.set(qn('w:start'), '1')
                sec1.header.is_linked_to_previous = False
                sec1.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec1.footer, 'center', '', '', False)

                # Section 2: Bab Isi (decimal, restart at 1, different first page)
                sec2 = doc.sections[2]
                sectPr2 = sec2._sectPr
                pg2 = sectPr2.find(qn('w:pgNumType'))
                if pg2 is None:
                    pg2 = OxmlElement('w:pgNumType')
                    sectPr2.append(pg2)
                pg2.set(qn('w:fmt'), 'decimal')
                pg2.set(qn('w:start'), '1')
                sec2.different_first_page_header_footer = True
                sec2.first_page_header.is_linked_to_previous = False
                sec2.first_page_footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec2.first_page_footer, 'center', '', '', False)
                sec2.header.is_linked_to_previous = False
                sec2.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec2.header, 'right', '', '', False)

                # Section 3: Daftar Pustaka (decimal, continuous)
                sec3 = doc.sections[3]
                sectPr3 = sec3._sectPr
                pg3 = sectPr3.find(qn('w:pgNumType'))
                if pg3 is None:
                    pg3 = OxmlElement('w:pgNumType')
                    sectPr3.append(pg3)
                pg3.set(qn('w:fmt'), 'decimal')
                if qn('w:start') in pg3.attrib:
                    del pg3.attrib[qn('w:start')]
                sec3.header.is_linked_to_previous = False
                sec3.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec3.header, 'right', '', '', False)

                doc.save(filename)
                return json.dumps({
                    "success": True,
                    "preset": "indonesian_thesis",
                    "paper": "A4 (21 x 29.7 cm)",
                    "margins": "Top 4cm, Left 4cm, Bottom 3cm, Right 3cm",
                    "font": "Times New Roman 12 pt, 1.5 line spacing",
                    "sections": [
                        "Section 0: Cover (tanpa penomoran)",
                        "Section 1: Bagian Awal (romawi i, ii... bawah tengah)",
                        "Section 2: Bab Isi (angka 1, 2... beda halaman pertama: bawah tengah vs kanan atas)",
                        "Section 3: Daftar Pustaka / Lampiran (angka lanjut, kanan atas)",
                    ]
                })

            elif p_name == "business":
                normal = doc.styles['Normal']
                normal.font.name = 'Calibri'
                normal.font.size = Pt(11)
                normal.paragraph_format.line_spacing = 1.15
                normal.paragraph_format.space_after = Pt(6)

                for sec in doc.sections:
                    sec.page_width = Cm(21.0)
                    sec.page_height = Cm(29.7)
                    sec.top_margin = Cm(2.54)
                    sec.bottom_margin = Cm(2.54)
                    sec.left_margin = Cm(2.54)
                    sec.right_margin = Cm(2.54)

                sec = doc.sections[0]
                sec.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec.footer, 'right', 'Page ', '', True)

                doc.save(filename)
                return json.dumps({
                    "success": True,
                    "preset": "business",
                    "paper": "A4 (21 x 29.7 cm)",
                    "margins": "2.54 cm all around",
                    "font": "Calibri 11 pt, 1.15 line spacing, 6pt after",
                    "page_numbers": "Footer right (Page X of Y)",
                })

            elif p_name == "legal":
                normal = doc.styles['Normal']
                normal.font.name = 'Times New Roman'
                normal.font.size = Pt(12)
                normal.paragraph_format.line_spacing = 2.0
                normal.paragraph_format.space_after = Pt(0)

                for sec in doc.sections:
                    sec.top_margin = Cm(2.54)
                    sec.bottom_margin = Cm(2.54)
                    sec.left_margin = Cm(2.54)
                    sec.right_margin = Cm(2.54)

                sec = doc.sections[0]
                sec.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec.footer, 'center', '', '', False)

                doc.save(filename)
                return json.dumps({
                    "success": True,
                    "preset": "legal",
                    "margins": "2.54 cm all around",
                    "font": "Times New Roman 12 pt, 2.0 (Double) spacing",
                    "page_numbers": "Footer center",
                })

            elif p_name in ("sinta_journal", "jurnal_sinta", "sinta", "journal"):
                normal = doc.styles['Normal']
                normal.font.name = 'Times New Roman'
                normal.font.size = Pt(10)
                normal.paragraph_format.line_spacing = 1.0
                normal.paragraph_format.space_before = Pt(0)
                normal.paragraph_format.space_after = Pt(4)
                normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                normal.paragraph_format.first_line_indent = Cm(0.75)

                while len(doc.sections) < 2:
                    doc.add_section(WD_SECTION.CONTINUOUS)

                # Section 0: Title, Authors, Abstract (1 Column)
                sec0 = doc.sections[0]
                sec0.page_width = Cm(21.0)
                sec0.page_height = Cm(29.7)
                sec0.top_margin = Cm(2.5)
                sec0.left_margin = Cm(2.5)
                sec0.bottom_margin = Cm(2.0)
                sec0.right_margin = Cm(2.0)
                cols0 = sec0._sectPr.find(qn('w:cols'))
                if cols0 is None:
                    cols0 = OxmlElement('w:cols')
                    sec0._sectPr.append(cols0)
                cols0.set(qn('w:num'), '1')

                # Section 1: Body (2 Columns, 0.65 cm spacing)
                sec1 = doc.sections[1]
                sec1.page_width = Cm(21.0)
                sec1.page_height = Cm(29.7)
                sec1.top_margin = Cm(2.5)
                sec1.left_margin = Cm(2.5)
                sec1.bottom_margin = Cm(2.0)
                sec1.right_margin = Cm(2.0)
                cols1 = sec1._sectPr.find(qn('w:cols'))
                if cols1 is None:
                    cols1 = OxmlElement('w:cols')
                    sec1._sectPr.append(cols1)
                cols1.set(qn('w:num'), '2')
                cols1.set(qn('w:space'), str(int(0.65 * 567)))

                sec1.footer.is_linked_to_previous = False
                _apply_page_num_to_target(sec1.footer, 'center', '', '', False)

                doc.save(filename)
                return json.dumps({
                    "success": True,
                    "preset": "sinta_journal",
                    "paper": "A4 (21 x 29.7 cm)",
                    "margins": "Top 2.5cm, Left 2.5cm, Bottom 2.0cm, Right 2.0cm",
                    "font": "Times New Roman 10 pt, single spacing, justify",
                    "structure": [
                        "Section 0: Judul, Penulis, Abstrak (1 Kolom)",
                        "Section 1: Isi Artikel (2 Kolom, spasi 0.65 cm, nomor halaman bawah tengah)",
                    ]
                })

            elif p_name in ("makalah", "paper"):
                normal = doc.styles['Normal']
                normal.font.name = 'Times New Roman'
                normal.font.size = Pt(12)
                normal.paragraph_format.line_spacing = 1.5
                normal.paragraph_format.space_before = Pt(0)
                normal.paragraph_format.space_after = Pt(0)
                normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                normal.paragraph_format.first_line_indent = Cm(1.0)

                while len(doc.sections) < 2:
                    doc.add_section(WD_SECTION.NEW_PAGE)

                for sec in doc.sections:
                    sec.page_width = Cm(21.0)
                    sec.page_height = Cm(29.7)
                    sec.top_margin = Cm(4.0)
                    sec.left_margin = Cm(4.0)
                    sec.bottom_margin = Cm(3.0)
                    sec.right_margin = Cm(3.0)

                sec0 = doc.sections[0]
                sec0.different_first_page_header_footer = True
                sec0.header.is_linked_to_previous = False
                sec0.footer.is_linked_to_previous = False

                sec1 = doc.sections[1]
                sec1.header.is_linked_to_previous = False
                sec1.footer.is_linked_to_previous = False
                sectPr1 = sec1._sectPr
                pg1 = sectPr1.find(qn('w:pgNumType'))
                if pg1 is None:
                    pg1 = OxmlElement('w:pgNumType')
                    sectPr1.append(pg1)
                pg1.set(qn('w:fmt'), 'decimal')
                pg1.set(qn('w:start'), '1')
                _apply_page_num_to_target(sec1.header, 'right', '', '', False)

                doc.save(filename)
                return json.dumps({
                    "success": True,
                    "preset": "makalah",
                    "paper": "A4 (21 x 29.7 cm)",
                    "margins": "Top 4cm, Left 4cm, Bottom 3cm, Right 3cm",
                    "font": "Times New Roman 12 pt, 1.5 line spacing, justify",
                    "sections": [
                        "Section 0: Cover Makalah (tanpa nomor)",
                        "Section 1: Isi Makalah (angka 1, 2... kanan atas)",
                    ]
                })

            else:
                return json.dumps({"error": f"Unknown preset '{preset}'. Choose from: 'indonesian_thesis', 'makalah', 'sinta_journal', 'business', 'legal'."})

    except Exception as e:
        return json.dumps({"error": str(e)})


async def add_section_break(
    filename: str,
    break_type: str = "new_page",
) -> str:
    """Add a section break to the end of the document.

    Args:
        filename: Path to the Word document.
        break_type: "new_page", "continuous", "even_page", "odd_page".
    """
    from docx.enum.section import WD_SECTION

    type_map = {
        "new_page": WD_SECTION.NEW_PAGE,
        "continuous": WD_SECTION.CONTINUOUS,
        "even_page": WD_SECTION.EVEN_PAGE,
        "odd_page": WD_SECTION.ODD_PAGE,
    }

    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    if break_type not in type_map:
        return f"Invalid break_type: {break_type}. Use: {list(type_map.keys())}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            doc.add_section(type_map[break_type])
            doc.save(filename)
            total_sections = len(doc.sections)
        return json.dumps({
            "success": True,
            "break_type": break_type,
            "total_sections": total_sections,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


async def set_paragraph_spacing(
    filename: str,
    paragraph_index: int = None,
    start_paragraph: int = None,
    end_paragraph: int = None,
    space_before_pt: float = None,
    space_after_pt: float = None,
    line_spacing: float = None,
    line_spacing_rule: str = None,
    alignment: str = None,
    first_line_indent_cm: float = None,
) -> str:
    """Set paragraph spacing, alignment, and indentation for one or a range of paragraphs.

    Args:
        filename: Path to the Word document.
        paragraph_index: Single paragraph (0-based). Ignored if start/end given.
        start_paragraph: Start of range (inclusive, 0-based).
        end_paragraph: End of range (inclusive, 0-based).
        space_before_pt: Space before paragraph in points.
        space_after_pt: Space after paragraph in points.
        line_spacing: Line spacing value (depends on rule).
        line_spacing_rule: "single", "1.5_lines", "double", "exactly", "at_least", "multiple".
        alignment: "justify", "left", "center", "right".
        first_line_indent_cm: First-line indent in cm (e.g. 1.0 for skripsi/makalah, 0.75 for SINTA journal).
    """
    from docx.enum.text import WD_LINE_SPACING

    rule_map = {
        "single": WD_LINE_SPACING.SINGLE,
        "1.5_lines": WD_LINE_SPACING.ONE_POINT_FIVE,
        "double": WD_LINE_SPACING.DOUBLE,
        "exactly": WD_LINE_SPACING.EXACTLY,
        "at_least": WD_LINE_SPACING.AT_LEAST,
        "multiple": WD_LINE_SPACING.MULTIPLE,
    }

    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            total = len(doc.paragraphs)

            # Determine range
            if start_paragraph is not None and end_paragraph is not None:
                indices = range(start_paragraph, min(end_paragraph + 1, total))
            elif paragraph_index is not None:
                if paragraph_index >= total:
                    return f"Paragraph {paragraph_index} does not exist. Document has {total} paragraphs."
                indices = [paragraph_index]
            else:
                # Apply to all
                indices = range(total)

            count = 0
            for i in indices:
                p = doc.paragraphs[i]
                pf = p.paragraph_format
                if space_before_pt is not None:
                    pf.space_before = Pt(space_before_pt)
                if space_after_pt is not None:
                    pf.space_after = Pt(space_after_pt)
                if line_spacing_rule is not None and line_spacing_rule in rule_map:
                    pf.line_spacing_rule = rule_map[line_spacing_rule]
                if line_spacing is not None:
                    if line_spacing_rule in ("exactly", "at_least"):
                        pf.line_spacing = Pt(line_spacing)
                    else:
                        pf.line_spacing = line_spacing
                if alignment is not None and alignment.lower() in _ALIGN_MAP:
                    p.alignment = _ALIGN_MAP[alignment.lower()]
                if first_line_indent_cm is not None:
                    pf.first_line_indent = Cm(first_line_indent_cm)
                count += 1

            doc.save(filename)
        return json.dumps({
            "success": True,
            "paragraphs_affected": count,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


async def add_bookmark(
    filename: str,
    paragraph_index: int,
    bookmark_name: str,
) -> str:
    """Add a named bookmark at a paragraph.

    Args:
        filename: Path to the Word document.
        paragraph_index: Paragraph to bookmark (0-based).
        bookmark_name: Bookmark name (no spaces, alphanumeric + underscore).
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            if paragraph_index >= len(doc.paragraphs):
                return f"Paragraph {paragraph_index} does not exist."

            para = doc.paragraphs[paragraph_index]

            # Generate a unique bookmark ID
            import random
            bm_id = str(random.randint(1000, 99999))

            # Insert bookmarkStart before paragraph content
            bm_start = parse_xml(
                f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bookmark_name}"/>'
            )
            bm_end = parse_xml(
                f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>'
            )

            para._p.insert(0, bm_start)
            para._p.append(bm_end)

            doc.save(filename)
        return json.dumps({
            "success": True,
            "bookmark_name": bookmark_name,
            "paragraph_index": paragraph_index,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


async def add_watermark(
    filename: str,
    text: str = "TASLAK",
    font_size: int = 72,
    font_color: str = "C0C0C0",
    rotation: int = -45,
    section_index: int = 0,
) -> str:
    """Add a diagonal text watermark to a document.

    Args:
        filename: Path to the Word document.
        text: Watermark text (e.g. "DRAFT", "TASLAK", "GİZLİ").
        font_size: Font size in points.
        font_color: Hex color without # (e.g. "C0C0C0").
        rotation: Rotation angle in degrees (e.g. -45).
        section_index: Which section to add watermark to (0-based).
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    is_writeable, err = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {err}"

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            if section_index >= len(doc.sections):
                return f"Section {section_index} does not exist."

            section = doc.sections[section_index]
            header = section.header
            header.is_linked_to_previous = False

            # Build a VML shape for the watermark
            # The shape is placed in a paragraph inside the header
            watermark_xml = (
                f'<w:r {nsdecls("w", "v", "o", "w10")}>'
                f'  <w:rPr><w:noProof/></w:rPr>'
                f'  <w:pict>'
                f'    <v:shapetype id="_x0000_t136" coordsize="21600,21600"'
                f'      o:spt="136" adj="10800"'
                f'      path="m@7,l@8,m@5,21600l@6,21600e">'
                f'      <v:formulas>'
                f'        <v:f eqn="sum #0 0 10800"/>'
                f'        <v:f eqn="prod #0 2 1"/>'
                f'        <v:f eqn="sum 21600 0 @1"/>'
                f'        <v:f eqn="sum 0 0 @2"/>'
                f'        <v:f eqn="sum 21600 0 @3"/>'
                f'        <v:f eqn="if @0 @3 0"/>'
                f'        <v:f eqn="if @0 21600 @1"/>'
                f'        <v:f eqn="if @0 0 @2"/>'
                f'        <v:f eqn="if @0 @4 21600"/>'
                f'        <v:f eqn="mid @5 @6"/>'
                f'        <v:f eqn="mid @8 @5"/>'
                f'        <v:f eqn="mid @7 @8"/>'
                f'        <v:f eqn="mid @6 @7"/>'
                f'        <v:f eqn="sum @6 0 @5"/>'
                f'      </v:formulas>'
                f'      <v:path textpathok="t" o:connecttype="custom"'
                f'        o:connectlocs="@9,0;@10,10800;@11,21600;@12,10800"'
                f'        o:connectangles="270,180,90,0"/>'
                f'      <v:textpath on="t" fitshape="t"/>'
                f'      <v:handles><v:h position="#0,bottomRight" xrange="6629,14971"/></v:handles>'
                f'      <o:lock v:ext="edit" text="t" shapetype="t"/>'
                f'    </v:shapetype>'
                f'    <v:shape id="PowerPlusWaterMarkObject"'
                f'      o:spid="_x0000_s2049" type="#_x0000_t136"'
                f'      style="position:absolute;margin-left:0;margin-top:0;'
                f'width:500pt;height:150pt;rotation:{rotation};'
                f'z-index:-251658752;mso-position-horizontal:center;'
                f'mso-position-horizontal-relative:margin;'
                f'mso-position-vertical:center;'
                f'mso-position-vertical-relative:margin"'
                f'      o:allowincell="f"'
                f'      fillcolor="#{font_color}" stroked="f">'
                f'      <v:fill opacity=".5"/>'
                f'      <v:textpath style="font-family:&quot;Calibri&quot;;font-size:{font_size}pt"'
                f'        string="{text}"/>'
                f'      <w10:wrap anchorx="margin" anchory="margin"/>'
                f'    </v:shape>'
                f'  </w:pict>'
                f'</w:r>'
            )

            p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
            p._p.append(parse_xml(watermark_xml))

            doc.save(filename)
        return json.dumps({
            "success": True,
            "text": text,
            "font_size": font_size,
            "color": font_color,
            "rotation": rotation,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})
