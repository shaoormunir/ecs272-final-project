# content = html.H1("End", style=dict(textAlign="center"))

import json
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from server import app
import pandas as pd
import dash_bootstrap_components as dbc
import dash

df = pd.read_csv("data/health/health-data.csv")

countries = sorted(df["country_name"].unique().tolist())
# print(countries)

health_factors = {
    "Hospital Beds per 1000": "mean_hospital_beds_per_1000",
    "Nurses per 1000": "mean_nurses_per_1000",
    "Physicians per 1000": "mean_physicians_per_1000",
    "Health Expenditure": "mean_health_expenditure_usd",
    "Tests per 1000": "total_tested_per_1000",
}

epidemiological_factors = {
    "Cases per 1000": "total_cases_per_1000",
    "Deaths per 1000": "total_deaths_per_1000",
    "Recovered per 1000": "total_recoveries_per_1000",
}

global_selected_countries = [
    "Afghanistan",
    "Australia",
    "Brazil",
    "Canada",
    "Egypt",
    "Germany",
    "India",
    "Japan",
    "Luxembourg",
    "Russia",
    "Singapore",
    "South Africa",
    "South Korea",
    "Spain",
    "Sri Lanka",
    "Turkey",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States of America",
]
global_epidemiological_factor = "Cases per 1000"
global_health_factor = "Physicians per 1000"


def get_updated_figure():
    global df
    global global_selected_countries
    global global_epidemiological_factor
    global global_health_factor
    df_temp = df[df["country_name"].isin(global_selected_countries)]

    # print(global_epidemiological_factor)
    # print(epidemiological_factors[global_epidemiological_factor])
    fig = px.scatter(
        df_temp,
        x="country_name",
        y=epidemiological_factors[global_epidemiological_factor],
        color="country_name",
        hover_name="country_name",
        size=health_factors[global_health_factor],
        trendline="ols",
        title="",
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title=global_epidemiological_factor,
        font=dict(size=12),
        # hide legend
        # xaxis_type="category",
    )

    return dbc.Row(
        justify="center",
        children=[
            dbc.Row(
                justify="center",
                children=[
                    dbc.Col(
                        width=6,
                        children=[
                            dbc.DropdownMenu(
                                label=global_epidemiological_factor,
                                color="warning",
                                size="lg",
                                id="health-dropdown-ep",
                                children=[
                                    dbc.DropdownMenuItem(
                                        ep_factor,
                                        id={
                                            "type": "ep_factor",
                                            "index": i,
                                        },
                                    )
                                    for i, ep_factor in enumerate(
                                        epidemiological_factors.keys()
                                    )
                                ],
                            )
                        ],
                    ),
                    dbc.Col(
                        width=6,
                        children=[
                            dbc.DropdownMenu(
                                label=global_health_factor,
                                color="success",
                                size="lg",
                                id="health-dropdown-health",
                                children=[
                                    dbc.DropdownMenuItem(
                                        health_factors,
                                        id={
                                            "type": "health_factor",
                                            "index": i,
                                        },
                                    )
                                    for i, health_factors in enumerate(
                                        health_factors.keys()
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
                    dcc.Graph(
                        figure=fig,
                        id="health-bubble-chart",
                        style=dict(height="80vh", width="100%"),
                        config={"displayModeBar": False},
                    ),
                ],
            ),
        ],
    )


content = html.Div(
    children=[
        html.Div(
            [
                dcc.Checklist(
                    id="countries-health",
                    options=[
                        {
                            "label": html.Div(
                                country,
                                style={
                                    "display": "inline",
                                    "font-size": 15,
                                    "padding-right": "0.2rem",
                                    "padding-right": "0.7rem",
                                },
                            ),
                            "value": country,
                        }
                        for country in countries
                    ],
                    value=[
                        "Afghanistan",
                        "Australia",
                        "Brazil",
                        "Canada",
                        "Egypt",
                        "Germany",
                        "India",
                        "Japan",
                        "Luxembourg",
                        "Russia",
                        "Singapore",
                        "South Africa",
                        "South Korea",
                        "Spain",
                        "Sri Lanka",
                        "Turkey",
                        "Ukraine",
                        "United Arab Emirates",
                        "United Kingdom",
                        "United States of America",
                    ],
                    inline=True,
                    style=dict(height="9vh", overflow="scroll"),
                ),
                dbc.Container(
                    fluid=True,
                    style=dict(height="80vh"),
                    children=[
                        html.Div(
                            id="health-data-portion",
                            children=[
                                get_updated_figure(),
                            ],
                        ),
                    ],
                ),
            ],
            # style=dict(textAlign="center", height="76vh"),
            id="health-output-container",
        ),
    ],
)


@app.callback(
    Output("health-data-portion", "children", allow_duplicate=True),
    [Input("countries-health", "value")],
    prevent_initial_call=True,
)
def update_map(countries):
    global global_selected_countries
    global_selected_countries = countries
    return get_updated_figure()


@app.callback(
    Output("health-data-portion", "children", allow_duplicate=True),
    [
        Input({"type": "ep_factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input({"type": "health_factor", "index": dash.dependencies.ALL}, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_map(ep_factor, health_factor):
    ctx = dash.callback_context
    global global_epidemiological_factor
    global global_health_factor

    # print("EP Factor: ", ep_factor)
    # print("Health Factor: ", health_factor)

    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        button_id = json.loads(button_id)

        type = button_id["type"]
        id = button_id["index"]

    if type == "ep_factor":
        global_epidemiological_factor = list(epidemiological_factors.keys())[id]
    elif type == "health_factor":
        global_health_factor = list(health_factors.keys())[id]

    return get_updated_figure()
