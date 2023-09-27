from os.path import join

import matplotlib
import pandas as pd
import plotly_express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from controller.PCA.PCA_GRAPHS import compute_PCA as cPCA
from loaded_data import df_annot_final, tables_path
from utils import get_header

matplotlib.use("Agg")

df_ROI_final = pd.read_csv(join(tables_path, "df_ROI_final.csv"))


def create_layout(app, df_ROI_final):
    # Page layouts
    return (
        html.Div(
            [
                html.Div([get_header(app)]),
                # page 1
                html.Div(
                    [
                        # Row 3
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        # Row 4
                        html.Div(
                            [
                                html.Div(
                                    [
                                        # PCA PLOT BUTTON AND GRAPH
                                        html.H5(
                                            [
                                                "Principal Component Analysis of all Regions of Interest"
                                            ],
                                            style={"marginLeft": "30px"},
                                        ),
                                        html.Button(
                                            "COMPUTE AND PLOT PCA",
                                            id="button",
                                            n_clicks=0,
                                            style={"marginLeft": "30px"},
                                        ),
                                        dcc.Graph(id="PCA"),
                                        dcc.Graph(id="sunburst1"),
                                        dcc.Graph(id="PCA_features"),
                                    ]
                                ),
                            ],
                            className="nine columns",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        # PCA PARAMETERS/SOURCE DATA SELECTION:
                                        html.H5(
                                            ["PCA parameters "],
                                            style={"marginLeft": "30px"},
                                        ),
                                        html.H6(
                                            ["Color grouping :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Dropdown(
                                            [
                                                "order",
                                                "family",
                                                "genus",
                                                "species",
                                                "biotope",
                                                "sound_id",
                                            ],
                                            value="species",
                                            id="color",
                                            style={"marginLeft": "10px"},
                                        ),
                                        html.H6(
                                            ["features :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Dropdown(
                                            [
                                                "basic",
                                                "shapes",
                                                "shapes+basic",
                                                "spectral",
                                                "spectral+basic",
                                                "temporal",
                                                "temporal+basic",
                                                "all",
                                            ],
                                            value="basic",
                                            id="features",
                                            style={"marginLeft": "10px"},
                                        ),  # noqa : E501
                                        html.H6(
                                            ["Roi detection method:"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Dropdown(
                                            ["manual", "auto"],
                                            value="manual",
                                            id="roi_method",
                                            style={"marginLeft": "10px"},
                                        ),
                                        html.H6(
                                            ["Dimensions"],
                                            className="subtitle padded",
                                            style={"marginLeft": "30px"},
                                        ),
                                        dcc.Input(
                                            id="dimensions",
                                            type="number",
                                            value=2,
                                            placeholder="dimensions",
                                            style={"marginLeft": "30px"},
                                        ),
                                        dcc.Graph(id="loadings"),
                                    ]
                                ),
                            ],
                            className="three columns",
                        ),
                        dcc.Store(id="datastore_PCA", storage_type="session"),
                        html.Div([], className="twelve columns"),
                    ]
                ),
            ]
        ),
    )


# callbacks


@app.callback(
    Output("PCA", "figure"),
    Output("PCA_features", "figure"),
    Output("sunburst1", "figure"),
    Output("loadings", "figure"),
    Input("button", "n_clicks"),
    State("features", "value"),
    State("dimensions", "value"),
    State("color", "value"),
    State("roi_method", "value"),
)
def generate_graphs(n, features, dimensions, color, roi_method):
    if n == 0:
        raise PreventUpdate

    if roi_method == "manual":
        data = df_annot_final

    if roi_method == "auto":
        data = df_ROI_final

    fig, fig2, loadings_graph = cPCA(
        df_ROI_final=data, features_options=features, dimensions=dimensions, color=color
    )

    data["birds"] = "Birds"
    sunburst = px.sunburst(
        data,
        path=["biotope", "family", "genus", "species"],
        width=750,
        height=650,
        title="Genus & Species distribution amongst Regions of interests <br><sup>Areas represent number of ROI, hover for info.</sup>",  # noqa : E501
    )

    return fig, fig2, sunburst, loadings_graph
