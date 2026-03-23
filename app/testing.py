
import altair as alt
import pandas as pd
import streamlit as st


def testchart():
    df = pd.DataFrame({
        "x": [1, 2, 3],
        "y": [2, 3, 5],
    })

    base = alt.Chart(df).mark_point().encode(
        x="x",
        y="y"
    )

    msg = pd.DataFrame({
        "line": ["Line 1", "Line 2", "Line 3"],
        "y": [0, 14, 28]
    })

    annotation = alt.Chart(msg).mark_text(
        align="right",
        baseline="top",
        fontSize=12
    ).encode(
        text="line",
        x=alt.value({"expr": "width"}),
        y="y"
    )

    return base + annotation



