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

# Page title
st.title("📊 Overview")

# Connection guard
if not session_manager.is_connected():
    st.warning("⚠️ No database connection found. Please connect to a database on the Home page.")
    st.stop()

# Get data from session
metadata = session_manager.get_metadata()
generated = session_manager.get_generated_content()
introspection_time = session_manager.get_introspection_time()

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.header(f"{database_name}")
st.caption(f"Server: {server}")

st.divider()

# Metrics row
tables = metadata.get('tables', [])
relationships = metadata.get('relationships', [])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📋 Tables",
        value=len(tables)
    )

with col2:
    st.metric(
        label="🔗 Relationships",
        value=len(relationships)
    )

with col3:
    st.metric(
        label="⏱️ Introspection Time",
        value=f"{introspection_time:.2f}s"
    )

st.divider()

# LLM-generated overview text in styled container
overview_text = generated.get('overview', '')

if overview_text:
    st.subheader("Database Overview")
    
    # Styled container for overview
    st.markdown(
        f"""
        <div style="
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
        ">
            {overview_text}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("ℹ️ No overview text available. This is generated during database introspection.")

st.divider()

# Table breakdown by schema
st.subheader("Table Breakdown by Schema")

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
    # Display as a clean list
    for schema, count in sorted_schemas:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{schema}**")
        with col2:
            st.markdown(f"{count} tables")
else:
    st.info("ℹ️ No tables found in this database.")

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob