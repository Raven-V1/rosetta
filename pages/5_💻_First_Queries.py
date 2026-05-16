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
from src import session_manager, llm_generator, query_executor

# Page title
st.title("💻 First Queries")

# Connection guard
if not session_manager.is_connected():
    st.warning("⚠️ No database connection found. Please connect to a database on the Home page.")
    st.stop()

# Get data from session
metadata = session_manager.get_metadata()
generated = session_manager.get_generated_content()

# Page header with database info
database_name = metadata.get('database_name', 'Unknown')
server = metadata.get('server', 'Unknown')

st.header(f"{database_name}")
st.caption(f"Server: {server}")

st.divider()

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
            
            st.success(f"✅ Generated {len(sample_queries)} sample queries")
        except Exception as e:
            st.error(f"❌ Failed to generate sample queries: {str(e)}")
            st.stop()

# Display introduction
st.markdown("""
These sample queries demonstrate common patterns and operations in this database.
Click **Run Query** to execute any query and see the results.
""")

st.divider()

# Display each query
for idx, query in enumerate(sample_queries):
    # Extract query details
    title = query.get('title', f'Query {idx + 1}')
    annotation = query.get('annotation', '')
    sql = query.get('sql', '')
    
    # Display query number and title
    st.subheader(f"{idx + 1}. {title}")
    
    # Display annotation (explanation)
    if annotation:
        st.markdown(annotation)
    
    # Display SQL in code block
    st.code(sql, language='sql')
    
    # Run Query button
    if st.button("▶️ Run Query", key=f"run_{idx}"):
        with st.spinner("Executing query..."):
            try:
                # Get connection string
                conn_string = session_manager.get_connection_string()
                
                # Execute query
                df = query_executor.execute_query(conn_string, sql)
                
                # Check if results are empty
                if df.empty:
                    st.warning("⚠️ Query executed successfully but returned no results.")
                else:
                    # Show success message with row count
                    st.success(f"✅ Query executed successfully! Retrieved {len(df)} rows.")
                    
                    # Display results
                    st.dataframe(df, use_container_width=True)
                    
                    # CSV download button
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"query_{idx + 1}_results.csv",
                        mime="text/csv",
                        key=f"download_{idx}"
                    )
                    
            except ValueError as e:
                # Handle validation errors
                st.error(f"❌ Invalid query: {str(e)}")
            except Exception as e:
                # Handle other errors
                st.error(f"❌ Query execution failed: {str(e)}")
    
    # Add divider between queries (except after last one)
    if idx < len(sample_queries) - 1:
        st.divider()

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob