

import streamlit as st
from backend_sulfuric import load_graph

CHART_HEIGHT = 600 #'stretch'

st.set_page_config(layout = 'wide')

graph = load_graph()
st.altair_chart(graph, width = 'stretch', height = CHART_HEIGHT)













