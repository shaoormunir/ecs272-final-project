# content = html.H1("End", style=dict(textAlign="center"))

import json
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from server import app
import pandas as pd
import dash_bootstrap_components as dbc
import dash

df = pd.read_parquet("data/health/health.parquet")

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

global_epidemiological_factor = "Cases per 1000"
global_health_factor = "Physicians per 1000"

global_selected_country = None


def get_updated_figure():
    global df
    global global_selected_country
    global global_epidemiological_factor
    global global_health_factor

    print("global_selected_country", global_selected_country)
    print("global_epidemiological_factor", global_epidemiological_factor)
    print("global_health_factor", global_health_factor)

    df_selected_country = df[df["country_name"] == global_selected_country]

    df_top_10 = df.sort_values(
        by=health_factors[global_health_factor], ascending=False
    ).head(10)

    df_top_10["color"] = "Top 10"

    # print(df_top_10.country_name.unique().tolist())
    # select bottom 10 whose health factor is not null or 0
    df_bottom_10 = (
        df[
            (df[health_factors[global_health_factor]] != 0)
            & (df[health_factors[global_health_factor]].notnull())
        ]
        .sort_values(by=health_factors[global_health_factor], ascending=True)
        .head(10)
    )

    df_bottom_10["color"] = "Bottom 10"

    # print(df_bottom_10.country_name.unique().tolist())

    df_selected_country["color"] = "Selected Country"

    df_combined = pd.concat([df_top_10, df_bottom_10, df_selected_country])

    # scale the health factor using min-max scaling
    # df_combined[health_factors[global_health_factor]] = (
    #     df_combined[health_factors[global_health_factor]]
    #     - df_combined[health_factors[global_health_factor]].min()
    # ) / (
    #     df_combined[health_factors[global_health_factor]].max()
    #     - df_combined[health_factors[global_health_factor]].min()
    # )

    # print(df_combined.country_name.unique().tolist())

    # print(global_epidemiological_factor)
    # print(epidemiological_factors[global_epidemiological_factor])

    # create a dot plot for the data where x-axis is the country name, y-axis is the epidemiological factor, and the size of the dot is the health factor

    fig = px.scatter(
        df_combined,
        x="country_name",
        y=epidemiological_factors[global_epidemiological_factor],
        size=health_factors[global_health_factor],
        # add labels for the x and y axis
        labels={
            "country_name": "Country",
            epidemiological_factors[
                global_epidemiological_factor
            ]: "Epidemiological Factor",
            health_factors[global_health_factor]: "Health Factor",
        },
        color="color",
        hover_name="country_name",
        hover_data={
            "country_name": False,
            epidemiological_factors[global_epidemiological_factor]: ":.2f",
            health_factors[global_health_factor]: ":.2f",
        },
        size_max=60,
        color_discrete_map={
            "Top 10": "#943c92",
            "Bottom 10": "#ff6bff",
            "Selected Country": "black",
        },
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
                                label=global_health_factor,
                                color="white",
                                # size="lg",
                                id="health-dropdown-health",
                                style=dict(border="1px dotted #6c757d"),
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
                    dbc.Col(
                        width=6,
                        children=[
                            dbc.DropdownMenu(
                                label=global_epidemiological_factor,
                                color="white",
                                # size="lg",
                                id="health-dropdown-ep",
                                # add a grey border to dropdown
                                style=dict(border="1px dotted #6c757d"),
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
                ],
            ),
            dbc.Row(
                justify="center",
                children=[
                    dbc.Col(
                        width=6,
                        children=[
                            html.Div(
                                style=dict(
                                    textAlign="center",
                                    marginTop="10px",
                                    fontSize="15px",
                                ),
                                children="Represented as the circle size",
                            )
                        ],
                    ),
                    dbc.Col(
                        width=6,
                        children=[
                            html.Div(
                                style=dict(
                                    textAlign="center",
                                    marginTop="10px",
                                    fontSize="15px",
                                ),
                                children="Represented by the y-axis",
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
                dbc.Container(
                    fluid=True,
                    style=dict(height="80vh"),
                    children=[
                        html.Div(
                            id="health-data-portion",
                            children=[],
                        ),
                    ],
                ),
            ],
            # style=dict(textAlign="center", height="76vh"),
            id="health-output-container",
        ),
    ],
)


# @app.callback(
#     Output("health-data-portion", "children", allow_duplicate=True),
#     [Input("countries-health", "value")],
#     prevent_initial_call=True,
# )
# def update_map(countries):
#     global global_selected_countries
#     global_selected_countries = countries
#     return get_updated_figure()


@app.callback(
    Output("health-data-portion", "children"),
    [
        Input({"type": "ep_factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input({"type": "health_factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input("selected-country-store", "data"),
    ],
)
def update_map(ep_factor, health_factor, selected_location):
    ctx = dash.callback_context
    global global_epidemiological_factor
    global global_health_factor
    global global_selected_country

    # print("EP Factor: ", ep_factor)
    # print("Health Factor: ", health_factor)

    if not ctx.triggered:
        global_selected_country = selected_location
        return get_updated_figure()
    else:
        try:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            button_id = json.loads(button_id)

            type = button_id["type"]
            id = button_id["index"]
        except:
            type = "skip"

    if type == "ep_factor":
        global_epidemiological_factor = list(epidemiological_factors.keys())[id]
    elif type == "health_factor":
        global_health_factor = list(health_factors.keys())[id]
        print("Updated health factor to: ", global_health_factor)

    return get_updated_figure()
