from dash import html, dcc, Input, Output
from server import app
import dash
import plotly.graph_objs as go
import pandas as pd

# read mob.csv using pandas
df = pd.read_csv("data/mobility/mob.csv")

# Extract year-month string as a new column from the date column
df["year_month"] = df["date"].apply(lambda x: x[:7])


"""
# Drop date column and Group by year-month and country to calculate the sum of each column
df = (
    df.drop(columns=["date"])
    .groupby(["year_month", "country_name"])
    .sum()
    .reset_index()
)

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
"""

df = (
    df.drop(columns=["date"])
    .groupby(["year_month", "country_name"])
    .agg(
        total_deaths=("new_deceased", "sum"),
        total_recoveries=("new_recovered", "sum"),
        total_vaccinated=("new_persons_fully_vaccinated", "sum"),
        total_active_cases=("new_confirmed", "sum"),
        mobility_residential=("mobility_residential", "mean"),
        mobility_workplaces=("mobility_workplaces", "mean"),
        mobility_transit_stations=("mobility_transit_stations", "mean"),
        mobility_grocery_and_pharmacy=("mobility_grocery_and_pharmacy", "mean"),
        mobility_parks=("mobility_parks", "mean"),
    )
    .reset_index()
    .sort_values("year_month")
)

# Extract distinct year-month string values as a separate variable from the date column
yr_mnth = df["year_month"].unique()


content = html.Div(
    style=dict(height="76vh", width="100%", textAlign="center"),
    children=[
        html.Div(
            [
                # dcc.Dropdown(
                #     options=[
                #         {"label": i, "value": i}
                #         for i in sorted(df["country_name"].unique().tolist())
                #     ],
                #     value="United States of America",
                #     id="country-dropdown",
                #     style=dict(display="inline-block", width="50%"),
                # ),
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
                    style=dict(display="inline-block", width="50%"),
                ),
            ],
            style=dict(textAlign="center", width="100%", display="inline-block"),
        ),
        html.Div(
            [
                dcc.Graph(
                    id="mobility-graph",
                    style=dict(height="75vh"),
                    config={"displayModeBar": False},
                ),
            ],
            style=dict(textAlign="center", width="100%"),
            id="dd-output-container",
        ),
    ],
)


@app.callback(
    Output("mobility-graph", "figure"),
    [Input("selected-country-store", "data"), Input("epidemiology-dropdown", "value")],
    # [Input("country-dropdown", "value"), Input("epidemiology-dropdown", "value")],
)
def update_charts(selected_location, selected_epidemiology_data):
    trace1 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_residential"].tolist(),
        name="Residential Mobility",
        yaxis="y",
    )
    trace2 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_workplaces"].tolist(),
        name="Workplaces Mobility",
        yaxis="y",
    )
    trace3 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            "mobility_transit_stations"
        ].tolist(),
        name="Transit Stations Mobility",
        yaxis="y",
    )
    trace4 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            "mobility_grocery_and_pharmacy"
        ].tolist(),
        name="Grocery & Pharmacy Mobility",
        yaxis="y",
    )
    trace5 = go.Bar(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location]["mobility_parks"].tolist(),
        name="Parks Mobility",
        yaxis="y",
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

    # print(yr_mnth)
    # print(df[df["country_name"] == selected_location][selected_epidemiology_data].tolist())

    line_trace = go.Scatter(
        x=yr_mnth,
        y=df[df["country_name"] == selected_location][
            selected_epidemiology_data
        ].tolist(),
        mode="lines",
        name=label,
        line=dict(color="black"),
        yaxis="y2",
    )

    data_line = [line_trace]

    layout = go.Layout(
        barmode="group",  # Change to "group" for grouped bar chart
        xaxis=dict(
            title="Month-Year",
            tickvals=yr_mnth,
            tickformat="%b %Y",
        ),
        yaxis=dict(title="Mobility Counts", showgrid=True),
        yaxis2=dict(
            title="Epidemiological Counts", overlaying="y", side="right", showgrid=True
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig = go.Figure(data=data_bar + data_line, layout=layout)

    """
    # find maximum sum of 5 mobility columns for the selected country and set it as the upper limit of y-axis
    ymin_left = min(
                    min(df[df["country_name"] == selected_location]["mobility_residential"].tolist()),
                    min(df[df["country_name"] == selected_location]["mobility_workplaces"].tolist()),
                    min(df[df["country_name"] == selected_location]["mobility_transit_stations"].tolist()),
                    min(df[df["country_name"] == selected_location]["mobility_grocery_and_pharmacy"].tolist()),
                    min(df[df["country_name"] == selected_location]["mobility_parks"].tolist())
                )
    ymax_left = max(
                    max(df[df["country_name"] == selected_location]["mobility_residential"].tolist()),
                    max(df[df["country_name"] == selected_location]["mobility_workplaces"].tolist()),
                    max(df[df["country_name"] == selected_location]["mobility_transit_stations"].tolist()),
                    max(df[df["country_name"] == selected_location]["mobility_grocery_and_pharmacy"].tolist()),
                    max(df[df["country_name"] == selected_location]["mobility_parks"].tolist())
                )
    ymin_right = min(df[df["country_name"] == selected_location][selected_epidemiology_data].tolist())
    ymax_right = max(df[df["country_name"] == selected_location][selected_epidemiology_data].tolist())

    
    fig.update_layout(
        yaxis_range=[ymin_left, ymax_left],  # Adjust the range as needed
        yaxis2_range=[ymin_right, ymax_right],  # Adjust the range as needed
    )
    """
    return fig
