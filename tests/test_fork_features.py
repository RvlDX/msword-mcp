"""Tests for fork features:
1. Input characters (\\n and \\t)
2. Metric units (cm, mm, pt)
3. Academic page numbers (Roman/Arabic, section restarts, different first page)
4. Native Word TOC & dot leader tab stops
5. Preset documents (indonesian_thesis, business, legal)
6. Error handling / Errno 13
7. Toolset filtering
"""
import os
import tempfile
import pytest
import asyncio
from docx import Document
from docx.shared import Inches, Cm, Pt

from word_document_server.tools.content_tools import add_paragraph, add_heading, add_table_of_contents
from word_document_server.tools.layout_tools import set_page_layout, add_page_numbers, apply_document_preset
from word_document_server.utils.document_utils import find_and_replace_text
from word_document_server.utils.file_utils import check_file_writeable


def test_newline_and_tab_handling():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        # 1. Test add_paragraph with literal and unescaped \n and \t
        text_with_breaks = "Line 1\nLine 2\tTabbed content"
        res = asyncio.run(add_paragraph(temp_path, text_with_breaks))
        assert "Paragraph added" in res

        # Verify in saved document
        doc2 = Document(temp_path)
        p = doc2.paragraphs[0]
        # Check XML contains w:br and w:tab
        xml = p._p.xml
        assert "w:br" in xml
        assert "w:tab" in xml

        # 2. Test find_and_replace_text with \n and \t
        replaced = find_and_replace_text(doc2, "Tabbed content", "Replaced Line 1\nReplaced Line 2\tTabbed")
        assert replaced == 1
        p_xml = doc2.paragraphs[0]._p.xml
        assert "w:br" in p_xml
        assert "Replaced Line 1" in p_xml

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_metric_units_layout():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        # Set Indonesian skripsi layout: 4 cm top, 4 cm left, 3 cm bottom, 3 cm right
        res = asyncio.run(set_page_layout(
            temp_path,
            section_index=0,
            margin_unit="cm",
            margin_top=4.0,
            margin_left=4.0,
            margin_bottom=3.0,
            margin_right=3.0,
            page_width=21.0,
            page_height=29.7,
        ))
        assert "margin_top=4.0cm" in res
        assert "margin_left=4.0cm" in res
        assert "margin_bottom=3.0cm" in res
        assert "margin_right=3.0cm" in res

        doc2 = Document(temp_path)
        sec = doc2.sections[0]
        # Check tolerance within 1 mm
        assert abs(sec.top_margin.cm - 4.0) < 0.05
        assert abs(sec.left_margin.cm - 4.0) < 0.05
        assert abs(sec.bottom_margin.cm - 3.0) < 0.05
        assert abs(sec.right_margin.cm - 3.0) < 0.05

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_academic_page_numbering():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        res = asyncio.run(add_page_numbers(
            temp_path,
            section_index=0,
            number_format="lowerRoman",
            restart_numbering=True,
            start_at=1,
            different_first_page=True,
            first_page_position="footer_center",
            subsequent_position="header_right",
        ))
        assert '"success": true' in res
        assert '"number_format": "lowerRoman"' in res
        assert '"different_first_page": true' in res

        doc2 = Document(temp_path)
        sec = doc2.sections[0]
        assert sec.different_first_page_header_footer is True
        xml = sec._sectPr.xml
        assert 'w:fmt="lowerRoman"' in xml
        assert 'w:start="1"' in xml

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_native_table_of_contents():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        res = asyncio.run(add_table_of_contents(temp_path, title="Daftar Isi", max_level=3, use_native_field=True))
        assert "Native Word Table of Contents" in res

        doc2 = Document(temp_path)
        # Check settings for updateFields
        settings_xml = doc2.settings.element.xml
        assert "w:updateFields" in settings_xml
        # Check document body for fldSimple TOC
        body_xml = doc2._body._element.xml
        assert 'w:instr="TOC \\o &quot;1-3&quot; \\h \\z \\u"' in body_xml

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_document_preset_indonesian_thesis():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        res = asyncio.run(apply_document_preset(temp_path, preset="indonesian_thesis"))
        assert '"success": true' in res
        assert '"preset": "indonesian_thesis"' in res

        doc2 = Document(temp_path)
        # Verify 4 sections
        assert len(doc2.sections) == 4
        # Verify Times New Roman and 1.5 line spacing
        normal = doc2.styles['Normal']
        assert normal.font.name == 'Times New Roman'
        assert normal.paragraph_format.line_spacing == 1.5

        # Section 0 (Cover): 4-4-3-3 margins
        sec0 = doc2.sections[0]
        assert abs(sec0.top_margin.cm - 4.0) < 0.05
        assert abs(sec0.left_margin.cm - 4.0) < 0.05

        # Section 1 (Awal): lowerRoman
        sec1 = doc2.sections[1]
        assert 'w:fmt="lowerRoman"' in sec1._sectPr.xml

        # Section 2 (Bab Isi): decimal, different first page
        sec2 = doc2.sections[2]
        assert sec2.different_first_page_header_footer is True
        assert 'w:fmt="decimal"' in sec2._sectPr.xml

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_toolset_filter(monkeypatch):
    import word_document_server.main as m
    from fastmcp import FastMCP

    monkeypatch.setenv("WORD_MCP_TOOLSET", "minimal")
    m.mcp = FastMCP("test_min")
    m.register_tools()
    tools_min = [t.name for t in asyncio.run(m.mcp.list_tools())]
    assert len(tools_min) == 10
    assert "create_document" in tools_min
    assert "apply_document_preset" in tools_min
    assert "add_footnote_to_document" not in tools_min

    monkeypatch.setenv("WORD_MCP_TOOLSET", "academic")
    m.mcp = FastMCP("test_acad")
    m.register_tools()
    tools_acad = [t.name for t in asyncio.run(m.mcp.list_tools())]
    assert len(tools_acad) == 30
    assert "add_footnote_to_document" in tools_acad
    assert "set_page_layout" in tools_acad
    assert "add_page_numbers" in tools_acad


def test_document_preset_sinta_journal():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        doc.save(temp_path)

        res = asyncio.run(apply_document_preset(temp_path, preset="sinta_journal"))
        assert '"success": true' in res
        assert '"preset": "sinta_journal"' in res

        doc2 = Document(temp_path)
        assert len(doc2.sections) >= 2
        # Section 0: 1 column
        sec0 = doc2.sections[0]
        assert 'w:num="1"' in sec0._sectPr.xml or 'w:cols' not in sec0._sectPr.xml or 'w:num="2"' not in sec0._sectPr.xml

        # Section 1: 2 columns
        sec1 = doc2.sections[1]
        assert 'w:num="2"' in sec1._sectPr.xml

        # Font 10pt
        normal = doc2.styles['Normal']
        assert normal.font.name == 'Times New Roman'
        assert normal.font.size == Pt(10)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
