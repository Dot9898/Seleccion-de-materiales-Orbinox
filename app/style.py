
from pathlib import Path
import streamlit as st

ROOT_PATH = Path(__file__).resolve().parent.parent

@st.cache_data
def style_css():
    with open(ROOT_PATH / 'app' / 'style.css') as css:
        style = css.read()
        return(style)

def set_style():
    st.markdown(f'<style>{style_css()}</style>', unsafe_allow_html = True)
