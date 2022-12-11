from loaded_data import df_annot_final, df_ROI_final
from utils import utils
from app import app
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from controller.UMAP.UMAP_GRAPHS import plot_umap
import matplotlib
matplotlib.use('Agg')

GENERIC_FEATURES = ['min_f', 'max_f', 'centroid_f',
                    'duration_t', 'bandwidth_f', 'area_tf']

SHAPE_FEATURES = ['shp_002', 'shp_003', 'shp_004', 'shp_005', 'shp_006', 'shp_007',
                  'shp_008', 'shp_009', 'shp_010', 'shp_011', 'shp_012', 'shp_013',
                  'shp_014', 'shp_015', 'shp_016', 'shp_017', 'shp_018', 'shp_019',
                  'shp_020', 'shp_021', 'shp_022', 'shp_023', 'shp_024', 'shp_025',
                  'shp_026', 'shp_027', 'shp_028', 'shp_029', 'shp_030', 'shp_031',
                  'shp_032', 'shp_033', 'shp_034', 'shp_035', 'shp_036', 'shp_037',
                  'shp_038', 'shp_039', 'shp_040', 'shp_041', 'shp_042', 'shp_043',
                  'shp_044', 'shp_045', 'shp_046', 'shp_047', 'shp_048']


SPECTRAL_FEATURES = ['MEANf', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf',
                     'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'ACI',
                     'NDSI', 'ROU']

TEMPORAL_FEATURES = ['ZCR', 'MEANt', 'VARt',
                     'SKEWt', 'KURTt', 'Ht']


def create_layout(app, df_ROI_final):
    # Page layouts
    return html.Div(
        [
            html.Div([utils.get_header(app)]),
            # page 1
            html.Div(
                [
                    # Row 3
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4("CDAC App"),
                                ],
                                className="product",
                            ),
                            html.Div([utils.get_menu()]),
                            html.Br([]),
                        ],
                        className="row",
                    ),
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
                                        ["Select features to be calculated on all ROIs"], style={
                                            'marginLeft': '30px'}
                                    ),
                                    html.H6(["Select Basic features :"], style={
                                        'marginLeft': '30px'}, className="subtitle padded"),
                                    dcc.Checklist([features for features in GENERIC_FEATURES], inputStyle={"margin-right": "10px", "margin-left": "10px"}, value=[
                                                  'min_f', 'max_f', 'centroid_f', 'duration_t', 'bandwidth_f', 'area_tf'], inline=True, id='basic_features', style={'marginLeft': '10px'}),

                                    html.H6(["Select Spectral features :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"),
                                    dcc.Checklist([features for features in SPECTRAL_FEATURES], inputStyle={"margin-right": "10px", "margin-left": "10px"}, value=[
                                    ], inline=True, id='spect_features', style={'marginLeft': '10px'}),

                                    html.H6(["Select Temporal features :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"),

                                    dcc.Checklist([features for features in TEMPORAL_FEATURES], inputStyle={"margin-right": "10px", "margin-left": "10px"}, value=[
                                    ], inline=True, id='select_family', style={'marginLeft': '10px'}),

                                    html.H6(["Add shapes ? :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"),
                                    dcc.Checklist(['COMPUTE_SHAPES'], value=[
                                    ], inline=True, id='shapes_toggle', inputStyle={"margin-right": "10px", "margin-left": "10px"}, style={'marginLeft': '10px'})], className="twelve columns"),

                            html.Button('COMPUTE ALL FEATURES', id='button', n_clicks=0, style={
                                        'marginLeft': '30px'}),
                        ]),
                ],
                className="twelve columns",
            ),

        ]),
