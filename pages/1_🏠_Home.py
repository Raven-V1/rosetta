"""
Home Page - Database Connection
Handles initial database connection and introspection.

Responsibilities:
- Display hero section with title and description
- Provide connection form for SQL Server credentials
- Build pyodbc connection string from user inputs
- Trigger database introspection and LLM content generation
- Display connection status and results
- Handle reconnection for already-connected sessions
"""

import streamlit as st
import time
from src import session_manager, db_inspector, llm_generator

# Page title
st.title("🌿 Rosetta")
st.markdown("*SQL Server Database Documentation Generator*")

st.divider()

# Check if already connected
if session_manager.is_connected():
    # Already connected - show current database and reconnect option
    metadata = session_manager.get_metadata()
    database_name = metadata.get('database_name', 'Unknown')
    server = metadata.get('server', 'Unknown')
    table_count = len(metadata.get('tables', []))
    
    st.success(f"✅ Connected to **{database_name}** on **{server}**")
    st.info(f"📊 Database contains **{table_count}** tables")
    
    st.divider()
    
    # Reconnect button
    if st.button("🔄 Connect to Different Database", type="primary"):
        session_manager.clear_session()
        st.rerun()
    
else:
    # Not connected - show connection form
    st.header("Connect to Database")
    st.markdown("Enter your SQL Server connection details to begin.")
    
    # Connection form
    with st.form("connection_form"):
        server = st.text_input(
            "Server",
            placeholder="localhost or server.domain.com",
            help="SQL Server hostname or IP address"
        )
        
        database = st.text_input(
            "Database",
            placeholder="AdventureWorks2025",
            help="Database name to connect to"
        )
        
        # Authentication method
        auth_method = st.radio(
            "Authentication Method",
            options=["Windows Authentication", "SQL Server Authentication"],
            help="Choose how to authenticate with SQL Server"
        )
        
        # SQL Server Authentication fields (only show if selected)
        username = None
        password = None
        if auth_method == "SQL Server Authentication":
            username = st.text_input(
                "Username",
                placeholder="sa",
                help="SQL Server username"
            )
            password = st.text_input(
                "Password",
                type="password",
                help="SQL Server password"
            )
        
        # Connection timeout
        timeout = st.number_input(
            "Connection Timeout (seconds)",
            min_value=5,
            max_value=120,
            value=30,
            help="How long to wait for connection before timing out"
        )
        
        # Submit button
        submitted = st.form_submit_button("🔌 Connect and Analyze", type="primary")
    
    # Process connection when form is submitted
    if submitted:
        # Validate inputs
        if not all([server, database]):
            st.error("❌ Server and Database fields are required")
        elif auth_method == "SQL Server Authentication" and not all([username, password]):
            st.error("❌ Username and Password are required for SQL Server Authentication")
        else:
            # Build pyodbc connection string based on authentication method
            if auth_method == "Windows Authentication":
                conn_string = (
                    f"Driver={{ODBC Driver 17 for SQL Server}};"
                    f"Server={server};"
                    f"Database={database};"
                    f"Trusted_Connection=yes;"
                    f"Connection Timeout={timeout};"
                )
            else:
                conn_string = (
                    f"Driver={{ODBC Driver 17 for SQL Server}};"
                    f"Server={server};"
                    f"Database={database};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"Connection Timeout={timeout};"
                )
            
            # Show spinner during introspection
            with st.spinner("🔍 Connecting and analyzing database..."):
                start_time = time.time()
                
                try:
                    # Step 1: Get database metadata
                    st.write("📊 Extracting database metadata...")
                    metadata = db_inspector.get_database_metadata(conn_string)
                    
                    # Step 2: Generate LLM content
                    st.write("🤖 Generating AI-powered documentation...")
                    generated_content = llm_generator.generate_tier1_content(metadata)
                    
                    # Calculate elapsed time
                    elapsed_time = time.time() - start_time
                    
                    # Step 3: Store in session state
                    session_manager.store_metadata(metadata)
                    session_manager.store_generated_content(generated_content)
                    session_manager.set_connected(True, conn_string)
                    session_manager.set_introspection_time(elapsed_time)
                    
                    # Success message
                    st.success(f"✅ Successfully connected to **{metadata['database_name']}** on **{metadata['server']}**")
                    st.info(f"📊 Analyzed **{len(metadata['tables'])}** tables in **{elapsed_time:.2f}** seconds")
                    
                    # Rerun to show connected state
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    # Error handling
                    st.error(f"❌ Connection failed: {str(e)}")
                    st.markdown("""
                    **Troubleshooting tips:**
                    - Verify server name and database name are correct
                    - Ensure SQL Server authentication is enabled
                    - Check username and password credentials
                    - Confirm network connectivity to the server
                    - Verify ODBC Driver 17 for SQL Server is installed
                    """)

# Footer
st.divider()
st.markdown("*Made with Bob*")

# Made with Bob