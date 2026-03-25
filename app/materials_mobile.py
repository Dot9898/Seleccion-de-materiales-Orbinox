
#encoding: utf-8

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
from style import set_style
from streamlit_searchbox import st_searchbox
from backend import load_data
from backend import make_fluid_search

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'

MAIN_TEXT_COLOR = '#3e4c59'
EMPTY_SPACE = '‎'
LOGO_WIDTH = 150
DISCLAIMER_LOGO_WIDTH = 230
MIN_LOGO_HEIGHT = 10
LOGO_HEIGHT = MIN_LOGO_HEIGHT

QUALITY_COLOR_WIDTH = 12
DIVIDER_COLOR = '#a1cae4'
DIVIDER_AND_BUTTONS_SPACING = 18
EXTRA_SPACING_TO_FIX_FIRST_BOTTOM_SCROLL = 1000



def img_to_html_jpg(img, width):
    buffer = BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return(f'<img src="data:image/jpeg;base64,{encoded}" width="{width}">')

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return(base64.b64encode(buffer.getvalue()).decode())

def display_centered_image(image, width):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/webp;base64,{image}" width={width}>
        </div>
        """, 
        unsafe_allow_html = True)

def write_justified_and_centered_text(text):
    st.markdown(f"<p style='text-align: justify; text-align-last: center'>{text}</p>", unsafe_allow_html = True)

@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    images['logo_b64'] = img_to_base64(images['logo'])
    images['blue'] = Image.open(IMG_PATH / 'blue.jpg')
    images['lblue'] = Image.open(IMG_PATH / 'light_blue.jpg')
    images['orange'] = Image.open(IMG_PATH / 'orange.jpg')
    images['red'] = Image.open(IMG_PATH / 'red.jpg')
    images['22'] = Image.open(IMG_PATH / 'twenty_two.jpg')
    images['48'] = Image.open(IMG_PATH / 'forty_eight.jpg')
    return(images)

def disable_disclaimer():
    st.session_state['show_disclaimer'] = False

def scroll_to_bottom():
    st.markdown('<meta http-equiv = "refresh" content = "0; url = #b">', unsafe_allow_html = True)

def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)

def print_text_and_icons_inline(text, icon_left, icon_right):
    if icon_left is not None:
        icon_left = img_to_html_jpg(icon_left, 20)
    else:
        icon_left = ''
    if icon_right is not None:
        icon_right = img_to_html_jpg(icon_right, 20)
    else:
        icon_right = ''

    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">
            {icon_left}
            <span style="font-size: 1rem; line-height: 1;">{text}</span>
            {icon_right}
        </div>
    """, unsafe_allow_html=True)

def print_icon_and_text_in_column(icon, text):
    icon_column, text_column = st.columns([1, 14])
    with icon_column:
        st.image(icon, width = QUALITY_COLOR_WIDTH)
    with text_column:
        st.write(text)

def horizontal_divider(color, thickness, margin):
    st.markdown(
        f"""
        <hr style="
            border: none;
            border-top: {thickness}px solid {color};
            margin: {margin};
        ">
        """,
        unsafe_allow_html=True,
    )

@st.dialog(EMPTY_SPACE, width = 'small', on_dismiss = disable_disclaimer)
def generate_disclaimer(logo):
    display_centered_image(logo, DISCLAIMER_LOGO_WIDTH)
    st.write('')
    st.write('')
    st.write('')
    text = 'La selección de materiales Orbinox se ofrece exclusivamente como recomendación. '\
           'Orbinox no garantiza precisión, conveniencia, ni durabilidad de las selecciones aquí descritas. '\
           'Para más información, contactar con nuestro equipo de ingenieros.'
    write_justified_and_centered_text(text)

def generate_title():
    #Needs html to center, markdown creates extra spacing
    st.html(f"""
    <div style="text-align: center;">
        <h3 style="
            margin: 0;
            line-height: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            text-align: center;
            font-size: 2.2rem;
            font-weight: 450;
            color: {MAIN_TEXT_COLOR};
        ">
            Selección de materiales
        </h3>
    </div>
    """)

def generate_logo(logo_b64):
    st.markdown(f"""
                <div style="
                    display: flex; flex-direction: column;
                    justify-content: flex-end;
                    align-items: center;
                    height: {LOGO_HEIGHT}px;
                ">
                    <img src="data:image/webp;base64,{logo_b64}" width="{LOGO_WIDTH}">
                </div>
                """,
                unsafe_allow_html = True)

def generate_title_and_logo(images):
    logo = images['logo_b64']
    generate_logo(logo)
    st.write('')
    st.write('')
    generate_title()
    st.write('')

def generate_searchbar_mobile(fluids, fluid_name_to_Fluid):
    st.write('')

    searched_fluid = None
    search_function = make_fluid_search(fluids)
    searched_fluid = st_searchbox(search_function, 
                                  placeholder = 'Buscar fluido...', 
                                  clear_on_submit = True, 
                                  edit_after_submit = 'option', 
                                  key = 'fluids_searchbox')
    if searched_fluid in fluid_name_to_Fluid:
        st.session_state['fluid_source'] = 'search'
        st.session_state['selected_fluid'] = fluid_name_to_Fluid[searched_fluid]
        st.session_state['searched'] = True
    else:
        st.session_state['searched'] = False
    st.session_state['fluids_searchbox']['result'] = None

def generate_letter_buttons(fluid_initials):
    selected_initial = None
    initials_columns = st.columns([1]*len(fluid_initials))
    for index in range(len(fluid_initials)):
        current_column = initials_columns[index]
        initial = fluid_initials[index]
        with current_column:
            if st.button(initial, 
                         key = f'{initial}_button', 
                         width = 'stretch', 
                         type = 'primary'):
                selected_initial = initial
    if selected_initial is not None:
        st.session_state['fluid_source'] = 'initial'
        st.session_state['selected_initial'] = selected_initial
        st.session_state['searched'] = True #Reusa el sistema de la searchbox para que al usar otro fluid_source, el dropdown se resetee

def generate_fluids_buttons_by_condition(fluids, condition, selected_condition): #Crea los botones que empiezan con A, 
                                                                                 #si condition == 'initial' #y selected_condition == 'A'
    if condition == 'family':
        fluids_with_condition = (fluid for fluid in fluids if fluid.family == selected_condition)
    if condition == 'initial':
        fluids_with_condition = (fluid for fluid in fluids if fluid.initial == selected_condition)
    while True:
        for current_column in st.columns([1]*8):
            try:
                fluid = next(fluids_with_condition)
            except:
                return()
            with current_column:
                if st.button(fluid.name, 
                             key = f'{fluid.name}_button', 
                             width = 'stretch', 
                             type = 'secondary'):
                    st.session_state['selected_fluid'] = fluid
                    scroll_to_bottom()

def generate_materials_mobile(selected_fluid, images):
    st.markdown(f"<p style='font-size: 2rem; font-weight: 450'>{selected_fluid}</p>", unsafe_allow_html = True)

    blue, light_blue, orange, red = images['blue'], images['lblue'], images['orange'], images['red']
    quality_to_colored_image = {1: red, 2: orange, 3: light_blue, 4: blue}
    icon_22, icon_48 = images['22'], images['48']
    temperature_to_icon = {3: None, 2: icon_48, 1: icon_22}

    materials_to_show, families_to_show = selected_fluid.materials_and_families_to_show(materials, only_inOrbinox = False, only_resistant = False)
    materials_to_show = sorted(materials_to_show, key = lambda material: (selected_fluid.resistance[material].quality, 
                                                                          selected_fluid.resistance[material].temperature), 
                                                                          reverse = True)
    families_order = ['Metales', 'Plásticos', 'Elastómeros', 'No metales']
    families_to_show = sorted(families_to_show, key = lambda family: families_order.index(family))

    for family in families_to_show:
        st.markdown(f"<p style='font-size: 1.6rem; font-weight: 550'>{family}</p>", unsafe_allow_html = True)
        
        for material in materials_to_show:
            if material.family == family:
                color_image = quality_to_colored_image[selected_fluid.resistance[material].quality]
                temperature_icon = temperature_to_icon[selected_fluid.resistance[material].temperature]
                text = material.name
                print_text_and_icons_inline(text, color_image, temperature_icon)
                st.write('')
        st.write('')
        st.write('')

def generate_legend_mobile(images):
    st.write('')
    st.write('')
    st.write('')

    icons = [images['blue'], images['lblue'], images['orange'], images['red'], images['48'], images['22']]
    texts =['Resistente', 'Aceptable', 'Poco resistente', 'No resistente', 'Hasta 48° C', 'Hasta 22° C']
    legend = zip(icons, texts)
    for icon, text in legend:
        print_text_and_icons_inline(text, icon, icon_right = None)
        st.write('')



#-----------------------------------------------------------------------------------------------------------------------------------------------



data = load_data()
images = load_images()
materials = data['materials']
fluids = data['fluids']
fluid_families = data['fluid_families']
fluid_initials = data['fluid_initials']
fluid_name_to_Fluid = data['fluid_name_to_Fluid']
material_name_to_Material = data['material_name_to_Material']

if 'fluid_source' not in st.session_state:
    st.session_state['fluid_source'] = None
if 'selected_family' not in st.session_state:
    st.session_state['selected_family'] = None
if 'selected_initial' not in st.session_state:
    st.session_state['selected_initial'] = None
if 'selected_fluid' not in st.session_state:
    st.session_state['selected_fluid'] = None
if 'searched' not in st.session_state:
    st.session_state['searched'] = False
if 'last_only_inOrbinox' not in st.session_state:
    st.session_state['last_only_inOrbinox'] = False
if 'last_only_resistant' not in st.session_state:
    st.session_state['last_only_resistant'] = False
if 'show_disclaimer' not in st.session_state:
    st.session_state['show_disclaimer'] = True


set_style()
st.set_page_config(layout = 'centered')

if st.session_state['show_disclaimer']:
    generate_disclaimer(images['logo_b64'])

generate_title_and_logo(images)
generate_searchbar_mobile(fluids, fluid_name_to_Fluid)
horizontal_divider(DIVIDER_COLOR, 2, '0')

if st.session_state['selected_fluid'] is not None:
    generate_materials_mobile(st.session_state['selected_fluid'], images)
    horizontal_divider(DIVIDER_COLOR, 2, '0')
    generate_legend_mobile(images)


if st.session_state['searched']:
    st.rerun()



