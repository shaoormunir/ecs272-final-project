# no need to delete this - it won't show up in the presentation unless you add it to presentation.py

# necessary imports - do not change
from dash import html, dcc, Input, Output, State
from datetime import datetime
import dash_bootstrap_components as dbc
from server import app
import plotly.graph_objects as go
import pandas as pd
import json
from random import randrange
from urllib.request import urlopen
import plotly.express as px


with open("data/intro/newgeo.json") as response:
    countries = json.load(response)

df = pd.read_csv("data/intro/test.csv")


def get_stat_card(title, color, value, height="18vh"):
    return dbc.Card(
        [
            dbc.CardHeader(
                title, style=dict(fontWeight="bold", fontSize="calc(0.4em + 0.4vw)")
            ),
            dbc.CardBody(
                [
                    html.H5(
                        value,
                        className="text-center",
                        style=dict(
                            fontSize="calc(0.5em + 0.5vw)",
                            fontWeight="bold",
                            margin="0px",
                            padding="0px",
                        ),
                    ),
                ],
                style=dict(
                    display="flex",
                    justifyContent="center",
                    alignItems="center",
                    height="100%",
                ),
            ),
        ],
        style=dict(height=height),
        color=color,
        inverse=True,
        className="mb-4",
    )


def get_region_card(title, color, value, height="18vh"):
    return dbc.Card(
        [
            dbc.CardHeader(
                title, style=dict(fontWeight="bold", fontSize="calc(0.5em + 0.5vw)")
            ),
            dbc.CardBody(
                [
                    html.H5(
                        value,
                        className="text-center",
                        style=dict(
                            fontSize="calc(0.5em + 0.5vw)",
                            margin="0px",
                            padding="0px",
                        ),
                    ),
                ],
                style=dict(
                    display="flex",
                    justifyContent="left",
                    alignItems="Left",
                    height="100%",
                ),
            ),
        ],
        style=dict(height=height),
        color=color,
        inverse=True,
        className="mb-4",
    )


def get_date_based_df(df, start_date, end_date):
    fig = px.choropleth_mapbox(
        df[
            (pd.to_datetime(df.date) >= start_date)
            & (pd.to_datetime(df.date) <= end_date)
        ],
        geojson=countries,
        locations="iso_3166_1_alpha_3",
        color="new_confirmed",
        color_continuous_scale="Viridis",
        range_color=(0, df.new_confirmed.max()),
        mapbox_style="carto-positron",
        zoom=2,
        center={"lat": 26.880431, "lon": 14.382461},
        opacity=0.5,
        labels={"new_confirmed": "Newly Confirmed Cases"},
    )
    return fig


fig = get_date_based_df(df, df.date.min(), df.date.max())

fig.update_layout(geo_scope="world")

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

content = (
    html.Div(
        style=dict(textAlign="center"),
        children=[
            html.H1(children="Overview: Covid-19 Dashboard"),
            html.Div(
                children="""
                Covid-19 Distribution of Cases Worldwide
            """
            ),
            dbc.Container(
                fluid=True,
                style=dict(height="80vh"),
                children=[
                    # content div
                    dbc.Row(
                        children=[
                            dbc.Col(
                                width=12,
                                children=[
                                    dcc.DatePickerRange(
                                        id="date-picker-range",
                                        min_date_allowed=df.date.min(),
                                        max_date_allowed=df.date.max(),
                                        initial_visible_month=df.date.min(),
                                        start_date=df.date.min(),
                                        end_date=df.date.max(),
                                    ),
                                ],
                            )
                        ],
                    ),
                    html.Div(
                        id="data-portion",
                        children=[
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        width=1,
                                        style=dict(
                                            height="80vh",
                                        ),
                                        children=[
                                            dbc.Row(
                                                children=[
                                                    get_stat_card(
                                                        "Total Active Cases",
                                                        "primary",
                                                        "1200",
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                children=[
                                                    get_stat_card(
                                                        "Total Deaths",
                                                        "danger",
                                                        "120",
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                children=[
                                                    get_stat_card(
                                                        "Total Recovered",
                                                        "success",
                                                        "1080",
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                children=[
                                                    get_stat_card(
                                                        "Total Vaccinated",
                                                        "warning",
                                                        "900",
                                                    )
                                                ]
                                            ),
                                        ],
                                    ),
                                    dbc.Col(
                                        width=9,
                                        style=dict(
                                            height="80vh",
                                        ),
                                        children=[
                                            html.Div(
                                                id="map-graph",
                                                children=[
                                                    dcc.Graph(
                                                        figure=fig,
                                                        style=dict(height="80vh"),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    dbc.Col(
                                        width=2,
                                        style=dict(
                                            height="80vh",
                                        ),
                                        children=[
                                            get_region_card(
                                                "Regional Statistics",
                                                "rgb(159 163 166)",
                                                "USA: 200",
                                                "80vh",
                                            ),
                                        ],
                                    ),
                                ]
                            )
                        ],
                    ),
                ],
            ),
        ],
    ),
)


# callback for date picker range
@app.callback(
    Output("data-portion", "children"),
    [Input("date-picker-range", "start_date"), Input("date-picker-range", "end_date")],
)
def update_map(start_date, end_date):
    print("Updating map with date range: ", start_date, end_date)

    # Convert slider values to dates
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    print("Start Date: ", start_date)
    print("End Date: ", end_date)

    # Call the function to get the updated figure based on the selected date range
    updated_fig = get_date_based_df(df, start_date, end_date)
    return dbc.Row(
        children=[
            dbc.Col(
                width=1,
                style=dict(
                    height="80vh",
                ),
                children=[
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Active Cases",
                                "primary",
                                "1200",
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Deaths",
                                "danger",
                                "Updated",
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Recovered",
                                "success",
                                "1080",
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Vaccinated",
                                "warning",
                                "900",
                            )
                        ]
                    ),
                ],
            ),
            dbc.Col(
                width=9,
                style=dict(
                    height="80vh",
                ),
                children=[
                    html.Div(
                        id="map-graph",
                        children=[
                            dcc.Graph(
                                figure=updated_fig,
                                style=dict(height="80vh"),
                            ),
                        ],
                    ),
                ],
            ),
            dbc.Col(
                width=2,
                style=dict(
                    height="80vh",
                ),
                children=[
                    get_region_card(
                        "Regional Statistics",
                        "rgb(159 163 166)",
                        "USA: 200",
                        "80vh",
                    ),
                ],
            ),
        ]
    )
