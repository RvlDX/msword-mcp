"""
Content tools for Word Document Server.

These tools add various types of content to Word documents,
including headings, paragraphs, tables, images, and page breaks.
"""
import os
from typing import List, Optional, Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from word_document_server.utils.document_utils import get_effective_text

from word_document_server.utils.file_utils import check_file_writeable, ensure_docx_extension, get_file_lock
from word_document_server.utils.document_utils import find_and_replace_text, insert_header_near_text, insert_numbered_list_near_text, insert_line_or_paragraph_near_text, replace_paragraph_block_below_header, replace_block_between_manual_anchors
from word_document_server.core.styles import ensure_heading_style, ensure_table_style


def populate_paragraph_text(
    paragraph,
    text: str,
    font_name: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[str] = None,
):
    """Parse text with newline (\\n) and tab (\\t) escape sequences, inserting <w:br/> and <w:tab/>."""
    if not text:
        return
    text = text.replace("\\r\\n", "\n").replace("\\r", "\n").replace("\\n", "\n").replace("\\t", "\t")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i > 0:
            run_br = paragraph.add_run()
            run_br.add_break()
        parts = line.split("\t")
        for j, part in enumerate(parts):
            if j > 0:
                run_tab = paragraph.add_run()
                run_tab.add_tab()
            if part:
                run = paragraph.add_run(part)
                if font_name:
                    run.font.name = font_name
                if font_size:
                    run.font.size = Pt(font_size)
                if bold is not None:
                    run.font.bold = bold
                if italic is not None:
                    run.font.italic = italic
                if color:
                    color_hex = color.lstrip('#')
                    run.font.color.rgb = RGBColor.from_string(color_hex)


async def add_heading(filename: str, text: str, level: int = 1,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, italic: Optional[bool] = None,
                      border_bottom: bool = False) -> str:
    """Add a heading to a Word document with optional formatting.

    Args:
        filename: Path to the Word document
        text: Heading text
        level: Heading level (1-9, where 1 is the highest level)
        font_name: Font family (e.g., 'Helvetica')
        font_size: Font size in points (e.g., 14)
        bold: True/False for bold text
        italic: True/False for italic text
        border_bottom: True to add bottom border (for section headers)
    """
    filename = ensure_docx_extension(filename)

    # Ensure level is converted to integer
    try:
        level = int(level)
    except (ValueError, TypeError):
        return "Invalid parameter: level must be an integer between 1 and 9"

    # Validate level range
    if level < 1 or level > 9:
        return f"Invalid heading level: {level}. Level must be between 1 and 9."

    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        # Suggest creating a copy
        return f"Cannot modify document: {error_message}. Consider creating a copy first or creating a new document."

    try:
        async with get_file_lock(filename):
            doc = Document(filename)

            # Ensure heading styles exist
            ensure_heading_style(doc)

            # Try to add heading with style
            try:
                heading = doc.add_heading(level=level)
                populate_paragraph_text(heading, text, font_name, font_size, bold, italic)
            except Exception as style_error:
                # If style-based approach fails, use direct formatting
                heading = doc.add_paragraph()
                heading.style = doc.styles['Normal']
                def_size = 16 if level == 1 else (14 if level == 2 else 12)
                populate_paragraph_text(
                    heading,
                    text,
                    font_name=font_name,
                    font_size=font_size or def_size,
                    bold=True if bold is None else bold,
                    italic=italic,
                )

            # Add bottom border if requested
            if border_bottom:
                pPr = heading._element.get_or_add_pPr()
                pBdr = OxmlElement('w:pBdr')

                bottom = OxmlElement('w:bottom')
                bottom.set(qn('w:val'), 'single')
                bottom.set(qn('w:sz'), '4')  # 0.5pt border
                bottom.set(qn('w:space'), '0')
                bottom.set(qn('w:color'), '000000')

                pBdr.append(bottom)
                pPr.append(pBdr)

            doc.save(filename)
        return f"Heading '{text}' (level {level}) added to {filename}"
    except Exception as e:
        return f"Failed to add heading: {str(e)}"


async def add_paragraph(filename: str, text: str, style: Optional[str] = None,
                        font_name: Optional[str] = None, font_size: Optional[int] = None,
                        bold: Optional[bool] = None, italic: Optional[bool] = None,
                        color: Optional[str] = None) -> str:
    """Add a paragraph to a Word document with optional formatting.

    Args:
        filename: Path to the Word document
        text: Paragraph text (supports \\n for line breaks and \\t for tabs)
        style: Optional paragraph style name
        font_name: Font family (e.g., 'Helvetica', 'Times New Roman')
        font_size: Font size in points (e.g., 14, 36)
        bold: True/False for bold text
        italic: True/False for italic text
        color: RGB color as hex string (e.g., '000000' for black)
    """
    filename = ensure_docx_extension(filename)

    if not os.path.exists(filename):
        return f"Document {filename} does not exist"

    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        # Suggest creating a copy
        return f"Cannot modify document: {error_message}. Consider creating a copy first or creating a new document."

    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            paragraph = doc.add_paragraph()
            populate_paragraph_text(paragraph, text, font_name, font_size, bold, italic, color)

            if style:
                try:
                    paragraph.style = style
                except KeyError:
                    # Style doesn't exist, use normal and report it
                    paragraph.style = doc.styles['Normal']
                    doc.save(filename)
                    return f"Style '{style}' not found, paragraph added with default style to {filename}"

            doc.save(filename)
        return f"Paragraph added to {filename}"
    except Exception as e:
        return f"Failed to add paragraph: {str(e)}"


async def add_table(filename: str, rows: int, cols: int, data: Optional[List[List[str]]] = None) -> str:
    """Add a table to a Word document.
    
    Args:
        filename: Path to the Word document
        rows: Number of rows in the table
        cols: Number of columns in the table
        data: Optional 2D array of data to fill the table
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        # Suggest creating a copy
        return f"Cannot modify document: {error_message}. Consider creating a copy first or creating a new document."
    
    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            table = doc.add_table(rows=rows, cols=cols)

            # Try to set the table style
            try:
                table.style = 'Table Grid'
            except KeyError:
                # If style doesn't exist, add basic borders
                pass

            # Fill table with data if provided
            if data:
                for i, row_data in enumerate(data):
                    if i >= rows:
                        break
                    for j, cell_text in enumerate(row_data):
                        if j >= cols:
                            break
                        table.cell(i, j).text = str(cell_text)

            doc.save(filename)
        return f"Table ({rows}x{cols}) added to {filename}"
    except Exception as e:
        return f"Failed to add table: {str(e)}"


async def add_picture(filename: str, image_path: str, width: Optional[float] = None) -> str:
    """Add an image to a Word document.
    
    Args:
        filename: Path to the Word document
        image_path: Path to the image file
        width: Optional width in inches (proportional scaling)
    """
    filename = ensure_docx_extension(filename)
    
    # Validate document existence
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Get absolute paths for better diagnostics
    abs_filename = os.path.abspath(filename)
    abs_image_path = os.path.abspath(image_path)
    
    # Validate image existence with improved error message
    if not os.path.exists(abs_image_path):
        return f"Image file not found: {abs_image_path}"
    
    # Check image file size
    try:
        image_size = os.path.getsize(abs_image_path) / 1024  # Size in KB
        if image_size <= 0:
            return f"Image file appears to be empty: {abs_image_path} (0 KB)"
    except Exception as size_error:
        return f"Error checking image file: {str(size_error)}"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(abs_filename)
    if not is_writeable:
        return f"Cannot modify document: {error_message}. Consider creating a copy first or creating a new document."
    
    try:
        async with get_file_lock(abs_filename):
            doc = Document(abs_filename)
            # Additional diagnostic info
            diagnostic = f"Attempting to add image ({abs_image_path}, {image_size:.2f} KB) to document ({abs_filename})"

            try:
                if width:
                    doc.add_picture(abs_image_path, width=Inches(width))
                else:
                    doc.add_picture(abs_image_path)
                doc.save(abs_filename)
            except Exception as inner_error:
                # More detailed error for the specific operation
                error_type = type(inner_error).__name__
                error_msg = str(inner_error)
                return f"Failed to add picture: {error_type} - {error_msg or 'No error details available'}\nDiagnostic info: {diagnostic}"
        return f"Picture {image_path} added to {filename}"
    except Exception as outer_error:
        # Fallback error handling
        error_type = type(outer_error).__name__
        error_msg = str(outer_error)
        return f"Document processing error: {error_type} - {error_msg or 'No error details available'}"


async def add_page_break(filename: str) -> str:
    """Add a page break to the document.
    
    Args:
        filename: Path to the Word document
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {error_message}. Consider creating a copy first."
    
    try:
        async with get_file_lock(filename):
            doc = Document(filename)
            doc.add_page_break()
            doc.save(filename)
        return f"Page break added to {filename}."
    except Exception as e:
        return f"Failed to add page break: {str(e)}"


async def add_table_of_contents(
    filename: str,
    title: str = "Table of Contents",
    max_level: int = 3,
    use_native_field: bool = True,
    tab_leader_dots: bool = True,
    dot_leader_tab_cm: float = 14.5,
) -> str:
    """Add a native Word Table of Contents (TOC) field or right tab stop with dot leader.
    
    Args:
        filename: Path to the Word document
        title: Optional title for the table of contents
        max_level: Maximum heading level to include (1-9)
        use_native_field: If True (default), inserts native Word XML TOC field (<w:fldSimple w:instr="TOC ..."/>)
                         and enables auto-update on open (<w:updateFields/>).
        tab_leader_dots: If use_native_field=False, generates explicit heading lines with right tab stops and dot leader.
        dot_leader_tab_cm: Position of right tab stop with dot leader in cm (default: 14.5 cm).
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {error_message}. Consider creating a copy first."
    
    try:
        # Ensure max_level is within valid range
        max_level = max(1, min(max_level, 9))

        async with get_file_lock(filename):
            doc = Document(filename)

            if use_native_field:
                # Enable updateFields in settings.xml so Word updates TOC automatically on open
                settings = doc.settings.element
                if settings.find(qn('w:updateFields')) is None:
                    settings.append(parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>'))

                if title:
                    doc.add_heading(title, level=1)

                p_toc = doc.add_paragraph()
                fld_xml = (
                    f'<w:fldSimple {nsdecls("w")} w:instr="TOC \\o &quot;1-{max_level}&quot; \\h \\z \\u">'
                    f'<w:r><w:rPr><w:noProof/></w:rPr><w:t>Daftar Isi (diperbarui otomatis oleh Word)</w:t></w:r>'
                    f'</w:fldSimple>'
                )
                p_toc._p.append(parse_xml(fld_xml))
                doc.add_page_break()
                doc.save(filename)
                return f"Native Word Table of Contents (levels 1-{max_level}) added to {filename} with auto-update enabled."

            # Alternative: Dot Leader Tab Stop
            headings = []
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.style and paragraph.style.name.startswith('Heading '):
                    try:
                        level = int(paragraph.style.name.split(' ')[1])
                        if level <= max_level:
                            headings.append({
                                'level': level,
                                'text': get_effective_text(paragraph),
                                'position': i
                            })
                    except (ValueError, IndexError):
                        pass

            if not headings:
                return f"No headings found in document {filename}. Table of contents not created."

            if title:
                doc.add_heading(title, level=1)

            for heading in headings:
                p = doc.add_paragraph()
                if tab_leader_dots:
                    p.paragraph_format.tab_stops.add_tab_stop(
                        Cm(dot_leader_tab_cm), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS
                    )
                indent = '    ' * (heading['level'] - 1)
                p.add_run(f"{indent}{heading['text']}\t")

            doc.add_page_break()
            doc.save(filename)

        return f"Table of contents with {len(headings)} entries (dot leader tab) added to {filename}"
    except Exception as e:
        return f"Failed to add table of contents: {str(e)}"


async def delete_paragraph(filename: str, paragraph_index: int) -> str:
    """Delete a paragraph from a document.
    
    Args:
        filename: Path to the Word document
        paragraph_index: Index of the paragraph to delete (0-based)
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {error_message}. Consider creating a copy first."
    
    try:
        async with get_file_lock(filename):
            doc = Document(filename)

            # Validate paragraph index
            if paragraph_index < 0 or paragraph_index >= len(doc.paragraphs):
                return f"Invalid paragraph index. Document has {len(doc.paragraphs)} paragraphs (0-{len(doc.paragraphs)-1})."

            # Delete the paragraph (by removing its content and setting it empty)
            # Note: python-docx doesn't support true paragraph deletion, this is a workaround
            paragraph = doc.paragraphs[paragraph_index]
            p = paragraph._p
            p.getparent().remove(p)

            doc.save(filename)
        return f"Paragraph at index {paragraph_index} deleted successfully."
    except Exception as e:
        return f"Failed to delete paragraph: {str(e)}"


async def search_and_replace(filename: str, find_text: str, replace_text: str) -> str:
    """Search for text and replace all occurrences.
    
    Args:
        filename: Path to the Word document
        find_text: Text to search for
        replace_text: Text to replace with
    """
    filename = ensure_docx_extension(filename)
    
    if not os.path.exists(filename):
        return f"Document {filename} does not exist"
    
    # Check if file is writeable
    is_writeable, error_message = check_file_writeable(filename)
    if not is_writeable:
        return f"Cannot modify document: {error_message}. Consider creating a copy first."
    
    try:
        async with get_file_lock(filename):
            doc = Document(filename)

            # Perform find and replace
            count = find_and_replace_text(doc, find_text, replace_text)

            if count > 0:
                doc.save(filename)
        if count > 0:
            return f"Replaced {count} occurrence(s) of '{find_text}' with '{replace_text}'."
        else:
            return f"No occurrences of '{find_text}' found."
    except Exception as e:
        return f"Failed to search and replace: {str(e)}"

async def insert_header_near_text_tool(filename: str, target_text: str = None, header_title: str = "", position: str = 'after', header_style: str = 'Heading 1', target_paragraph_index: int = None) -> str:
    """Insert a header (with specified style) before or after the target paragraph. Specify by text or paragraph index."""
    async with get_file_lock(filename):
        return insert_header_near_text(filename, target_text, header_title, position, header_style, target_paragraph_index)

async def insert_numbered_list_near_text_tool(filename: str, target_text: str = None, list_items: list = None, position: str = 'after', target_paragraph_index: int = None, bullet_type: str = 'bullet') -> str:
    """Insert a bulleted or numbered list before or after the target paragraph. Specify by text or paragraph index."""
    async with get_file_lock(filename):
        return insert_numbered_list_near_text(filename, target_text, list_items, position, target_paragraph_index, bullet_type)

async def insert_line_or_paragraph_near_text_tool(filename: str, target_text: str = None, line_text: str = "", position: str = 'after', line_style: str = None, target_paragraph_index: int = None) -> str:
    """Insert a new line or paragraph (with specified or matched style) before or after the target paragraph. Specify by text or paragraph index."""
    async with get_file_lock(filename):
        return insert_line_or_paragraph_near_text(filename, target_text, line_text, position, line_style, target_paragraph_index)

async def replace_paragraph_block_below_header_tool(filename: str, header_text: str, new_paragraphs: list, detect_block_end_fn=None) -> str:
    """Reemplaza el bloque de párrafos debajo de un encabezado, evitando modificar TOC."""
    async with get_file_lock(filename):
        return replace_paragraph_block_below_header(filename, header_text, new_paragraphs, detect_block_end_fn)

async def replace_block_between_manual_anchors_tool(filename: str, start_anchor_text: str, new_paragraphs: list, end_anchor_text: str = None, match_fn=None, new_paragraph_style: str = None) -> str:
    """Replace all content between start_anchor_text and end_anchor_text (or next logical header if not provided)."""
    async with get_file_lock(filename):
        return replace_block_between_manual_anchors(filename, start_anchor_text, new_paragraphs, end_anchor_text, match_fn, new_paragraph_style)
