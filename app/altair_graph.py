
from pathlib import Path
from math import pi as PI
import streamlit as st
import numpy as np
import pandas as pd
import altair
from constants import FILE_NAME_TO_CURVE_NAME
from constants import CURVE_NAME_TO_COLOR

ROOT_PATH = Path(__file__).resolve().parent.parent
CURVES_PATH = ROOT_PATH / 'data' / 'sulfuric_acid_curves'

EMPTY_SPACE = '\u00A0'

X_MIN = 5
X_MAX = 100 #125
Y_MIN = 0
Y_MAX = 180

LATTICE_X_STEP = 2 #int
LATTICE_Y_STEP = 5

LEGEND_ORIENTATION = 'left'
LEGEND_COLUMNS = 1
TOOLTIP_DECIMALS = 2 #min 2 for curve smoothness

HOVERED_CURVE_THICKNESS = 2.6
NON_HOVERED_CURVE_THICKNESS = 1.6

CURVES_POINTS_RADIUS = 12#8
AREA_UNDER_CURVE_OPACITY = 0.15

CLICKED_POINT_COLOR = '#1F84B5'
CLICKED_POINT_OPACITY = 1.0
CLICKED_POINT_RADIUS = 5

CHLORIDES_MESSAGES = [
'La resistencia de los materiales al ácido sulfúrico con cloruros depende de la concentración de estos.', 
'Las curvas mostradas son válidas para el ácido sulfúrico con 2000 ppm de cloruros, equivalente a:', 
'2.3 g/L con ácido concentrado al 20%', 
'3.7 g/L con ácido concentrado al 98%', 
'', 
'Como regla general, los materiales resistentes en función de', 
'la concentración de cloruros son los siguientes:', 
'Hasta 2 g/L: Acero inoxidable 316', 
'Hasta 10: Duplex 2205', 
'Hasta 15: 254 SMO', 
'Más de 15 g/L: Hastelloy C o titanio']

MESSAGES_X_SHIFT = -9
MESSAGES_Y_SHIFT = 25
MESSAGES_SEPARATION = 18
MESSAGES_SIZE = 14
MESSAGES_COLOR = '#3e4c59'

#debug
CURVES_POINTS_OPACITY = 0. #unused
LATTICE_POINTS_RADIUS = 10 #unused
LATTICE_POINTS_OPACITY = 0 #unused
HOVERED_CURVE_OPACITY = 1.0 #unused
NON_HOVERED_CURVE_OPACITY = 0.4 #unused

CLICKED_POINT_AREA = PI * CLICKED_POINT_RADIUS ** 2
CURVES_POINTS_AREA = PI * CURVES_POINTS_RADIUS ** 2
CURVES_POINTS_AREA_MOBILE = PI * (CURVES_POINTS_RADIUS + 3) ** 2
LATTICE_POINTS_AREA = PI * LATTICE_POINTS_RADIUS ** 2 #unused



class Curve:

    def __init__(self, name, data, segments):
        self.name = name
        self.data = data
        self.segments = segments

    def __repr__(self):
        return(self.name)
    
    def is_resistant(self, concentration, temperature):
        for segment in self.segments:
            concentrations = segment['x']
            temperatures = segment['y']
            if not (concentrations.min() <= concentration <= concentrations.max()):
                continue
            max_resistant_temperature_interpolated = np.interp(concentration, concentrations, temperatures)
            if temperature <= max_resistant_temperature_interpolated:
                return(True)
        return(False)


def get_segments(data):
    mask = data['y'].isna()
    separator_index = data.index[mask]

    if len(separator_index) == 0:
        return([data])

    elif len(separator_index) == 1:
        index = separator_index[0]
        left_half = data.loc[:index - 1]
        right_half = data.loc[index + 1:]
        return([left_half, right_half])
    
    return(None)

def multiply_point_quantity_and_round(data, factor, round = 2):
    x = data['x'].values
    y = data['y'].values
    points_number = len(x)
    new_points_number = points_number * factor
    new_x = np.linspace(x.min(), x.max(), new_points_number)
    new_y = np.interp(new_x, x, y)
    new_x = np.round(new_x, round)
    new_y = np.round(new_y, round)
    new_data = pd.DataFrame({'x': new_x, 'y': new_y})
    return(new_data)

@st.cache_resource
def load_lattice_data():
    lattice_data = create_lattice_data(X_MIN + 1, X_MAX, LATTICE_X_STEP, Y_MIN, Y_MAX, LATTICE_Y_STEP)
    lattice_data['Point'] = lattice_data.index
    return(lattice_data)

@st.cache_resource
def create_lattice_data(x_min, x_max, x_step, y_min, y_max, y_step):
    points = []
    for x in range(x_min, x_max + 1, x_step):
        for y in range(y_min, y_max + 1, y_step):
            points.append({'x': x, 'y': y})

    lattice_data = pd.DataFrame(points)
    return(lattice_data)

@st.cache_resource
def load_curves():
    curves_by_name = {}

    curve_names = pd.read_csv(CURVES_PATH / 'curve_names.csv', 
                              header = None)
    curve_names = list(curve_names.iloc[:, 0])

    for curve_name in curve_names:
        curve_data = pd.read_csv(CURVES_PATH / 'curves' / (curve_name + '.csv'), 
                                 dtype = float, 
                                 header = None, 
                                 names = ['x', 'y'])
        curve_data = curve_data.sort_values('x')
        curve_data = curve_data.drop_duplicates()

        segments = get_segments(curve_data)
        if len(segments) == 1:
            curve_data = multiply_point_quantity_and_round(segments[0], 2, TOOLTIP_DECIMALS)
        elif len(segments) == 2:
            left_half = multiply_point_quantity_and_round(segments[0], 2, TOOLTIP_DECIMALS)
            right_half = multiply_point_quantity_and_round(segments[1], 2, TOOLTIP_DECIMALS)
            separator = pd.DataFrame({'x': [40.00000], 'y': [np.nan]})
            curve_data = pd.concat([left_half, separator, right_half], ignore_index = True)
        else:
            raise Exception('Curve data has more than two segments')

        real_curve_name = FILE_NAME_TO_CURVE_NAME[curve_name]        
        curve = Curve(real_curve_name, curve_data, segments)
        curves_by_name[real_curve_name] = curve

    return(curves_by_name)

@st.cache_resource
def load_all_curves_data():
    curves_by_name = load_curves()
    curves_data = []
    for name, curve in curves_by_name.items():
        curve.data['Material'] = name   #Add the name of the curve to differentiate between datasets, format required by Altair
        curves_data.append(curve.data)
    all_curves_data = pd.concat(curves_data)
    return(all_curves_data)

def add_messages(chart, anchor_point):
    text_layers = []
    shift = MESSAGES_Y_SHIFT
    for message in CHLORIDES_MESSAGES:
        text = anchor_point.mark_text(align = 'right', baseline = 'bottom', color = MESSAGES_COLOR, 
                                      dx = MESSAGES_X_SHIFT, dy = shift, fontSize = MESSAGES_SIZE)
        text = text.encode(text = altair.value(message))
        text_layers.append(text)
        shift = shift + MESSAGES_SEPARATION
    
    for layer in text_layers:
        chart += layer
    return(chart)

def generate_graph(curves_to_show, highlighted_point_coordinates, chlorides_message, mobile = False):
    all_curves_data = load_all_curves_data()
    lattice_data = load_lattice_data()
    altair.data_transformers.disable_max_rows()

    curves_base = altair.Chart(all_curves_data)
    lattice = altair.Chart(lattice_data)

    curves_base = curves_base.encode(x = altair.X('x', title = f'Concentración {EMPTY_SPACE}(%)', scale = altair.Scale(domain = [X_MIN, X_MAX])))
    curves_base = curves_base.encode(y = altair.Y('y', title = f'Temperatura {EMPTY_SPACE}(°C)', scale = altair.Scale(domain = [Y_MIN, Y_MAX])))
    #curves_base = curves_base.transform_filter(altair.datum.x <= X_MAX)
    curves_base = curves_base.transform_filter(altair.FieldOneOfPredicate(field = 'Material', oneOf = curves_to_show))

    lattice = lattice.encode(x = altair.X('x', scale = altair.Scale(domain = [X_MIN, X_MAX])))
    lattice = lattice.encode(y = altair.Y('y', scale = altair.Scale(domain = [Y_MIN, Y_MAX])))


    names = curves_to_show
    colors = [CURVE_NAME_TO_COLOR[name] for name in names]
    scale = altair.Scale(domain = names, range = colors)
    if not mobile:
        legend = altair.Legend(title = None, columns = LEGEND_COLUMNS, orient = LEGEND_ORIENTATION, symbolOpacity = 1)#, symbolStrokeWidth = 3)
    else:
        legend = None
    color = altair.Color('Material', scale = scale, legend = legend)
    curves_base = curves_base.encode(color = color)

    hovered_curve = altair.selection_point(on = 'pointerover', fields = ['Material'], empty = False)
    clicked_curve = altair.selection_point(fields = ['Material'], on = 'click', empty = False)

    curve_points_area = CURVES_POINTS_AREA_MOBILE if mobile else CURVES_POINTS_AREA_MOBILE
    curve_points = curves_base.mark_circle(size = curve_points_area, opacity = CURVES_POINTS_OPACITY, clip = True)
    curve_points = curve_points.add_params(hovered_curve)

    lines = curves_base.mark_line(interpolate = 'monotone', clip = True)
    lines_width = altair.condition(hovered_curve, altair.value(HOVERED_CURVE_THICKNESS), altair.value(NON_HOVERED_CURVE_THICKNESS))
    lines = lines.encode(strokeWidth = lines_width)
    #lines = lines.encode(opacity = altair.condition(hover, altair.value(HOVERED_CURVE_OPACITY), altair.value(NON_HOVERED_CURVE_OPACITY)))
    lines = lines.add_params(clicked_curve)

    area = curves_base.transform_filter(clicked_curve)
    area = area.mark_area(opacity = AREA_UNDER_CURVE_OPACITY, clip = True)

    ##UNCOMMENT WHEN STREAMLIT LAYERED CHARTS VALUES CAN BE PASSED TO MAIN PROGRAM (implementation from Streamlit side in process)
    ##clicked_point = altair.selection_point(nearest = True, on = 'click', empty = False)

    lattice_points = lattice.mark_circle(opacity = 0) #size = LATTICE_POINTS_AREA, opacity = LATTICE_POINTS_OPACITY, clip = True
    ##lattice_points = lattice_points.add_params(clicked_point)

    shown_point = lattice.mark_point(size = CLICKED_POINT_AREA, filled = True, clip = True)
    shown_x_coord, shown_y_coord = highlighted_point_coordinates
    if shown_x_coord is not None and shown_y_coord is not None:
        coord_condition = altair.FieldEqualPredicate(field = 'x', equal = shown_x_coord) & altair.FieldEqualPredicate(field = 'y', equal = shown_y_coord)
        shown_point = shown_point.transform_filter(coord_condition)
        ##?shown_point = shown_point.encode(opacity = altair.condition(clicked_point, altair.value(CLICKED_POINT_OPACITY), altair.value(0)))
    else:
        shown_point = shown_point.encode(opacity = altair.value(0)) #Don't show point if either coord is None
    shown_point = shown_point.encode(color = altair.value(CLICKED_POINT_COLOR))

    chart = lattice_points
    if curves_to_show != []:
        chart += curve_points + lines + area

    if chlorides_message:
        anchor_condition = (altair.datum.x == X_MAX) & (altair.datum.y == Y_MAX)
        anchor_point = lattice.transform_filter(anchor_condition)
        anchor_point = anchor_point.mark_point()
        chart = add_messages(chart, anchor_point)
        
        #Make shown point opacity = 0 if over the text?

    chart = chart + shown_point

    return(chart)











