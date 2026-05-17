"""
Overview Page - Database Overview
Displays high-level database information and metrics.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Display database name and server as page header
- Metrics row: table count, relationship count, introspection time
- LLM-generated overview text in a styled container
- Table breakdown: list schemas with table counts
- No business logic, reads only from session_manager
"""

import streamlit as st
from src import session_manager
from src.ui_utils import render_sidebar_brand

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Overview</h1>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Connection guard
if not session_manager.is_connected():
    st.markdown("""
    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#ff8389;'>⚠ No database connection found. Please connect to a database on the Home page.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Get data from session
metadata = session_manager.get_metadata()
generated = session_manager.get_generated_content()
introspection_time = session_manager.get_introspection_time()

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.markdown(f"<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>{database_name}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;'>Server: {server}</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Metrics row
tables = metadata.get('tables', [])
relationships = metadata.get('relationships', [])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Tables",
        value=len(tables)
    )

with col2:
    st.metric(
        label="Relationships",
        value=len(relationships)
    )

with col3:
    st.metric(
        label="Introspection Time",
        value=f"{introspection_time:.2f}s"
    )

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# LLM-generated overview text in styled container with IBM Carbon design tokens
overview_text = generated.get('overview', '')

if overview_text:
    st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Database Overview</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    
    # Styled container for overview with IBM Carbon design tokens
    st.markdown(
        f"""
        <div style="
            background-color: #161616;
            border: 1px solid #393939;
            color: #e0e0e0;
            padding: 1.5rem;
            border-radius: 4px;
            border-left: 4px solid #0f62fe;
        ">
            {overview_text}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown("""
    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#78a9ff;'>ℹ No overview text available. This is generated during database introspection.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Table breakdown by schema
st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Table Breakdown by Schema</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

# Group tables by schema
schema_counts = {}
for table in tables:
    schema = table.get('schema', 'Unknown')
    if schema not in schema_counts:
        schema_counts[schema] = 0
    schema_counts[schema] += 1

# Sort schemas by table count (descending)
sorted_schemas = sorted(schema_counts.items(), key=lambda x: x[1], reverse=True)

if sorted_schemas:
    # Display as a clean list with IBM Carbon design tokens
    for schema, count in sorted_schemas:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<p style='font-size:0.875rem;color:#f4f4f4;font-weight:600;'>{schema}</p>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;'>{count} tables</p>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#78a9ff;'>ℹ No tables found in this database.</span>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)