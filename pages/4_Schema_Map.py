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
from src.ui_utils import render_sidebar_brand

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Schema Map</h1>", unsafe_allow_html=True)

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
tables = metadata.get('tables', [])
relationships = metadata.get('relationships', [])

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.markdown(f"<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>{database_name}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;'>Server: {server}</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Check if there are tables to visualize
if not tables:
    st.markdown("""
    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#78a9ff;'>ℹ No tables found in this database.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    st.markdown("*Made with Bob*")
    st.stop()

# Import streamlit-agraph for graph visualization
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    
    st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Database Schema Visualization</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>Interactive graph showing tables and their relationships. Drag nodes to rearrange.</p>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    
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
        
        # Only include edge if both tables are in filtered set and not a self-referential loop
        if (parent_table in filtered_table_names and referenced_table in filtered_table_names
                and parent_table != referenced_table):
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
        st.markdown(f"""
        <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
            <span style='color:#ff8389;'>⚠ Graph visualization failed: {str(graph_error)}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
            <span style='color:#78a9ff;'>ℹ Displaying relationships in table format instead.</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Fallback: Display relationships as a table
        if relationships:
            st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Foreign Key Relationships</h2>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            
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
            st.markdown("""
            <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#78a9ff;'>ℹ No relationships found in this database.</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    
    # Display legend for schema colors
    st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Schema Legend</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    
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
    st.markdown("""
    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#ff8389;'>✗ Graph visualization requires the streamlit-agraph package.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>To install it, run:</p>", unsafe_allow_html=True)
    st.code("pip install streamlit-agraph", language="bash")
    
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    
    # Fallback: Display relationships as a table
    if relationships:
        st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Foreign Key Relationships</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>Install streamlit-agraph to see the interactive graph visualization.</p>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        
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
        st.markdown("""
        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
            <span style='color:#78a9ff;'>ℹ No relationships found in this database.</span>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)