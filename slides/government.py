from ctypes import alignment
from dash import html, dcc, Input, Output, State
from server import app

import dash
import plotly.graph_objs as go
import pandas as pd

import plotly.express as px


def find_transitions(lst):
    transitions = []
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1]:
            transitions.append(i)
    return transitions


df = pd.read_csv("data/government/gov.csv")
# df['date'] = df['date'].astype(str)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(by="date")

# Compute total_deaths for each country and date combination
df["total_deaths"] = df.groupby(["country_name", "date"])["new_deceased"].transform(
    "sum"
)

# Compute total_recoveries for each country and date combination
df["total_recoveries"] = df.groupby(["country_name", "date"])[
    "new_recovered"
].transform("sum")

# Compute total_vaccinated for each country and date combination
df["total_vaccinated"] = df.groupby(["country_name", "date"])[
    "new_persons_fully_vaccinated"
].transform("sum")

# Compute total_active_cases for each country and date combination
df["total_active_cases"] = df.groupby(["country_name", "date"])[
    "new_confirmed"
].transform("sum")


content = html.Div(
    style=dict(height="76vh", width="100%", textAlign="center"),
    children=[
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": i, "value": i}
                        for i in sorted(df["country_name"].unique().tolist())
                    ],
                    value="United States of America",
                    id="country-dropdown",
                ),
            ],
            style=dict(textAlign="center", width="40%", display="inline-block"),
        ),
        html.Div(
            [
                dcc.Graph(
                    id="government-graph",
                    style=dict(height="76vh", overflow="scroll"),
                    config={"displayModeBar": False},
                ),
            ],
            style=dict(textAlign="center", height="76vh"),
            id="dd-output-container",
        ),
    ],
)


@app.callback(
    Output("government-graph", "figure"),
    [Input("country-dropdown", "value")],
)
def update_charts(selected_location):
    selected_df = df[df["country_name"] == selected_location]
    dates = selected_df["date"].astype(str).tolist()
    active_cases = selected_df["total_active_cases"].tolist()
    deaths = selected_df["total_deaths"].tolist()
    recoveries = selected_df["total_recoveries"].tolist()
    vaccinated = selected_df["total_vaccinated"].tolist()

    # print(len(df), len(selected_df), len(dates), len(active_cases), len(deaths), len(recoveries), len(vaccinated))
    # print(dates, active_cases)
    # print(selected_df)

    governement_response_columns = [
        "school_closing",
        "workplace_closing",
        "cancel_public_events",
        "restrictions_on_gatherings",
        "public_transport_closing",
        "stay_at_home_requirements",
        "restrictions_on_internal_movement",
        "international_travel_controls",
        "debt_relief",
        "public_information_campaigns",
        "testing_policy",
        "contact_tracing",
        "facial_coverings",
        "vaccination_policy",
    ]

    trace1 = go.Scatter(
        x=dates,
        y=active_cases,
        mode="lines",
        name="Total Active Cases",
        line=dict(color="blue"),
        hoverinfo="text",
        text=[
            "Date: {}<br>Active Cases: {}".format(date, int(active))
            for date, active in zip(dates, active_cases)
        ],
    )

    trace2 = go.Scatter(
        x=dates,
        y=deaths,
        mode="lines",
        name="Total Death Cases",
        line=dict(color="red"),
        hoverinfo="text",
        text=[
            "Date: {}<br>Deaths: {}".format(date, int(death))
            for date, death in zip(dates, deaths)
        ],
    )

    trace3 = go.Scatter(
        x=dates,
        y=recoveries,
        mode="lines",
        name="Total Recoveries",
        line=dict(color="green"),
        hoverinfo="text",
        text=[
            "Date: {}<br>Recoveries: {}".format(date, int(recovery))
            for date, recovery in zip(dates, recoveries)
        ],
    )

    trace4 = go.Scatter(
        x=dates,
        y=vaccinated,
        mode="lines",
        name="Total Vaccinated",
        line=dict(color="orange"),
        hoverinfo="text",
        text=[
            "Date: {}<br>Vaccinated: {}".format(date, int(vaccinated_value))
            for date, vaccinated_value in zip(dates, vaccinated)
        ],
    )

    data_line = [trace1, trace2, trace3, trace4]
    tick_labels = [
        date.strftime("%Y-%m-%d") if i % 10 == 0 else ""
        for i, date in enumerate(selected_df["date"])
    ]

    for column in governement_response_columns:
        events = selected_df[column].tolist()
        indexes = find_transitions(events)
        y_axis_range = [
            min(active_cases + deaths + recoveries + vaccinated),
            max(active_cases + deaths + recoveries + vaccinated),
        ]
        y_values = [y_axis_range[0], y_axis_range[1]]
        for idx in indexes:
            if events[idx] == "Restrictions":
                data_line.append(
                    go.Scatter(
                        x=[str(selected_df.iloc[idx]["date"])] * 2,
                        y=y_values,
                        yaxis="y2",
                        mode="lines",
                        text=f'{" ".join(word.capitalize() for word in column.split("_"))} Restriction IMPOSED',
                        hoverinfo="text",
                        line_dash="solid",
                        line_color="black",
                        showlegend=False,
                    )
                )
            else:
                data_line.append(
                    go.Scatter(
                        x=[str(selected_df.iloc[idx]["date"])] * 2,
                        y=y_values,
                        yaxis="y2",
                        mode="lines",
                        text=f'{" ".join(word.capitalize() for word in column.split("_"))} Restriction REMOVED',
                        hoverinfo="text",
                        line_dash="dash",
                        line_color="black",
                        showlegend=False,
                    )
                )

        layout = go.Layout(
            xaxis=dict(
                title="Date",
                tickvals=dates,
                ticktext=tick_labels,
                tickmode="array",
            ),
            yaxis=dict(title="Epidemiological Counts", showgrid=True),
            yaxis2=dict(overlaying="y", fixedrange=False, visible=False),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            hovermode="x",  # "x unified" => spikemode
            spikedistance=0,
        )

    fig = go.Figure(data=data_line, layout=layout)

    # for column in governement_response_columns:
    #     events = selected_df[column].tolist()
    #     indexes = find_transitions(events)
    #     for idx in indexes:
    #         if events[idx] == "Restrictions":
    #             fig.add_vline(x=selected_df["date"].iloc[idx], line_width=2, line_dash="solid", line_color="black")
    #         else:
    #             fig.add_vline(x=selected_df["date"].iloc[idx], line_width=2, line_dash="dash", line_color="black") # x=dates[idx]

    return fig
