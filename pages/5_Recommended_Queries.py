"""
First Queries Page - Sample SQL Queries
Displays LLM-generated sample queries and allows users to execute them.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Generate sample queries if not already generated
- Display each query with title, annotation, and SQL code
- Allow users to execute queries and view results
- Provide CSV download for query results
"""

import streamlit as st
from dotenv import load_dotenv
from src import session_manager, llm_generator, query_executor
from src.ui_utils import render_sidebar_brand

# Load environment variables
load_dotenv()

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Recommended Queries</h1>", unsafe_allow_html=True)

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

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.markdown(f"<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>{database_name}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:0.875rem;color:#c6c6c6;'>Server: {server}</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Check if sample queries exist, generate if not
sample_queries = generated.get('sample_queries', [])

if not sample_queries:
    # Generate sample queries
    with st.spinner("Generating sample queries..."):
        try:
            sample_queries = llm_generator.generate_sample_queries(metadata)
            
            # Store in session
            session_manager.store_generated_content({
                'sample_queries': sample_queries
            })
            
            st.markdown(f"""
            <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#42be65;font-weight:600;'>✓ Generated {len(sample_queries)} sample queries</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#ff8389;'>✗ Failed to generate sample queries: {str(e)}</span>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

# Display introduction
st.markdown("<p style='font-size:0.875rem;color:#e0e0e0;'>These sample queries demonstrate common patterns and operations in this database. Click <strong>Run Query</strong> to execute any query and see the results.</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Display each query
for idx, query in enumerate(sample_queries):
    # Extract query details
    title = query.get('title', f'Query {idx + 1}')
    annotation = query.get('annotation', '')
    sql = query.get('sql', '')
    
    # Display query number and title with IBM Carbon design tokens
    st.markdown(f"<h3 style='font-size:1.25rem;font-weight:600;color:#f4f4f4;'>{idx + 1}. {title}</h3>", unsafe_allow_html=True)
    
    # Display annotation (explanation)
    if annotation:
        st.markdown(f"<p style='font-size:0.875rem;color:#e0e0e0;'>{annotation}</p>", unsafe_allow_html=True)
    
    # Display SQL in code block
    st.code(sql, language='sql')
    
    # Run Query button
    if st.button("Run Query", key=f"run_{idx}"):
        with st.spinner("Executing query..."):
            try:
                # Get connection string
                conn_string = session_manager.get_connection_string()
                
                # Execute query
                df = query_executor.execute_query(conn_string, sql)
                
                # Check if results are empty
                if df.empty:
                    st.markdown("""
                    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#ff8389;'>⚠ Query executed successfully but returned no results.</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show success message with row count
                    st.markdown(f"""
                    <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#42be65;font-weight:600;'>✓ Query executed successfully! Retrieved {len(df)} rows.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display results
                    st.dataframe(df, use_container_width=True)
                    
                    # CSV download button
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"query_{idx + 1}_results.csv",
                        mime="text/csv",
                        key=f"download_{idx}"
                    )
                    
            except ValueError as e:
                # Handle validation errors with IBM Carbon design tokens
                st.markdown(f"""
                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#ff8389;'>✗ Invalid query: {str(e)}</span>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                # Handle other errors with IBM Carbon design tokens
                st.markdown(f"""
                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#ff8389;'>✗ Query execution failed: {str(e)}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Add spacing between queries (except after last one)
    if idx < len(sample_queries) - 1:
        st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)