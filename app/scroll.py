

import streamlit as st

st.set_page_config(layout="wide")

# ---- Scroll trigger at top ----
st.markdown("""
<a href="#bottom-anchor">
    <button style="
        padding: 0.5rem 1rem;
        font-size: 16px;
        cursor: pointer;
    ">
        Scroll to bottom
    </button>
</a>
""", unsafe_allow_html=True)

# ---- Large content ----
for i in range(100):
    st.write(f"Line {i}")

# ---- Bottom anchor ----
st.markdown('<div id="bottom-anchor"></div>', unsafe_allow_html=True)
st.write("Bottom reached")

