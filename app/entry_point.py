
import streamlit as st

materials_page = st.Page('materials.py', title = 'Materiales')
sulfuric_page = st.Page('acid.py', title = 'Ácido sulfúrico')

current_page = st.navigation([materials_page, sulfuric_page], position = 'top')
current_page.run()
