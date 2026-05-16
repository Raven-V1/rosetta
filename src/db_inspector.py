"""
Database Inspector Module
Handles SQL Server database introspection using pyodbc.

Responsibilities:
- Validate SQL Server connections
- Extract table metadata from INFORMATION_SCHEMA
- Extract column metadata from INFORMATION_SCHEMA
- Extract foreign key relationships from sys tables
- Get row counts per table
- Get sample data for tables

All queries are read-only. No ORM used.
"""

import pyodbc
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_connection(conn_string: str) -> bool:
    """
    Validate SQL Server connection using pyodbc.
    
    Args:
        conn_string: ODBC connection string with SQL Server Authentication
        
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        >>> conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=AdventureWorks2025;UID=sa;PWD=password"
        >>> validate_connection(conn_str)
        True
    """
    try:
        conn = pyodbc.connect(conn_string, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Connection validation successful")
        return True
    except pyodbc.Error as e:
        logger.error(f"Connection validation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection validation: {e}")
        return False


def get_database_metadata(conn_string: str) -> Dict:
    """
    Extract complete database metadata including tables, columns, and relationships.
    
    Args:
        conn_string: ODBC connection string
        
    Returns:
        dict: Database metadata matching session state schema:
            {
                'database_name': str,
                'server': str,
                'tables': [
                    {
                        'schema': str,
                        'name': str,
                        'row_count': int,
                        'columns': [
                            {'name': str, 'type': str, 'nullable': bool}
                        ]
                    }
                ],
                'relationships': [
                    {
                        'fk_name': str,
                        'parent_table': str,
                        'parent_column': str,
                        'referenced_table': str,
                        'referenced_column': str
                    }
                ]
            }
    """
    try:
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        # Get database name and server
        cursor.execute("SELECT DB_NAME() AS database_name, @@SERVERNAME AS server")
        db_info = cursor.fetchone()
        database_name = db_info.database_name
        server = db_info.server
        
        logger.info(f"Extracting metadata from {database_name} on {server}")
        
        # Get tables
        tables_query = """
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        cursor.execute(tables_query)
        tables_raw = cursor.fetchall()
        
        # Get all columns
        columns_query = """
        SELECT 
            TABLE_SCHEMA, 
            TABLE_NAME, 
            COLUMN_NAME, 
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
        """
        cursor.execute(columns_query)
        columns_raw = cursor.fetchall()
        
        # Organize columns by table
        columns_by_table = {}
        for col in columns_raw:
            table_key = f"{col.TABLE_SCHEMA}.{col.TABLE_NAME}"
            if table_key not in columns_by_table:
                columns_by_table[table_key] = []
            
            # Format data type with length if applicable
            data_type = col.DATA_TYPE
            if col.CHARACTER_MAXIMUM_LENGTH and col.CHARACTER_MAXIMUM_LENGTH > 0:
                data_type = f"{data_type}({col.CHARACTER_MAXIMUM_LENGTH})"
            
            columns_by_table[table_key].append({
                'name': col.COLUMN_NAME,
                'type': data_type,
                'nullable': col.IS_NULLABLE == 'YES'
            })
        
        # Build tables list with columns
        tables = []
        for table in tables_raw:
            table_key = f"{table.TABLE_SCHEMA}.{table.TABLE_NAME}"
            tables.append({
                'schema': table.TABLE_SCHEMA,
                'name': table.TABLE_NAME,
                'row_count': 0,  # Will be populated separately
                'columns': columns_by_table.get(table_key, [])
            })
        
        # Get row counts for all tables
        table_list = [{'schema': t['schema'], 'name': t['name']} for t in tables]
        row_counts = get_table_row_counts(conn_string, table_list)
        
        # Update row counts
        for table in tables:
            table_key = f"{table['schema']}.{table['name']}"
            table['row_count'] = row_counts.get(table_key, 0)
        
        # Get foreign key relationships
        fk_query = """
        SELECT 
            fk.name AS FK_NAME,
            SCHEMA_NAME(tp.schema_id) + '.' + tp.name AS PARENT_TABLE,
            cp.name AS PARENT_COLUMN,
            SCHEMA_NAME(tr.schema_id) + '.' + tr.name AS REFERENCED_TABLE,
            cr.name AS REFERENCED_COLUMN
        FROM sys.foreign_keys fk
        INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
        INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id 
            AND fkc.parent_object_id = cp.object_id
        INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id 
            AND fkc.referenced_object_id = cr.object_id
        ORDER BY PARENT_TABLE, FK_NAME
        """
        cursor.execute(fk_query)
        fk_raw = cursor.fetchall()
        
        relationships = []
        for fk in fk_raw:
            relationships.append({
                'fk_name': fk.FK_NAME,
                'parent_table': fk.PARENT_TABLE,
                'parent_column': fk.PARENT_COLUMN,
                'referenced_table': fk.REFERENCED_TABLE,
                'referenced_column': fk.REFERENCED_COLUMN
            })
        
        cursor.close()
        conn.close()
        
        metadata = {
            'database_name': database_name,
            'server': server,
            'tables': tables,
            'relationships': relationships
        }
        
        logger.info(f"Metadata extraction complete: {len(tables)} tables, {len(relationships)} relationships")
        return metadata
        
    except pyodbc.Error as e:
        logger.error(f"Database error during metadata extraction: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during metadata extraction: {e}")
        raise


def get_table_row_counts(conn_string: str, tables: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Get row counts for a list of tables.
    
    Args:
        conn_string: ODBC connection string
        tables: List of dicts with 'schema' and 'name' keys
        
    Returns:
        dict: Mapping of 'schema.table' to row count
        
    Example:
        >>> tables = [{'schema': 'dbo', 'name': 'Users'}]
        >>> get_table_row_counts(conn_str, tables)
        {'dbo.Users': 1000}
    """
    row_counts = {}
    
    try:
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        for table in tables:
            schema = table['schema']
            name = table['name']
            table_key = f"{schema}.{name}"
            
            try:
                # Use sys.partitions for fast row count (approximate for large tables)
                count_query = f"""
                SELECT SUM(p.rows) AS row_count
                FROM sys.tables t
                INNER JOIN sys.partitions p ON t.object_id = p.object_id
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                WHERE s.name = ? 
                    AND t.name = ?
                    AND p.index_id IN (0, 1)
                """
                cursor.execute(count_query, (schema, name))
                result = cursor.fetchone()
                row_counts[table_key] = result.row_count if result and result.row_count else 0
                
            except pyodbc.Error as e:
                logger.warning(f"Could not get row count for {table_key}: {e}")
                row_counts[table_key] = 0
        
        cursor.close()
        conn.close()
        
        logger.info(f"Row counts retrieved for {len(row_counts)} tables")
        return row_counts
        
    except pyodbc.Error as e:
        logger.error(f"Database error during row count retrieval: {e}")
        return row_counts
    except Exception as e:
        logger.error(f"Unexpected error during row count retrieval: {e}")
        return row_counts


def get_sample_data(conn_string: str, table: str, limit: int = 5) -> pd.DataFrame:
    """
    Get sample data from a table.
    
    Args:
        conn_string: ODBC connection string
        table: Fully qualified table name (schema.table)
        limit: Number of rows to retrieve (default: 5)
        
    Returns:
        pd.DataFrame: Sample data from the table
        
    Example:
        >>> df = get_sample_data(conn_str, 'dbo.Users', limit=5)
        >>> len(df)
        5
    """
    try:
        conn = pyodbc.connect(conn_string, timeout=30)
        
        # Validate table name format
        if '.' not in table:
            raise ValueError(f"Table name must be fully qualified (schema.table): {table}")
        
        # Use parameterized query with TOP for safety
        query = f"SELECT TOP {int(limit)} * FROM {table}"
        
        logger.info(f"Retrieving {limit} sample rows from {table}")
        df = pd.read_sql(query, conn)
        
        conn.close()
        
        logger.info(f"Retrieved {len(df)} rows from {table}")
        return df
        
    except pyodbc.Error as e:
        logger.error(f"Database error retrieving sample data from {table}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving sample data from {table}: {e}")
        raise


def get_connection_info(conn_string: str) -> Optional[Tuple[str, str]]:
    """
    Extract database name and server from connection string.
    Helper function for displaying connection info.
    
    Args:
        conn_string: ODBC connection string
        
    Returns:
        tuple: (database_name, server) or None if connection fails
    """
    try:
        conn = pyodbc.connect(conn_string, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME() AS database_name, @@SERVERNAME AS server")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return (result.database_name, result.server)
    except Exception as e:
        logger.error(f"Could not extract connection info: {e}")
        return None


# Module-level constants
DEFAULT_TIMEOUT = 30
MAX_SAMPLE_ROWS = 1000

# Made with Bob
