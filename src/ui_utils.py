import base64
import os
import streamlit as st
from functools import lru_cache


@lru_cache(maxsize=1)
def _logo_base64() -> str:
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Belvenar_logo.png')
    with open(logo_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def render_sidebar_brand():
    logo = _logo_base64()
    st.sidebar.markdown(
        f"""<div style='text-align:center;padding:0.75rem 0 0.5rem;'>
            <img src='data:image/png;base64,{logo}' width='80' style='display:inline-block;'>
            <p style='font-size:1.3rem;font-weight:700;color:#f4f4f4;margin:0.6rem 0 0;letter-spacing:0.01em;'>Belvenar Analytics</p>
        </div>""",
        unsafe_allow_html=True
    )
    st.sidebar.divider()
