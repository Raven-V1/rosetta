"""
Database Inspector Module
Handles database introspection for SQL Server (via pyodbc) and SQLite (via sqlite3).

Responsibilities:
- Validate database connections (SQL Server and SQLite)
- Extract table metadata from INFORMATION_SCHEMA (SQL Server) or sqlite_master (SQLite)
- Extract column metadata from INFORMATION_SCHEMA (SQL Server) or PRAGMA (SQLite)
- Extract foreign key relationships from sys tables (SQL Server) or PRAGMA (SQLite)
- Get row counts per table
- Get sample data for tables

All queries are read-only. No ORM used.
"""

import pyodbc
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_connection(conn_string: str) -> bool:
    """
    Validate database connection.
    Supports both SQL Server (via pyodbc) and SQLite (via sqlite3).
    
    Args:
        conn_string: ODBC connection string or SQLite connection string (sqlite:///path)
        
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        >>> conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=AdventureWorks2025;UID=sa;PWD=password"
        >>> validate_connection(conn_str)
        True
        >>> conn_str = "sqlite:///demo_data.db"
        >>> validate_connection(conn_str)
        True
    """
    try:
        # Check if this is a SQLite connection
        if conn_string.startswith('sqlite:///'):
            db_path = conn_string.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("SQLite connection validation successful")
            return True
        else:
            # SQL Server connection
            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("SQL Server connection validation successful")
            return True
    except (pyodbc.Error, sqlite3.Error) as e:
        logger.error(f"Connection validation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection validation: {e}")
        return False

def _get_sqlite_metadata(conn_string: str) -> Dict:
    """
    Extract metadata from SQLite database.
    
    Args:
        conn_string: SQLite connection string (sqlite:///path)
        
    Returns:
        dict: Database metadata
    """
    try:
        # Extract database path from connection string
        db_path = conn_string.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        database_name = db_path.split('/')[-1].replace('.db', '')
        server = 'SQLite'
        
        logger.info(f"Extracting metadata from SQLite database: {database_name}")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = [row[0] for row in cursor.fetchall()]
        
        tables = []
        for table_name in table_names:
            # Get columns for this table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_raw = cursor.fetchall()
            
            columns = []
            for col in columns_raw:
                # col format: (cid, name, type, notnull, dflt_value, pk)
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'nullable': col[3] == 0  # notnull=0 means nullable
                })
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            tables.append({
                'schema': 'main',  # SQLite uses 'main' as default schema
                'name': table_name,
                'row_count': row_count,
                'columns': columns
            })
        
        # Get foreign key relationships
        relationships = []
        for table_name in table_names:
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fks = cursor.fetchall()
            
            for fk in fks:
                # fk format: (id, seq, table, from, to, on_update, on_delete, match)
                relationships.append({
                    'fk_name': f"fk_{table_name}_{fk[3]}",
                    'parent_table': f"main.{table_name}",
                    'parent_column': fk[3],
                    'referenced_table': f"main.{fk[2]}",
                    'referenced_column': fk[4]
                })
        
        cursor.close()
        conn.close()
        
        metadata = {
            'database_name': database_name,
            'server': server,
            'tables': tables,
            'relationships': relationships
        }
        
        logger.info(f"SQLite metadata extraction complete: {len(tables)} tables, {len(relationships)} relationships")
        return metadata
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error during metadata extraction: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during SQLite metadata extraction: {e}")
        raise



def get_database_metadata(conn_string: str) -> Dict:
    """
    Extract complete database metadata including tables, columns, and relationships.
    Supports both SQL Server (via pyodbc) and SQLite (via sqlite3).
    
    Args:
        conn_string: ODBC connection string or SQLite connection string (sqlite:///path)
        
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
    # Check if this is a SQLite connection
    if conn_string.startswith('sqlite:///'):
        return _get_sqlite_metadata(conn_string)
    
    try:
        # Connection timeout is specified in the connection string
        conn = pyodbc.connect(conn_string)
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
        # Connection timeout is specified in the connection string
        conn = pyodbc.connect(conn_string)
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
    Supports both SQL Server (via pyodbc) and SQLite (via sqlite3).
    
    Args:
        conn_string: ODBC connection string or SQLite connection string (sqlite:///path)
        table: Fully qualified table name (schema.table) or just table name for SQLite
        limit: Number of rows to retrieve (default: 5)
        
    Returns:
        pd.DataFrame: Sample data from the table
        
    Example:
        >>> df = get_sample_data(conn_str, 'dbo.Users', limit=5)
        >>> len(df)
        5
        >>> df = get_sample_data('sqlite:///demo_data.db', 'main.customers', limit=5)
        >>> len(df)
        5
    """
    try:
        # Check if this is a SQLite connection
        if conn_string.startswith('sqlite:///'):
            db_path = conn_string.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            
            # For SQLite, extract just the table name (remove schema prefix if present)
            table_name = table.split('.')[-1] if '.' in table else table
            
            # Use LIMIT for SQLite
            query = f"SELECT * FROM {table_name} LIMIT {int(limit)}"
            
            logger.info(f"Retrieving {limit} sample rows from {table_name}")
            df = pd.read_sql(query, conn)
            
            conn.close()
            
            logger.info(f"Retrieved {len(df)} rows from {table_name}")
            return df
        else:
            # SQL Server connection
            conn = pyodbc.connect(conn_string)
            
            # Validate table name format
            if '.' not in table:
                raise ValueError(f"Table name must be fully qualified (schema.table): {table}")
            
            # Use TOP for SQL Server
            query = f"SELECT TOP {int(limit)} * FROM {table}"
            
            logger.info(f"Retrieving {limit} sample rows from {table}")
            df = pd.read_sql(query, conn)
            
            conn.close()
            
            logger.info(f"Retrieved {len(df)} rows from {table}")
            return df
        
    except (pyodbc.Error, sqlite3.Error) as e:
        logger.error(f"Database error retrieving sample data from {table}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving sample data from {table}: {e}")
        raise


def get_connection_info(conn_string: str) -> Optional[Tuple[str, str]]:
    """
    Extract database name and server from connection string.
    Helper function for displaying connection info.
    Supports both SQL Server (via pyodbc) and SQLite (via sqlite3).
    
    Args:
        conn_string: ODBC connection string or SQLite connection string (sqlite:///path)
        
    Returns:
        tuple: (database_name, server) or None if connection fails
    """
    try:
        # Check if this is a SQLite connection
        if conn_string.startswith('sqlite:///'):
            db_path = conn_string.replace('sqlite:///', '')
            database_name = db_path.split('/')[-1].replace('.db', '')
            server = 'SQLite'
            return (database_name, server)
        else:
            # SQL Server connection
            conn = pyodbc.connect(conn_string)
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
