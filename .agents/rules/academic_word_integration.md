# Academic Writing + Word Live Integration Rules

Aturan ini mengintegrasikan seluruh alur kerja penulisan ilmiah Bahasa Indonesia (`academic-writing-skills`) dengan server eksekusi langsung dokumen Microsoft Word (`word-live` / `msword-mcp`).

## 1. Prinsip Utama

1. **Metodologi & Konten**: Dipandu oleh modul `academic-writing-skills` (`academic-writing`, `outline`, `draft`, `edit`, `audit`). Tidak boleh ada data, responden, sitasi, atau angka rekaan.
2. **Eksekusi Dokumen**: Saat pengguna mengolah atau meminta hasil dalam format Microsoft Word (`.docx`), seluruh aksi pembacaan, pembuatan, penataan gaya, dan revisi wajib dieksekusi langsung melalui tool MCP `word-live`.

## 2. Pemetaan Skill ke Tool `word-live`

### A. Skill `outline` (Penyusunan & Restrukturisasi Kerangka)
- **Ekstraksi Struktur Eksisting**: Gunakan `get_document_outline` atau `get_document_text` untuk membaca kerangka naskah yang sudah ada.
- **Penerapan Kerangka Baru**:
  - Terapkan penomoran heading hierarkis standar skripsi/jurnal (mis. Bab I, 1.1, 1.1.1) menggunakan `word_live_setup_heading_numbering` atau `add_heading`.
  - Sisipkan pembatas halaman antar-bab utama via `add_page_break` atau `add_section_break`.

### B. Skill `draft` (Penulisan Naskah Bab I s.d. V)
- **Tata Letak Halaman (Page Setup)**:
  - Terapkan margin standar akademik Indonesia (mis. 4 cm kiri, 4 cm atas, 3 cm kanan, 3 cm bawah pada kertas A4) via `set_page_layout` / `word_live_set_page_layout`.
- **Penulisan Paragraf**:
  - Tulis paragraf menggunakan `add_paragraph` atau `word_live_insert_paragraphs`.
  - Atur spasi paragraf (Times New Roman 12pt, line spacing 1.5 atau 2.0, first line indent 1 cm) via `set_paragraph_spacing`.
- **Tabel & Data**:
  - Buat tabel akademik formal (border terbuka, tanpa border vertikal tebal) via `add_table` dan `format_table`.
- **Sitasi & Catatan Kaki**:
  - Jika pedoman institusi mewajibkan footnote, gunakan `add_footnote_robust`.

### C. Skill `edit` (Penyuntingan EYD V, KBBI, & Kalimat Efektif)
- **Pelacakan Perubahan (Track Changes)**:
  - Setiap penggantian istilah, koreksi saltik (typo), penghapusan pola teks AI (*ai-patterns*), atau restrukturisasi kalimat wajib menggunakan mode pelacakan agar transparan untuk pembimbing/penulis.
  - Panggil `track_replace`, `track_insert`, atau `track_delete` (atau `word_live_replace_text` dengan konfirmasi).

### D. Skill `audit` (Pemeriksaan Logika, Konsistensi, & Pedoman)
- **Sematkan Temuan Langsung ke Dokumen**:
  - Dilarang hanya mencetak daftar temuan di jendela percakapan jika naskah Word sedang dibuka.
  - Masukkan temuan audit (gap logika, klaim tanpa bukti, sitasi tidak sinkron daftar pustaka, ketidaksesuaian pedoman) langsung sebagai komentar Word di paragraf terkait via `add_comment` atau `word_live_add_comment`.

## 3. Aturan Baku Tipografi & Layout Dokumen (Wajib Otomatis Tanpa Diminta Ulang)

1. **BAB & Judul BAB**:
   - Wajib **Rata Tengah (Center)**, Huruf Kapital (Uppercase), Bold, Times New Roman 14pt (BAB) dan 14pt (Judul).
   - **Dilarang keras** diformat Rata Kanan-Kiri (Justify) atau Rata Kiri.
   - Wajib diset `keep_with_next: true` agar judul tidak tertinggal sendirian di dasar halaman (mencegah orphan header).
   - Setiap BAB baru wajib diawali dengan `add_page_break` atau `page_break_before: true` hanya pada nomor Bab (jangan pasang page break pada nomor Bab DAN judul Bab sekaligus agar tidak terpisah halaman).

2. **Sub-Bab & Heading Sekunder (1.1, 1.2, a., b., dst.)**:
   - Wajib **Rata Kiri (Left)**, Bold, Times New Roman 12pt, tanpa inden baris pertama (`first_line_indent_cm: 0`).
   - Wajib diset `keep_with_next: true`.

3. **Paragraf Narasi / Teks Isi**:
   - Wajib **Rata Kanan-Kiri (Justified)**.
   - **Wajib menjorok pada baris pertama (First Line Indent)** sebesar 1.0 cm (`first_line_indent_cm: 1.0`). Dilarang membiarkan awal paragraf rata/flat tanpa indentasi.
   - Spasi baris wajib **1.5 spasi** (`line_spacing_rule: "1.5_lines"`). Dilarang memasukkan angka point kecil (<10) ke parameter `line_spacing` agar teks tidak bertumpuk.
   - Spasi setelah paragraf (`space_after_pt`): 6.0 pt, spasi sebelum: 0 pt.

4. **Daftar Poin & Penomoran (1, 2, 3... atau a, b, c...)**:
   - Wajib diformat rapi dengan hanging indent/left indent (0.75 cm - 1.0 cm), bukan first line indent paragraf narasi.
   - Teks rata kiri atau justify, spasi 1.5, jarak antar poin 2–4 pt.

5. **Penomoran Halaman (Page Numbers)**:
   - Setiap dokumen naskah utuh wajib dipasangi nomor halaman aktif via `word_live_add_page_numbers` atau `add_page_numbers` pada posisi footer (bawah tengah) atau header (kanan atas) sesuai pedoman instansi.
