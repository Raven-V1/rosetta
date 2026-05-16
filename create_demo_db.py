"""
Create demo SQLite database for Rosetta Streamlit app.
Generates demo_data.db with 6 tables and realistic sample data.
"""

import sqlite3
from datetime import datetime, timedelta
import random

# Database path
DB_PATH = 'demo_data.db'

# Sample data
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 
               'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Thomas', 
               'Linda', 'Charles', 'Barbara', 'Daniel', 'Susan']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
              'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
              'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
          'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
          'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis',
          'Seattle', 'Denver', 'Boston']

STATES = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA', 'TX', 'FL',
          'TX', 'OH', 'NC', 'CA', 'IN', 'WA', 'CO', 'MA']

PRODUCT_CATEGORIES = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']

PRODUCT_NAMES = {
    'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Smart Watch'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Dress'],
    'Home & Garden': ['Coffee Maker', 'Vacuum Cleaner', 'Blender', 'Garden Tools', 'Lamp'],
    'Sports': ['Basketball', 'Tennis Racket', 'Yoga Mat', 'Dumbbells', 'Running Shoes'],
    'Books': ['Fiction Novel', 'Cookbook', 'Biography', 'Self-Help', 'Science Fiction']
}

DEPARTMENT_NAMES = ['Sales', 'Marketing', 'Engineering', 'Human Resources', 'Finance', 'Operations']

ORDER_STATUSES = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

def create_database():
    """Create the demo database with all tables and sample data."""
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    print("Dropping existing tables if they exist...")
    
    # Drop tables in reverse order of dependencies
    cursor.execute('DROP TABLE IF EXISTS order_items')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS customers')
    cursor.execute('DROP TABLE IF EXISTS employees')
    cursor.execute('DROP TABLE IF EXISTS departments')
    
    print("Creating tables...")
    
    # Create departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        manager_id INTEGER,
        budget REAL NOT NULL
    )
    ''')
    
    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        department_id INTEGER NOT NULL,
        hire_date TEXT NOT NULL,
        salary REAL NOT NULL,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    ''')
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        zip TEXT NOT NULL
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        description TEXT
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')
    
    print("Inserting sample data...")
    
    # Insert departments (20 rows)
    departments_data = []
    for i, dept_name in enumerate(DEPARTMENT_NAMES * 4):  # Repeat to get 24, we'll use 20
        if i >= 20:
            break
        budget = random.uniform(100000, 1000000)
        departments_data.append((f"{dept_name} {i//6 + 1}" if i >= 6 else dept_name, None, budget))
    
    cursor.executemany('INSERT INTO departments (name, manager_id, budget) VALUES (?, ?, ?)', 
                      departments_data[:20])
    
    # Insert employees (20 rows)
    employees_data = []
    base_date = datetime(2020, 1, 1)
    for i in range(20):
        first_name = FIRST_NAMES[i]
        last_name = LAST_NAMES[i]
        email = f"{first_name.lower()}.{last_name.lower()}{i}@company.com"
        dept_id = (i % 6) + 1  # Distribute across 6 departments
        hire_date = (base_date + timedelta(days=random.randint(0, 1825))).strftime('%Y-%m-%d')
        salary = random.uniform(40000, 150000)
        employees_data.append((first_name, last_name, email, dept_id, hire_date, salary))
    
    cursor.executemany('''INSERT INTO employees 
                         (first_name, last_name, email, department_id, hire_date, salary) 
                         VALUES (?, ?, ?, ?, ?, ?)''', employees_data)
    
    # Update department managers
    for i in range(1, 7):
        cursor.execute('UPDATE departments SET manager_id = ? WHERE id = ?', (i, i))
    
    # Insert customers (20 rows)
    customers_data = []
    for i in range(20):
        name = f"{FIRST_NAMES[i]} {LAST_NAMES[(i+5) % 20]}"
        email = f"customer{i+1}@email.com"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        address = f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine'])} St"
        city = CITIES[i]
        state = STATES[i]
        zip_code = f"{random.randint(10000, 99999)}"
        customers_data.append((name, email, phone, address, city, state, zip_code))
    
    cursor.executemany('''INSERT INTO customers 
                         (name, email, phone, address, city, state, zip) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', customers_data)
    
    # Insert products (20 rows)
    products_data = []
    product_id = 1
    for category in PRODUCT_CATEGORIES:
        for product_name in PRODUCT_NAMES[category]:
            if product_id > 20:
                break
            price = random.uniform(9.99, 999.99)
            stock = random.randint(0, 500)
            description = f"High-quality {product_name.lower()} in {category.lower()} category"
            products_data.append((product_name, category, price, stock, description))
            product_id += 1
    
    cursor.executemany('''INSERT INTO products 
                         (name, category, price, stock_quantity, description) 
                         VALUES (?, ?, ?, ?, ?)''', products_data)
    
    # Insert orders (20 rows)
    orders_data = []
    base_order_date = datetime(2024, 1, 1)
    for i in range(20):
        customer_id = (i % 20) + 1
        order_date = (base_order_date + timedelta(days=random.randint(0, 500))).strftime('%Y-%m-%d')
        total_amount = random.uniform(50, 2000)
        status = random.choice(ORDER_STATUSES)
        orders_data.append((customer_id, order_date, total_amount, status))
    
    cursor.executemany('''INSERT INTO orders 
                         (customer_id, order_date, total_amount, status) 
                         VALUES (?, ?, ?, ?)''', orders_data)
    
    # Insert order_items (20 rows)
    order_items_data = []
    for i in range(20):
        order_id = (i % 20) + 1
        product_id = (i % 20) + 1
        quantity = random.randint(1, 5)
        # Get product price
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        unit_price = cursor.fetchone()[0]
        order_items_data.append((order_id, product_id, quantity, unit_price))
    
    cursor.executemany('''INSERT INTO order_items 
                         (order_id, product_id, quantity, unit_price) 
                         VALUES (?, ?, ?, ?)''', order_items_data)
    
    # Commit changes
    conn.commit()
    
    # Verify data
    print("\nVerifying data...")
    tables = ['departments', 'employees', 'customers', 'products', 'orders', 'order_items']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    # Close connection
    conn.close()
    
    print(f"\nDatabase created successfully: {DB_PATH}")

if __name__ == '__main__':
    create_database()

# Made with Bob
