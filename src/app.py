import sys

import dash
import dash_bootstrap_components as dbc

sys.dont_write_bytecode = True


app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server
