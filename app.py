"""
Rosetta - SQL Server Database Documentation Generator
Main entry point for the Streamlit application.

Responsibilities:
- Set page configuration
- Initialize session state
- Redirect to Home page
"""

import streamlit as st
from dotenv import load_dotenv
from src import session_manager

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Rosetta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# IBM Plex Sans font integration
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    code {
        font-family: 'IBM Plex Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Belvenar logo in sidebar
st.logo("assets/Belvenar_logo.png")

# Initialize session state
session_manager._initialize_session_state()

# Redirect to Home page
st.switch_page("pages/1_Home.py")

# Made with Bob