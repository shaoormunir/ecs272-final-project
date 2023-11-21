from ctypes import alignment
from dash import html, dcc, Input, Output, State
from server import app

import dash
import plotly.graph_objs as go
import pandas as pd

# read mob.csv using pandas
df = pd.read_csv("data/mobility/mob.csv")

# Extract year-month string as a new column from the date column
df["year_month"] = df["date"].apply(lambda x: x[:7])

# Drop date column and Group by year-month and country to calculate the sum of each column
df = (
    df.drop(columns=["date"])
    .groupby(["year_month", "country_name"])
    .sum()
    .reset_index()
)

# Extract distinct year-month string values as a separate variable from the date column
yr_mnth = df["year_month"].unique()

# Extract residential mobility values for the selected country and select deceased values for the selected country
# df_res = df[df["country_name"] == selected_location]["mobility_residential"].tolist()

# Compute total_deaths for each country and date combination

df["total_deaths"] = df.groupby(["country_name", "year_month"])[
    "new_deceased"
].transform("sum")

# Compute total_recoveries for each country and date combination
df["total_recoveries"] = df.groupby(["country_name", "year_month"])[
    "new_recovered"
].transform("sum")

# Compute total_vaccinated for each country and date combination
df["total_vaccinated"] = df.groupby(["country_name", "year_month"])[
    "new_persons_fully_vaccinated"
].transform("sum")

# Compute total_active_cases for each country and date combination
df["total_active_cases"] = df.groupby(["country_name", "year_month"])[
    "new_confirmed"
].transform("sum")


content = html.Div(
    style=dict(height="80vh", width="100%", textAlign="center"),
    children=[
        html.Div(
            [
                html.H1("Effect of Mobility"),
                dcc.Dropdown(
                    options=[
                        {"label": i, "value": i} for i in df["country_name"].unique()
                    ],
                    value="United States of America",
                    id="country-dropdown",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "Total Active Cases", "value": "total_active_cases"},
                        {"label": "Total Deaths", "value": "total_deaths"},
                        {"label": "Total Recoveries", "value": "total_recoveries"},
                        {
                            "label": "Total Fully Vaccinated",
                            "value": "total_vaccinated",
                        },
                    ],
                    value="total_active_cases",
                    id="epidemiology-dropdown",
                ),
            ],
            style=dict(textAlign="center", width="40%", display="inline-block"),
        ),
        html.Div(
            [
                dcc.Graph(id="mobility-graph", style=dict(height="80vh")),
            ],
            style=dict(textAlign="center", height="80vh"),
            id="dd-output-container",
        ),
    ],
)


@app.callback(
    Output("mobility-graph", "figure"),
    [Input("country-dropdown", "value"), Input("epidemiology-dropdown", "value")],
)
def update_charts(selected_location, selected_epidemiology_data):
    trace1 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_residential"].tolist(),
        name="Residential Mobility",
    )
    trace2 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_workplaces"].tolist(),
        name="Workplaces Mobility",
    )
    trace3 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            "mobility_transit_stations"
        ].tolist(),
        name="Transit Stations Mobility",
    )
    trace4 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            "mobility_grocery_and_pharmacy"
        ].tolist(),
        name="Grocery & Pharmacy Mobility",
    )
    trace5 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_parks"].tolist(),
        name="Parks Mobility",
    )

    data_bar = [trace1, trace2, trace3, trace4, trace5]

    if selected_epidemiology_data == "total_active_cases":
        label = "Total Active Cases"
    elif selected_epidemiology_data == "total_deaths":
        label = "Total Deaths"
    elif selected_epidemiology_data == "total_recoveries":
        label = "Total Recoveries"
    elif selected_epidemiology_data == "total_vaccinated":
        label = "Total Fully Vaccinated"

    line_trace = go.Scatter(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            selected_epidemiology_data
        ].tolist(),
        mode="lines",
        name=label,
        line=dict(color="black"),
    )

    data_line = [line_trace]

    layout = go.Layout(
        barmode="stack",
        xaxis=dict(title="Month-Year", tickvals=yr_mnth),
        yaxis=dict(title="Mobility Counts", showgrid=True),
        yaxis2=dict(
            title="Epidemiological Counts", overlaying="y", side="right", showgrid=True
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # find maximum sum of 5 mobility columns for the selected country and set it as the upper limit of y-axis
    ymax_left = (
        df[df["country_name"] == selected_location][
            [
                "mobility_residential",
                "mobility_workplaces",
                "mobility_transit_stations",
                "mobility_grocery_and_pharmacy",
                "mobility_parks",
            ]
        ]
        .sum(axis=1)
        .max()
    )

    fig = go.Figure(data=data_bar + data_line, layout=layout)
    fig.update_layout(
        yaxis_range=[0, ymax_left],  # Adjust the range as needed
        yaxis2_range=[0, 100],  # Adjust the range as needed
    )
    return fig
