<div align="center">

# msword-mcp

**High-performance Word MCP Server — Live editing in Microsoft Word, Academic Publishing Presets, and OpenXML manipulation**

`Live editing` &middot; `Academic & SINTA Presets` &middot; `Metric Units (cm/mm)` &middot; `Native TOC` &middot; `Token Bloat Filtering` &middot; `Tracked changes`

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform: Windows + macOS/Linux](https://img.shields.io/badge/platform-Windows%20%2B%20macOS%2FLinux-lightgrey)]()

</div>

---

**msword-mcp** (enhanced fork) gives any AI assistant that supports [MCP](https://modelcontextprotocol.io/) full control of Microsoft Word (including Google Antigravity, Cursor, Claude Desktop, VS Code, Windsurf, and Codex). Open a document, tell the AI what you need, and watch it happen — formatting, academic thesis layouts, multi-column journal structures, tracked changes, comments, and all. Changes can appear live in your open Word window or be processed offline directly via OpenXML.

<table>
<tr>
<td width="50%">

### Without msword-mcp

- AI can discuss your document but can't touch it
- You copy-paste between AI and Word, losing formatting
- Manual margin calculation (converting cm to inches manually)
- Academic page numbering (Roman vs Arabic, different first page per chapter) is painful
- Track changes? You do those manually after the fact

</td>
<td width="50%">

### With msword-mcp

- "Apply Indonesian thesis preset with 4-4-3-3 cm margins" — done in 1 call
- "Setup SINTA 2-column journal template" — done automatically
- Changes appear live in your open Word document
- Native Word TOC fields with dot leaders and auto-update
- Real tracked changes with your name, not XML hacks

</td>
</tr>
</table>

### See it in action

https://github.com/user-attachments/assets/fbb09af4-1e25-4e49-94d0-45b363278810

## What Sets This Apart

- **Academic, Thesis & SINTA Presets** — 1-call setup for Indonesian Thesis (`4-4-3-3 cm`, Roman prelims, Arabic chapters with different first page), SINTA 2-column articles, and Makalah.
- **Metric Unit Support** — Configure margins and paper sizes directly in centimeters (`cm`), millimeters (`mm`), points (`pt`), or inches.
- **Native Word TOC (<w:fldSimple>)** — Clean XML fields that auto-update in Word with right tab stop dot leaders.
- **Token Bloat Reduction (`WORD_MCP_TOOLSET`)** — Switch between `minimal` (10 tools), `academic` (30 tools), `live_only` (45 tools), or `full` profiles to save up to 75% LLM context window.
- **Office 365 / OneDrive COM Reliability** — ROT fallback scanning and clear `PermissionError [Errno 13]` handling when files are open in Word GUI.
- **Live editing** — Edit documents while they're open in Word. No save-close-reopen cycle.
- **Full undo** — Every AI action is a single Ctrl+Z. Made a mistake? Just undo it.
- **Native tracked changes** — Real Word revisions with your name, not XML hacks.
- **Threaded comments** — Add, reply, resolve, and delete comments like a human reviewer.

## Quick Start

Install from source:

```bash
git clone https://github.com/RvlDX/msword-mcp.git
cd msword-mcp
pip install -e .
```

## Client Installation

<details open>
<summary><b>Google Antigravity (AGY)</b></summary>

Add to your Antigravity MCP configuration (`mcp_config.json` or Antigravity MCP Settings):

```json
{
  "mcpServers": {
    "word": {
      "command": "python",
      "args": ["-m", "word_document_server.main"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "WORD_MCP_TOOLSET": "academic"
      }
    }
  }
}
```

Or via Antigravity CLI:
```bash
agy mcp add word -- python -m word_document_server.main
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "word": {
      "command": "uvx",
      "args": ["word-mcp-live"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "MCP_AUTHOR_INITIALS": "YN"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Claude Code</b></summary>

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "word": {
      "command": "uvx",
      "args": ["word-mcp-live"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "MCP_AUTHOR_INITIALS": "YN"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

**One-click:** Click the install button at the top of this page.

**Manual:** Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "word": {
      "command": "uvx",
      "args": ["word-mcp-live"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "MCP_AUTHOR_INITIALS": "YN"
      }
    }
  }
}
```

</details>

<details>
<summary><b>VS Code / Copilot</b></summary>

**One-click:** [Install in VS Code](vscode:mcp/install?%7B%22name%22%3A%20%22word%22%2C%20%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22word-mcp-live%22%5D%7D)

**Manual:** Add to your VS Code `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "word": {
        "command": "uvx",
        "args": ["word-mcp-live"],
        "env": {
          "MCP_AUTHOR": "Your Name",
          "MCP_AUTHOR_INITIALS": "YN"
        }
      }
    }
  }
}
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "word": {
      "command": "uvx",
      "args": ["word-mcp-live"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "MCP_AUTHOR_INITIALS": "YN"
      }
    }
  }
}
```

</details>

<details>
<summary><b>OpenAI Codex (CLI, desktop app, IDE)</b></summary>

```bash
codex mcp add word --env MCP_AUTHOR="Your Name" -- uvx word-mcp-live
```

Or add to `~/.codex/config.toml`:

```toml
[mcp_servers.word]
command = "uvx"
args = ["word-mcp-live"]
startup_timeout_sec = 60
tool_timeout_sec = 120

[mcp_servers.word.env]
MCP_AUTHOR = "Your Name"
```

In the desktop app: Settings → MCP servers → Add server. On Windows, run Codex natively, not under WSL — live tools need native Windows.

</details>

<details>
<summary><b>Docker</b></summary>

```json
{
  "mcpServers": {
    "word": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/ykarapazar/word-mcp-live"],
      "env": {
        "MCP_AUTHOR": "Your Name",
        "MCP_AUTHOR_INITIALS": "YN"
      }
    }
  }
}
```

> Note: Docker mode supports cross-platform tools only. Live editing requires a native (non-Docker) install on Windows or macOS with Word running.

</details>

> **`MCP_AUTHOR`** sets your name on tracked changes and comments (default: `"Author"`). **`MCP_AUTHOR_INITIALS`** sets comment initials.

## Two Modes

|  | Works everywhere | Live editing (Word open) |
|---|---|---|
| **What it does** | Create and edit saved .docx files | Edit documents live while you work in Word |
| **Platform** | Windows, macOS, Linux | Windows (COM) and macOS (JXA) |
| **Undo** | File-level saves | Per-action Ctrl+Z (Windows); per-operation undo (macOS) |
| **Best for** | Batch processing, document generation | Interactive editing, formatting, review |

Both modes work together. The AI picks the right one for the task.

### macOS Live Editing (New in v1.5.0)

Live tools now work on macOS via JavaScript for Automation (JXA). Same tool names, same parameters — the server detects your platform and uses the right automation backend.

| Feature | Windows | macOS |
|---------|---------|-------|
| Text read/write/find/replace | COM | JXA |
| Formatting (bold, font, style) | COM | JXA |
| Track changes & revisions | COM | JXA |
| Comments (add, delete, list) | COM | JXA |
| Tables (add, read, modify rows/cells) | COM | JXA |
| Page layout, headers, bookmarks | COM | JXA |
| Table formatting (`word_live_format_table`) | COM | Not available |
| Images, multi-paragraph insert | COM | Not available |
| Equations, cross-references | COM | Not available |
| Snapshot diff/status, document properties | COM | Not available |
| Threaded comment replies | COM | Not available |
| Comment resolve/unresolve | COM | Not available |
| Undo history inspection | COM | Not available |
| Watermarks | COM | Not available |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_AUTHOR` | `"Author"` | Author name for tracked changes and comments |
| `MCP_AUTHOR_INITIALS` | `""` | Author initials for comments |
| `MCP_TRANSPORT` | `stdio` | Transport type: `stdio`, `sse`, or `streamable-http` |
| `MCP_HOST` | `0.0.0.0` | Host to bind (for SSE/HTTP transports) |
| `MCP_PORT` | `8000` | Port to bind (for SSE/HTTP transports) |
| `WORD_MCP_TOOLSET` | `full` | Toolset filter profile to reduce context bloat: `minimal` (10 tools), `academic` (30 tools), `live_only` (45 tools), or `full` (121 tools) |

For remote deployment, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

## 🎓 Academic, Thesis & Journal Publishing Support

`msword-mcp` is pre-configured with complete out-of-the-box support for academic guidelines (Indonesian Skripsi/Thesis, Makalah, and SINTA 1–6 / IEEE Journals):

### 1. Indonesian Thesis / Skripsi (`indonesian_thesis`)
Setup an entire compliant thesis structure with 1 tool call:
- **Paper & Margins**: A4, 4-4-3-3 cm (Left 4 cm, Top 4 cm, Bottom 3 cm, Right 3 cm).
- **Typography**: Times New Roman 12 pt, 1.5 line spacing, Justified alignment, 1.0 cm first-line indent.
- **Section & Academic Page Numbering**:
  - **Cover**: No page numbers.
  - **Preliminaries (Halaman Judul, Pengesahan, Abstrak, Daftar Isi)**: Lowercase Roman numerals (`i, ii, iii...`), footer center.
  - **Chapters (BAB I s/d BAB V)**: Arabic numerals (`1, 2, 3...`), restart at 1. First page of each chapter in bottom-center, subsequent pages in top-right.
  - **References (Daftar Pustaka)**: Continuous Arabic numbering in top-right.

```json
// Tool call
apply_document_preset({"filename": "skripsi.docx", "preset": "indonesian_thesis"})
```

### 2. SINTA Journal / IEEE 2-Column Articles (`sinta_journal`)
Compliant with Indonesian SINTA 1–6 and scientific conference templates:
- **Section 0 (Title, Authors, Abstract, Keywords)**: Single column (1-col).
- **Section 1 (Body: Pendahuluan, Metode, Hasil, Diskusi, Pustaka)**: Two columns (2-col, 0.65 cm spacing, continuous section break).
- **Typography**: Times New Roman 10 pt, single spacing, 4 pt space after, Justified alignment, 0.75 cm indent.

```json
// Tool call
apply_document_preset({"filename": "jurnal_sinta.docx", "preset": "sinta_journal"})
```

### 3. Complete Thesis Skeleton Generation (`setup_thesis_structure`)
Generate a complete Indonesian thesis structure with 1 tool call:
- Section 0: Cover (Judul, Penulis, Lembaga, Tahun).
- Section 1: Halaman Awal (Lembar Pengesahan, Kata Pengantar, Abstrak ID & EN, Daftar Isi) dengan penomoran romawi (`i, ii, iii...`).
- Section 2: Bab I Pendahuluan s.d. Bab V Penutup dengan penomoran arab (`1, 2, 3...`) dan Heading 1 & Heading 2 lengkap.
- Section 3: Daftar Pustaka dan Lampiran.

```json
// Tool call
setup_thesis_structure({
  "filename": "skripsi_lengkap.docx",
  "title": "Analisis Pengaruh Sistem Informasi Terhadap Kinerja Karyawan",
  "author": "Nama Mahasiswa",
  "nim": "12345678",
  "institution": "Universitas Indonesia",
  "faculty": "Fakultas Ilmu Komputer",
  "city": "Jakarta",
  "year": "2026"
})
```

### 4. Academic Formatting Audit & Inline Annotations (`audit_academic_formatting`, `annotate_audit_findings`)
Automatically inspect a Word document against academic formatting standards (A4, margins 4-4-3-3 cm, Times New Roman 12 pt, 1.5 spacing, 1 cm first-line indent, and mandatory chapters):
- `audit_academic_formatting`: Returns structured audit report with compliance score (0-100), passed checks, failed checks, and revision recommendations.
- `annotate_audit_findings`: Automatically injects native Word review comments anchored to problematic paragraphs.
- `extract_citations_and_bibliography`: Extracts in-text citations (APA/narrative) and cross-checks them against the Daftar Pustaka section.

### 5. Native Word Table of Contents (TOC)
Inserts native Word OpenXML fields (`<w:fldSimple w:instr="TOC \o '1-3' \h \z \u"/>`) with `<w:updateFields/>` so Word calculates exact page numbers when opened:

```json
// Tool call
add_table_of_contents({
  "filename": "skripsi.docx",
  "title": "DAFTAR ISI",
  "max_level": 3,
  "use_native_field": true
})
```

## Example Prompts

Just tell the AI what you want in plain language:

```
"Draft a contract with tracked changes so my colleague can review"
"Format all headings as Cambria 13pt bold and add automatic numbering"
"Add a comment on paragraph 3 asking about the deadline"
"Find every mention of 'ABC Corp' and replace with 'XYZ Ltd' as a tracked change"
"Set the page to A4 landscape with 2cm margins"
"Insert a table of contents based on the document headings"
"Add page numbers in the footer and our company name in the header"
"Insert a cross-reference to Heading 2 in paragraph 5"
```

## Usage Examples

### Example 1: Read a document (cross-platform)

**Tool call:** `get_document_text`
```json
{ "filename": "C:/Documents/report.docx" }
```
**Expected output:**
```json
{
  "status": "success",
  "paragraphs": [
    {"index": 0, "text": "Quarterly Report", "style": "Heading 1"},
    {"index": 1, "text": "Revenue increased by 15% compared to Q3.", "style": "Normal"},
    {"index": 2, "text": "Key Metrics", "style": "Heading 2"}
  ],
  "total_paragraphs": 3
}
```

### Example 2: Live editing with tracked changes (Windows)

**Tool call:** `word_live_replace_text`
```json
{
  "filename": "report.docx",
  "find_text": "ABC Corporation",
  "replace_text": "XYZ Ltd",
  "match_case": true,
  "replace_all": true,
  "track_changes": true
}
```
**Expected output:**
```json
{
  "status": "success",
  "replacements": 4,
  "message": "Replaced 4 occurrences (tracked changes enabled)"
}
```
The replacements appear as tracked changes in Word with strikethrough on "ABC Corporation" and underline on "XYZ Ltd".

### Example 3: Add a comment anchored to text (cross-platform)

**Tool call:** `add_comment`
```json
{
  "filename": "C:/Documents/contract.docx",
  "target_text": "payment within 30 days",
  "comment_text": "Should we extend this to 45 days?",
  "author": "Jane Smith"
}
```
**Expected output:**
```json
{
  "status": "success",
  "message": "Comment added by Jane Smith on 'payment within 30 days'"
}
```
The comment appears in Word's Review panel, anchored to the specified text.

## Tool Reference

**120 tools** across two modes — see the [complete tool reference](TOOLS.md) for details.

| Category | Count |
|----------|-------|
| Cross-platform (python-docx) | 75 |
| Windows Live (COM automation) | 45 (44 `word_live_*` + `word_screen_capture`) |
| macOS Live (JXA automation) | 32 (of the 45 live tools) |

## Requirements

- **Python 3.11+**
- `python-docx`, `fastmcp`, `msoffcrypto-tool` (installed automatically)
- **Windows Live tools:** Windows 10/11 + Microsoft Word + `pywin32` (installed automatically)
- **macOS Live tools:** macOS + Microsoft Word for Mac (uses built-in JXA — no extra dependencies)

> The cross-platform tools work without Word installed — only python-docx is needed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and how to add new tools.

Found a bug? [Open an issue](https://github.com/RvlDX/msword-mcp/issues/new?template=bug_report.md).
Have an idea? [Request a feature](https://github.com/RvlDX/msword-mcp/issues/new?template=feature_request.md).

## Acknowledgments

Built on top of [ykarapazar/word-mcp-live](https://github.com/ykarapazar/word-mcp-live) and [GongRzhe/Office-Word-MCP-Server](https://github.com/GongRzhe/Office-Word-MCP-Server) (MIT License).

Academic writing skill workflow integrated with [academic-writing-skills](https://github.com/Nbill27/academic-writing-skills) by [Nbill27](https://github.com/Nbill27) (Indonesian academic writing rules, outline, drafting, EYD V editing, and research coherence audit).

Additional libraries: [python-docx](https://python-docx.readthedocs.io/) &middot; [FastMCP](https://github.com/modelcontextprotocol/python-sdk) &middot; [pywin32](https://github.com/mhammond/pywin32)

## Privacy

This server runs entirely on your local machine. No data is collected, transmitted, or stored. See the full [Privacy Policy](PRIVACY.md).

## Support

- **Bug reports:** [Open an issue](https://github.com/RvlDX/msword-mcp/issues/new?template=bug_report.md)
- **Feature requests:** [Request a feature](https://github.com/RvlDX/msword-mcp/issues/new?template=feature_request.md)
- **Discussions:** [GitHub Discussions](https://github.com/RvlDX/msword-mcp/discussions)

## License

MIT License — see [LICENSE](LICENSE) for details.

## Star History

<a href="https://star-history.com/#RvlDX/msword-mcp&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=RvlDX/msword-mcp&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=RvlDX/msword-mcp&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=RvlDX/msword-mcp&type=Date" />
 </picture>
</a>

<!-- mcp-name: io.github.RvlDX/msword-mcp -->
