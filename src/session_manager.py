"""
Session Manager Module
Manages Streamlit session state for the Rosetta project.

Responsibilities:
- Initialize all session state keys on first load
- Store and retrieve database metadata
- Store and retrieve LLM-generated content
- Track connection status
- Clear session state
"""

import streamlit as st
from typing import Optional


def _initialize_session_state() -> None:
    """
    Initialize all session state keys with default values on first load.
    Called automatically by other functions to ensure state exists.
    """
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    
    if 'conn_string' not in st.session_state:
        st.session_state.conn_string = ''
    
    if 'metadata' not in st.session_state:
        st.session_state.metadata = {
            'database_name': '',
            'server': '',
            'tables': [],
            'relationships': []
        }
    
    if 'generated' not in st.session_state:
        st.session_state.generated = {
            'overview': '',
            'table_descriptions': {},
            'table_groups': {},
            'important_tables': [],
            'sample_queries': []
        }
    
    if 'introspection_time' not in st.session_state:
        st.session_state.introspection_time = 0.0
    
    if 'saved_connections' not in st.session_state:
        st.session_state.saved_connections = []


def store_metadata(metadata: dict) -> None:
    """
    Store database metadata in session state.
    
    Args:
        metadata: Dictionary containing database metadata with keys:
            - database_name: str
            - server: str
            - tables: list of table dictionaries
            - relationships: list of relationship dictionaries
    """
    _initialize_session_state()
    st.session_state.metadata = metadata


def get_metadata() -> dict:
    """
    Retrieve database metadata from session state.
    
    Returns:
        Dictionary containing database metadata, or empty structure if not set.
    """
    _initialize_session_state()
    return st.session_state.metadata


def store_generated_content(content: dict) -> None:
    """
    Store LLM-generated content in session state.
    
    Args:
        content: Dictionary containing generated content with keys:
            - overview: str (optional)
            - table_descriptions: dict (optional)
            - table_groups: dict (optional)
            - important_tables: list (optional)
            - sample_queries: list (optional)
    
    Note: Only provided keys will be updated; others remain unchanged.
    """
    _initialize_session_state()
    
    # Update only the keys that are provided
    for key in ['overview', 'table_descriptions', 'table_groups', 
                'important_tables', 'sample_queries']:
        if key in content:
            st.session_state.generated[key] = content[key]


def get_generated_content() -> dict:
    """
    Retrieve LLM-generated content from session state.
    
    Returns:
        Dictionary containing generated content, or empty structure if not set.
    """
    _initialize_session_state()
    return st.session_state.generated


def is_connected() -> bool:
    """
    Check if database connection has been established.
    
    Returns:
        True if connected, False otherwise.
    """
    _initialize_session_state()
    return st.session_state.connected


def set_connected(connected: bool, conn_string: str = '') -> None:
    """
    Set connection status and optionally store connection string.
    
    Args:
        connected: Connection status
        conn_string: Connection string (optional, only stored if connected=True)
    """
    _initialize_session_state()
    st.session_state.connected = connected
    
    if connected and conn_string:
        st.session_state.conn_string = conn_string
    elif not connected:
        # Clear connection string when disconnecting
        st.session_state.conn_string = ''


def get_connection_string() -> str:
    """
    Retrieve stored connection string.
    
    Returns:
        Connection string, or empty string if not set.
    """
    _initialize_session_state()
    return st.session_state.conn_string


def set_introspection_time(time_seconds: float) -> None:
    """
    Store the time taken for database introspection.
    
    Args:
        time_seconds: Time in seconds
    """
    _initialize_session_state()
    st.session_state.introspection_time = time_seconds


def get_introspection_time() -> float:
    """
    Retrieve the stored introspection time.
    
    Returns:
        Time in seconds, or 0.0 if not set.
    """
    _initialize_session_state()
    return st.session_state.introspection_time


def clear_session() -> None:
    """
    Clear all session state data.
    Resets to initial state as if the app was just loaded.
    """
    # Clear all keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reinitialize with defaults
    _initialize_session_state()

# Made with Bob
