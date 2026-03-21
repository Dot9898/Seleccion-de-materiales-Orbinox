

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
from style import set_style
import backend_sulfuric
from constants import FAMILIES
from constants import FAMILY_TO_CURVE_NAME

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'

MAIN_TEXT_COLOR = '#3e4c59'
LOGO_WIDTH = 200
MIN_LOGO_HEIGHT = 100
LOGO_HEIGHT = MIN_LOGO_HEIGHT + 0
TITLE_HEIGHT_ALIGNED_WITH_LOGO = LOGO_HEIGHT + 28
TITLE_HEIGHT = TITLE_HEIGHT_ALIGNED_WITH_LOGO
TITLE_AND_TOGGLES_SPACING = 20

GRAPH_HEIGHT = 550 #'stretch'


def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return(base64.b64encode(buffer.getvalue()).decode())

@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    images['logo_b64'] = img_to_base64(images['logo'])
    return(images)

def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)

def generate_title():
    st.markdown(f"""
                <div style="display: flex; flex-direction: column; justify-content: flex-end; height: {TITLE_HEIGHT}px;">
                    <h4 style="margin: 0; font-size: 2.9rem; font-weight: 450; color: {MAIN_TEXT_COLOR}">
                        Resistencia química al ácido sulfúrico
                    </h4>
                </div>
                """,
                unsafe_allow_html = True)

def generate_logo(images):
    logo = images['logo_b64']
    st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: flex-end;
                    align-items: flex-end;
                    height: {LOGO_HEIGHT}px;
                ">
                    <img src="data:image/webp;base64,{logo}" width="{LOGO_WIDTH}">
                </div>
                """,
                unsafe_allow_html = True)

def generate_title_and_logo(images):
    title_column, logo_column = st.columns([5, 1])
    with title_column:
        generate_title()
    with logo_column:
        generate_logo(images)

def generate_toggles():
    columns = st.columns([1] * 5)
    for index in range(5):
        with columns[index]:
            family = FAMILIES[index]
            key = f'{family} toggle'
            st.toggle(family, 
                      key = key, 
                      value = True if family == 'Cauchos' else False, 
                      label_visibility = 'visible', 
                      help=None)

def generate_graph_from_toggles():
    curves_to_show = []
    for family in FAMILIES:
        key = f'{family} toggle'
        if st.session_state[key]:
            curves_to_show = curves_to_show + FAMILY_TO_CURVE_NAME[family]
    graph = backend_sulfuric.generate_graph(curves_to_show)
    st.altair_chart(graph, width = 'stretch', height = GRAPH_HEIGHT)#, key = 'Gráfico', selection_mode = 'clicked_point', on_select = 'rerun')

def generate_sliders():
    
    st.slider('Temperatura', 
              key = 'Temperatura_slider', 
              min_value = 0, 
              max_value = 180, 
              step = 5, 
              format = '%.0f °C')
    
    st.slider('Concentración', 
              key = 'Concentración_slider', 
              min_value = 6, 
              max_value = 100, 
              step = 2, 
              format = '%.0f%%')

def print_family(family, resistant_materials):
    materials_to_print = []
    for material in sorted(FAMILY_TO_CURVE_NAME[family]):
        if material in resistant_materials:
            material_text = f"<span style = 'font-size: 1.15em; font-weight: 550'>{material}</span>"
            materials_to_print.append(material_text)

    printed = False
    if len(materials_to_print) >= 1:
        
        st.markdown(f"""<div style = "margin-bottom: 4.5px">
                    <p style = "font-weight: 650; margin: 0">{family}</p>
                    </div>""", unsafe_allow_html = True)
        
        slightly_bigger_newline = "<span style = 'display: block; height: 3.5px'></span>"
        materials_text = slightly_bigger_newline.join(materials_to_print)
        st.caption(materials_text, unsafe_allow_html = True)
        
        printed = True

    return(printed)

def print_resistant_materials(concentration, temperature):
    if concentration is None or temperature is None:
        pass
    
    resistant_materials = backend_sulfuric.get_resistant_materials(concentration, temperature)

    if len(resistant_materials) >= 1:
        st.markdown(f"""<div style = "margin-bottom: 8px">
                    <p style = "font-size: 1.1em; font-weight: 700; margin: 0">Materiales resistentes</p>
                    </div>""", unsafe_allow_html = True)

    columns = st.columns([1] * 2)
    column_index = 0
    for family in FAMILIES:
        current_column = columns[column_index]
        with current_column:
            printed = print_family(family, resistant_materials)
        if printed:
            column_index = (column_index + 1) % 2

    if False:
        column_index = 2
        for family in FAMILIES:
            if column_index == 2:
                columns = st.columns([1] * 2)
                column_index = 0
            current_column = columns[column_index]
            with current_column:
                printed = print_family(family, resistant_materials)

            if printed:
                column_index = column_index + 1


        st.markdown(f"""<div style = "margin-bottom: 0px">
                        <div style = "font-weight: 700">{family}</div>""", unsafe_allow_html=True)







set_style()
st.set_page_config(layout = 'wide')

images = load_images()
generate_title_and_logo(images)

add_vertical_spacing(TITLE_AND_TOGGLES_SPACING)
generate_toggles()

graph_column, sliders_column = st.columns([4, 1])
with graph_column:
    generate_graph_from_toggles()
with sliders_column:
    generate_sliders()
    print_resistant_materials(st.session_state['Concentración_slider'], st.session_state['Temperatura_slider'])






