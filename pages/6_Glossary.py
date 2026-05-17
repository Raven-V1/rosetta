"""
Glossary Page - Table Reference
Searchable and filterable table glossary with detailed information.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Search box that filters tables by name in real time
- Table list: each entry shows table name, schema, row count, one-line description
- Click to expand: shows full column list with name, type, nullable
- Schema filter dropdown (All Schemas, or specific schema)
- No business logic, reads only from session_manager
"""

import streamlit as st
from src import session_manager
from src.ui_utils import render_sidebar_brand

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Glossary</h1>", unsafe_allow_html=True)

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

tables = metadata.get('tables', [])
table_descriptions = generated.get('table_descriptions', {})

# Get unique schemas for filter
schemas = sorted(list(set(table.get('schema', 'Unknown') for table in tables)))

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Filters row
col1, col2 = st.columns([2, 1])

with col1:
    # Search box
    search_query = st.text_input(
        "Search tables",
        placeholder="Type to filter by table name...",
        label_visibility="collapsed"
    )

with col2:
    # Schema filter dropdown
    schema_options = ["All Schemas"] + schemas
    selected_schema = st.selectbox(
        "Schema Filter",
        options=schema_options,
        label_visibility="collapsed"
    )

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Filter tables based on search and schema
filtered_tables = tables

# Apply schema filter
if selected_schema != "All Schemas":
    filtered_tables = [t for t in filtered_tables if t.get('schema') == selected_schema]

# Apply search filter (case-insensitive)
if search_query:
    search_lower = search_query.lower()
    filtered_tables = [
        t for t in filtered_tables 
        if search_lower in t.get('name', '').lower()
    ]

# Display results count
st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;'>Showing {len(filtered_tables)} of {len(tables)} tables</p>", unsafe_allow_html=True)

# Display filtered tables
if filtered_tables:
    for table in filtered_tables:
        schema = table.get('schema', 'Unknown')
        name = table.get('name', 'Unknown')
        row_count = table.get('row_count', 0)
        columns = table.get('columns', [])
        
        # Get table description (one-line)
        table_key = f"{schema}.{name}"
        description = table_descriptions.get(table_key, "No description available.")
        
        # Create expander for each table with IBM Carbon design tokens
        with st.expander(f"**{schema}.{name}** ({row_count:,} rows)"):
            # Show description
            st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;font-style:italic;'>{description}</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            
            # Show columns in a clean format
            if columns:
                st.markdown("<p style='font-size:0.875rem;color:#f4f4f4;font-weight:600;'>Columns:</p>", unsafe_allow_html=True)
                
                # Create a table-like display
                for col in columns:
                    col_name = col.get('name', 'Unknown')
                    col_type = col.get('type', 'Unknown')
                    col_nullable = col.get('nullable', False)
                    
                    # Format nullable indicator
                    nullable_indicator = "NULL" if col_nullable else "NOT NULL"
                    nullable_color = "#888888" if col_nullable else "#4CAF50"
                    
                    # Display column info
                    st.markdown(
                        f"""
                        <div style="
                            padding: 0.75rem;
                            margin: 0.25rem 0;
                            background-color: #161616;
                            border: 1px solid #393939;
                            border-radius: 4px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        ">
                            <span style="color: #f4f4f4; flex: 1;"><strong>{col_name}</strong></span>
                            <span style="color: #c6c6c6; flex: 1; text-align: center;">{col_type}</span>
                            <span style="color: {nullable_color}; font-size: 0.875rem; flex: 0 0 80px; text-align: right;">{nullable_indicator}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("""
                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#78a9ff;'>ℹ No column information available.</span>
                </div>
                """, unsafe_allow_html=True)
else:
    # No results found with IBM Carbon design tokens
    if search_query or selected_schema != "All Schemas":
        st.markdown("""
        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
            <span style='color:#78a9ff;'>ℹ No tables match your search criteria. Try adjusting your filters.</span>
        </div>
        """, unsafe_allow_html=True)
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