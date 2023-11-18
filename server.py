from presentation import presentation_title
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        dbc.icons.BOOTSTRAP,
    ],
)
app.config.suppress_callback_exceptions = True
app.title = presentation_title
server = app.server
