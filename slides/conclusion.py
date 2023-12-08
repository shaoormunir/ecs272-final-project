# content = html.H1("End", style=dict(textAlign="center"))

from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from server import app
import pandas as pd


df = pd.read_csv("data/conclusion/conclusion.csv")
# print(df.columns)

countries = sorted(df["Countries"].unique().tolist())
# print(countries)

# Sort DataFrame by GDP in descending order
df_sorted_desc = df.sort_values(by='gdp_usd', ascending=False)

# Select the top 10 rows based on highest GDP
top_10_high_gdp = df_sorted_desc.head(10)

# Select the bottom 10 rows based on lowest GDP
bottom_10_low_gdp = df_sorted_desc.tail(10)


content = html.Div(
    style=dict(height="76vh", width="100%", textAlign="center"),
    children=[
        html.Div(
            [
                # dcc.Checklist(
                #     id="countries",
                #     options=[
                #         {
                #             "label": html.Div(
                #                 country,
                #                 style={
                #                     "display": "inline",
                #                     "font-size": 15,
                #                     "padding-right": "0.2rem",
                #                     "padding-right": "0.7rem",
                #                 },
                #             ),
                #             "value": country,
                #         }
                #         for country in countries
                #     ],
                #     value=[
                #         "Afghanistan",
                #         "Australia",
                #         "Brazil",
                #         "Canada",
                #         "Egypt",
                #         "Germany",
                #         "India",
                #         "Japan",
                #         "Luxembourg",
                #         "Russia",
                #         "Singapore",
                #         "South Africa",
                #         "South Korea",
                #         "Spain",
                #         "Sri Lanka",
                #         "Turkey",
                #         "Ukraine",
                #         "United Arab Emirates",
                #         "United Kingdom",
                #         "United States of America",
                #     ],
                #     inline=True,
                #     style=dict(height="9vh", overflow="scroll"),
                # ),
                dcc.Graph(
                    id="graph",
                    style=dict(height="74vh", overflow="scroll"),
                    config={"displayModeBar": False},
                ),
            ],
            style=dict(textAlign="center", height="76vh"),
            id="dd-output-container",
        ),
    ],
)


# @app.callback(Output("graph", "figure"), Input("countries", "value"))
@app.callback(Output("graph", "figure"), Input("selected-country-store", "data"))
def filter_heatmap(user_selected_country):
    global df, top_10_high_gdp, bottom_10_low_gdp;

    # Check if the user-selected country is in the top or bottom 10
    user_selected_row = df[df['Countries'] == user_selected_country]
    
    # Case 1: User-selected country is not in the top or bottom 10
    if not(user_selected_row.empty):
        df_data = pd.concat([top_10_high_gdp.head(10), bottom_10_low_gdp.head(10), user_selected_row])

    # Case 2: User-selected country is in the top or bottom 10
    else:
        df_data = pd.concat([top_10_high_gdp, bottom_10_low_gdp])
    
    # countries_to_display = sorted(df_data["Countries"].unique().tolist())
    countries_to_display = df_data["Countries"].unique().tolist()
    
    result_df = df_data.set_index("Countries").transpose()
    # print(df_data.head())

    initial_index = list(result_df.index)
    final_index = []
    for ind_val in initial_index:
        new_val = (
            " ".join([word.capitalize() for word in str(ind_val).split("_")])
            .replace(" Usd", " (USD)")
            .replace(" Per 1000", " (Per 1000)")
            .replace("Lt", " < ").replace("Gt", " >= ")
            + " "
        )
        final_index.append(new_val)

    # print(final_index)
    result_df.set_index(pd.Index(final_index), inplace=True)
    result_df = result_df.rename_axis(index="Different Factors")
    
    result_df = (
        result_df
    )
    
    fig = px.imshow(result_df[countries_to_display], text_auto=True, aspect="auto")
    fig.update_traces(hovertemplate="Country: %{y}<br>Factor: %{x}<br>Value: %{z}")
    return fig
