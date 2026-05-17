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
from dotenv import load_dotenv
from src import session_manager, llm_generator
from src.ui_utils import render_sidebar_brand

# Load environment variables
load_dotenv()

render_sidebar_brand()

# Page title with IBM Carbon design tokens
st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Spotlight</h1>", unsafe_allow_html=True)

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

# Introduction
st.markdown("<p style='font-size:0.875rem;color:#e0e0e0;'>Welcome to your database! Below are the <strong>top 5 most important tables</strong> to understand first. These tables were identified based on their relationships, data volume, and business significance.</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

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
            # Authentication or configuration errors with IBM Carbon design tokens
            st.markdown("""
            <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#ff8389;font-weight:600;'>✗ LLM Configuration Error</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.875rem;color:#ff8389;'>{str(e)}</p>", unsafe_allow_html=True)
            
            st.markdown("""
                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#78a9ff;'>ℹ Check your GROQ_API_KEY in Streamlit secrets (Settings &gt; Secrets).</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
            st.markdown("*Made with Bob*")
            st.stop()
            
        except Exception as e:
            st.markdown("""
            <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#ff8389;font-weight:600;'>✗ Unexpected Error</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.875rem;color:#ff8389;'>An unexpected error occurred while analyzing the database: {str(e)}</p>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                <span style='color:#78a9ff;'>ℹ Please try refreshing the page or reconnecting to the database.</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
            st.markdown("*Made with Bob*")
            st.stop()

# Display top 5 tables
if not important_tables:
    st.markdown("""
    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#78a9ff;'>ℹ No tables found to analyze.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    st.markdown("*Made with Bob*")
    st.stop()

st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Top 5 Most Important Tables</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

# Display each table as a numbered card
for idx, table_info in enumerate(important_tables[:5], start=1):
    # Extract table information
    table_name = table_info.get('table', 'Unknown')
    description = table_info.get('description', 'No description available')
    reasoning = table_info.get('reasoning', 'No reasoning provided')
    connections = table_info.get('connections', 0)
    
    # Create a container for the card with IBM Carbon design tokens
    with st.container():
        # Card header with number and table name
        st.markdown(f"<h3 style='font-size:1.25rem;font-weight:600;color:#f4f4f4;'>{idx}. {table_name}</h3>", unsafe_allow_html=True)
        
        # Description
        st.markdown(f"<p style='font-size:0.875rem;color:#e0e0e0;'><strong>What it is:</strong> {description}</p>", unsafe_allow_html=True)
        
        # Reasoning
        st.markdown(f"<p style='font-size:0.875rem;color:#e0e0e0;'><strong>Why it matters:</strong> {reasoning}</p>", unsafe_allow_html=True)
        
        # Connection count
        connection_text = "connection" if connections == 1 else "connections"
        st.markdown(f"<p style='font-size:0.875rem;color:#e0e0e0;'><strong>Relationships:</strong> Connected to {connections} other table{'' if connections == 1 else 's'}</p>", unsafe_allow_html=True)
        
        # Add spacing between cards (except after the last one)
        if idx < len(important_tables[:5]):
            st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)