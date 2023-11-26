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
import dash_dangerously_set_inner_html
import dash

with open("data/exploration/newgeo.json") as response:
    countries = json.load(response)

df = pd.read_csv("data/exploration/exploration.csv")


global_factor = "Hospital Beds per 1000"
global_ep_factor = "Confirmed Cases per 1000"

factors_dict = {
    "Hospital Beds per 1000": "hospital_beds_per_1000",
    "Nurses per 1000": "nurses_per_1000",
    "Physicians per 1000": "physicians_per_1000",
    "Tests per 1000": "tested_per_1000",
    "Vaccinated per 1000": "fully_vaccinated_per_1000",
    "Health Expenditure": "health_expenditure_usd",
    "GDP per Capita": "gdp_per_capita_usd",
    "Human Development Index": "human_capital_index",
    "Population Density": "population_density",
    "Smoking Prevalence": "smoking_prevalence",
    "Diabetes Prevalence": "diabetes_prevalence",
}

ep_factors_dict = {
    "Confirmed Cases per 1000": "confirmed_per_1000",
    "Deaths per 1000": "deceased_per_1000",
    "Recovered per 1000": "recovered_per_1000",
}


def get_exploration_figure(
    fig,
):
    return dbc.Row(
        children=[
            dbc.Row(
                justify="right",
                children=[
                    dbc.Col(
                        width=6,
                        children=[
                            dbc.DropdownMenu(
                                label=global_factor,
                                color="warning",
                                size="lg",
                                id="exploration-dropdown-factor",
                                children=[
                                    dbc.DropdownMenuItem(
                                        factor, id={"type": "factor", "index": i}
                                    )
                                    for i, factor in enumerate(factors_dict.keys())
                                ],
                            )
                        ],
                    ),
                    dbc.Col(
                        width=6,
                        children=[
                            dbc.DropdownMenu(
                                label=global_ep_factor,
                                color="success",
                                size="lg",
                                id="exploration-dropdown-ep-factor",
                                children=[
                                    dbc.DropdownMenuItem(
                                        ep_factor,
                                        id={"type": "ep_factor", "index": i},
                                    )
                                    for i, ep_factor in enumerate(
                                        ep_factors_dict.keys()
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            ),
            dbc.Col(
                width=12,
                style=dict(
                    height="80vh",
                ),
                children=[
                    html.Div(
                        id="exploration-map-graph",
                        children=[
                            dcc.Graph(
                                figure=fig,
                                id="exploration-world-map",
                                style=dict(height="80vh", width="100%"),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )


def get_updated_map(df, factor, ep_factor):
    df_temp = df[["iso_3166_1_alpha_3", "country_name", factor, ep_factor]]
    df_temp["ratio"] = df_temp[factor] / df_temp[ep_factor]

    fig = px.choropleth_mapbox(
        df_temp,
        geojson=countries,
        locations="iso_3166_1_alpha_3",
        color="ratio",
        hover_name="country_name",
        color_continuous_scale="Viridis",
        range_color=(0, df_temp.ratio.max()),
        mapbox_style="open-street-map",
        zoom=1,
        center={"lat": 26.880431, "lon": 14.382461},
        opacity=0.5,
        labels={
            "ratio": "Ratio",
            "iso_3166_1_alpha_3": "Country",
        },
    )

    fig.update_layout(geo_scope="world")

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


fig = get_updated_map(df, "hospital_beds_per_1000", "confirmed_per_1000")

content = (
    html.Div(
        style=dict(textAlign="center"),
        children=[
            dbc.Container(
                fluid=True,
                style=dict(height="80vh"),
                children=[
                    html.Div(
                        id="exploration-data-portion",
                        children=[
                            get_exploration_figure(
                                fig,
                            )
                        ],
                    ),
                ],
            ),
        ],
    ),
)


# callback for the two dropdowns with id's exploration-dropdown-factor and exploration-dropdown-ep-factor
@app.callback(
    Output("exploration-data-portion", "children"),
    [
        Input({"type": "factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input({"type": "ep_factor", "index": dash.dependencies.ALL}, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_map(factor, ep_factor):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        # print(button_id)
        button_id = json.loads(button_id)
        type = button_id["type"]
        id = button_id["index"]

    # update the global variables
    global global_factor
    global global_ep_factor
    if type == "factor":
        factor = list(factors_dict.values())[id]
        ep_factor = list(ep_factors_dict.values())[0]
        global_factor = list(factors_dict.keys())[id]

    else:
        factor = list(factors_dict.values())[0]
        ep_factor = list(ep_factors_dict.values())[id]
        global_ep_factor = list(ep_factors_dict.keys())[id]
    # print("Factor: ", factor)
    # print("EP Factor: ", ep_factor)

    return get_exploration_figure(get_updated_map(df, factor, ep_factor))
