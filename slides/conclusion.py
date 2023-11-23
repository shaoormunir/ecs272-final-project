# content = html.H1("End", style=dict(textAlign="center"))

from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from server import app
import pandas as pd


df = pd.read_csv("data/conclusion/conclusion.csv")

countries = sorted(df["Countries"].unique().tolist())
print(countries)

df_data = df.set_index('Countries').transpose()
print(df_data.head())

initial_index = list(df_data.index)
final_index = []
for ind_val in initial_index:
    new_val = " ".join([word.capitalize() for word in str(ind_val).split("_")]).replace(" Usd", " (USD)").replace(" Per 1000", " (Per 1000)") + " "
    final_index.append(new_val)

print(final_index)
df_data.set_index(pd.Index(final_index), inplace=True)
df_data = df_data.rename_axis(index='Different Factors')



content = html.Div(
    style=dict(height="76vh", width="100%", textAlign="center"),
    children=[
        html.Div(
            [
                    html.Div(
                    [
                        html.H3("Relative Comparison of Factors across Countries", style={"color": "white"}),  # Customize text color
                    ],
                    style={
                        "background-color": "#007bff",  # Set background color of the box
                        "padding": "2px",  # Add padding for better aesthetics
                        "border-radius": "10px",  # Add rounded corners to the box
                        "text-align": "center",  # Center-align the text within the box
                    },
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown("\nScroll & Select Countries to Perform 0-1 Scaled Factor Comparison"),
                dcc.Checklist(
                    id='countries',
                    options=[{'label': html.Div(country, style={"display": "inline", "font-size": 15, "padding-right": "0.2rem", "padding-right": "0.7rem"}), "value": country} for country in countries],
                    value=["Afghanistan", "Australia", "Brazil", "Canada", "Egypt", "Germany", 
                           "India", "Japan", "Luxembourg", "Russia", 
                           "Singapore", "South Africa", "South Korea", "Spain", "Sri Lanka", 
                           "Turkey", "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America"],
                    inline=True,
                    style=dict(height="9vh", overflow='scroll'),
                ),
                dcc.Graph(id="graph", style=dict(height="74vh", overflow='scroll')),
            ],
            style=dict(textAlign="center", height="76vh"),
            id="dd-output-container",
        ),
    ],
)


@app.callback(
    Output("graph", "figure"), 
    Input("countries", "value"))
def filter_heatmap(cols):
    global df_data;
    df_data = df_data # px.data.medals_wide(indexed=True) # replace with your own data source
    fig = px.imshow(df_data[cols], text_auto=True, aspect="auto")
    fig.update_traces(hovertemplate="Country: %{y}<br>Factor: %{x}<br>Value: %{z}")
    return fig