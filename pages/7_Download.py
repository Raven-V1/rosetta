"""
Download Page - Export Onboarding Documentation
Download the complete onboarding guide as a PDF file.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Preview section: show full scrollable markdown content
- Download button: st.download_button with PDF export
  filename: {database_name}_onboarding.pdf
  mime: application/pdf
- Stats section: show word count and section count of the export
- Calls markdown_exporter.export_to_markdown(st.session_state)
- No business logic, reads only from session_manager
"""

import streamlit as st
from src import session_manager, markdown_exporter
from src.ui_utils import render_sidebar_brand
from io import BytesIO
import re

try:
    import html as _html
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    _reportlab_available = True
except ImportError:
    _reportlab_available = False

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Download</h1>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Connection guard
if not session_manager.is_connected():
    st.markdown("""
    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#ff8389;'>⚠ No database connection found. Please connect to a database on the Home page.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Get metadata for database name
metadata = session_manager.get_metadata()
database_name = metadata.get('database_name', 'database')

# Generate the markdown export
markdown_content = markdown_exporter.export_to_markdown(st.session_state)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Preview section with full scrollable content
st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Preview</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>Full markdown content (scrollable):</p>", unsafe_allow_html=True)

# Display full markdown content using st.markdown with scrollable container
with st.container(height=500):
    st.markdown(markdown_content)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Stats section
st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Export Statistics</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

# Calculate word count
word_count = len(markdown_content.split())

# Calculate section count (count lines starting with ##)
section_count = markdown_content.count('\n## ')

col1, col2 = st.columns(2)

with col1:
    st.metric("Word Count", f"{word_count:,}")

with col2:
    st.metric("Sections", section_count)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Download button
st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Download</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)


def generate_pdf(markdown_content: str, database_name: str) -> bytes:
    LOGO_PATH = 'assets/Belvenar_logo.png'
    PAGE_W, PAGE_H = letter
    MARGIN = 0.75 * inch

    # ── Header / footer drawn on every page ──────────────────────────────────
    def draw_page(canvas, doc):
        canvas.saveState()
        # Header
        header_y = PAGE_H - 0.55 * inch
        try:
            canvas.drawImage(
                LOGO_PATH, MARGIN, header_y + 0.05 * inch,
                width=0.28 * inch, height=0.28 * inch,
                preserveAspectRatio=True, mask='auto'
            )
            name_x = MARGIN + 0.36 * inch
        except Exception:
            name_x = MARGIN
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(colors.HexColor('#161616'))
        canvas.drawString(name_x, header_y + 0.1 * inch, 'Belvenar Analytics')
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#525252'))
        canvas.drawRightString(PAGE_W - MARGIN, header_y + 0.1 * inch, database_name)
        canvas.setStrokeColor(colors.HexColor('#0f62fe'))
        canvas.setLineWidth(0.75)
        canvas.line(MARGIN, header_y, PAGE_W - MARGIN, header_y)
        # Footer
        footer_y = 0.55 * inch
        canvas.setStrokeColor(colors.HexColor('#e0e0e0'))
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, footer_y, PAGE_W - MARGIN, footer_y)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#6f6f6f'))
        canvas.drawString(MARGIN, footer_y - 0.17 * inch,
                          'Belvenar Analytics  ·  Database Onboarding Guide')
        canvas.drawRightString(PAGE_W - MARGIN, footer_y - 0.17 * inch,
                               f'Page {doc.page}')
        canvas.restoreState()

    # ── Document ─────────────────────────────────────────────────────────────
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )

    # ── Styles ────────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'RTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#161616'),
        spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    h1_style = ParagraphStyle(
        'RH1', parent=styles['Heading1'],
        fontSize=14, textColor=colors.HexColor('#0f62fe'),
        spaceBefore=20, spaceAfter=8, fontName='Helvetica-Bold'
    )
    h2_style = ParagraphStyle(
        'RH2', parent=styles['Heading2'],
        fontSize=12, textColor=colors.HexColor('#161616'),
        spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold'
    )
    h3_style = ParagraphStyle(
        'RH3', parent=styles['Heading3'],
        fontSize=10, textColor=colors.HexColor('#393939'),
        spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold'
    )
    code_style = ParagraphStyle(
        'RCode', parent=styles['Code'],
        fontSize=7.5, leftIndent=10, rightIndent=10,
        spaceBefore=4, spaceAfter=8,
        backColor=colors.HexColor('#f4f4f4'),
        fontName='Courier', leading=11
    )
    body_style = ParagraphStyle(
        'RBody', parent=styles['BodyText'],
        fontSize=9, textColor=colors.HexColor('#161616'),
        spaceAfter=3, leading=13
    )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def to_para(text: str) -> str:
        """Escape & then apply markdown bold/italic for reportlab Paragraph."""
        text = text.replace('&', '&amp;')
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        return text

    def build_md_table(tbl_lines):
        """Convert markdown table lines into a styled reportlab Table."""
        def parse_row(s):
            return [cell.strip() for cell in s.strip().strip('|').split('|')]
        header = parse_row(tbl_lines[0])
        data = [parse_row(l) for l in tbl_lines[2:] if l.strip().startswith('|')]
        all_rows = [header] + data
        ncols = max(len(r) for r in all_rows)
        all_rows = [r + [''] * (ncols - len(r)) for r in all_rows]
        usable_w = PAGE_W - 2 * MARGIN
        t = Table(all_rows, colWidths=[usable_w / ncols] * ncols, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), colors.HexColor('#393939')),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#f4f4f4'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.25, colors.HexColor('#c6c6c6')),
            ('LEFTPADDING',   (0, 0), (-1, -1), 5),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
            ('TOPPADDING',    (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    # ── Parser ────────────────────────────────────────────────────────────────
    story = []
    sec = []   # buffer for the current #### table-entry block (KeepTogether'd)

    def flush():
        """Flush sec buffer as a KeepTogether block into story."""
        if sec:
            story.append(KeepTogether(sec[:]))
            sec.clear()

    def add(elem):
        """Add an element to sec if inside a #### block, else directly to story."""
        (sec if sec else story).append(elem)

    lines_list = markdown_content.split('\n')
    i = 0
    in_code = False
    code_acc = []

    while i < len(lines_list):
        line = lines_list[i]

        # ── Code fences ──────────────────────────────────────────────────────
        if line.strip().startswith('```'):
            if in_code:
                if code_acc:
                    raw = _html.escape('\n'.join(code_acc))
                    raw = raw.replace('\n', '<br/>')
                    add(Paragraph(f'<font name="Courier">{raw}</font>', code_style))
                    code_acc.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_acc.append(line)
            i += 1
            continue

        # ── Markdown table block ──────────────────────────────────────────────
        if (line.strip().startswith('|')
                and i + 1 < len(lines_list)
                and re.match(r'\s*\|[-| :]+\|', lines_list[i + 1])):
            tbl = []
            while i < len(lines_list) and lines_list[i].strip().startswith('|'):
                tbl.append(lines_list[i])
                i += 1
            if len(tbl) >= 2:
                add(build_md_table(tbl))
                add(Spacer(1, 6))
            continue

        # ── #### heading — start a new KeepTogether section ──────────────────
        if line.startswith('#### '):
            flush()
            sec.append(Paragraph(to_para(line[5:].strip()), h3_style))
            i += 1
            continue

        # ── Higher headings — flush pending section, add directly to story ───
        if line.startswith('# '):
            flush()
            story.append(Paragraph(to_para(line[2:].strip()), title_style))
            i += 1
            continue
        if line.startswith('## '):
            flush()
            story.append(Paragraph(to_para(line[3:].strip()), h1_style))
            i += 1
            continue
        if line.startswith('### '):
            flush()
            story.append(Paragraph(to_para(line[4:].strip()), h2_style))
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────────
        if line.strip() == '---':
            flush()
            story.append(Spacer(1, 10))
            i += 1
            continue

        # ── Empty line ────────────────────────────────────────────────────────
        if not line.strip():
            add(Spacer(1, 4))
            i += 1
            continue

        # ── Regular text (bold, italic, bullet) ───────────────────────────────
        text = to_para(line.strip())
        if text.startswith('- '):
            text = '• ' + text[2:]
        add(Paragraph(text, body_style))
        i += 1

    flush()

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    buffer.seek(0)
    return buffer.getvalue()


filename = f"{database_name}_onboarding.pdf"

if _reportlab_available:
    pdf_data = generate_pdf(markdown_content, database_name)
    st.download_button(
        label="Download PDF File",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.markdown("""
    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#ff8389;'>✗ PDF export unavailable: <code>reportlab</code> is not installed on this server.
        Run <code>pip install reportlab</code> to enable PDF downloads.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
    <span style='color:#78a9ff;'>ℹ The file will be saved as {filename}</span>
</div>
""", unsafe_allow_html=True)

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)
