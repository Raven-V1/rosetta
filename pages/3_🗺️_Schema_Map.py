"""
Schema Map Page - Visual Database Schema Relationships
Displays an interactive graph visualization of database tables and their relationships.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Display database name and server as page header
- Create interactive graph visualization using streamlit-agraph
- Show nodes for tables (sized by row count, colored by schema)
- Show edges for foreign key relationships
- Display legend for schema colors
- Fallback to table view if graph rendering fails
"""

import streamlit as st
from src import session_manager

# Page title
st.title("🗺️ Schema Map")

# Connection guard
if not session_manager.is_connected():
    st.warning("⚠️ No database connection found. Please connect to a database on the Home page.")
    st.stop()

# Get data from session
metadata = session_manager.get_metadata()
tables = metadata.get('tables', [])
relationships = metadata.get('relationships', [])

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.header(f"{database_name}")
st.caption(f"Server: {server}")

st.divider()

# Check if there are tables to visualize
if not tables:
    st.info("ℹ️ No tables found in this database.")
    st.divider()
    st.markdown("*Made with Bob*")
    st.stop()

# Import streamlit-agraph for graph visualization
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    
    st.subheader("Database Schema Visualization")
    st.markdown("Interactive graph showing tables and their relationships. Drag nodes to rearrange.")
    
    # Extract all unique schemas from tables
    all_schemas = list(set(table.get('schema', 'Unknown') for table in tables))
    all_schemas.sort()  # Sort for consistent display
    
    # Schema filter multiselect
    selected_schemas = st.multiselect(
        "Filter by Schema:",
        options=all_schemas,
        default=all_schemas
    )
    
    # Filter tables based on selected schemas
    if selected_schemas:
        filtered_tables = [t for t in tables if t.get('schema', 'Unknown') in selected_schemas]
    else:
        filtered_tables = tables
    
    # Create color mapping for schemas
    schemas = all_schemas
    color_palette = [
        "#FF6B6B",  # Red
        "#4ECDC4",  # Teal
        "#45B7D1",  # Blue
        "#FFA07A",  # Light Salmon
        "#98D8C8",  # Mint
        "#F7DC6F",  # Yellow
        "#BB8FCE",  # Purple
        "#85C1E2",  # Sky Blue
        "#F8B739",  # Orange
        "#52B788",  # Green
    ]
    
    schema_colors = {}
    for idx, schema in enumerate(schemas):
        schema_colors[schema] = color_palette[idx % len(color_palette)]
    
    # Create nodes for each filtered table
    nodes = []
    for table in filtered_tables:
        schema = table.get('schema', 'Unknown')
        table_name = table.get('name', 'Unknown')
        row_count = table.get('row_count', 0)
        
        # Full table identifier (used as node id for edge connections)
        full_name = f"{schema}.{table_name}"
        
        # Calculate node size based on row count
        # Min size 10, scale by row_count/100, max size 50
        node_size = min(10 + row_count / 100, 50)
        
        # Create node with simplified label (just table name)
        node = Node(
            id=full_name,
            label=table_name,  # Show only table name, not schema prefix
            size=node_size,
            color=schema_colors.get(schema, "#CCCCCC")
        )
        nodes.append(node)
    
    # Create set of filtered table full names for quick lookup
    filtered_table_names = set(f"{t.get('schema', 'Unknown')}.{t.get('name', 'Unknown')}" for t in filtered_tables)
    
    # Create edges for relationships where both tables are in selected schemas
    edges = []
    for rel in relationships:
        parent_table = rel.get('parent_table', '')
        referenced_table = rel.get('referenced_table', '')
        
        # Only include edge if both parent and referenced tables are in filtered set
        if parent_table in filtered_table_names and referenced_table in filtered_table_names:
            # Create edge without label
            edge = Edge(
                source=parent_table,
                target=referenced_table,
                type="CURVE_SMOOTH"
            )
            edges.append(edge)
    
    # Configure graph visualization
    config = Config(
        width="100%",
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        node={
            'labelProperty': 'label',
            'renderLabel': True,
            'fontSize': 12,
            'fontColor': '#000000'
        },
        link={
            'renderLabel': False  # Don't render edge labels
        }
    )
    
    # Render the graph
    try:
        agraph(nodes=nodes, edges=edges, config=config)
    except Exception as graph_error:
        st.warning(f"⚠️ Graph visualization failed: {str(graph_error)}")
        st.info("Displaying relationships in table format instead.")
        
        # Fallback: Display relationships as a table
        if relationships:
            st.subheader("Foreign Key Relationships")
            
            # Prepare data for display
            rel_data = []
            for rel in relationships:
                rel_data.append({
                    'FK Name': rel.get('fk_name', 'N/A'),
                    'From Table': rel.get('parent_table', 'N/A'),
                    'From Column': rel.get('parent_column', 'N/A'),
                    'To Table': rel.get('referenced_table', 'N/A'),
                    'To Column': rel.get('referenced_column', 'N/A')
                })
            
            st.dataframe(rel_data, use_container_width=True)
        else:
            st.info("ℹ️ No relationships found in this database.")
    
    st.divider()
    
    # Display legend for schema colors
    st.subheader("Schema Legend")
    
    # Create columns for legend (max 4 per row)
    num_schemas = len(schemas)
    cols_per_row = 4
    num_rows = (num_schemas + cols_per_row - 1) // cols_per_row
    
    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            schema_idx = row * cols_per_row + col_idx
            if schema_idx < num_schemas:
                schema = schemas[schema_idx]
                color = schema_colors[schema]
                with cols[col_idx]:
                    # Display color swatch with schema name
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="
                                width: 20px;
                                height: 20px;
                                background-color: {color};
                                border-radius: 50%;
                                margin-right: 10px;
                                border: 1px solid #ccc;
                            "></div>
                            <span style="font-size: 14px;">{schema}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

except ImportError:
    # streamlit-agraph not installed
    st.error("❌ Graph visualization requires the `streamlit-agraph` package.")
    st.markdown("""
    To install it, run:
    ```bash
    pip install streamlit-agraph
    ```
    """)
    
    st.divider()
    
    # Fallback: Display relationships as a table
    if relationships:
        st.subheader("Foreign Key Relationships")
        st.markdown("*Install streamlit-agraph to see the interactive graph visualization.*")
        
        # Prepare data for display
        rel_data = []
        for rel in relationships:
            rel_data.append({
                'FK Name': rel.get('fk_name', 'N/A'),
                'From Table': rel.get('parent_table', 'N/A'),
                'From Column': rel.get('parent_column', 'N/A'),
                'To Table': rel.get('referenced_table', 'N/A'),
                'To Column': rel.get('referenced_column', 'N/A')
            })
        
        st.dataframe(rel_data, use_container_width=True)
    else:
        st.info("ℹ️ No relationships found in this database.")

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob