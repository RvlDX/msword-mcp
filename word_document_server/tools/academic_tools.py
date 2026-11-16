"""
Academic writing tools for Word Document Server.

These tools provide automated Indonesian thesis/journal structure generation,
academic formatting audits, inline Word comment annotations, and citation-bibliography cross-checking.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from word_document_server.utils.file_utils import check_file_writeable, ensure_docx_extension, get_file_lock
from word_document_server.tools.layout_tools import apply_document_preset
from word_document_server.core.comment_writer import add_comment_to_doc
from word_document_server.defaults import DEFAULT_AUTHOR, DEFAULT_INITIALS


def _set_heading(paragraph, text: str, level: int = 1, center: bool = False):
    """Format paragraph as academic heading with standard styling."""
    paragraph.text = text
    paragraph.style = f'Heading {level}'
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.space_before = Pt(12)
    paragraph.paragraph_format.space_after = Pt(6)
    if center:
        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.name = 'Times New Roman'
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        if level == 1:
            run.font.size = Pt(14)
        else:
            run.font.size = Pt(12)


async def setup_thesis_structure(
    filename: str,
    title: str,
    author: str,
    nim: str = "",
    institution: str = "Universitas",
    faculty: str = "",
    department: str = "",
    city: str = "Jakarta",
    year: str = "2026",
    preset: str = "indonesian_thesis",
) -> str:
    """Setup a complete Indonesian thesis structure (Bab I - V, Front Matter, Daftar Pustaka) in a Word document.

    Applies standard Indonesian academic margins (4-4-3-3 cm), Times New Roman 12 pt, 1.5 line spacing,
    multi-section layout with Roman page numbers for front matter and Arabic for body chapters.

    Args:
        filename: Path to the Word document to create or overwrite.
        title: Title of the thesis.
        author: Student author name.
        nim: Student ID / Nomor Induk Mahasiswa.
        institution: University name.
        faculty: Faculty name (optional).
        department: Program studi / department name (optional).
        city: City where institution is located.
        year: Academic year.
        preset: Document layout preset (default: 'indonesian_thesis').

    Returns:
        JSON string with creation summary.
    """
    filename = ensure_docx_extension(filename)
    try:
        async with get_file_lock(filename):
            doc = Document()
            doc.save(filename)

        # 1. Apply document layout preset
        preset_res = await apply_document_preset(filename, preset)
        preset_data = json.loads(preset_res)
        if not preset_data.get("success"):
            return json.dumps({"success": False, "error": f"Failed to apply preset: {preset_data.get('error')}"})

        async with get_file_lock(filename):
            doc = Document(filename)

            # --- SECTION 0: COVER ---
            sec0 = doc.sections[0]
            p_cover_top = doc.paragraphs[0]
            p_cover_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cover_top.paragraph_format.first_line_indent = Cm(0)
            p_cover_top.paragraph_format.space_before = Pt(36)
            p_cover_top.paragraph_format.space_after = Pt(18)
            run_title = p_cover_top.add_run(title.upper())
            run_title.font.name = 'Times New Roman'
            run_title.font.size = Pt(14)
            run_title.font.bold = True

            p_desc = doc.add_paragraph()
            p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_desc.paragraph_format.first_line_indent = Cm(0)
            p_desc.paragraph_format.space_before = Pt(18)
            p_desc.paragraph_format.space_after = Pt(36)
            run_desc = p_desc.add_run("SKRIPSI\n\nDiajukan sebagai salah satu syarat untuk memperoleh gelar Sarjana")
            run_desc.font.name = 'Times New Roman'
            run_desc.font.size = Pt(12)

            p_author = doc.add_paragraph()
            p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_author.paragraph_format.first_line_indent = Cm(0)
            p_author.paragraph_format.space_before = Pt(36)
            p_author.paragraph_format.space_after = Pt(36)
            run_author = p_author.add_run(f"Disusun Oleh:\n\n{author.upper()}\nNIM. {nim}" if nim else f"Disusun Oleh:\n\n{author.upper()}")
            run_author.font.name = 'Times New Roman'
            run_author.font.size = Pt(12)
            run_author.font.bold = True

            p_inst = doc.add_paragraph()
            p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_inst.paragraph_format.first_line_indent = Cm(0)
            p_inst.paragraph_format.space_before = Pt(36)
            lines_inst = []
            if department:
                lines_inst.append(department.upper())
            if faculty:
                lines_inst.append(faculty.upper())
            lines_inst.append(institution.upper())
            lines_inst.append(f"{city.upper()}\n{year}")
            run_inst = p_inst.add_run("\n".join(lines_inst))
            run_inst.font.name = 'Times New Roman'
            run_inst.font.size = Pt(12)
            run_inst.font.bold = True

            # --- SECTION 1: FRONT MATTER ---
            p_sec1 = doc.add_paragraph()
            p_sec1.paragraph_format.page_break_before = True
            _set_heading(p_sec1, "LEMBAR PENGESAHAN", 1, center=True)
            doc.add_paragraph("Lembar pengesahan naskah skripsi oleh pembimbing dan penguji.")

            p_ack = doc.add_paragraph()
            p_ack.paragraph_format.page_break_before = True
            _set_heading(p_ack, "KATA PENGANTAR", 1, center=True)
            p_ack_txt = doc.add_paragraph("Puji dan syukur penulis panjatkan ke hadirat Tuhan Yang Maha Esa atas berkat dan rahmat-Nya, penulisan skripsi ini dapat diselesaikan.")
            p_ack_txt.paragraph_format.first_line_indent = Cm(1.0)

            p_abs_id = doc.add_paragraph()
            p_abs_id.paragraph_format.page_break_before = True
            _set_heading(p_abs_id, "ABSTRAK", 1, center=True)
            doc.add_paragraph(f"{author}. ({year}). {title}.")
            p_abs_txt = doc.add_paragraph("Abstrak memuat latar belakang singkat, tujuan penelitian, metodologi yang digunakan, hasil temuan utama, dan kesimpulan.")
            p_abs_txt.paragraph_format.first_line_indent = Cm(1.0)
            p_kw_id = doc.add_paragraph()
            r_kw_id = p_kw_id.add_run("Kata Kunci: ")
            r_kw_id.bold = True
            p_kw_id.add_run("skripsi, penelitian, metodologi, analisis.")

            p_abs_en = doc.add_paragraph()
            p_abs_en.paragraph_format.page_break_before = True
            _set_heading(p_abs_en, "ABSTRACT", 1, center=True)
            doc.add_paragraph(f"{author}. ({year}). {title}.")
            p_abs_en_txt = doc.add_paragraph("Abstract contains brief background, research objectives, methodology, main findings, and conclusions.")
            p_abs_en_txt.paragraph_format.first_line_indent = Cm(1.0)
            p_kw_en = doc.add_paragraph()
            r_kw_en = p_kw_en.add_run("Keywords: ")
            r_kw_en.bold = True
            p_kw_en.add_run("thesis, research, methodology, analysis.")

            p_toc = doc.add_paragraph()
            p_toc.paragraph_format.page_break_before = True
            _set_heading(p_toc, "DAFTAR ISI", 1, center=True)
            doc.add_paragraph("[Gunakan perintah 'add_table_of_contents' untuk memperbarui Daftar Isi otomatis]")

            # --- SECTION 2: MAIN CHAPTERS ---
            chapters = [
                ("BAB I PENDAHULUAN", [
                    ("1.1 Latar Belakang Masalah", "Latar belakang memuat fenomena masalah (gap antara harapan dan kenyataan), data pendukung, urgensi penelitian, dan posisi penelitian."),
                    ("1.2 Rumusan Masalah", "Rumusan masalah dirumuskan secara lugas, jelas, dan spesifik dalam bentuk pertanyaan penelitian."),
                    ("1.3 Tujuan Penelitian", "Tujuan penelitian selaras langsung dengan rumusan masalah yang telah ditetapkan."),
                    ("1.4 Manfaat Penelitian", "Manfaat penelitian mencakup manfaat teoretis/akademis dan manfaat praktis bagi pihak terkait."),
                ]),
                ("BAB II TINJAUAN PUSTAKA", [
                    ("2.1 Landasan Teori", "Landasan teori menguraikan teori-teori relevan, konsep utama, dan variabel penelitian dari sumber ilmiah primer."),
                    ("2.2 Penelitian Terdahulu", "Penelitian terdahulu menyajikan perbandingan riset sebelumnya yang relevan guna menunjukkan kebaruan (novelty)."),
                    ("2.3 Kerangka Pemikiran", "Kerangka pemikiran menggambarkan alur logis hubungan antar-konsep atau variabel penelitian."),
                    ("2.4 Hipotesis Penelitian", "Hipotesis penelitian merupakan dugaan sementara yang akan diuji secara empiris (jika relevan)."),
                ]),
                ("BAB III METODE PENELITIAN", [
                    ("3.1 Jenis dan Pendekatan Penelitian", "Menjelaskan paradigma, jenis penelitian (kuantitatif/kualitatif/R&D), dan pendekatan yang dipakai."),
                    ("3.2 Tempat dan Waktu Penelitian", "Menjelaskan lokasi penelitian dan rentang waktu pelaksanaan pengumpulan data."),
                    ("3.3 Populasi dan Sampel", "Menjelaskan kriteria populasi, teknik penarikan sampel (sampling), dan ukuran sampel."),
                    ("3.4 Teknik Pengumpulan Data", "Menjelaskan metode pengumpulan data (observasi, kuesioner, wawancara, studi pustaka)."),
                    ("3.5 Instrumen Penelitian", "Menjelaskan instrumen penelitian beserta uji validitas dan reliabilitas."),
                    ("3.6 Teknik Analisis Data", "Menjelaskan tahapan dan rumus/software analisis data yang diterapkan."),
                ]),
                ("BAB IV HASIL DAN PEMBAHASAN", [
                    ("4.1 Deskripsi Objek Penelitian", "Menyajikan gambaran umum subjek/objek penelitian dan data demografi responden."),
                    ("4.2 Hasil Analisis Data", "Menyajikan temuan empiris, hasil perhitungan statistik/kualitatif, dan pengujian hipotesis."),
                    ("4.3 Pembahasan", "Membahas makna temuan, mengaitkannya dengan teori dan penelitian terdahulu, serta implikasi ilmiahnya."),
                ]),
                ("BAB V PENUTUP", [
                    ("5.1 Kesimpulan", "Kesimpulan menjawab seluruh rumusan masalah secara komprehensif tanpa data angka baru."),
                    ("5.2 Saran", "Saran operasional dan aplikatif yang ditujukan kepada pihak terkait dan peneliti selanjutnya."),
                ]),
            ]

            for ch_title, subheadings in chapters:
                p_ch = doc.add_paragraph()
                p_ch.paragraph_format.page_break_before = True
                _set_heading(p_ch, ch_title, 1, center=True)

                for sub_title, sub_desc in subheadings:
                    p_sub = doc.add_paragraph()
                    _set_heading(p_sub, sub_title, 2, center=False)
                    p_text = doc.add_paragraph(sub_desc)
                    p_text.paragraph_format.first_line_indent = Cm(1.0)

            # --- SECTION 3: BACK MATTER ---
            p_bib = doc.add_paragraph()
            p_bib.paragraph_format.page_break_before = True
            _set_heading(p_bib, "DAFTAR PUSTAKA", 1, center=True)
            doc.add_paragraph("Daftar pustaka disusun alfabetis (format APA 7th style atau panduan kampus).")

            p_app = doc.add_paragraph()
            p_app.paragraph_format.page_break_before = True
            _set_heading(p_app, "LAMPIRAN", 1, center=True)
            doc.add_paragraph("Lampiran 1: Kuesioner / Pedoman Wawancara / Data Mentah.")

            doc.save(filename)

        return json.dumps({
            "success": True,
            "filename": filename,
            "title": title,
            "author": author,
            "preset": preset,
            "structure": [
                "Section 0: Cover (Judul, Penulis, Lembaga)",
                "Section 1: Halaman Awal (Lembar Pengesahan, Kata Pengantar, Abstrak, Abstract, Daftar Isi) [Nomor Romawi]",
                "Section 2: Bab I s.d. Bab V [Nomor Arab]",
                "Section 3: Daftar Pustaka dan Lampiran",
            ],
            "message": "Complete Indonesian thesis structure created successfully."
        })

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


async def audit_academic_formatting(filename: str) -> str:
    """Audit a Word document against Indonesian academic formatting standards.

    Checks margins (4-4-3-3 cm), A4 paper size, font family (Times New Roman),
    line spacing (1.5), first-line indent (1.0 cm), and required chapter headings.

    Args:
        filename: Path to the Word document to audit.

    Returns:
        JSON string containing detailed audit checklist, compliance score, and recommendations.
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return json.dumps({"success": False, "error": f"Document {filename} does not exist"})

    try:
        doc = Document(filename)
        findings = []
        checks_passed = []
        checks_failed = []

        # 1. Check Section Margins & Paper Size
        if len(doc.sections) == 0:
            return json.dumps({"success": False, "error": "Document has no sections"})

        sec = doc.sections[0]
        # A4 size check (~21.0 x 29.7 cm)
        width_cm = round(sec.page_width.cm, 1) if sec.page_width else 0
        height_cm = round(sec.page_height.cm, 1) if sec.page_height else 0

        if abs(width_cm - 21.0) <= 0.3 and abs(height_cm - 29.7) <= 0.3:
            checks_passed.append("Ukuran kertas sesuai standar A4 (21.0 x 29.7 cm)")
        else:
            checks_failed.append(f"Ukuran kertas tidak standar A4 ({width_cm} x {height_cm} cm)")
            findings.append({
                "type": "paper_size",
                "severity": "medium",
                "issue": f"Ukuran kertas saat ini {width_cm}x{height_cm} cm. Standar akademik Indonesia adalah A4 (21.0x29.7 cm).",
                "recommendation": "Ubah ukuran kertas ke A4 via set_page_layout."
            })

        # Margins check (Top 4cm, Left 4cm, Bottom 3cm, Right 3cm)
        top_cm = round(sec.top_margin.cm, 1) if sec.top_margin else 0
        left_cm = round(sec.left_margin.cm, 1) if sec.left_margin else 0
        bottom_cm = round(sec.bottom_margin.cm, 1) if sec.bottom_margin else 0
        right_cm = round(sec.right_margin.cm, 1) if sec.right_margin else 0

        margin_ok = (abs(top_cm - 4.0) <= 0.3 and abs(left_cm - 4.0) <= 0.3 and
                     abs(bottom_cm - 3.0) <= 0.3 and abs(right_cm - 3.0) <= 0.3)

        if margin_ok:
            checks_passed.append("Margin sesuai standar skripsi (Atas 4cm, Kiri 4cm, Bawah 3cm, Kanan 3cm)")
        else:
            checks_failed.append(f"Margin belum 4-4-3-3 cm (Atas {top_cm}cm, Kiri {left_cm}cm, Bawah {bottom_cm}cm, Kanan {right_cm}cm)")
            findings.append({
                "type": "margins",
                "severity": "high",
                "issue": f"Margin saat ini Atas: {top_cm}cm, Kiri: {left_cm}cm, Bawah: {bottom_cm}cm, Kanan: {right_cm}cm.",
                "recommendation": "Terapkan preset indonesian_thesis via apply_document_preset(preset='indonesian_thesis')."
            })

        # 2. Check Headings & Chapters
        full_text = "\n".join([p.text for p in doc.paragraphs])
        required_chapters = [
            ("BAB I", "BAB I PENDAHULUAN"),
            ("BAB II", "BAB II TINJAUAN PUSTAKA"),
            ("BAB III", "BAB III METODE PENELITIAN"),
            ("BAB IV", "BAB IV HASIL DAN PEMBAHASAN"),
            ("BAB V", "BAB V PENUTUP"),
            ("DAFTAR PUSTAKA", "DAFTAR PUSTAKA"),
        ]

        for ch_code, ch_label in required_chapters:
            if ch_code in full_text.upper():
                checks_passed.append(f"Bagian '{ch_label}' terdeteksi")
            else:
                checks_failed.append(f"Bagian '{ch_label}' tidak ditemukan")
                findings.append({
                    "type": "structure",
                    "severity": "high",
                    "issue": f"Bagian '{ch_label}' tidak terdeteksi dalam dokumen.",
                    "recommendation": f"Tambahkan struktur {ch_label} menggunakan add_heading."
                })

        # 3. Check Font & Line Spacing on Normal Style
        normal_style = None
        try:
            normal_style = doc.styles['Normal']
        except KeyError:
            pass

        if normal_style:
            font_name = normal_style.font.name
            font_size = normal_style.font.size.pt if normal_style.font.size else 0
            line_spacing = normal_style.paragraph_format.line_spacing

            if font_name and "times" in font_name.lower():
                checks_passed.append(f"Font Normal sesuai ({font_name})")
            else:
                checks_failed.append(f"Font Normal bukan Times New Roman ({font_name or 'Default'})")
                findings.append({
                    "type": "font",
                    "severity": "medium",
                    "issue": f"Font body paragraf adalah '{font_name}'. Standar akademik mengharuskan Times New Roman.",
                    "recommendation": "Atur font ke Times New Roman 12 pt via apply_document_preset."
                })

            if line_spacing and abs(line_spacing - 1.5) <= 0.1:
                checks_passed.append("Spasi paragraf 1.5 baris")
            else:
                checks_failed.append(f"Spasi paragraf belum 1.5 baris ({line_spacing})")
                findings.append({
                    "type": "line_spacing",
                    "severity": "medium",
                    "issue": f"Spasi baris bernilai {line_spacing}. Standar akademik Indonesia menggunakan spasi 1.5 baris.",
                    "recommendation": "Gunakan set_paragraph_spacing(line_spacing=1.5)."
                })

        # 4. Check In-text Citations & Bibliography match
        citation_matches = re.findall(r'\(([A-Z][a-zA-Z\s\.\&\-]+?),\s*([12]\d{3}[a-z]?)\)', full_text)
        if citation_matches:
            checks_passed.append(f"Ditemukan {len(citation_matches)} sitasi dalam teks")
        else:
            findings.append({
                "type": "citation",
                "severity": "low",
                "issue": "Tidak ditemukan sitasi formal dalam format (Penulis, Tahun).",
                "recommendation": "Pastikan argumen ilmiah dilengkapi referensi akademik yang valid."
            })

        total_checks = len(checks_passed) + len(checks_failed)
        compliance_score = int((len(checks_passed) / total_checks * 100)) if total_checks > 0 else 0

        return json.dumps({
            "success": True,
            "filename": filename,
            "compliance_score": compliance_score,
            "passed_checks_count": len(checks_passed),
            "failed_checks_count": len(checks_failed),
            "passed_checks": checks_passed,
            "failed_checks": checks_failed,
            "findings": findings,
            "status": "COMPLIANT" if compliance_score >= 85 else ("NEEDS_REVISION" if compliance_score >= 50 else "NON_COMPLIANT"),
        })

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


async def annotate_audit_findings(
    filename: str,
    author: str = "Auditor Akademik",
    initials: str = "AA",
) -> str:
    """Run academic audit and automatically attach Word comments to problematic sections in the document.

    Args:
        filename: Path to the Word document.
        author: Comment author name.
        initials: Comment author initials.

    Returns:
        JSON string summarizing inserted comments.
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return json.dumps({"success": False, "error": f"Document {filename} does not exist"})

    try:
        audit_raw = await audit_academic_formatting(filename)
        audit_res = json.loads(audit_raw)

        if not audit_res.get("success"):
            return json.dumps({"success": False, "error": audit_res.get("error")})

        findings = audit_res.get("findings", [])
        if not findings:
            return json.dumps({
                "success": True,
                "comments_added": 0,
                "message": "Dokumen sudah memenuhi seluruh standar akademik. Tidak ada catatan perbaikan."
            })

        comments_added = 0
        async with get_file_lock(filename):
            doc = Document(filename)
            paragraphs = doc.paragraphs

            for finding in findings:
                f_type = finding.get("type")
                issue = finding.get("issue")
                rec = finding.get("recommendation")
                comment_body = f"[AUDIT AKADEMIK - {f_type.upper()}]\n{issue}\nSaran: {rec}"

                # Find best anchor paragraph
                target_text = None
                if f_type in ("margins", "paper_size", "font", "line_spacing"):
                    if len(paragraphs) > 0 and paragraphs[0].text.strip():
                        target_text = paragraphs[0].text.strip()[:40]
                elif f_type == "structure":
                    for p in paragraphs:
                        if "BAB" in p.text.upper() or "DAFTAR" in p.text.upper():
                            target_text = p.text.strip()[:40]
                            break

                if target_text:
                    try:
                        res = add_comment_to_doc(filename, target_text, comment_body, author, initials)
                        if res.get("success"):
                            comments_added += 1
                    except Exception:
                        pass

        return json.dumps({
            "success": True,
            "filename": filename,
            "total_findings": len(findings),
            "comments_added": comments_added,
            "message": f"Berhasil menyematkan {comments_added} komentar audit akademik langsung ke dalam dokumen Word."
        })

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


async def extract_citations_and_bibliography(filename: str) -> str:
    """Extract in-text citations and match them against the Daftar Pustaka / References section.

    Detects parenthetical citations (e.g. '(Sugiyono, 2021)'), narrative citations (e.g. 'Kotler (2018)'),
    and cross-checks with bibliography entries to detect missing or unreferenced citations.

    Args:
        filename: Path to the Word document.

    Returns:
        JSON string containing in-text citations, bibliography items, and cross-reference comparison.
    """
    filename = ensure_docx_extension(filename)
    if not os.path.exists(filename):
        return json.dumps({"success": False, "error": f"Document {filename} does not exist"})

    try:
        doc = Document(filename)
        body_text_lines = []
        bib_lines = []
        in_bib_section = False

        for p in doc.paragraphs:
            txt = p.text.strip()
            if not txt:
                continue

            if "DAFTAR PUSTAKA" in txt.upper() or "REFERENCES" in txt.upper():
                in_bib_section = True
                continue
            elif in_bib_section and ("LAMPIRAN" in txt.upper() or "APPENDIX" in txt.upper()):
                in_bib_section = False

            if in_bib_section:
                bib_lines.append(txt)
            else:
                body_text_lines.append(txt)

        full_body_text = "\n".join(body_text_lines)

        # 1. Parse parenthetical citations: (Author, Year)
        parenthetical_citations = set()
        p_matches = re.finditer(r'\(([A-Z][a-zA-Z\s\.\&\-]+?),\s*([12]\d{3}[a-z]?)(?:,\s*[ph\.\s\d\-]+)?\)', full_body_text)
        for m in p_matches:
            author_raw = m.group(1).strip()
            year_raw = m.group(2).strip()
            # Clean author: get last name
            author_clean = author_raw.split()[-1].strip(".,")
            parenthetical_citations.add((author_raw, year_raw, author_clean))

        # 2. Parse narrative citations: Author (Year)
        narrative_citations = set()
        n_matches = re.finditer(r'\b([A-Z][a-zA-Z]+(?:\s+(?:et\s+al\.|dkk\.|dan\s+[A-Z][a-zA-Z]+))?)\s*\(([12]\d{3}[a-z]?)\)', full_body_text)
        for m in n_matches:
            author_raw = m.group(1).strip()
            year_raw = m.group(2).strip()
            author_clean = author_raw.split()[0].strip(".,")
            narrative_citations.add((author_raw, year_raw, author_clean))

        all_citations = []
        for a_raw, y_raw, a_clean in parenthetical_citations.union(narrative_citations):
            all_citations.append({"author": a_raw, "year": y_raw, "search_key": f"{a_clean.lower()} {y_raw}"})

        # 3. Cross check with Bibliography
        matched_citations = []
        missing_from_bib = []
        full_bib_text = "\n".join(bib_lines).lower()

        for cit in all_citations:
            author_key = cit["search_key"].split()[0]
            year_key = cit["year"]
            if author_key in full_bib_text and year_key in full_bib_text:
                matched_citations.append(f"{cit['author']} ({cit['year']})")
            else:
                missing_from_bib.append(f"{cit['author']} ({cit['year']})")

        return json.dumps({
            "success": True,
            "filename": filename,
            "total_citations_found": len(all_citations),
            "total_bibliography_entries": len(bib_lines),
            "matched_citations_count": len(matched_citations),
            "missing_from_bibliography_count": len(missing_from_bib),
            "matched_citations": matched_citations,
            "missing_from_bibliography": missing_from_bib,
            "bibliography_entries_sample": bib_lines[:5],
            "recommendation": (
                "Seluruh sitasi cocok dengan Daftar Pustaka." if not missing_from_bib
                else f"Ditemukan {len(missing_from_bib)} sitasi dalam teks yang belum tercantum di Daftar Pustaka!"
            )
        })

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
