"""
Home Page - Database Connection
Handles initial database connection and introspection.
"""

import streamlit as st
import time
from dotenv import load_dotenv
from src import session_manager, db_inspector, llm_generator

# Load environment variables
load_dotenv()

# Sidebar branding
st.sidebar.image("assets/Belvenar_logo.png", width=80)
st.sidebar.markdown("**Belvenar Analytics**")
st.sidebar.divider()

st.markdown("<h1 style='font-size:2rem;font-weight:600;color:#f4f4f4;'>Rosetta</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>SQL Server Database Documentation Generator</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

# Check if already connected
if session_manager.is_connected():
    metadata = session_manager.get_metadata()
    database_name = metadata.get('database_name', 'Unknown')
    server = metadata.get('server', 'Unknown')
    table_count = len(metadata.get('tables', []))

    # Success status box with IBM Carbon design tokens
    st.markdown(f"""
    <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#42be65;font-weight:600;'>✓ Connected to {database_name} on {server}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Info box with IBM Carbon design tokens
    st.markdown(f"""
    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
        <span style='color:#78a9ff;'>ℹ Database contains {table_count} tables</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    if st.button("Connect to Different Database", type="primary"):
        session_manager.clear_session()
        st.rerun()

else:
    st.markdown("<h2 style='font-size:1.5rem;font-weight:600;color:#f4f4f4;'>Connect to Database</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # Try Demo button
    if st.button("🎯 Try Demo", type="secondary", use_container_width=True):
        demo_db_path = "demo_data.db"
        conn_string = f"sqlite:///{demo_db_path}"

        with st.spinner("Loading demo database..."):
            import os
            start_time = time.time()

            if not os.path.exists(demo_db_path):
                st.error("Demo database not found. Run `python create_demo_db.py` to generate it.")
                st.stop()

            try:
                st.write("Extracting database metadata...")
                metadata = db_inspector.get_database_metadata(conn_string)
                
                st.write("Generating AI-powered documentation...")
                generated_content = llm_generator.generate_tier1_content(metadata)
                
                elapsed_time = time.time() - start_time
                
                session_manager.store_metadata(metadata)
                session_manager.store_generated_content(generated_content)
                session_manager.set_connected(True, conn_string)
                session_manager.set_introspection_time(elapsed_time)
                
                # Success message with IBM Carbon design tokens
                st.markdown(f"""
                <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#42be65;font-weight:600;'>✓ Successfully connected to demo database!</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#78a9ff;'>ℹ Analyzed {len(metadata['tables'])} tables in {elapsed_time:.2f} seconds</span>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
                
            except ValueError as e:
                # Warning message with IBM Carbon design tokens
                st.markdown(f"""
                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#ff8389;'>⚠ AI generation failed: {str(e)}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#78a9ff;'>ℹ Continuing with basic documentation. Check your GROQ_API_KEY in Streamlit secrets.</span>
                </div>
                """, unsafe_allow_html=True)
                generated_content = {
                    'overview': llm_generator._get_fallback_overview(metadata),
                    'table_descriptions': llm_generator._get_fallback_descriptions(metadata.get('tables', []))
                }
                elapsed_time = time.time() - start_time
                session_manager.store_metadata(metadata)
                session_manager.store_generated_content(generated_content)
                session_manager.set_connected(True, conn_string)
                session_manager.set_introspection_time(elapsed_time)
                st.rerun()
            except Exception as e:
                # Error message with IBM Carbon design tokens
                st.markdown(f"""
                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#ff8389;'>✗ Demo connection failed: {str(e)}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'>Enter your SQL Server connection details to begin.</p>", unsafe_allow_html=True)

    with st.form("connection_form"):
        server = st.text_input(
            "Server",
            value="localhost",
            help="SQL Server hostname or IP address. Use localhost\\INSTANCENAME for named instances."
        )

        database = st.text_input(
            "Database",
            value="",
            help="Database name to connect to"
        )

        auth_method = st.radio(
            "Authentication Method",
            options=["Windows Authentication", "SQL Server Authentication"],
            help="Choose how to authenticate with SQL Server"
        )

        username = None
        password = None
        if auth_method == "SQL Server Authentication":
            username = st.text_input("Username", placeholder="sa")
            password = st.text_input("Password", type="password")

        timeout = st.number_input(
            "Connection Timeout (seconds)",
            min_value=5,
            max_value=120,
            value=30
        )

        submitted = st.form_submit_button("Connect and Analyze", type="primary")

    if submitted:
        if not all([server, database]):
            st.error("Server and Database fields are required")
        elif auth_method == "SQL Server Authentication" and not all([username, password]):
            st.error("Username and Password are required for SQL Server Authentication")
        else:
            server_str = server.strip()
            is_local = server_str.lower() in ('localhost', '.', '(local)')
            # Use shared-memory protocol for local connections (no TCP/IP required)
            effective_server = f"lpc:{server_str}" if is_local else server_str

            if auth_method == "Windows Authentication":
                conn_string = (
                    f"Driver={{ODBC Driver 17 for SQL Server}};"
                    f"Server={effective_server};"
                    f"Database={database};"
                    f"Trusted_Connection=yes;"
                    f"TrustServerCertificate=yes;"
                    f"Connection Timeout={timeout};"
                )
            else:
                conn_string = (
                    f"Driver={{ODBC Driver 17 for SQL Server}};"
                    f"Server={effective_server};"
                    f"Database={database};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"TrustServerCertificate=yes;"
                    f"Connection Timeout={timeout};"
                )

            with st.spinner("Connecting and analyzing database..."):
                start_time = time.time()

                try:
                    st.write("Extracting database metadata...")
                    metadata = db_inspector.get_database_metadata(conn_string)
                except Exception as e:
                    err_str = str(e)
                    st.markdown(f"""
                    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#ff8389;'>✗ Database connection failed: {err_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if 'HYT00' in err_str or 'timeout' in err_str.lower():
                        st.markdown("""
                        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#78a9ff;'><strong>Login timeout — common causes:</strong><br>
                            - Use the exact server name from SSMS: open SSMS, the name shown in the connection dialog is what to enter here<br>
                            - Named instance: use <code>COMPUTERNAME\\SQLEXPRESS</code> or <code>localhost\\SQLEXPRESS</code><br>
                            - SQL Server service is not running: check Services or SQL Server Configuration Manager<br>
                            - TCP/IP disabled: SQL Server Configuration Manager &gt; SQL Server Network Configuration &gt; enable TCP/IP, then restart the service</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#78a9ff;'><strong>Troubleshooting tips:</strong><br>
                            - Verify server name and database name are correct<br>
                            - Ensure the authentication method matches your SQL Server config<br>
                            - Confirm ODBC Driver 17 for SQL Server is installed</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.stop()

                try:
                    st.write("Generating AI-powered documentation...")
                    generated_content = llm_generator.generate_tier1_content(metadata)
                except ValueError as e:
                    st.markdown(f"""
                    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#ff8389;'>⚠ AI generation failed: {str(e)}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("""
                    <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#78a9ff;'>ℹ Continuing with basic documentation. Check your GROQ_API_KEY in Streamlit secrets.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    generated_content = {
                        'overview': llm_generator._get_fallback_overview(metadata),
                        'table_descriptions': llm_generator._get_fallback_descriptions(metadata.get('tables', []))
                    }
                except Exception as e:
                    st.markdown(f"""
                    <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                        <span style='color:#ff8389;'>⚠ AI generation encountered an error: {str(e)}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    generated_content = {
                        'overview': llm_generator._get_fallback_overview(metadata),
                        'table_descriptions': llm_generator._get_fallback_descriptions(metadata.get('tables', []))
                    }

                elapsed_time = time.time() - start_time

                session_manager.store_metadata(metadata)
                session_manager.store_generated_content(generated_content)
                session_manager.set_connected(True, conn_string)
                session_manager.set_introspection_time(elapsed_time)

                st.markdown(f"""
                <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#42be65;font-weight:600;'>✓ Successfully connected to {metadata['database_name']} on {metadata['server']}</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                    <span style='color:#78a9ff;'>ℹ Analyzed {len(metadata['tables'])} tables in {elapsed_time:.2f} seconds</span>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()

# Footer
st.divider()
col1, col2 = st.columns([1, 11])
with col1:
    st.image("assets/bob_logo.png", width=50)
with col2:
    st.markdown("*Made with Bob*", unsafe_allow_html=True)