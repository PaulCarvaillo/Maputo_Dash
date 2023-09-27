import json
from os.path import join

from dash import dcc, html

from utils import get_assets_dir, get_header

json_file_path = join(get_assets_dir(), "features.json")
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

GENERIC_FEATURES = data["GENERIC_FEATURES"]
SHAPE_FEATURES = data["SHAPE_FEATURES"]
SPECTRAL_FEATURES = data["SPECTRAL_FEATURES"]
TEMPORAL_FEATURES = data["TEMPORAL_FEATURES"]


def create_layout(app, df_ROI_final):
    # Page layouts
    return (
        html.Div(
            [
                html.Div([get_header(app)]),
                # page 1
                html.Div(
                    [
                        # Row 4
                        html.Div(
                            [
                                html.Div(
                                    [
                                        # PCA PLOT BUTTON AND GRAPH
                                        html.H5(
                                            [
                                                "Select features to be calculated on all ROIs"
                                            ],
                                            style={"marginLeft": "30px"},
                                        ),
                                        html.H6(
                                            ["Select Basic features :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Checklist(
                                            [features for features in GENERIC_FEATURES],
                                            inputStyle={
                                                "margin-right": "10px",
                                                "margin-left": "10px",
                                            },
                                            value=[
                                                "min_f",
                                                "max_f",
                                                "centroid_f",
                                                "duration_t",
                                                "bandwidth_f",
                                                "area_tf",
                                            ],
                                            inline=True,
                                            id="basic_features",
                                            style={"marginLeft": "10px"},
                                        ),
                                        html.H6(
                                            ["Select Spectral features :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Checklist(
                                            [
                                                features
                                                for features in SPECTRAL_FEATURES
                                            ],
                                            inputStyle={
                                                "margin-right": "10px",
                                                "margin-left": "10px",
                                            },
                                            value=[],
                                            inline=True,
                                            id="spect_features",
                                            style={"marginLeft": "10px"},
                                        ),
                                        html.H6(
                                            ["Select Temporal features :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Checklist(
                                            [
                                                features
                                                for features in TEMPORAL_FEATURES
                                            ],
                                            inputStyle={
                                                "margin-right": "10px",
                                                "margin-left": "10px",
                                            },
                                            value=[],
                                            inline=True,
                                            id="select_family",
                                            style={"marginLeft": "10px"},
                                        ),
                                        html.H6(
                                            ["Add shapes ? :"],
                                            style={"marginLeft": "30px"},
                                            className="subtitle padded",
                                        ),
                                        dcc.Checklist(
                                            ["COMPUTE_SHAPES"],
                                            value=[],
                                            inline=True,
                                            id="shapes_toggle",
                                            inputStyle={
                                                "margin-right": "10px",
                                                "margin-left": "10px",
                                            },
                                            style={"marginLeft": "10px"},
                                        ),
                                    ],
                                    className="twelve columns",
                                ),
                                html.Button(
                                    "COMPUTE ALL FEATURES",
                                    id="button",
                                    n_clicks=0,
                                    style={"marginLeft": "30px"},
                                ),
                            ]
                        ),
                    ],
                    className="twelve columns",
                ),
            ]
        ),
    )
