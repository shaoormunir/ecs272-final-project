# no need to delete this - it won't show up in the presentation unless you add it to presentation.py

# necessary imports - do not change
from dash import html, dcc, Input, Output, State
from server import app
import plotly.graph_objects as go
import pandas as pd
import json

from urllib.request import urlopen


with urlopen(
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
) as response:
    counties = json.load(response)

# custom imports
# ...


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
    dtype={"fips": str},
)

import plotly.express as px


fig = px.choropleth_mapbox(
    df,
    geojson=counties,
    locations="fips",
    color="unemp",
    color_continuous_scale="Viridis",
    range_color=(0, 12),
    mapbox_style="carto-positron",
    zoom=3,
    center={"lat": 37.0902, "lon": -95.7129},
    opacity=0.5,
    labels={"unemp": "unemployment rate"},
)

fig.update_layout(geo_scope="world")

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

content = html.Div(
    style=dict(textAlign="center"),
    children=[
        html.H1(children="Identified Geothermal Systems of the Western USA"),
        html.Div(
            children="""
        This data was provided by the USGS.
    """
        ),
        dcc.Graph(id="example-map", figure=fig, style=dict(height="80vh")),
    ],
)


@app.callback(Output("intro-div", "children"), [Input("intro-button", "n_clicks")])
def create_template_graph(n):
    return "Button has been clicked {} times.".format(n)
