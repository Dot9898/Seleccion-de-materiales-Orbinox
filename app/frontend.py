
#encoding: utf-8

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
from streamlit_searchbox import st_searchbox
from backend import get_data
from backend import make_fluid_search

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'
LOGO_WIDTH = 200
QUALITY_COLOR_WIDTH = 12
DIVIDER_COLOR = '#66c6f3fa'
DIVIDER_AND_BUTTONS_SPACING = 18
EXTRA_SPACING_TO_FIX_FIRST_BOTTOM_SCROLL = 1000
SPECIAL_FLUIDS = ['Agua blanca', 'Agua de mar', f'Ácido sulfúrico (75% - 100%)', 'Cal']



@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    images['blue'] = Image.open(IMG_PATH / 'blue.jpg')
    images['lblue'] = Image.open(IMG_PATH / 'light_blue.jpg')
    images['orange'] = Image.open(IMG_PATH / 'orange.jpg')
    images['red'] = Image.open(IMG_PATH / 'red.jpg')
    images['22'] = Image.open(IMG_PATH / 'twenty_two.jpg')
    images['48'] = Image.open(IMG_PATH / 'forty_eight.jpg')
    return(images)

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

def scroll_to_bottom():
    st.markdown('<meta http-equiv = "refresh" content = "0; url = #b">', unsafe_allow_html = True)

def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)

def print_text_and_icon_inline(text, temp_img, reverse):
    temp_html = ''
    if temp_img is not None:
        temp_html = img_to_html_jpg(temp_img, 20)

    if not reverse:
        st.markdown(f"""
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">
                <span style="font-size: 1rem; line-height: 1;">{text}</span>
                {temp_html}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">
                {temp_html}
                <span style="font-size: 1rem; line-height: 1;">{text}</span>
            </div>
        """, unsafe_allow_html=True)

def print_material_and_quality_in_columns(material, color_image, temperature_icon):
    color_column, material_column = st.columns([1, 14])
    with color_column:
        st.image(color_image, width = QUALITY_COLOR_WIDTH)
    with material_column:
        text = material.name
        print_text_and_icon_inline(text, temperature_icon, reverse = False)

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

def generate_title_and_logo(images):
    title_column, logo_column = st.columns([3, 1])

    with title_column:
        st.markdown("""
                    <div style="display: flex; flex-direction: column; justify-content: flex-end; height: 150px;">
                        <h4 style="margin: 0; font-size: 3rem; font-weight: 450;">
                            Selección de materiales
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True)

    with logo_column:
        logo = images['logo']
        logo = img_to_base64(logo)
        st.markdown(f"""
                    <div style="
                        display: flex;
                        justify-content: flex-end;
                        align-items: flex-end;
                        height: 122px;
                    ">
                        <img src="data:image/png;base64,{logo}" width="{LOGO_WIDTH}">
                    </div>
                    """,
                    unsafe_allow_html=True)

def generate_searchbars(fluids, fluid_families, fluid_name_to_Fluid):
    st.write('')
    search_column, dropdown_column = st.columns([3, 1])

    with dropdown_column:
        selected_family = None

        #Searched y fluid_family_dropdown son usados para que la el resultado de la searchbox
        #no siga sobrescribiendo el resultados de los botones después de que un botón se selecciona.
        if st.session_state['searched']:
            st.session_state['fluid_family_dropdown'] = None

        selected_family = st.selectbox('Tipo de fluido', #Desactivar el poder escribir en la caja está fuera de las capacidades de Streamlit
                                        fluid_families, 
                                        label_visibility = 'collapsed', 
                                        accept_new_options = False, 
                                        index = None, 
                                        placeholder = 'Buscar por tipo (opcional)', 
                                        key = 'fluid_family_dropdown')
        if selected_family is not None:
            st.session_state['fluid_source'] = 'family'
            st.session_state['selected_family'] = selected_family
        elif st.session_state['fluid_source'] != 'initial':
            st.session_state['fluid_source'] = None
        
    with search_column: #arreglar la alineación con el dropdown
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
            if st.button(initial):
                selected_initial = initial
    if selected_initial is not None:
        st.session_state['fluid_source'] = 'initial'
        st.session_state['selected_initial'] = selected_initial
        st.session_state['searched'] = True #Reusa el sistema de la searchbox para que al usar otro fluid_source, el dropdown se resetee

def generate_fluids_buttons_by_condition(fluids, condition, selected_condition): #Crea los botones que empiezan con A, 
                                                                                 #si condition == 'initial' #y selected_condition == 'A'
    
    if condition == 'special':
        fluids_with_condition = [fluid for fluid in fluids if fluid.name in selected_condition]
        columns = st.columns(len(selected_condition) * [1])
        for index in range(len(fluids_with_condition)):
            fluid = fluids_with_condition[index]
            current_column = columns[index]
            key = fluid.name + '_special'
            with current_column:
                if st.button(fluid.name, width = 'stretch', key = key):
                    st.session_state['selected_fluid'] = fluid
                    st.session_state['fluid_source'] = 'special'
                    scroll_to_bottom()
        return()
    
    if condition == 'family':
        fluids_with_condition = (fluid for fluid in fluids if fluid.family == selected_condition)
    if condition == 'initial':
        fluids_with_condition = (fluid for fluid in fluids if fluid.initial == selected_condition)
    while True:
        for current_column in st.columns([1]*8):
            try:
                fluid = next(fluids_with_condition) #Why did I do it this way
            except:
                return()
            with current_column:
                if st.button(fluid.name, width = 'stretch'):
                    st.session_state['selected_fluid'] = fluid
                    scroll_to_bottom()

def generate_checkboxes_and_materials(selected_fluid, images):
    materials_columns = st.columns([2, 2, 2, 1, 1])
    checkboxes_column = materials_columns[4]

    #Por algún motivo el session state de las checkboxes se reinician (temporalmente) al escribir en la searchbox, lo que hace que
    #defaulteen a True al escribir o seleccionar una búsqueda, y no se reinicien hasta que haya otra interacción de usuario.
    #Usar last_only como valor default soluciona esto.
    with checkboxes_column:
        only_resistant = st.checkbox('Mostrar solo los materiales más resistentes', 
                                     value = st.session_state['last_only_resistant'], 
                                     key = 'only_resistant')
        only_inOrbinox = st.checkbox('Mostrar solo materiales disponibles en Orbinox', 
                                     value = st.session_state['last_only_inOrbinox'], 
                                     key = 'only_inOrbinox')
        st.session_state['last_only_resistant'] = st.session_state['only_resistant']
        st.session_state['last_only_inOrbinox'] = st.session_state['only_inOrbinox']
        

    blue, light_blue, orange, red = images['blue'], images['lblue'], images['orange'], images['red']
    quality_to_colored_image = {1: red, 2: orange, 3: light_blue, 4: blue}
    icon_22, icon_48 = images['22'], images['48']
    temperature_to_icon = {3: None, 2: icon_48, 1: icon_22}

    materials_to_show, families_to_show = selected_fluid.materials_and_families_to_show(materials, only_inOrbinox, only_resistant)
    materials_to_show = sorted(materials_to_show, key = lambda material: (selected_fluid.resistance[material].quality, 
                                                                          selected_fluid.resistance[material].temperature), 
                                                                          reverse = True)
    families_order = ['Metales', 'Plásticos', 'Elastómeros', 'No metales']
    families_to_show = sorted(families_to_show, key = lambda family: families_order.index(family))

    columns_and_families = zip(materials_columns, families_to_show)
    for family_column, family in columns_and_families:
        with family_column:
            st.subheader(family)
            
            if family != 'No metales':
                half_columns = st.columns([1, 1])
                half_counter = 0
                for material in materials_to_show:
                    if material.family == family:
                        current_half = half_columns[half_counter%2]
                        with current_half:
                            color_image = quality_to_colored_image[selected_fluid.resistance[material].quality]
                            temperature_icon = temperature_to_icon[selected_fluid.resistance[material].temperature]
                            print_material_and_quality_in_columns(material, color_image, temperature_icon)
                        half_counter = half_counter + 1
            else:
                for material in materials_to_show:
                    if material.family == family:
                        color_image = quality_to_colored_image[selected_fluid.resistance[material].quality]
                        temperature_icon = temperature_to_icon[selected_fluid.resistance[material].temperature]
                        print_material_and_quality_in_columns(material, color_image, temperature_icon)

def generate_legend(images):
    st.write('')
    st.write('')
    st.write('')

    legend_columns = st.columns([1]*8)
    icons = [images['blue'], images['lblue'], images['orange'], images['red'], images['48'], images['22']]
    texts =['Resistente', 'Aceptable', 'Poco resistente', 'No resistente', 'Hasta 48° C', 'Hasta 22° C']
    legend = zip(legend_columns, icons, texts)
    for column, icon, text in legend:
        with column:
            if icon in [images['48'], images['22']]:
                print_text_and_icon_inline(text, icon, reverse = True)
            else:
                print_icon_and_text_in_column(icon, text)


#-----------------------------------------------------------------------------------------------------------------------------------------------


data = get_data()
images = load_images()
materials = data['materials']
fluids = data['fluids']
fluid_families = data['fluid_families']
fluid_initials = data['fluid_initials']
fluid_name_to_Fluid = data['fluid_name_to_Fluid']
material_name_to_Material = data['material_name_to_Material']
st.set_page_config(layout = 'wide')

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


generate_title_and_logo(images)
generate_searchbars(fluids, fluid_families, fluid_name_to_Fluid)
generate_letter_buttons(fluid_initials)
generate_fluids_buttons_by_condition(fluids, 'special', SPECIAL_FLUIDS)
horizontal_divider(DIVIDER_COLOR, 2, '0')

if st.session_state['fluid_source'] == 'family':
    add_vertical_spacing(DIVIDER_AND_BUTTONS_SPACING)
    generate_fluids_buttons_by_condition(fluids, 'family', st.session_state['selected_family'])
    horizontal_divider(DIVIDER_COLOR, 2, '0')

elif st.session_state['fluid_source'] == 'initial':
    add_vertical_spacing(DIVIDER_AND_BUTTONS_SPACING)
    generate_fluids_buttons_by_condition(fluids, 'initial', st.session_state['selected_initial'])
    horizontal_divider(DIVIDER_COLOR, 2, '0')


#Bottom scroll on button click
st.markdown('<div id = "b"></div>', unsafe_allow_html = True)

fluid = st.session_state['selected_fluid']
if fluid is not None:
    st.header(fluid.name)
    if fluid.name in SPECIAL_FLUIDS:
        pressure_column, temperature_column, empty_column = st.columns([1, 1, 2])
        with pressure_column:
            st.slider('Presión')
        with temperature_column:
            st.slider('Temperatura')
    generate_checkboxes_and_materials(fluid, images)
    generate_legend(images)
else:
    add_vertical_spacing(EXTRA_SPACING_TO_FIX_FIRST_BOTTOM_SCROLL)


if st.session_state['searched']:
    st.rerun()


