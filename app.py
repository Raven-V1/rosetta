"""
Rosetta - SQL Server Database Documentation Generator
Main entry point for the Streamlit application.

Responsibilities:
- Set page configuration
- Initialize session state
- Redirect to Home page
"""

import streamlit as st
from src import session_manager

# Page configuration
st.set_page_config(
    page_title="Rosetta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
session_manager._initialize_session_state()

# Redirect to Home page
st.switch_page("pages/1_🏠_Home.py")

# Made with Bob