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

# Page title
st.title("📖 Glossary")

# Connection guard
if not session_manager.is_connected():
    st.warning("⚠️ No database connection found. Please connect to a database on the Home page.")
    st.stop()

# Get data from session
metadata = session_manager.get_metadata()
generated = session_manager.get_generated_content()

tables = metadata.get('tables', [])
table_descriptions = generated.get('table_descriptions', {})

# Get unique schemas for filter
schemas = sorted(list(set(table.get('schema', 'Unknown') for table in tables)))

st.divider()

# Filters row
col1, col2 = st.columns([2, 1])

with col1:
    # Search box
    search_query = st.text_input(
        "🔍 Search tables",
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

st.divider()

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
st.caption(f"Showing {len(filtered_tables)} of {len(tables)} tables")

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
        
        # Create expander for each table
        with st.expander(f"**{schema}.{name}** ({row_count:,} rows)"):
            # Show description
            st.markdown(f"*{description}*")
            
            st.divider()
            
            # Show columns in a clean format
            if columns:
                st.markdown("**Columns:**")
                
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
                            padding: 8px;
                            margin: 4px 0;
                            background-color: #f9f9f9;
                            border-radius: 5px;
                            display: flex;
                            justify-content: space-between;
                        ">
                            <span><strong>{col_name}</strong></span>
                            <span style="color: #666;">{col_type}</span>
                            <span style="color: {nullable_color}; font-size: 0.85em;">{nullable_indicator}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("ℹ️ No column information available.")
else:
    # No results found
    if search_query or selected_schema != "All Schemas":
        st.info("🔍 No tables match your search criteria. Try adjusting your filters.")
    else:
        st.info("ℹ️ No tables found in this database.")

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob