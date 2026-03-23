

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
from style import set_style
from altair_graph import generate_graph, load_curves
from constants import FAMILIES
from constants import FAMILY_TO_CURVE_NAMES

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'

MAIN_TEXT_COLOR = '#3e4c59'
LOGO_WIDTH = 200
NAVIGATION_MENU_HEIGHT = 35
MIN_LOGO_HEIGHT = 100 - NAVIGATION_MENU_HEIGHT
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

def get_resistant_materials(concentration, temperature):
    resistant_materials = []
    curves_by_name = load_curves()
    for name, curve in curves_by_name.items():
        if curve.is_resistant(concentration, temperature):
            resistant_materials.append(name)

    if 'Punto de ebullición' in resistant_materials:
        resistant_materials.remove('Punto de ebullición')
    return(resistant_materials)



def set_selected_coords():
    if (st.session_state['sliders_were_touched']) and ('Concentración_slider' in st.session_state) and ('Temperatura_slider' in st.session_state):
        selected_concentration = st.session_state['Concentración_slider']
        selected_temperature = st.session_state['Temperatura_slider']
    else:
        selected_concentration = None
        selected_temperature = None
    return(selected_concentration, selected_temperature)

def set_sliders_to_touched():
    st.session_state['sliders_were_touched'] = True

def chlorides_checkbox_callback():
    checked = st.session_state['Ácido con cloruros_checkbox']
    
    if checked:
        for family in FAMILIES:
            toggle_key = f'{family}_toggle'
            st.session_state[toggle_key] = False
        st.session_state['Metales_toggle'] = True
    
    if not checked:
        for family in FAMILIES:
            toggle_key = f'{family}_toggle'
            st.session_state[toggle_key] = False
        st.session_state['Cauchos_toggle'] = True



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
    title_column, logo_column = st.columns([3, 1])
    with title_column:
        generate_title()
    with logo_column:
        generate_logo(images)

def generate_toggles():
    columns = st.columns([1] * 4)
    for index in range(4):
        with columns[index]:
            family = FAMILIES[index]
            key = f'{family}_toggle'
            disabled = False
            if st.session_state['Ácido con cloruros_checkbox'] and family != 'Metales':
                disabled = True
            st.toggle(family, 
                      key = key, 
                      value = True if family == 'Cauchos' else False, 
                      label_visibility = 'visible', 
                      disabled = disabled, 
                      help=None)

def generate_chlorides_checkbox():
    st.checkbox('Ácido con cloruros', 
                value = False, 
                key = 'Ácido con cloruros_checkbox', 
                on_change = chlorides_checkbox_callback)
    
def generate_graph_from_toggles_and_sliders_and_checkbox():
    curves_to_show = []

    if st.session_state['Ácido con cloruros_checkbox']:
        chlorides_message = True
        if st.session_state['Metales_toggle']:
            curves_to_show = curves_to_show + FAMILY_TO_CURVE_NAMES['Metales (ácido con cloruros)']
    
    else:
        chlorides_message = False
        for family in FAMILIES:
            key = f'{family}_toggle'
            if st.session_state[key]:
                curves_to_show = curves_to_show + FAMILY_TO_CURVE_NAMES[family]

    selected_coords = set_selected_coords()
    graph = generate_graph(curves_to_show, selected_coords, chlorides_message)
    st.altair_chart(graph, width = 'stretch', height = GRAPH_HEIGHT)#, key = 'Gráfico')

def generate_sliders():
    
    st.slider('Temperatura', 
              key = 'Temperatura_slider', 
              min_value = 0, 
              max_value = 180, 
              step = 5, 
              format = '%.0f °C', 
              on_change = set_sliders_to_touched)
    
    st.slider('Concentración', 
              key = 'Concentración_slider', 
              min_value = 6, 
              max_value = 100, 
              step = 2, 
              format = '%.0f%%', 
              on_change = set_sliders_to_touched)

def print_family(family, resistant_materials):
    materials_to_print = []
    for material in sorted(FAMILY_TO_CURVE_NAMES[family]):
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

    chlorides_checked = st.session_state['Ácido con cloruros_checkbox']
    resistant_materials = get_resistant_materials(concentration, temperature)
    if chlorides_checked:
        resistant_materials = [material for material in resistant_materials if material in FAMILY_TO_CURVE_NAMES['Metales (ácido con cloruros)']]

    if len(resistant_materials) >= 1:
        st.markdown(f"""<div style = "margin-bottom: 8px">
                    <p style = "font-size: 1.1em; font-weight: 700; margin: 0">Materiales resistentes</p>
                    </div>""", unsafe_allow_html = True)

    if chlorides_checked:
        print_family('Metales (ácido con cloruros)', resistant_materials)

    else:
        columns = st.columns([1] * 2)
        column_index = 0
        for family in FAMILIES:
            current_column = columns[column_index]
            with current_column:
                printed = print_family(family, resistant_materials)
            if printed:
                column_index = (column_index + 1) % 2

def write_chlorides_info(): #unused
    st.write('La resistencia de los materiales al ácido sulfúrico con cloruros depende de la concentración de estos.')
    st.write('Las curvas mostradas son válidas para el ácido sulfúrico con 2000 ppm de cloruros, equivalente a:')
    st.write('2.3 g/L con ácido concentrado al 20%%')
    st.write('3.7 g/L con ácido concentrado al 98%%')
    st.write('Como regla general, los materiales resistentes en función de la concentración de cloruros son los siguientes:')
    st.write('Hasta 2 g/L: Acero inoxidable 316')
    st.write('Hasta 10: Duplex 2205')
    st.write('Hasta 15: 254 SMO')
    st.write('Más de 15 g/L: Hastelloy C o titanio')




#----------------------------------------------------------------------------------------------------------------------------------------




if 'sliders_were_touched' not in st.session_state:
    st.session_state['sliders_were_touched'] = False


set_style()
st.set_page_config(layout = 'wide')

images = load_images()
generate_title_and_logo(images)

add_vertical_spacing(TITLE_AND_TOGGLES_SPACING)

graph_column, sliders_column = st.columns([4, 1])
with sliders_column:
    generate_chlorides_checkbox()
with graph_column:
    generate_toggles()
    generate_graph_from_toggles_and_sliders_and_checkbox()
with sliders_column:
    generate_sliders()
    print_resistant_materials(st.session_state['Concentración_slider'], st.session_state['Temperatura_slider'])









