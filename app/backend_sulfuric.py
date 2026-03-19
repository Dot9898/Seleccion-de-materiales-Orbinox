
from pathlib import Path
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

HOVERED_CURVE_OPACITY = 1.0 #unused
NON_HOVERED_CURVE_OPACITY = 0.4 #unused
HOVERED_CURVE_THICKNESS = 2.6
NON_HOVERED_CURVE_THICKNESS = 1.6
AREA_UNDER_CURVE_OPACITY = 0.15

LEGEND_ORIENTATION = 'left'
LEGEND_COLUMNS = 1


class Curve:

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.segments = self.get_segments()

    def __repr__(self):
        return(self.name)
    
    def get_segments(self):
        data = self.data
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

        real_curve_name = FILE_NAME_TO_CURVE_NAME[curve_name]
        
        curve = Curve(real_curve_name, curve_data)
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

def generate_graph(curves_to_show):
    all_curves_data = load_all_curves_data()
    altair.data_transformers.disable_max_rows()

    base_chart = altair.Chart(all_curves_data)

    base_chart = base_chart.encode(x = altair.X('x', title = f'Concentración {EMPTY_SPACE}(%)', scale = altair.Scale(domain = [X_MIN, X_MAX])))
    base_chart = base_chart.encode(y = altair.Y('y', title = f'Temperatura {EMPTY_SPACE}(°C)', scale = altair.Scale(domain = [Y_MIN, Y_MAX])))
    base_chart = base_chart.transform_filter(altair.FieldOneOfPredicate(field = 'Material', oneOf = curves_to_show))
    base_chart = base_chart.transform_filter(altair.datum.x <= X_MAX)

    names = curves_to_show
    colors = [CURVE_NAME_TO_COLOR[name] for name in names]
    scale = altair.Scale(domain = names, range = colors)
    legend = altair.Legend(title = None, columns = LEGEND_COLUMNS, orient = LEGEND_ORIENTATION, symbolOpacity = 1)#, symbolStrokeWidth = 3)
    color = altair.Color('Material', scale = scale, legend = legend)
    base_chart = base_chart.encode(color = color)

    hovered_curve = altair.selection_point(on = 'pointerover', fields = ['Material'], empty = False)
    clicked_curve = altair.selection_point(fields = ['Material'], on = 'click', empty = False)
    
    points = base_chart.mark_circle(size = 4000, opacity = 0)
    points = points.add_params(hovered_curve)

    lines = base_chart.mark_line(clip = True)
    lines = lines.encode(strokeWidth = altair.condition(hovered_curve, altair.value(HOVERED_CURVE_THICKNESS), altair.value(NON_HOVERED_CURVE_THICKNESS)))
    #lines = lines.encode(opacity = altair.condition(hover, altair.value(HOVERED_CURVE_OPACITY), altair.value(NON_HOVERED_CURVE_OPACITY)))
    lines = lines.add_params(clicked_curve)

    area = base_chart.transform_filter(clicked_curve)
    area = area.mark_area(opacity = AREA_UNDER_CURVE_OPACITY, clip = True)
    
    full_chart = points + lines + area
    return(full_chart)

def get_resistant_materials(concentration, temperature):
    resistant_materials = []
    curves_by_name = load_curves()
    for name, curve in curves_by_name.items():
        if curve.is_resistant(concentration, temperature):
            resistant_materials.append(name)
            
    if 'Punto de ebullición' in resistant_materials:
        resistant_materials.remove('Punto de ebullición')
    return(resistant_materials)









