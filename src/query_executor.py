"""
Query Executor Module
Handles safe execution of read-only SQL queries with validation and timeout.

Responsibilities:
- Validate queries to ensure they are read-only (SELECT, WITH)
- Execute queries with timeout and row limits
- Return results as pandas DataFrames
- Handle errors gracefully without exposing sensitive information

All queries are read-only. No ORM used.
"""

import pyodbc
import pandas as pd
import re
import logging
from typing import Optional
import signal
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Forbidden SQL keywords (write operations)
FORBIDDEN_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 
    'ALTER', 'CREATE', 'TRUNCATE'
]

# Allowed SQL keywords (read operations)
ALLOWED_KEYWORDS = ['SELECT', 'WITH']

# Query execution limits
MAX_ROWS = 1000
DEFAULT_TIMEOUT = 30


def validate_query(query: str) -> bool:
    """
    Validate that a query is read-only and safe to execute.
    
    Rejects queries containing: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
    Allows queries with: SELECT, WITH (CTEs)
    
    Args:
        query: SQL query string to validate
        
    Returns:
        bool: True if query is valid (read-only), False otherwise
        
    Example:
        >>> validate_query("SELECT * FROM Users")
        True
        >>> validate_query("DELETE FROM Users")
        False
        >>> validate_query("WITH cte AS (SELECT * FROM Users) SELECT * FROM cte")
        True
    """
    if not query or not query.strip():
        logger.warning("Empty query provided")
        return False
    
    # Convert to uppercase for case-insensitive checking
    query_upper = query.upper()
    
    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        # Use word boundaries to avoid false positives (e.g., "INSERTED" column name)
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_upper):
            logger.warning(f"Query rejected: contains forbidden keyword '{keyword}'")
            return False
    
    # Check that query contains at least one allowed keyword
    has_allowed = False
    for keyword in ALLOWED_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_upper):
            has_allowed = True
            break
    
    if not has_allowed:
        logger.warning("Query rejected: does not contain SELECT or WITH")
        return False
    
    logger.info("Query validation passed")
    return True


def execute_query(conn_string: str, query: str) -> pd.DataFrame:
    """
    Execute a validated SQL query and return results as a DataFrame.
    
    Enforces maximum row limit of 1000 rows and 30 second timeout.
    Returns empty DataFrame on error instead of raising exceptions.
    
    Args:
        conn_string: ODBC connection string
        query: SQL query to execute (must pass validate_query)
        
    Returns:
        pd.DataFrame: Query results (max 1000 rows), or empty DataFrame on error
        
    Raises:
        ValueError: If query fails validation
        
    Example:
        >>> conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;..."
        >>> df = execute_query(conn_str, "SELECT TOP 10 * FROM Users")
        >>> len(df) <= 10
        True
    """
    # Validate query first
    if not validate_query(query):
        logger.error("Query validation failed")
        raise ValueError("Query validation failed: query contains forbidden operations or is not a SELECT/WITH statement")
    
    try:
        # Execute with timeout
        return execute_with_timeout(conn_string, query, timeout=DEFAULT_TIMEOUT)
        
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Log error without exposing connection string
        logger.error(f"Query execution failed: {type(e).__name__}: {str(e)}")
        return pd.DataFrame()


def execute_with_timeout(conn_string: str, query: str, timeout: int = 30) -> pd.DataFrame:
    """
    Execute a query with a timeout limit.
    
    Wrapper function that enforces timeout for query execution.
    Returns empty DataFrame on timeout or error.
    
    Args:
        conn_string: ODBC connection string
        query: SQL query to execute
        timeout: Maximum execution time in seconds (default: 30)
        
    Returns:
        pd.DataFrame: Query results (max 1000 rows), or empty DataFrame on error/timeout
        
    Example:
        >>> df = execute_with_timeout(conn_str, "SELECT * FROM LargeTable", timeout=10)
    """
    try:
        # Connect with timeout
        conn = pyodbc.connect(conn_string, timeout=timeout)
        
        # Wrap query to limit rows
        limited_query = f"SELECT TOP {MAX_ROWS} * FROM ({query}) AS limited_result"
        
        logger.info(f"Executing query with {timeout}s timeout and {MAX_ROWS} row limit")
        
        # Execute query and read into DataFrame
        # pandas read_sql handles the cursor and fetching
        df = pd.read_sql(limited_query, conn, timeout=timeout)
        
        conn.close()
        
        logger.info(f"Query executed successfully: {len(df)} rows returned")
        return df
        
    except pyodbc.Error as e:
        # Database-specific errors
        logger.error(f"Database error during query execution: {type(e).__name__}")
        return pd.DataFrame()
        
    except pd.io.sql.DatabaseError as e:
        # Pandas SQL errors (including timeout)
        logger.error(f"Query execution error: {type(e).__name__}")
        return pd.DataFrame()
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error during query execution: {type(e).__name__}")
        return pd.DataFrame()


# Module-level constants
__all__ = [
    'validate_query',
    'execute_query', 
    'execute_with_timeout',
    'MAX_ROWS',
    'DEFAULT_TIMEOUT'
]

# Made with Bob