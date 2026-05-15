"""
Download Page - Export Onboarding Documentation
Download the complete onboarding guide as a Markdown file.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Preview section: show first 500 characters of the markdown export
- Download button: st.download_button with the full markdown string
  filename: {database_name}_onboarding.md
  mime: text/markdown
- Stats section: show word count and section count of the export
- Calls markdown_exporter.export_to_markdown(st.session_state)
- No business logic, reads only from session_manager
"""

import streamlit as st
from src import session_manager, markdown_exporter

# Page title
st.title("⬇️ Download")

# Connection guard
if not session_manager.is_connected():
    st.warning("⚠️ No database connection found. Please connect to a database on the Home page.")
    st.stop()

# Get metadata for database name
metadata = session_manager.get_metadata()
database_name = metadata.get('database_name', 'database')

# Generate the markdown export
markdown_content = markdown_exporter.export_to_markdown(st.session_state)

st.divider()

# Preview section
st.subheader("📄 Preview")
st.caption("First 500 characters of the export:")

preview_text = markdown_content[:500]
if len(markdown_content) > 500:
    preview_text += "..."

st.code(preview_text, language="markdown")

st.divider()

# Stats section
st.subheader("📊 Export Statistics")

# Calculate word count
word_count = len(markdown_content.split())

# Calculate section count (count lines starting with ##)
section_count = markdown_content.count('\n## ')

col1, col2 = st.columns(2)

with col1:
    st.metric("Word Count", f"{word_count:,}")

with col2:
    st.metric("Sections", section_count)

st.divider()

# Download button
st.subheader("💾 Download")

filename = f"{database_name}_onboarding.md"

st.download_button(
    label="📥 Download Markdown File",
    data=markdown_content,
    file_name=filename,
    mime="text/markdown",
    use_container_width=True
)

st.info(f"ℹ️ The file will be saved as `{filename}`")

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob