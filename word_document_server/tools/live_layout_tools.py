"""COM-based layout tools for Microsoft Word.

These tools operate on documents currently open in Word via COM automation.
They provide layout, header/footer, spacing, bookmark, watermark, and section
management for files that are open (and locked) in Word.
"""

import json
import sys

from word_document_server.core.word_com import describe_error

# macOS JXA dispatch
_MAC_AVAILABLE = sys.platform == 'darwin'

# 1 inch = 72 points (avoid app.InchesToPoints which can fail on some COM setups)
_PTS_PER_INCH = 72.0


def _parse_live_unit_pts(value: Optional[float], unit: str = "cm", fallback_inches: Optional[float] = None):
    """Convert metric or imperial input to points for Word COM."""
    if value is not None:
        u = unit.lower().strip()
        if u in ("cm", "centimeter", "centimeters"):
            return value * (72.0 / 2.54), f"{value}cm"
        elif u in ("mm", "millimeter", "millimeters"):
            return value * (72.0 / 25.4), f"{value}mm"
        elif u in ("pt", "point", "points"):
            return float(value), f"{value}pt"
        elif u in ("inch", "inches", "in"):
            return value * 72.0, f"{value}in"
        else:
            return value * (72.0 / 2.54), f"{value}cm"
    if fallback_inches is not None:
        return fallback_inches * 72.0, f"{fallback_inches}in"
    return None, None


async def word_live_set_page_layout(
    filename: str = None,
    section_index: int = 1,
    orientation: str = None,
    margin_unit: str = "cm",
    margin_top: float = None,
    margin_bottom: float = None,
    margin_left: float = None,
    margin_right: float = None,
    page_width: float = None,
    page_height: float = None,
    page_width_inches: float = None,
    page_height_inches: float = None,
    margin_top_inches: float = None,
    margin_bottom_inches: float = None,
    margin_left_inches: float = None,
    margin_right_inches: float = None,
) -> str:
    """Set page layout for a section in an open Word document.

    Args:
        filename: Document name or path (None = active document).
        section_index: Section number (1-indexed, COM style). Default 1.
        orientation: "portrait" or "landscape".
        margin_unit: Unit for margins and dimensions: "cm", "mm", "inch", or "pt". Default "cm".
        margin_top: Top margin in specified unit.
        margin_bottom: Bottom margin in specified unit.
        margin_left: Left margin in specified unit.
        margin_right: Right margin in specified unit.
        page_width: Page width in specified unit.
        page_height: Page height in specified unit.
        page_width_inches: Page width in inches (legacy fallback).
        page_height_inches: Page height in inches (legacy fallback).
        margin_top_inches: Top margin in inches (legacy fallback).
        margin_bottom_inches: Bottom margin in inches (legacy fallback).
        margin_left_inches: Left margin in inches (legacy fallback).
        margin_right_inches: Right margin in inches (legacy fallback).

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_set_page_layout
        # Mac JXA page setup values are in points
        top_pts, _ = _parse_live_unit_pts(margin_top, margin_unit, margin_top_inches)
        bot_pts, _ = _parse_live_unit_pts(margin_bottom, margin_unit, margin_bottom_inches)
        left_pts, _ = _parse_live_unit_pts(margin_left, margin_unit, margin_left_inches)
        right_pts, _ = _parse_live_unit_pts(margin_right, margin_unit, margin_right_inches)
        w_pts, _ = _parse_live_unit_pts(page_width, margin_unit, page_width_inches)
        h_pts, _ = _parse_live_unit_pts(page_height, margin_unit, page_height_inches)

        return mac_set_page_layout(
            filename=filename, section_index=section_index, orientation=orientation,
            page_width=w_pts, page_height=h_pts,
            top_margin=top_pts, bottom_margin=bot_pts,
            left_margin=left_pts, right_margin=right_pts,
        )

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        if section_index < 1 or section_index > doc.Sections.Count:
            return json.dumps({
                "error": f"Section {section_index} out of range (1-{doc.Sections.Count})"
            })

        with undo_record(app, "MCP: Set Page Layout", doc):
            ps = doc.Sections(section_index).PageSetup
            changes = []

            if orientation is not None:
                # wdOrientPortrait=0, wdOrientLandscape=1
                if orientation.lower() == "landscape":
                    ps.Orientation = 1
                    changes.append("orientation=landscape")
                elif orientation.lower() == "portrait":
                    ps.Orientation = 0
                    changes.append("orientation=portrait")

            pw, pw_desc = _parse_live_unit_pts(page_width, margin_unit, page_width_inches)
            if pw is not None:
                ps.PageWidth = pw
                changes.append(f"width={pw_desc}")

            ph, ph_desc = _parse_live_unit_pts(page_height, margin_unit, page_height_inches)
            if ph is not None:
                ps.PageHeight = ph
                changes.append(f"height={ph_desc}")

            mt, mt_desc = _parse_live_unit_pts(margin_top, margin_unit, margin_top_inches)
            if mt is not None:
                ps.TopMargin = mt
                changes.append(f"margin_top={mt_desc}")

            mb, mb_desc = _parse_live_unit_pts(margin_bottom, margin_unit, margin_bottom_inches)
            if mb is not None:
                ps.BottomMargin = mb
                changes.append(f"margin_bottom={mb_desc}")

            ml, ml_desc = _parse_live_unit_pts(margin_left, margin_unit, margin_left_inches)
            if ml is not None:
                ps.LeftMargin = ml
                changes.append(f"margin_left={ml_desc}")

            mr, mr_desc = _parse_live_unit_pts(margin_right, margin_unit, margin_right_inches)
            if mr is not None:
                ps.RightMargin = mr
                changes.append(f"margin_right={mr_desc}")

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "section": section_index,
            "changes": changes,
        })

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_add_header_footer(
    filename: str = None,
    section_index: int = 1,
    header_text: str = None,
    footer_text: str = None,
    header_alignment: str = "center",
    footer_alignment: str = "center",
) -> str:
    """Add header and/or footer text to a section in an open Word document.

    Args:
        filename: Document name or path (None = active document).
        section_index: Section number (1-indexed).
        header_text: Text for the header. None = don't change.
        footer_text: Text for the footer. None = don't change.
        header_alignment: "left", "center", "right".
        footer_alignment: "left", "center", "right".

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_add_header_footer
        return mac_add_header_footer(filename=filename, section_index=section_index, header_text=header_text, footer_text=footer_text)

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        if section_index < 1 or section_index > doc.Sections.Count:
            return json.dumps({
                "error": f"Section {section_index} out of range (1-{doc.Sections.Count})"
            })

        with undo_record(app, "MCP: Add Header/Footer", doc):
            # Alignment map: 0=left, 1=center, 2=right
            align_map = {"left": 0, "center": 1, "right": 2}
            added = []

            # wdHeaderFooterPrimary = 1
            section = doc.Sections(section_index)

            if header_text is not None:
                hdr = section.Headers(1)  # Primary header
                hdr.Range.Text = header_text
                hdr.Range.ParagraphFormat.Alignment = align_map.get(
                    header_alignment.lower(), 1
                )
                added.append("header")

            if footer_text is not None:
                ftr = section.Footers(1)  # Primary footer
                ftr.Range.Text = footer_text
                ftr.Range.ParagraphFormat.Alignment = align_map.get(
                    footer_alignment.lower(), 1
                )
                added.append("footer")

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "section": section_index,
            "added": added,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_add_page_numbers(
    filename: str = None,
    section_index: int = 1,
    position: str = "footer",
    alignment: str = "center",
    prefix: str = "",
    suffix: str = "",
    include_total: bool = False,
) -> str:
    """Add page numbers to header or footer in an open Word document.

    Args:
        filename: Document name or path (None = active document).
        section_index: Section number (1-indexed).
        position: "header" or "footer".
        alignment: "left", "center", "right".
        prefix: Text before page number.
        suffix: Text after page number.
        include_total: If True, adds " / N" after page number.

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_add_page_numbers
        return mac_add_page_numbers(filename=filename, section_index=section_index, position=position, alignment=alignment, prefix=prefix, suffix=suffix, include_total=include_total)

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        if section_index < 1 or section_index > doc.Sections.Count:
            return json.dumps({
                "error": f"Section {section_index} out of range (1-{doc.Sections.Count})"
            })

        with undo_record(app, "MCP: Add Page Numbers", doc):
            # PageNumberAlignment: 0=left, 1=center, 2=right
            align_map = {"left": 0, "center": 1, "right": 2}
            pn_alignment = align_map.get(alignment.lower(), 1)

            section = doc.Sections(section_index)
            # wdHeaderFooterPrimary = 1
            target = section.Headers(1) if position == "header" else section.Footers(1)

            # Add page numbers via PageNumbers collection
            target.PageNumbers.Add(PageNumberAlignment=pn_alignment)

            # Add prefix/suffix/total by editing the range
            if prefix or suffix or include_total:
                rng = target.Range
                existing_text = rng.Text

                # Build the text with field codes
                # Clear and rebuild
                rng.Delete()

                if prefix:
                    rng.InsertAfter(prefix)

                # Insert PAGE field
                # wdFieldPage = 33
                rng.Collapse(0)  # wdCollapseEnd
                app.Selection.GoTo(What=1, Name=str(section_index))  # navigate to section
                field_range = target.Range
                field_range.Collapse(0)
                doc.Fields.Add(Range=field_range, Type=33)  # wdFieldPage

                if include_total:
                    end_range = target.Range
                    end_range.Collapse(0)
                    end_range.InsertAfter(" / ")
                    end_range = target.Range
                    end_range.Collapse(0)
                    doc.Fields.Add(Range=end_range, Type=26)  # wdFieldNumPages

                if suffix:
                    end_range = target.Range
                    end_range.Collapse(0)
                    end_range.InsertAfter(suffix)

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "section": section_index,
            "position": position,
            "alignment": alignment,
            "include_total": include_total,
        })

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_add_section_break(
    filename: str = None,
    break_type: str = "new_page",
) -> str:
    """Add a section break to an open Word document.

    Args:
        filename: Document name or path (None = active document).
        break_type: "new_page", "continuous", "even_page", "odd_page".

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_add_section_break
        return mac_add_section_break(filename=filename, break_type=break_type)

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        # wdSectionBreakNextPage=2, Continuous=3, EvenPage=4, OddPage=5
        type_map = {
            "new_page": 2,
            "continuous": 3,
            "even_page": 4,
            "odd_page": 5,
        }

        if break_type not in type_map:
            return json.dumps({
                "error": f"Invalid break_type: {break_type}. Use: {list(type_map.keys())}"
            })

        with undo_record(app, "MCP: Add Section Break", doc):
            # Insert at end of document
            end_pos = doc.Content.End - 1
            rng = doc.Range(end_pos, end_pos)
            rng.InsertBreak(Type=type_map[break_type])

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "break_type": break_type,
            "total_sections": doc.Sections.Count,
        })

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_set_paragraph_spacing(
    filename: str = None,
    paragraph_index: int = None,
    start_paragraph: int = None,
    end_paragraph: int = None,
    space_before_pt: float = None,
    space_after_pt: float = None,
    line_spacing: float = None,
    line_spacing_rule: str = None,
    keep_with_next: bool = None,
    keep_together: bool = None,
    alignment: str = None,
) -> str:
    """Set paragraph spacing and layout properties in an open Word document.

    Args:
        filename: Document name or path (None = active document).
        paragraph_index: Single paragraph (1-indexed). Ignored if start/end given.
        start_paragraph: Start of range (1-indexed, inclusive).
        end_paragraph: End of range (1-indexed, inclusive).
        space_before_pt: Space before paragraph in points.
        space_after_pt: Space after paragraph in points.
        line_spacing: Line spacing value IN POINTS (depends on rule).
            IMPORTANT: For "multiple" rule, value is in points, NOT a multiplier.
            Single spacing (1.0) = 12pt. So: 1.15 lines = 13.8pt, 1.5 lines = 18pt,
            2.0 lines = 24pt. Formula: desired_lines * 12 = points_value.
        line_spacing_rule: "single"(0), "1.5_lines"(1), "double"(2),
                           "at_least"(3), "exactly"(4), "multiple"(5).
        keep_with_next: Keep paragraph with next paragraph on same page (True/False).
        keep_together: Keep all lines of paragraph on same page (True/False).
        alignment: Paragraph alignment - "left"(0), "center"(1), "right"(2), "justify"(3).

    Returns:
        JSON with count of affected paragraphs.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_set_paragraph_spacing
        return mac_set_paragraph_spacing(filename=filename, paragraph_index=paragraph_index, start_paragraph=start_paragraph, end_paragraph=end_paragraph, space_before=space_before_pt, space_after=space_after_pt, line_spacing=line_spacing, keep_with_next=keep_with_next, keep_together=keep_together, alignment=alignment)

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        total = doc.Paragraphs.Count

        # wdLineSpacing rules
        rule_map = {
            "single": 0,
            "1.5_lines": 1,
            "double": 2,
            "at_least": 3,
            "exactly": 4,
            "multiple": 5,
        }

        # Determine range of paragraphs (1-indexed)
        if start_paragraph is not None and end_paragraph is not None:
            indices = range(max(1, start_paragraph), min(end_paragraph + 1, total + 1))
        elif paragraph_index is not None:
            if paragraph_index < 1 or paragraph_index > total:
                return json.dumps({
                    "error": f"paragraph_index {paragraph_index} out of range (1-{total})"
                })
            indices = [paragraph_index]
        else:
            indices = range(1, total + 1)

        with undo_record(app, "MCP: Set Paragraph Spacing", doc):
            count = 0
            for i in indices:
                pf = doc.Paragraphs(i).Format
                if space_before_pt is not None:
                    pf.SpaceBefore = space_before_pt
                if space_after_pt is not None:
                    pf.SpaceAfter = space_after_pt
                if line_spacing_rule is not None and line_spacing_rule in rule_map:
                    pf.LineSpacingRule = rule_map[line_spacing_rule]
                if line_spacing is not None:
                    pf.LineSpacing = line_spacing
                if keep_with_next is not None:
                    pf.KeepWithNext = keep_with_next
                if keep_together is not None:
                    pf.KeepTogether = keep_together
                if alignment is not None:
                    align_map = {"left": 0, "center": 1, "right": 2, "justify": 3}
                    if alignment in align_map:
                        pf.Alignment = align_map[alignment]
                count += 1

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "paragraphs_affected": count,
        })

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_add_bookmark(
    filename: str = None,
    paragraph_index: int = 1,
    bookmark_name: str = "",
) -> str:
    """Add a named bookmark at a paragraph in an open Word document.

    Args:
        filename: Document name or path (None = active document).
        paragraph_index: Paragraph to bookmark (1-indexed).
        bookmark_name: Bookmark name (alphanumeric + underscore, no spaces).

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        from word_document_server.core.word_mac import mac_add_bookmark
        return mac_add_bookmark(filename=filename, paragraph_index=paragraph_index, bookmark_name=bookmark_name)

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    if not bookmark_name:
        return json.dumps({"error": "bookmark_name is required"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        if paragraph_index < 1 or paragraph_index > doc.Paragraphs.Count:
            return json.dumps({
                "error": f"paragraph_index {paragraph_index} out of range (1-{doc.Paragraphs.Count})"
            })

        with undo_record(app, "MCP: Add Bookmark", doc):
            rng = doc.Paragraphs(paragraph_index).Range
            doc.Bookmarks.Add(bookmark_name, rng)

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "bookmark_name": bookmark_name,
            "paragraph_index": paragraph_index,
        })

    except Exception as e:
        return json.dumps({"error": describe_error(e)})


async def word_live_add_watermark(
    filename: str = None,
    text: str = "TASLAK",
    font_size: int = 72,
    font_color: str = "C0C0C0",
    rotation: int = -45,
    section_index: int = 1,
) -> str:
    """[Windows only] Add a diagonal text watermark to an open Word document.

    Args:
        filename: Document name or path (None = active document).
        text: Watermark text (e.g. "TASLAK", "DRAFT", "GİZLİ").
        font_size: Font size in points.
        font_color: Hex color without # (e.g. "C0C0C0").
        rotation: Rotation angle in degrees (e.g. -45).
        section_index: Section number (1-indexed).

    Returns:
        JSON with result info.
    """
    if _MAC_AVAILABLE:
        return json.dumps({"error": "word_live_add_watermark is not yet implemented on macOS"})

    if sys.platform != "win32":
        return json.dumps({"error": "Live layout tools are only available on Windows"})

    try:
        from word_document_server.core.word_com import get_word_app, find_document, undo_record

        app = get_word_app()
        doc = find_document(app, filename)

        if section_index < 1 or section_index > doc.Sections.Count:
            return json.dumps({
                "error": f"Section {section_index} out of range (1-{doc.Sections.Count})"
            })

        with undo_record(app, "MCP: Add Watermark", doc):
            section = doc.Sections(section_index)
            header = section.Headers(1)  # wdHeaderFooterPrimary

            # Parse color
            c = font_color.lstrip("#")
            r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            rgb_color = r + (g << 8) + (b << 16)

            # AddTextEffect(PresetTextEffect, Text, FontName, FontSize,
            #               FontBold, FontItalic, Left, Top)
            # COM requires positional args
            shape = header.Shapes.AddTextEffect(
                0, text, "Calibri", font_size, False, False, 0, 0
            )

            # Configure shape
            shape.Fill.ForeColor.RGB = rgb_color
            shape.Fill.Transparency = 0.5
            shape.Line.Visible = False  # msoFalse
            shape.Rotation = rotation
            shape.LockAspectRatio = False

            # Position relative to page center
            # msoRelativeHorizontalPositionMargin = 0
            # msoRelativeVerticalPositionMargin = 0
            shape.RelativeHorizontalPosition = 0
            shape.RelativeVerticalPosition = 0
            shape.Left = -999995  # wdShapeCenter (magic value for centering)
            shape.Top = -999995  # wdShapeCenter

            # Send behind text
            shape.WrapFormat.Type = 3  # wdWrapBehind
            shape.WrapFormat.AllowOverlap = True

        return json.dumps({
            "success": True,
            "document": doc.Name,
            "text": text,
            "font_size": font_size,
            "color": font_color,
            "rotation": rotation,
            "section": section_index,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": describe_error(e)})
