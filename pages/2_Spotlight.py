"""
Start Here Page - Top 5 Most Important Tables
Displays the most important tables in the database, ranked by the LLM.

Responsibilities:
- Guard: if not session_manager.is_connected(), show warning and stop
- Display database name and server as page header
- Generate or retrieve top 5 important tables using LLM
- Display each table as a numbered card with details
- Show table name, description, reasoning, and connection count
"""

import streamlit as st
from src import session_manager, llm_generator

# Page title
st.title("Spotlight")

# Connection guard
if not session_manager.is_connected():
    st.warning("No database connection found. Please connect to a database on the Home page.")
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

# Introduction
st.markdown("""
Welcome to your database! Below are the **top 5 most important tables** to understand first.
These tables were identified based on their relationships, data volume, and business significance.
""")

st.divider()

# Check if important_tables exist in session
important_tables = generated.get('important_tables', [])

if not important_tables:
    # Generate important tables using LLM
    with st.spinner("Analyzing database structure..."):
        try:
            important_tables = llm_generator.rank_important_tables(metadata)
            
            # Store in session for future use
            session_manager.store_generated_content({'important_tables': important_tables})
            
        except ValueError as e:
            # Authentication or configuration errors
            st.error(f"**LLM Configuration Error**")
            st.error(str(e))
            
            # Provide helpful guidance based on the error
            error_str = str(e).lower()
            if "api_key" in error_str or "apikey" in error_str:
                st.info("""
                **How to fix:**
                1. Obtain an IBM Cloud API key from https://cloud.ibm.com/iam/apikeys
                2. Set the `WATSONX_API_KEY` environment variable
                3. Restart the application
                """)
            elif "project_id" in error_str or "project" in error_str:
                st.info("""
                **How to fix:**
                1. Create or access a watsonx.ai project at https://dataplatform.cloud.ibm.com/
                2. Copy the project ID from the project settings
                3. Set the `WATSONX_PROJECT_ID` environment variable
                4. Restart the application
                """)
            else:
                st.info("Please check your IBM Cloud credentials and watsonx.ai configuration.")
            
            st.divider()
            st.markdown("*Made with Bob*")
            st.stop()
            
        except Exception as e:
            st.error(f"**Unexpected Error**")
            st.error(f"An unexpected error occurred while analyzing the database: {str(e)}")
            st.info("Please try refreshing the page or reconnecting to the database.")
            st.divider()
            st.markdown("*Made with Bob*")
            st.stop()

# Display top 5 tables
if not important_tables:
    st.info("No tables found to analyze.")
    st.divider()
    st.markdown("*Made with Bob*")
    st.stop()

st.subheader("Top 5 Most Important Tables")

# Display each table as a numbered card
for idx, table_info in enumerate(important_tables[:5], start=1):
    # Extract table information
    table_name = table_info.get('table', 'Unknown')
    description = table_info.get('description', 'No description available')
    reasoning = table_info.get('reasoning', 'No reasoning provided')
    connections = table_info.get('connections', 0)
    
    # Create a container for the card
    with st.container():
        # Card header with number and table name
        st.markdown(f"### {idx}. `{table_name}`")
        
        # Description
        st.markdown(f"**What it is:** {description}")
        
        # Reasoning
        st.markdown(f"**Why it matters:** {reasoning}")
        
        # Connection count
        connection_text = "connection" if connections == 1 else "connections"
        st.markdown(f"**Relationships:** Connected to {connections} other table{'' if connections == 1 else 's'}")
        
        # Add divider between cards (except after the last one)
        if idx < len(important_tables[:5]):
            st.divider()

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=30)
with col2:
    st.markdown("*Made with Bob*")