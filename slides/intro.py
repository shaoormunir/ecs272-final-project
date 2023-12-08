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

with open("data/intro/newgeo.json") as response:
    countries = json.load(response)

df = pd.read_csv("data/intro/intro.csv")

global_start_date = df.date.min()
global_end_date = df.date.max()


def get_main_figure(
    fig, total_active, total_deaths, total_recovered, total_vaccinated, top_10_countries
):
    return dbc.Row(
        children=[
            dbc.Col(
                width=2,
                style=dict(
                    height="80vh",
                ),
                children=[
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Active Cases",
                                "danger",
                                total_active,
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Deaths",
                                "primary",
                                total_deaths,
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Recovered",
                                "success",
                                total_recovered,
                            )
                        ]
                    ),
                    dbc.Row(
                        children=[
                            get_stat_card(
                                "Total Vaccinated",
                                "warning",
                                total_vaccinated,
                            )
                        ]
                    ),
                ],
            ),
            dbc.Col(
                width=8,
                style=dict(
                    height="80vh",
                ),
                children=[
                    html.Div(
                        id="map-graph",
                        children=[
                            dcc.Graph(
                                figure=fig,
                                id="world-map",
                                style=dict(height="80vh", width="100%"),
                                config={"displayModeBar": False},
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
                    dbc.Button(
                        "Reset View",
                        id="reset-map",
                        className="mb-3",
                        style=dict(
                            width="100%",
                            height="5vh",
                            fontSize="calc(0.5em + 0.5vw)",
                            backgroundColor="#8e9295",
                        ),
                    ),
                    get_region_card(
                        "Regional Statistics",
                        "#8e9295",
                        top_10_countries,
                        "73vh",
                    ),
                ],
            ),
        ]
    )


def get_stat_card(title, color, value, height="18vh"):
    return dbc.Card(
        [
            dbc.CardHeader(
                title, style=dict(fontWeight="bold", fontSize="calc(0.5em + 0.5vw)")
            ),
            dbc.CardBody(
                [
                    html.H5(
                        f"{int(value):,d}",
                        className="text-center",
                        style=dict(
                            fontSize="calc(0.7em + 0.7vw)",
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
                        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(value),
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
                    justifyContent="center",
                    # textAlign="center",
                    # alignItems="center",
                    height="100%",
                ),
            ),
        ],
        style=dict(height=height),
        color=color,
        inverse=True,
        className="mb-4",
    )


def get_date_based_values(df, start_date, end_date, subregion=False):
    df_temp = df[
        (pd.to_datetime(df.date) >= start_date) & (pd.to_datetime(df.date) <= end_date)
    ]
    # aggregate new cases by country

    df_aggregate = (
        df_temp.groupby(["iso_3166_1_alpha_3", "country_name"])
        .agg(
            {
                "new_confirmed": "sum",
                "new_deceased": "sum",
                "new_recovered": "sum",
                "new_persons_fully_vaccinated": "sum",
            }
        )
        .reset_index()
    )
    fig = px.choropleth_mapbox(
        df_aggregate,
        geojson=countries,
        locations="iso_3166_1_alpha_3",
        color="new_confirmed",
        hover_name="country_name",
        color_continuous_scale="ylorrd",
        range_color=(0, df.new_confirmed.max()),
        mapbox_style="open-street-map",
        zoom=1,
        center={"lat": 26.880431, "lon": 14.382461},
        opacity=0.5,
        labels={
            "new_confirmed": "Confirmed Cases",
            "iso_3166_1_alpha_3": "Country",
        },
    )

    total_recovered = df_temp.new_recovered.sum()
    total_deaths = df_temp.new_deceased.sum()
    total_vaccinated = df_temp.new_persons_fully_vaccinated.sum()
    total_active = df_temp.new_confirmed.sum() - total_recovered - total_deaths

    # create a single string of the top 10 countries with the format:
    # Country : New Cases

    if subregion == False:
        df_top_10 = df_aggregate.sort_values(by="new_confirmed", ascending=False).head(
            10
        )
        top_10_countries = ""
        for i in range(df_top_10.shape[0]):
            top_10_countries += (
                f"{i+1}. "
                + df_top_10.iloc[i].country_name
                + ": "
                + str(f"{int(df_top_10.iloc[i].new_confirmed):,d}")
                + "<br>"
                + "<br>"
            )
    else:
        df_top_10 = (
            df_temp[df_temp.subregion1_name != "0"]
            .groupby(["subregion1_name"])
            .agg(
                {
                    "new_confirmed": "sum",
                }
            )
            .reset_index()
            .sort_values(by="new_confirmed", ascending=False)
            .head(10)
        )
        top_10_countries = ""
        for i in range(df_top_10.shape[0]):
            top_10_countries += (
                f"{i+1}. "
                + df_top_10.iloc[i].subregion1_name
                + ": "
                + str(f"{int(df_top_10.iloc[i].new_confirmed):,d}")
                + "<br>"
                + "<br>"
            )

    if total_active < 0:
        total_active = 0

    # print("Total Active Cases: ", total_active)
    # print("Total Deaths: ", total_deaths)
    # print("Total Recovered: ", total_recovered)
    # print("Total Vaccinated: ", total_vaccinated)
    return (
        fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    )


(
    fig,
    total_active,
    total_deaths,
    total_recovered,
    total_vaccinated,
    top_10_countries,
) = get_date_based_values(df, df.date.min(), df.date.max())

fig.update_layout(geo_scope="world")

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

content = (
    html.Div(
        style=dict(textAlign="center"),
        children=[
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
                            get_main_figure(
                                fig,
                                total_active,
                                total_deaths,
                                total_recovered,
                                total_vaccinated,
                                top_10_countries,
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
    Output("data-portion", "children", allow_duplicate=True),
    [
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        # Input("world-map", "clickData"),
    ],
    prevent_initial_call=True,
)
def update_map(start_date, end_date):
    # trigger = dash.callback_context.triggered[0]["prop_id"]
    # print("Trigger: ", trigger)

    print("Updating map with date range: ", start_date, end_date)

    # Convert slider values to dates
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # change the global start and end date
    global global_start_date
    global global_end_date
    global_start_date = start_date
    global_end_date = end_date

    # print("Start Date: ", start_date)
    # print("End Date: ", end_date)

    # Call the function to get the updated figure based on the selected date range
    (
        updated_fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    ) = get_date_based_values(df, start_date, end_date)
    return get_main_figure(
        updated_fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    )


# callback for the choropleth map
@app.callback(
    Output("data-portion", "children", allow_duplicate=True),
    [Input("world-map", "clickData")],
    prevent_initial_call=True,
)
def display_click_data(clickData):
    # print("Click Data: ", clickData)
    if clickData is None:
        (
            updated_fig,
            total_active,
            total_deaths,
            total_recovered,
            total_vaccinated,
            top_10_countries,
        ) = get_date_based_values(df, global_start_date, global_end_date)
        return get_main_figure(
            updated_fig,
            total_active,
            total_deaths,
            total_recovered,
            total_vaccinated,
            top_10_countries,
        )
    country = clickData["points"][0]["location"]
    # print("Country: ", country)

    df_temp = df[df.iso_3166_1_alpha_3 == country]

    total_recovered = df_temp.new_recovered.sum()
    total_deaths = df_temp.new_deceased.sum()
    total_vaccinated = df_temp.new_persons_fully_vaccinated.sum()
    total_active = df_temp.new_confirmed.sum() - total_recovered - total_deaths

    if total_active < 0:
        total_active = 0

    (
        updated_fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    ) = get_date_based_values(
        df_temp, global_start_date, global_end_date, subregion=True
    )

    return get_main_figure(
        updated_fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    )


# callback for reset button
@app.callback(
    Output("data-portion", "children"),
    Output("date-picker-range", "start_date"),
    Output("date-picker-range", "end_date"),
    [Input("reset-map", "n_clicks")],
    prevent_initial_call=True,
)
def reset_map(n_clicks):
    if n_clicks is None:
        return dash.no_update
    # print("Resetting Map")
    (
        updated_fig,
        total_active,
        total_deaths,
        total_recovered,
        total_vaccinated,
        top_10_countries,
    ) = get_date_based_values(df, df.date.min(), df.date.max())
    return (
        get_main_figure(
            updated_fig,
            total_active,
            total_deaths,
            total_recovered,
            total_vaccinated,
            top_10_countries,
        ),
        df.date.min(),
        df.date.max(),
    )
