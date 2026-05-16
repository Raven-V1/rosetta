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
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re

# Sidebar branding
st.sidebar.image("assets/Belvenar_logo.png", width=160)
st.sidebar.markdown("**Belvenar Analytics**")
st.sidebar.divider()

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
    """
    Generate a PDF from markdown content.
    
    Args:
        markdown_content: The markdown text to convert to PDF
        database_name: Name of the database for the title
        
    Returns:
        bytes: PDF file content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=12,
        spaceBefore=12,
        backColor=colors.HexColor('#f5f5f5')
    )
    
    body_style = styles['BodyText']
    
    story = []
    
    # Parse markdown content line by line
    lines = markdown_content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    # Escape special characters for reportlab
                    code_text = code_text.replace('&', '&').replace('<', '<').replace('>', '>')
                    story.append(Paragraph(f'<font name="Courier">{code_text}</font>', code_style))
                    code_lines = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Skip empty lines
        if not line.strip():
            if story:  # Only add spacer if there's content before it
                story.append(Spacer(1, 6))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading1_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, heading2_style))
        elif line.startswith('#### '):
            text = line[5:].strip()
            story.append(Paragraph(text, heading3_style))
        # Handle horizontal rules
        elif line.strip() == '---':
            story.append(Spacer(1, 12))
        # Handle bold text and other formatting
        elif line.strip().startswith('**') or line.strip().startswith('- ') or line.strip().startswith('|'):
            # Process markdown formatting
            text = line.strip()
            # Convert markdown bold to HTML bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Convert markdown italic to HTML italic
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            # Handle list items
            if text.startswith('- '):
                text = '• ' + text[2:]
            # Escape special characters
            text = text.replace('&', '&').replace('<b>', '<b>').replace('</b>', '</b>').replace('<i>', '<i>').replace('</i>', '</i>')
            story.append(Paragraph(text, body_style))
        else:
            # Regular paragraph
            text = line.strip()
            # Convert markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            story.append(Paragraph(text, body_style))
        
        i += 1
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# Generate PDF
pdf_data = generate_pdf(markdown_content, database_name)

filename = f"{database_name}_onboarding.pdf"

st.download_button(
    label="Download PDF File",
    data=pdf_data,
    file_name=filename,
    mime="application/pdf",
    use_container_width=True
)

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
