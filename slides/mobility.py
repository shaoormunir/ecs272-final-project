from ctypes import alignment
from dash import html, dcc, Input, Output, State
from server import app

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

yr_mnth = ["Apr 2016", "July 2016", "Oct 2016"]

content = html.Div(
    [
        html.Div(
            [
                html.H1("Effect of Mobility"),
                dcc.Dropdown(
                    options=[
                        {"label": "NYC", "value": "NYC"},
                        {"label": "MTL", "value": "MTL"},
                        {"label": "SF", "value": "SF"},
                    ],
                    value="NYC",
                    id="country-dropdown",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "Line Data 1", "value": "line_data_1"},
                        {"label": "Line Data 2", "value": "line_data_2"},
                        # Add more options as needed
                    ],
                    value="line_data_1",
                    id="epidemiology-dropdown",
                ),
            ],
            style=dict(textAlign="center", width="40%", display="inline-block"),
        ),
        html.Div(
            [
                dcc.Graph(id="mobility-graph"),
            ],
            style=dict(textAlign="center"),
            id="dd-output-container",
        ),
    ]
)


@app.callback(
    Output("mobility-graph", "figure"),
    [Input("country-dropdown", "value"), Input("epidemiology-dropdown", "value")],
)
def update_charts(selected_location, selected_line_data):
    trace1 = go.Bar(x=yr_mnth, y=[20, 14, 23], name="Residential Mobility")
    trace2 = go.Bar(x=yr_mnth, y=[12, 18, 29], name="Workplaces Mobility")
    trace3 = go.Bar(x=yr_mnth, y=[20, 5, 12], name="Transit Stations Mobility")
    trace4 = go.Bar(x=yr_mnth, y=[3, 18, 4], name="Grocery & Pharmacy Mobility")
    trace5 = go.Bar(x=yr_mnth, y=[12, 3, 29], name="Parks Mobility")

    data_bar = [trace1, trace2, trace3, trace4, trace5]

    if selected_line_data == "line_data_1":
        line_trace = go.Scatter(
            x=yr_mnth,
            y=[5, 45, 20],
            mode="lines",
            name="Number of Deaths",
            line=dict(color="black"),  # Set line color to black
        )
    else:
        line_trace = go.Scatter(
            x=yr_mnth,
            y=[55, 10, 35],
            mode="lines",
            name="Number of Recoveries",
            line=dict(color="black"),  # Set line color to black
        )

    data_line = [line_trace]

    layout = go.Layout(
        barmode="stack",
        xaxis=dict(title="Month-Year", tickvals=yr_mnth),
        yaxis=dict(title="Mobility Counts", showgrid=True),
        yaxis2=dict(
            title="Epidemiological Counts", overlaying="y", side="right", showgrid=True
        ),
        legend=dict(orientation="h", y=1.12, x=0.1),
    )

    fig = go.Figure(data=data_bar + data_line, layout=layout)
    fig.update_layout(
        yaxis_range=[0, 100],  # Adjust the range as needed
        yaxis2_range=[0, 100],  # Adjust the range as needed
    )
    return fig
