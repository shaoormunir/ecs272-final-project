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

glob_selected_country = None

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
                        width=5,
                        children=[
                            dbc.DropdownMenu(
                                label=global_factor,
                                color="white",
                                # size="lg",
                                id="exploration-dropdown-factor",
                                style=dict(border="1px dotted #6c757d"),
                                children=[
                                    dbc.DropdownMenuItem(
                                        factor, id={"type": "factor", "index": i}
                                    )
                                    for i, factor in enumerate(factors_dict.keys())
                                ],
                            )
                        ],
                    ),
                    # add a text box with the value "divided"
                    dbc.Col(
                        width=2,
                        children=[
                            html.Div(
                                style=dict(
                                    textAlign="center",
                                    marginTop="10px",
                                    fontSize="20px",
                                ),
                                children="divided by",
                            )
                        ],
                    ),
                    dbc.Col(
                        width=5,
                        children=[
                            dbc.DropdownMenu(
                                label=global_ep_factor,
                                color="white",
                                # size="lg",
                                id="exploration-dropdown-ep-factor",
                                style=dict(border="1px dotted #6c757d"),
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


def get_updated_map(df, factor, ep_factor, selected_country):
    df_temp = df[["iso_3166_1_alpha_3", "country_name", factor, ep_factor]]

    df_temp.loc[:, "ratio"] = df_temp[ep_factor] / df_temp[factor]

    print("Selected Country: ", selected_country)
    # print(df_temp.country_name.unique())

    global_country_ratio = df_temp[df_temp["country_name"] == selected_country][
        "ratio"
    ].values[0]

    print(
        "Ep factor for selected country: ",
        df_temp[df_temp["country_name"] == selected_country][ep_factor].values[0],
    )

    print(
        "Factor for selected country: ",
        df_temp[df_temp["country_name"] == selected_country][factor].values[0],
    )

    print("Ep factor is: ", ep_factor)
    print("Factor is: ", factor)

    print("Ratio for selected country: ", global_country_ratio)

    # # update ratio of other countries in reference to the selected country
    # df_temp.loc[:, "ratio"] = df_temp["ratio"] / global_country_ratio

    # remove inf values
    df_temp = df_temp.replace([float("inf"), float("-inf")], float("NaN"))

    # remove outliers using the interquartile range
    Q1 = df_temp["ratio"].quantile(0.25)
    Q3 = df_temp["ratio"].quantile(0.75)
    IQR = Q3 - Q1
    df_temp = df_temp[
        (df_temp["ratio"] >= Q1 - 1.5 * IQR) & (df_temp["ratio"] <= Q3 + 1.5 * IQR)
    ]

    # scale values relative to the selected country
    df_temp.loc[:, "ratio"] = df_temp["ratio"] / global_country_ratio

    fig = px.choropleth_mapbox(
        df_temp,
        geojson=countries,
        locations="iso_3166_1_alpha_3",
        color="ratio",
        hover_name="country_name",
        color_continuous_scale="reds",
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


# fig = get_updated_map(df, "hospital_beds_per_1000", "confirmed_per_1000")

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
                        children=[],
                    ),
                ],
            ),
        ],
    ),
)


# @app.callback(
#     Output("exploration-data-portion", "children", allow_duplicate=True),
#     [Input("selected-country-store", "data")],
#     prevent_initial_call="initial_duplicate",
# )
# def update_map(selected_location):
#     global glob_selected_country
#     glob_selected_country = selected_location
#     return get_updated_map(
#         df,
#         factors_dict[global_factor],
#         ep_factors_dict[global_ep_factor],
#         selected_location,
#     )


# callback for the two dropdowns with id's exploration-dropdown-factor and exploration-dropdown-ep-factor
@app.callback(
    Output("exploration-data-portion", "children"),
    [
        Input({"type": "factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input({"type": "ep_factor", "index": dash.dependencies.ALL}, "n_clicks"),
        Input("selected-country-store", "data"),
    ],
)
def update_map(factor, ep_factor, selected_location):
    ctx = dash.callback_context
    global global_factor
    global global_ep_factor
    global glob_selected_country

    if selected_location is None:
        selected_location = glob_selected_country

    print("Factor: ", factor)
    print("EP Factor: ", ep_factor)
    print("Selected Location: ", selected_location)
    if not ctx.triggered:
        # return dash.no_update
        return get_exploration_figure(
            get_updated_map(
                df,
                factors_dict[global_factor],
                ep_factors_dict[global_ep_factor],
                selected_location,
            )
        )
    else:
        try:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            # print(button_id)
            button_id = json.loads(button_id)
            type = button_id["type"]
            id = button_id["index"]
        except:
            type = "skip"
            ep_factor = ep_factors_dict[global_ep_factor]
            factor = factors_dict[global_factor]
    # update the global variables
    if type == "factor":
        factor = list(factors_dict.values())[id]
        ep_factor = list(ep_factors_dict.values())[0]
        global_factor = list(factors_dict.keys())[id]

    elif type == "ep_factor":
        factor = list(factors_dict.values())[0]
        ep_factor = list(ep_factors_dict.values())[id]
        global_ep_factor = list(ep_factors_dict.keys())[id]
    # print("Factor: ", factor)
    # print("EP Factor: ", ep_factor)

    return get_exploration_figure(
        get_updated_map(df, factor, ep_factor, selected_location)
    )
