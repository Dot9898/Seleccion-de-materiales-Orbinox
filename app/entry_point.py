
from pathlib import Path
import streamlit as st

ROOT_PATH = Path(__file__).resolve().parent.parent

materials_page = st.Page(ROOT_PATH / 'app' / 'materials.py', title = 'Materiales')
sulfuric_page = st.Page(ROOT_PATH / 'app' / 'acid.py', title = 'Ácido sulfúrico')

current_page = st.navigation([materials_page, sulfuric_page], position = 'top')
current_page.run()
