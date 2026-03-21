
import altair as alt
import pandas as pd
import streamlit as st


@st.cache_resource
def testgraph(df):

    df = df.copy()
    df["id"] = df.index

    sel = alt.selection_point(
        fields=["id"],
        nearest=True,
        on="click",
        empty=False
    )

    base = alt.Chart(df)

    hit = base.mark_circle(
        size=200,
        opacity=0
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[5, 100])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 180]))
    ).add_params(sel)

    points = base.mark_circle(
        size=40,
        color="lightgray"
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[5, 100])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 180]))
    )

    cross = base.transform_filter(sel).mark_text(
        text="✕",
        size=18,
        color="red"
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[5, 100])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 180]))
    )

    chart = (points + hit + cross).properties(
        width=600,
        height=400
    )

    graph = chart

    return(graph)







