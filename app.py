from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import importlib

from server import app, server
from presentation import (
    slide_order,
    slide_titles,
    slide_subtitles,
)

glob_selected_country = None


# add the slides to the object space if they are in the slide order
for x in os.listdir(os.getcwd() + "/slides"):
    slide_name = x.split(".")[0]
    if slide_name in slide_order:
        globals()["slide_" + slide_name] = importlib.import_module(
            "slides." + slide_name
        )


# helper function that returns dict of enumerated slide names
def slide_dict():
    d = {v: k for k, v in dict(enumerate(slide_order)).items()}
    d["/"] = 0
    return d


def slide_title_dict():
    d = {v: k for k, v in dict(enumerate(slide_titles)).items()}
    d["/"] = 0
    return d


def slide_subtitle_dict():
    d = {v: k for k, v in dict(enumerate(slide_subtitles)).items()}
    d["/"] = 0
    return d


nav_style = dict(
    textAlign="center",
)


def nav_button_div(text):
    """helper function to return the navigation buttons easily"""

    FA_icon = html.I(className=text)
    return html.Div(dbc.Button([FA_icon, ""], className="me-2"))


# logo if there is one
def get_logo():
    assets = os.listdir(os.getcwd() + "/assets/")
    split_assets = [x.split(".")[0] for x in assets]
    for i, x in enumerate(split_assets):
        if x == "logo":
            return html.Img(src="assets/" + assets[i], style=dict(height="50px"))
    return html.Img(
        height="40px",
        src="https://github.com/russellromney/dash-slides/assets/raw/logo.png",
    )


# Read Country Data
country_data = pd.read_csv("data/intro/index.csv")


app.layout = html.Div(
    [
        # URL control
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="selected-country-store", storage_type="session"),
        dbc.Container(
            fluid=True,
            children=[
                html.Div(id="current-slide", style=dict(display="none", children="")),
                # nav div
                dbc.Row(
                    justify="center",
                    # style=dict(
                    #     position="fixed",
                    #     marginTop="10px",
                    #     width="100%",
                    #     top="0",
                    # ),
                    children=[
                        # previous
                        dbc.Col(
                            width=2,
                            style=dict(textAlign="left"),
                            children=[
                                dcc.Link(
                                    id="previous-link",
                                    href="",
                                    children=nav_button_div(
                                        "fa-solid fa-arrow-left me-2"
                                    ),
                                ),
                            ],
                        ),  # end previous
                        # slide count
                        # dbc.Col(
                        #     width=2,
                        #     style=nav_style,
                        #     children=[
                        #         dbc.DropdownMenu(
                        #             id="slide-count",
                        #             size="lg",
                        #             children=[
                        #                 dbc.DropdownMenuItem(
                        #                     s,
                        #                     href="/" + s,
                        #                 )
                        #                 for s in slide_order
                        #             ],
                        #         )
                        #     ],
                        # ),  # end slide count
                        # next
                        dbc.Col(
                            width=8,
                            id="slide-information",
                            children=[],
                        ),
                        dbc.Col(
                            width=2,
                            style=dict(textAlign="right"),
                            children=[
                                dcc.Link(
                                    id="next-link",
                                    href="",
                                    children=nav_button_div(
                                        "fa-solid fa-arrow-right me-2"
                                    ),
                                ),
                            ],
                        ),  # end next
                    ],
                ),
                dbc.Row(
                    justify="center",
                    # style=dict(
                    #     position="fixed",
                    #     marginTop="10px",
                    #     width="100%",
                    #     top="0",
                    # ),
                    children=[
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {"label": i, "value": i}
                                        for i in sorted(
                                            country_data["country_name"]
                                            .unique()
                                            .tolist()
                                        )
                                    ],
                                    value="United States of America",
                                    id="global-dropdown",
                                ),
                            ],
                            style=dict(
                                textAlign="center", width="40%", display="inline-block"
                            ),
                        ),
                    ],
                ),
            ],
        ),
        # navigation header
        dbc.Container(
            fluid=True,
            children=[
                # content div
                dbc.Row(
                    style=dict(position="sticky", margin="10px"),
                    children=[
                        dbc.Col(
                            width=12,
                            style=nav_style,
                            children=[
                                html.Div(
                                    id="page-content",
                                    style=dict(
                                        textAlign="center",
                                        margin="auto",
                                        marginTop="0px",
                                        width="100%",
                                        height="auto",
                                    ),
                                )
                            ],
                        )
                    ],
                ),
            ],
        ),
    ]
)


###
# url function
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def change_slide(pathname):
    """gets current slide goes either back a slide or forward a slide"""
    if pathname == "/" or pathname == "/" + slide_order[0] or pathname == None:
        return globals()["slide_" + slide_order[0]].content
    else:
        try:
            pathname = pathname.split("/")[1].strip()
            return globals()["slide_" + pathname].content
        except:
            return "404"


###


###
# Update Country and store the selection to the global state
@app.callback(
    Output("selected-country-store", "data"), Input("global-dropdown", "value")
)
def update_selected_country(selected_country):
    return selected_country


###


###
# navigation functions
@app.callback(
    [Output("next-link", "href"), Output("previous-link", "href")],
    [Input("current-slide", "children")],
    [State("url", "pathname")],
)
def navigate(current_slide, pathname):
    """
    - listens to
        - next/previous buttons
    - determines the current slide name
    - changes 'next' and 'previous' to the names of the slides on each side of the current slide
    - if this is the last or first slide, 'next' or 'previous' will just refresh the current slide
    """
    next_slide = current_slide
    previous_slide = current_slide
    current_order = slide_dict()[current_slide]
    num_slides = max(slide_dict().values())

    # if we're on the first slide, clicking 'previous' just refreshes the page
    if current_order != 0:
        previous_slide = slide_order[current_order - 1]
    # if we're on the last slide, clicking 'next' just refreshes the page
    if current_order != num_slides:
        next_slide = slide_order[current_order + 1]

    return next_slide, previous_slide


@app.callback(Output("current-slide", "children"), [Input("url", "pathname")])
def set_slide_state(pathname):
    """
    returns the name of the current slide based on the pathname
    this runs first and triggers navigate (changes the relative hrefs of 'next' and 'previous')
    """
    if pathname == None:
        return "/"
    if "/" in pathname:
        if pathname == "/":
            return pathname
        return pathname.split("/")[1].strip()


@app.callback(
    Output("slide-information", "children"), [Input("current-slide", "children")]
)
def update_information(current_slide):
    """
    updates the slide information (title and subtitle)
    """
    current_order = slide_dict()[current_slide]
    title = slide_titles[current_order]
    subtitle = slide_subtitles[current_order]
    return (
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            title,
                            style={"color": "white"},
                        ),  # Customize text color
                    ],
                    style={
                        "background-color": "#007bff",  # Set background color of the box
                        "padding": "2px",  # Add padding for better aesthetics
                        "border-radius": "10px",  # Add rounded corners to the box
                        "text-align": "center",  # Center-align the text within the box
                    },
                ),
                dcc.Markdown(
                    "\n" + subtitle,
                    # center the text
                    style=dict(textAlign="center"),
                ),
            ]
        ),
    )


if __name__ == "__main__":
    app.run_server(
        port=8050,
        host="localhost",
        debug=True,
    )
