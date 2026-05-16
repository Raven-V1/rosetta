"""
Test script to verify db_inspector.py works with SQLite database.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

sys.path.insert(0, 'src')

from db_inspector import (
    validate_connection,
    get_database_metadata,
    get_sample_data,
    get_connection_info
)

# SQLite connection string
CONN_STRING = 'sqlite:///demo_data.db'

def test_validate_connection():
    """Test connection validation."""
    print("Testing validate_connection...")
    result = validate_connection(CONN_STRING)
    print(f"  Connection valid: {result}")
    assert result == True, "Connection validation failed"
    print("  [PASSED]\n")

def test_get_connection_info():
    """Test getting connection info."""
    print("Testing get_connection_info...")
    info = get_connection_info(CONN_STRING)
    print(f"  Database: {info[0]}, Server: {info[1]}")
    assert info is not None, "Failed to get connection info"
    assert info[1] == 'SQLite', "Server should be 'SQLite'"
    print("  [PASSED]\n")

def test_get_database_metadata():
    """Test metadata extraction."""
    print("Testing get_database_metadata...")
    metadata = get_database_metadata(CONN_STRING)
    
    print(f"  Database: {metadata['database_name']}")
    print(f"  Server: {metadata['server']}")
    print(f"  Tables: {len(metadata['tables'])}")
    print(f"  Relationships: {len(metadata['relationships'])}")
    
    # Verify we have the expected tables
    table_names = [t['name'] for t in metadata['tables']]
    expected_tables = ['departments', 'employees', 'customers', 'products', 'orders', 'order_items']
    
    print("\n  Tables found:")
    for table in metadata['tables']:
        print(f"    - {table['schema']}.{table['name']} ({table['row_count']} rows, {len(table['columns'])} columns)")
    
    for expected in expected_tables:
        assert expected in table_names, f"Expected table '{expected}' not found"
    
    print("\n  Foreign key relationships:")
    for rel in metadata['relationships']:
        print(f"    - {rel['parent_table']}.{rel['parent_column']} -> {rel['referenced_table']}.{rel['referenced_column']}")
    
    assert len(metadata['relationships']) > 0, "No relationships found"
    print("\n  [PASSED]\n")

def test_get_sample_data():
    """Test getting sample data."""
    print("Testing get_sample_data...")
    
    # Test with different tables
    tables_to_test = ['main.customers', 'main.products', 'main.orders']
    
    for table in tables_to_test:
        df = get_sample_data(CONN_STRING, table, limit=3)
        print(f"  {table}: {len(df)} rows, {len(df.columns)} columns")
        assert len(df) > 0, f"No data returned for {table}"
        assert len(df) <= 3, f"Too many rows returned for {table}"
    
    print("  [PASSED]\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing db_inspector.py with SQLite database")
    print("=" * 60 + "\n")
    
    try:
        test_validate_connection()
        test_get_connection_info()
        test_get_database_metadata()
        test_get_sample_data()
        
        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob
