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


def create_layout(app, df_ROI_final):
    # Page layouts
    return html.Div(
        [
            html.Div([utils.get_header(app)]),
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
                                        ["Uniform Manifold Approximation and Projection of all Regions of Interest"], style={
                                            'marginLeft': '30px'}
                                    ),
                                    html.Button('COMPUTE AND PLOT UMAPS', id='button', n_clicks=0, style={
                                        'marginLeft': '30px'}),

                                    dcc.Graph(id='UMAP'),
                                    # dcc.Graph(id='PCA_features'),

                                ]),
                        ],
                        className="nine columns",
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    # PCA PARAMETERS/SOURCE DATA SELECTION:
                                    html.H5(
                                        ["UMAP parameters "], style={
                                            'marginLeft': '30px'}
                                    ),

                                    html.H6(
                                        ["Color grouping :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['order', 'family', 'genus', 'species', 'sound_id', 'biotope'], value='species', id='color', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["features :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['all', 'basic', 'shapes', 'shapes+basic', 'spectral', 'spectral+basic', 'temporal', 'temporal+basic', 'all'], value='basic', id='features', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["Roi detection method:"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['manual', 'auto'], value='manual', id='roi_method', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["n_neighbours"], className="subtitle padded", style={
                                            'marginLeft': '30px'},
                                    ),
                                    dcc.Input(id="dimensions", type="number", value=2, placeholder="n_neighbours", style={
                                              'marginLeft': '30px'})
                                ]),
                        ],
                        className="two columns",
                    ),

                    dcc.Store(id='datastore_PCA', storage_type='session'),
                    html.Div([html.H6(["Select Biotope :"], style={
                        'marginLeft': '30px'}, className="subtitle padded"),
                        dcc.Checklist([biotope for biotope in df_annot_final.biotope.unique()], value=[
                        ], inline=True, id='select_biotope', style={'marginLeft': '10px'}),

                        html.H6(["Select Families :"], style={
                                'marginLeft': '30px'}, className="subtitle padded"),
                        dcc.Checklist([family for family in df_annot_final.family.unique()], value=[
                        ], inline=True, id='select_family', style={'marginLeft': '10px'}),

                        html.H6(["Select Species :"], style={
                                'marginLeft': '30px'}, className="subtitle padded"),
                        dcc.Checklist([species for species in df_annot_final.species.unique()], value=[
                        ], inline=True, id='select_species', style={'marginLeft': '10px'})], className="twelve columns"),

                ])
        ]),
# callbacks


@app.callback(Output("UMAP", "figure"), Input("select_family", "value"), Input("select_biotope", "value"), Input("select_species", "value"), Input("button", "n_clicks"), Input("features", "value"), Input("dimensions", "value"), Input("color", "value"), Input("roi_method", "value"))
def generate_graphs(select_family, select_biotope, select_species, n, features, dimensions, color, roi_method):
    if n == 0:
        raise PreventUpdate

    if roi_method == 'manual':
        data = df_annot_final

    if roi_method == 'auto':
        data = df_ROI_final

    if select_family != []:
        data = data[data['family'].isin(select_family)]
    if select_biotope != []:
        data = data[data['biotope'].isin(select_biotope)]
    if select_species != []:
        data = data[data['species'].isin(select_species)]

    fig = plot_umap(df_ROI_final=data, features_options=features,
                    n_components=dimensions, color=color, init='random', random_state=0, method=roi_method)

    return fig
