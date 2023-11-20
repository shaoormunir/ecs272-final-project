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


with open("data/intro/newgeo.json") as response:
    countries = json.load(response)

# custom imports
# ...


df = pd.read_csv("data/intro/test.csv")

# df.date = pd.to_datetime(df.date)


def get_stat_card(title, color, value, height="18.67vh"):
    return dbc.Card(
        [
            dbc.CardHeader(title, style=dict(fontWeight="bold", fontSize="1.5rem")),
            dbc.CardBody(
                [
                    html.H5(
                        value,
                        className="text-center",
                        style=dict(
                            fontSize="4rem",
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


def get_region_card(title, color, value, height="18.67vh"):
    return dbc.Card(
        [
            dbc.CardHeader(title, style=dict(fontWeight="bold", fontSize="1.5rem")),
            dbc.CardBody(
                [
                    html.H5(
                        value,
                        className="text-center",
                        style=dict(
                            fontSize="1.2rem",
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


import plotly.express as px


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

# numdate = [x for x in range(8760)]

# df["date"] = pd.to_datetime(df["date"])
numdate = df.date.unique().tolist()
# sorted_dates = df["date"].sort_values().unique()
# first_days_of_month = sorted_dates[
#     sorted_dates.astype("datetime64[M]")
#     == sorted_dates - pd.to_timedelta(sorted_dates.day - 1, unit="d")
# ]
# first_days_of_month = df.groupby("year_month")["date"].min().reset_index(drop=True)


# print([df["date"][x] for x in range(len(numdate))])

# print(numdate)

content = html.Div(
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
                    style=dict(position="sticky", margin="10px"),
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
                                            "Total Active Cases", "primary", "1200"
                                        )
                                    ]
                                ),
                                dbc.Row(
                                    children=[
                                        get_stat_card("Total Deaths", "danger", "120")
                                    ]
                                ),
                                dbc.Row(
                                    children=[
                                        get_stat_card(
                                            "Total Recovered", "success", "1080"
                                        )
                                    ]
                                ),
                                dbc.Row(
                                    children=[
                                        get_stat_card(
                                            "Total Vaccinated", "warning", "900"
                                        )
                                    ]
                                ),
                            ],
                        ),
                        dbc.Col(
                            width=10,
                            style=dict(id="example-map", style=dict(height="80vh")),
                            children=[
                                dcc.DatePickerRange(
                                    id="date-picker-range",
                                    min_date_allowed=df.date.min(),
                                    max_date_allowed=df.date.max(),
                                    initial_visible_month=df.date.min(),
                                    start_date=df.date.min(),
                                    end_date=df.date.max(),
                                    calendar_orientation="horizontal",
                                ),
                                html.Div(
                                    id="map-graph",
                                    children=[
                                        dcc.Graph(
                                            figure=fig,
                                            style=dict(height="80vh"),
                                        ),
                                    ],
                                ),
                                # dcc.RangeSlider(
                                #     id="date-slider",
                                #     min=0,
                                #     max=len(numdate) - 1,
                                #     value=[0, len(numdate) - 1],
                                #     marks={
                                #         i: {
                                #             "label": numdate[i],
                                #             "style": {"color": "#7fafdf"},
                                #         }
                                #         for i in range(len(numdate))
                                #     },
                                #     step=1,
                                #     tooltip={
                                #         "always_visible": True,
                                #         "placement": "top",
                                #     },
                                # ),
                            ],
                        ),
                        dbc.Col(
                            width=1,
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
                    ],
                ),
            ],
        ),
    ],
)


# @app.callback(Output("example-map", "figure"), [Input("date-slider", "value")])
# def update_map(date_range):
#     print("Updating map with date range: ", date_range)

#     # Convert slider values to dates
#     start_date = pd.to_datetime(df["date"].min()) + pd.to_timedelta(
#         date_range[0], unit="D"
#     )
#     end_date = pd.to_datetime(df["date"].min()) + pd.to_timedelta(
#         date_range[1], unit="D"
#     )

#     print("Start Date: ", start_date)
#     print("End Date: ", end_date)

#     # Call the function to get the updated figure based on the selected date range
#     fig = get_date_based_df(df, start_date, end_date)
#     return fig


# callback for date picker range
@app.callback(
    Output("map-graph", "children"),
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
    fig = get_date_based_df(df, start_date, end_date)
    return html.Div(
        children=[
            dcc.Graph(
                figure=fig,
                style=dict(height="80vh"),
            ),
        ],
    )


# @app.callback(
#     Output("current-date-display", "children"), [Input("date-slider", "value")]
# )
# def update_current_date_display(value):
#     start_date = sorted_dates[value[0]].strftime("%Y-%m-%d")
#     end_date = sorted_dates[value[1]].strftime("%Y-%m-%d")
#     return f"Start Date: {start_date}, End Date: {end_date}"


@app.callback(Output("intro-div", "children"), [Input("intro-button", "n_clicks")])
def create_template_graph(n):
    return "Button has been clicked {} times.".format(n)
