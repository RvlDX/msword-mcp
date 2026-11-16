"""
Unit tests for academic writing tools in word_document_server.tools.academic_tools.
"""

import json
import os
import tempfile
import pytest
import asyncio
from docx import Document

from word_document_server.tools.academic_tools import (
    setup_thesis_structure,
    audit_academic_formatting,
    annotate_audit_findings,
    extract_citations_and_bibliography,
)


def test_setup_thesis_structure():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        res_str = asyncio.run(setup_thesis_structure(
            filename=temp_path,
            title="Analisis Pengaruh Penerapan Kecerdasan Buatan Terhadap Kinerja Mahasiswa",
            author="Budi Santoso",
            nim="12345678",
            institution="Universitas Indonesia",
            faculty="Fakultas Ilmu Komputer",
            department="Teknik Informatika",
            city="Jakarta",
            year="2026",
            preset="indonesian_thesis",
        ))
        data = json.loads(res_str)
        assert data.get("success") is True
        assert "structure" in data

        doc = Document(temp_path)
        # Check sections exist
        assert len(doc.sections) >= 4

        # Check full text contains major chapter titles
        full_text = "\n".join([p.text for p in doc.paragraphs])
        assert "BAB I PENDAHULUAN" in full_text
        assert "BAB II TINJAUAN PUSTAKA" in full_text
        assert "BAB III METODE PENELITIAN" in full_text
        assert "BAB IV HASIL DAN PEMBAHASAN" in full_text
        assert "BAB V PENUTUP" in full_text
        assert "DAFTAR PUSTAKA" in full_text

        # Verify cover content
        assert "BUDI SANTOSO" in full_text.upper()
        assert "12345678" in full_text

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_audit_academic_formatting():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        # First generate structured thesis
        asyncio.run(setup_thesis_structure(
            filename=temp_path,
            title="Sistem Informasi Akademik",
            author="Ahmad",
            nim="11223344",
        ))

        audit_str = asyncio.run(audit_academic_formatting(temp_path))
        audit = json.loads(audit_str)

        assert audit.get("success") is True
        assert audit.get("compliance_score") >= 80
        assert "passed_checks" in audit
        assert len(audit.get("passed_checks")) > 0

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_extract_citations_and_bibliography():
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name

    try:
        doc = Document()
        p1 = doc.add_paragraph("Kecerdasan buatan berkembang sangat pesat dalam dekade terakhir (Sugiyono, 2021).")
        p2 = doc.add_paragraph("Menurut Kotler (2018), kepuasan pengguna merupakan indikator keberhasilan sistem.")
        p3 = doc.add_paragraph("Studi lain menyebutkan efisiensi model transformer (Vaswani, 2017).")

        p_bib_head = doc.add_paragraph("DAFTAR PUSTAKA")
        p_bib1 = doc.add_paragraph("Sugiyono. (2021). Metode Penelitian Kuantitatif, Kualitatif, dan R&D. Alfabeta.")
        p_bib2 = doc.add_paragraph("Kotler, P., & Keller, K. L. (2018). Marketing Management (15th ed.). Pearson.")
        # Vaswani is deliberately missing from bib

        doc.save(temp_path)

        res_str = asyncio.run(extract_citations_and_bibliography(temp_path))
        data = json.loads(res_str)

        assert data.get("success") is True
        assert data.get("total_citations_found") >= 2
        assert data.get("total_bibliography_entries") == 2

        # Sugiyono and Kotler should match
        matched_text = " ".join(data.get("matched_citations", []))
        assert "Sugiyono" in matched_text or "2021" in matched_text

        # Vaswani should be reported missing
        missing_text = " ".join(data.get("missing_from_bibliography", []))
        assert "Vaswani" in missing_text

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
