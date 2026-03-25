
from pathlib import Path
import streamlit as st
from screen_mode import get_screen_mode

ROOT_PATH = Path(__file__).resolve().parent.parent

screen_mode = get_screen_mode()
if screen_mode == 'desktop':
    materials_page = st.Page(ROOT_PATH / 'app' / 'materials_desktop.py', title = 'Materiales')
    sulfuric_page = st.Page(ROOT_PATH / 'app' / 'acid_mobile.py', title = 'Ácido sulfúrico')
if screen_mode == 'mobile':
    materials_page = st.Page(ROOT_PATH / 'app' / 'materials_mobile.py', title = 'Materiales')
    sulfuric_page = st.Page(ROOT_PATH / 'app' / 'acid_mobile.py', title = 'Ácido sulfúrico')

current_page = st.navigation([materials_page, sulfuric_page], position = 'top')
current_page.run()

