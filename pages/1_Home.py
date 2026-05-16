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
st.sidebar.image("assets/Belvenar_logo.png", width=160)
st.sidebar.markdown("**Belvenar Analytics**")
st.sidebar.divider()

# Page title with IBM Carbon design tokens
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

    # Initialize saved_connections in session_manager
    session_manager._initialize_session_state()

    # Try Demo button above tabs
    if st.button("🎯 Try Demo", type="secondary", use_container_width=True):
        demo_db_path = "demo_data.db"
        conn_string = f"sqlite:///{demo_db_path}"
        
        with st.spinner("Loading demo database..."):
            import os
            import time
            start_time = time.time()
            
            # Check if demo database exists, create if not
            if not os.path.exists(demo_db_path):
                st.info("Creating demo database...")
                import sqlite3
                conn = sqlite3.connect(demo_db_path)
                cursor = conn.cursor()
                
                # Create tables with realistic data
                cursor.execute("""
                    CREATE TABLE customers (
                        customer_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE products (
                        product_id INTEGER PRIMARY KEY,
                        product_name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL,
                        stock_quantity INTEGER DEFAULT 0
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE orders (
                        order_id INTEGER PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        total_amount REAL NOT NULL,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE order_items (
                        order_item_id INTEGER PRIMARY KEY,
                        order_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        unit_price REAL NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders(order_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE departments (
                        department_id INTEGER PRIMARY KEY,
                        department_name TEXT NOT NULL,
                        location TEXT,
                        budget REAL
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE employees (
                        employee_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        department_id INTEGER,
                        hire_date TEXT,
                        salary REAL,
                        FOREIGN KEY (department_id) REFERENCES departments(department_id)
                    )
                """)
                
                # Insert sample data
                customers_data = [
                    (1, 'John', 'Doe', 'john.doe@email.com', '555-0101', '2024-01-15'),
                    (2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', '2024-01-16'),
                    (3, 'Bob', 'Johnson', 'bob.j@email.com', '555-0103', '2024-01-17'),
                    (4, 'Alice', 'Williams', 'alice.w@email.com', '555-0104', '2024-01-18'),
                    (5, 'Charlie', 'Brown', 'charlie.b@email.com', '555-0105', '2024-01-19'),
                    (6, 'Diana', 'Davis', 'diana.d@email.com', '555-0106', '2024-01-20'),
                    (7, 'Eve', 'Miller', 'eve.m@email.com', '555-0107', '2024-01-21'),
                    (8, 'Frank', 'Wilson', 'frank.w@email.com', '555-0108', '2024-01-22'),
                    (9, 'Grace', 'Moore', 'grace.m@email.com', '555-0109', '2024-01-23'),
                    (10, 'Henry', 'Taylor', 'henry.t@email.com', '555-0110', '2024-01-24'),
                    (11, 'Ivy', 'Anderson', 'ivy.a@email.com', '555-0111', '2024-01-25'),
                    (12, 'Jack', 'Thomas', 'jack.t@email.com', '555-0112', '2024-01-26'),
                    (13, 'Kate', 'Jackson', 'kate.j@email.com', '555-0113', '2024-01-27'),
                    (14, 'Leo', 'White', 'leo.w@email.com', '555-0114', '2024-01-28'),
                    (15, 'Mia', 'Harris', 'mia.h@email.com', '555-0115', '2024-01-29'),
                    (16, 'Noah', 'Martin', 'noah.m@email.com', '555-0116', '2024-01-30'),
                    (17, 'Olivia', 'Garcia', 'olivia.g@email.com', '555-0117', '2024-01-31'),
                    (18, 'Paul', 'Martinez', 'paul.m@email.com', '555-0118', '2024-02-01'),
                    (19, 'Quinn', 'Robinson', 'quinn.r@email.com', '555-0119', '2024-02-02'),
                    (20, 'Ruby', 'Clark', 'ruby.c@email.com', '555-0120', '2024-02-03')
                ]
                cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)', customers_data)
                
                products_data = [
                    (1, 'Laptop Pro', 'Electronics', 1299.99, 50),
                    (2, 'Wireless Mouse', 'Electronics', 29.99, 200),
                    (3, 'USB-C Cable', 'Accessories', 19.99, 500),
                    (4, 'Monitor 27"', 'Electronics', 399.99, 75),
                    (5, 'Keyboard Mechanical', 'Electronics', 149.99, 100),
                    (6, 'Webcam HD', 'Electronics', 79.99, 150),
                    (7, 'Headphones', 'Electronics', 199.99, 120),
                    (8, 'Desk Lamp', 'Furniture', 49.99, 80),
                    (9, 'Office Chair', 'Furniture', 299.99, 40),
                    (10, 'Standing Desk', 'Furniture', 599.99, 25),
                    (11, 'Notebook Set', 'Stationery', 14.99, 300),
                    (12, 'Pen Pack', 'Stationery', 9.99, 400),
                    (13, 'Tablet 10"', 'Electronics', 449.99, 60),
                    (14, 'Phone Case', 'Accessories', 24.99, 250),
                    (15, 'Screen Protector', 'Accessories', 12.99, 350),
                    (16, 'Power Bank', 'Electronics', 39.99, 180),
                    (17, 'Backpack', 'Accessories', 69.99, 90),
                    (18, 'Water Bottle', 'Accessories', 19.99, 200),
                    (19, 'Desk Organizer', 'Furniture', 34.99, 110),
                    (20, 'Cable Management', 'Accessories', 15.99, 220)
                ]
                cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', products_data)
                
                departments_data = [
                    (1, 'Sales', 'New York', 500000),
                    (2, 'Engineering', 'San Francisco', 1200000),
                    (3, 'Marketing', 'Chicago', 400000),
                    (4, 'HR', 'Boston', 300000),
                    (5, 'Finance', 'New York', 600000),
                    (6, 'Operations', 'Seattle', 450000),
                    (7, 'Customer Support', 'Austin', 350000),
                    (8, 'Product', 'San Francisco', 800000),
                    (9, 'Legal', 'New York', 400000),
                    (10, 'IT', 'Seattle', 550000),
                    (11, 'Research', 'Boston', 700000),
                    (12, 'Design', 'Los Angeles', 500000),
                    (13, 'Quality Assurance', 'Austin', 400000),
                    (14, 'Business Development', 'Chicago', 450000),
                    (15, 'Data Analytics', 'San Francisco', 650000),
                    (16, 'Security', 'Seattle', 500000),
                    (17, 'Training', 'Boston', 300000),
                    (18, 'Procurement', 'Chicago', 350000),
                    (19, 'Facilities', 'New York', 250000),
                    (20, 'Communications', 'Los Angeles', 400000)
                ]
                cursor.executemany('INSERT INTO departments VALUES (?, ?, ?, ?)', departments_data)
                
                employees_data = [
                    (1, 'Sarah', 'Connor', 2, '2020-03-15', 95000),
                    (2, 'John', 'Reese', 2, '2019-06-01', 105000),
                    (3, 'Emily', 'Chen', 1, '2021-01-10', 75000),
                    (4, 'Michael', 'Scott', 3, '2018-09-20', 85000),
                    (5, 'Pam', 'Beesly', 4, '2019-11-05', 65000),
                    (6, 'Jim', 'Halpert', 1, '2020-02-14', 78000),
                    (7, 'Dwight', 'Schrute', 1, '2017-05-30', 82000),
                    (8, 'Angela', 'Martin', 5, '2018-08-12', 72000),
                    (9, 'Kevin', 'Malone', 5, '2019-04-22', 68000),
                    (10, 'Oscar', 'Martinez', 5, '2020-07-18', 74000),
                    (11, 'Stanley', 'Hudson', 1, '2016-12-01', 80000),
                    (12, 'Phyllis', 'Vance', 1, '2017-03-25', 76000),
                    (13, 'Ryan', 'Howard', 8, '2021-06-15', 70000),
                    (14, 'Kelly', 'Kapoor', 7, '2020-09-08', 62000),
                    (15, 'Toby', 'Flenderson', 4, '2018-01-20', 67000),
                    (16, 'Creed', 'Bratton', 13, '2015-11-11', 71000),
                    (17, 'Meredith', 'Palmer', 6, '2017-07-04', 69000),
                    (18, 'Darryl', 'Philbin', 6, '2019-02-28', 73000),
                    (19, 'Andy', 'Bernard', 1, '2020-10-12', 77000),
                    (20, 'Erin', 'Hannon', 7, '2021-03-05', 58000)
                ]
                cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)', employees_data)
                
                orders_data = [
                    (1, 1, '2024-02-01', 1329.98, 'completed'),
                    (2, 2, '2024-02-02', 429.98, 'completed'),
                    (3, 3, '2024-02-03', 199.99, 'shipped'),
                    (4, 4, '2024-02-04', 649.98, 'completed'),
                    (5, 5, '2024-02-05', 79.99, 'pending'),
                    (6, 6, '2024-02-06', 899.98, 'completed'),
                    (7, 7, '2024-02-07', 149.99, 'shipped'),
                    (8, 8, '2024-02-08', 1899.97, 'completed'),
                    (9, 9, '2024-02-09', 334.98, 'pending'),
                    (10, 10, '2024-02-10', 599.99, 'completed'),
                    (11, 11, '2024-02-11', 24.98, 'completed'),
                    (12, 12, '2024-02-12', 449.99, 'shipped'),
                    (13, 13, '2024-02-13', 94.98, 'completed'),
                    (14, 14, '2024-02-14', 1299.99, 'pending'),
                    (15, 15, '2024-02-15', 279.98, 'completed'),
                    (16, 16, '2024-02-16', 39.99, 'shipped'),
                    (17, 17, '2024-02-17', 69.99, 'completed'),
                    (18, 18, '2024-02-18', 54.98, 'completed'),
                    (19, 19, '2024-02-19', 299.99, 'pending'),
                    (20, 20, '2024-02-20', 179.97, 'completed')
                ]
                cursor.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)', orders_data)
                
                order_items_data = [
                    (1, 1, 1, 1, 1299.99), (2, 1, 2, 1, 29.99),
                    (3, 2, 4, 1, 399.99), (4, 2, 2, 1, 29.99),
                    (5, 3, 7, 1, 199.99),
                    (6, 4, 1, 1, 1299.99), (7, 4, 5, 1, 149.99), (8, 4, 3, 10, 19.99),
                    (9, 5, 6, 1, 79.99),
                    (10, 6, 10, 1, 599.99), (11, 6, 9, 1, 299.99),
                    (12, 7, 5, 1, 149.99),
                    (13, 8, 1, 1, 1299.99), (14, 8, 10, 1, 599.99),
                    (15, 9, 9, 1, 299.99), (16, 9, 14, 1, 24.99), (17, 9, 15, 1, 12.99),
                    (18, 10, 10, 1, 599.99),
                    (19, 11, 11, 1, 14.99), (20, 11, 12, 1, 9.99),
                    (21, 12, 13, 1, 449.99),
                    (22, 13, 14, 2, 24.99), (23, 13, 15, 2, 12.99), (24, 13, 3, 1, 19.99),
                    (25, 14, 1, 1, 1299.99),
                    (26, 15, 7, 1, 199.99), (27, 15, 6, 1, 79.99),
                    (28, 16, 16, 1, 39.99),
                    (29, 17, 17, 1, 69.99),
                    (30, 18, 18, 2, 19.99), (31, 18, 15, 1, 12.99),
                    (32, 19, 9, 1, 299.99),
                    (33, 20, 2, 3, 29.99), (34, 20, 3, 5, 19.99)
                ]
                cursor.executemany('INSERT INTO order_items VALUES (?, ?, ?, ?, ?)', order_items_data)
                
                conn.commit()
                conn.close()
                st.success("Demo database created!")
            
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
                    <span style='color:#78a9ff;'>ℹ Continuing with basic documentation. Check your WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables.</span>
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

    tab1, tab2 = st.tabs(["Saved Connections", "New Connection"])

    with tab1:
        if len(st.session_state.saved_connections) == 0:
            st.info("No saved connections yet. Use the New Connection tab to create your first connection.")
        else:
            st.markdown("Select a saved connection to connect:")
            st.markdown("")

            for idx, saved_conn in enumerate(st.session_state.saved_connections):
                col1, col2 = st.columns([3, 1])

                with col1:
                    display_name = f"{saved_conn['server']} - {saved_conn['database']}"
                    st.markdown(f"**{display_name}**")
                    auth_display = saved_conn['auth_method']
                    if saved_conn['auth_method'] == "SQL Server Authentication":
                        auth_display += f" (User: {saved_conn.get('username', 'N/A')})"
                    st.caption(f"Auth: {auth_display} | Timeout: {saved_conn['timeout']}s")

                with col2:
                    if st.button("Connect", key=f"connect_saved_{idx}", type="primary"):
                        server_val = saved_conn['server']
                        database_val = saved_conn['database']
                        auth_method_val = saved_conn['auth_method']
                        timeout_val = saved_conn['timeout']

                        if auth_method_val == "SQL Server Authentication":
                            st.error("SQL Server Authentication connections require password re-entry. Please use the New Connection tab.")
                            st.stop()

                        conn_string = (
                            f"Driver={{ODBC Driver 17 for SQL Server}};"
                            f"Server={server_val};"
                            f"Database={database_val};"
                            f"Trusted_Connection=yes;"
                            f"Connection Timeout={timeout_val};"
                        )

                        with st.spinner("Connecting and analyzing database..."):
                            start_time = time.time()
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

                                # Success messages with IBM Carbon design tokens
                                st.markdown(f"""
                                <div style='background:#044317;border:1px solid #24a148;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#42be65;font-weight:600;'>✓ Successfully connected to {metadata['database_name']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#78a9ff;'>ℹ Analyzed {len(metadata['tables'])} tables in {elapsed_time:.2f} seconds</span>
                                </div>
                                """, unsafe_allow_html=True)
                                time.sleep(1)
                                st.rerun()

                            except pyodbc_error_types() as e:
                                # Error message with IBM Carbon design tokens
                                st.markdown(f"""
                                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#ff8389;'>✗ Database connection failed: {str(e)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'><strong>Troubleshooting tips:</strong></p>", unsafe_allow_html=True)
                                st.markdown("<p style='font-size:0.875rem;color:#e0e0e0;'>- Verify server name and database name are correct<br>- Ensure Windows Authentication is available<br>- Confirm network connectivity to the server<br>- Verify ODBC Driver 17 for SQL Server is installed</p>", unsafe_allow_html=True)
                            except ValueError as e:
                                st.markdown(f"""
                                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#ff8389;'>✗ AI generation failed: {str(e)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.markdown("""
                                <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#78a9ff;'>ℹ The database connected successfully but AI documentation could not be generated. Check your WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables.</span>
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.markdown(f"""
                                <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                                    <span style='color:#ff8389;'>✗ Unexpected error: {str(e)}</span>
                                </div>
                                """, unsafe_allow_html=True)

                st.divider()

    with tab2:
        st.markdown("Enter your SQL Server connection details to begin.")

        with st.form("connection_form"):
            server = st.text_input(
                "Server",
                value="localhost",
                help="SQL Server hostname or IP address"
            )

            database = st.text_input(
                "Database",
                value="AdventureWorks2025",
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

                with st.spinner("Connecting and analyzing database..."):
                    start_time = time.time()

                    # Step 1: Test database connection first
                    try:
                        st.write("Extracting database metadata...")
                        metadata = db_inspector.get_database_metadata(conn_string)
                    except Exception as e:
                        # Error message with IBM Carbon design tokens
                        st.markdown(f"""
                        <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#ff8389;'>✗ Database connection failed: {str(e)}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.875rem;color:#c6c6c6;'><strong>Troubleshooting tips:</strong></p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.875rem;color:#e0e0e0;'>- Verify server name and database name are correct<br>- Ensure SQL Server authentication is enabled<br>- Check username and password credentials<br>- Confirm network connectivity to the server<br>- Verify ODBC Driver 17 for SQL Server is installed</p>", unsafe_allow_html=True)
                        st.stop()

                    # Step 2: Generate LLM content separately
                    try:
                        st.write("Generating AI-powered documentation...")
                        generated_content = llm_generator.generate_tier1_content(metadata)
                    except ValueError as e:
                        # Warning message with IBM Carbon design tokens
                        st.markdown(f"""
                        <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#ff8389;'>⚠ AI generation failed: {str(e)}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("""
                        <div style='background:#001141;border:1px solid #0f62fe;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#78a9ff;'>ℹ Continuing with basic documentation. Check your WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        generated_content = {
                            'overview': llm_generator._get_fallback_overview(metadata),
                            'table_descriptions': llm_generator._get_fallback_descriptions(metadata.get('tables', []))
                        }
                    except Exception as e:
                        # Warning message with IBM Carbon design tokens
                        st.markdown(f"""
                        <div style='background:#2d0709;border:1px solid #da1e28;border-radius:4px;padding:1rem;margin:1rem 0;'>
                            <span style='color:#ff8389;'>⚠ AI generation encountered an error: {str(e)}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        generated_content = {
                            'overview': llm_generator._get_fallback_overview(metadata),
                            'table_descriptions': llm_generator._get_fallback_descriptions(metadata.get('tables', []))
                        }

                    # Step 3: Store results regardless of LLM success
                    elapsed_time = time.time() - start_time

                    session_manager.store_metadata(metadata)
                    session_manager.store_generated_content(generated_content)
                    session_manager.set_connected(True, conn_string)
                    session_manager.set_introspection_time(elapsed_time)

                    connection_key = f"{server}|{database}"
                    existing_keys = [f"{conn['server']}|{conn['database']}" for conn in st.session_state.saved_connections]

                    if connection_key not in existing_keys:
                        saved_conn = {
                            'server': server,
                            'database': database,
                            'auth_method': auth_method,
                            'timeout': timeout
                        }
                        if auth_method == "SQL Server Authentication":
                            saved_conn['username'] = username
                        st.session_state.saved_connections.append(saved_conn)

                    # Success messages with IBM Carbon design tokens
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