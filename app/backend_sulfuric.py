
from pathlib import Path
import streamlit as st
import pandas as pd
import altair

ROOT_PATH = Path(__file__).resolve().parent.parent
CURVES_PATH = ROOT_PATH / 'data' / 'sulfuric_acid_curves'

X_MIN = 5
X_MAX = 100 #125
Y_MIN = 0
Y_MAX = 180
HOVERED_CURVE_OPACITY = 1.0 #unused
NON_HOVERED_CURVE_OPACITY = 0.4 #unused
HOVERED_CURVE_THICKNESS = 2.6
NON_HOVERED_CURVE_THICKNESS = 1.6
AREA_UNDER_CURVE_OPACITY = 0.15


ALIASES = {}


class Curve:

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return(self.name)


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
        
        curve = Curve(curve_name, curve_data)
        curves_by_name[curve_name] = curve

    return(curves_by_name)

@st.cache_resource
def load_all_curves_data():
    curves_by_name = load_curves()
    curves_data = []
    for name, curve in curves_by_name.items():
        curve.data['material'] = name   #Add the name of the curve to different between datasets, format required by Altair
        curves_data.append(curve.data)
    all_curves_data = pd.concat(curves_data)
    return(all_curves_data)

def generate_graph():
    all_curves_data = load_all_curves_data()
    altair.data_transformers.disable_max_rows()

    base_chart = altair.Chart(all_curves_data)
    base_chart = base_chart.transform_filter(altair.FieldOneOfPredicate(field = 'material', oneOf = ['AISI 316', '904 L']))
    base_chart = base_chart.transform_filter(altair.datum.x <= X_MAX)

    base_chart = base_chart.encode(x = altair.X('x', scale = altair.Scale(domain = [X_MIN, X_MAX])))
    base_chart = base_chart.encode(y = altair.Y('y', scale = altair.Scale(domain = [Y_MIN, Y_MAX])))
    base_chart = base_chart.encode(color = 'material')#, detail = 'material')

    hovered_curve = altair.selection_point(on = 'pointerover', fields = ['material'], empty = False)
    clicked_curve = altair.selection_point(fields = ['material'], on = 'click', empty = False)
    
    points = base_chart.mark_circle(size = 6000, opacity = 0)
    points = points.add_params(hovered_curve)

    lines = base_chart.mark_line(clip = True)
    lines = lines.encode(strokeWidth = altair.condition(hovered_curve, altair.value(HOVERED_CURVE_THICKNESS), altair.value(NON_HOVERED_CURVE_THICKNESS)))
    #lines = lines.encode(opacity = altair.condition(hover, altair.value(HOVERED_CURVE_OPACITY), altair.value(NON_HOVERED_CURVE_OPACITY)))
    lines = lines.add_params(clicked_curve)

    area = base_chart.transform_filter(clicked_curve)
    area = area.mark_area(opacity = AREA_UNDER_CURVE_OPACITY, clip = True)
    
    full_chart = points + lines + area
    return(full_chart)











