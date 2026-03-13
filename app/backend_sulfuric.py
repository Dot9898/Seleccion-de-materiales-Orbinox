
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

@st.cache_resource
def load_graph():
    all_curves_data = load_all_curves_data()
    altair.data_transformers.disable_max_rows()
    chart = altair.Chart(all_curves_data)
    chart = chart.mark_line(clip = True)
    #chart = chart.transform_filter((altair.datum.x >= X_MIN) & (altair.datum.x <= X_MAX))
    chart = chart.encode(x = altair.X('x', scale = altair.Scale(domain = [X_MIN, X_MAX])))
    chart = chart.encode(y = altair.Y('y', scale = altair.Scale(domain = [Y_MIN, Y_MAX])))
    chart = chart.encode(color = 'material')
    return(chart)










