from utils import utils
from app import app
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from controller.UMAP.UMAP_GRAPHS import plot_umap
import matplotlib
matplotlib.use('Agg')
from loaded_data import df_annot_final



df_ROI_final = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_ROI_final.csv')

# df_annot_final = pd.read_csv(
#     '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_annot_final.csv')



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
                                    html.H4("Birds of Maputo Special Reserve"),
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
                                        ['order', 'family', 'genus', 'species'], value='species', id='color', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["features :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['all','basic', 'shapes', 'shapes+basic', 'spectral','spectral+basic', 'temporal','temporal+basic', 'all'], value='basic', id='features', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["Roi detection method:"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['manual', 'auto'], value='manual', id='roi_method', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["Dimensions(2D/3D)"], className="subtitle padded", style={
                                            'marginLeft': '30px'},
                                    ),
                                    dcc.Input(id="dimensions", type="number", value=2, placeholder="dimensions", style={
                                              'marginLeft': '30px'})
                                ]),
                        ],
                        className="three columns",
                    ),
                    dcc.Store(id='datastore_PCA', storage_type='session'),
                    html.Div([
                    ],
                        className="twelve columns")
                ])
        ]),
# callbacks


@app.callback(Output("UMAP", "figure"), Input("button", "n_clicks"), Input("features", "value"), Input("dimensions", "value"), Input("color", "value"), Input("roi_method", "value"))
def generate_graphs(n, features, dimensions, color, roi_method):
    if n == 0:
        raise PreventUpdate

    if roi_method == 'manual':
        data = df_annot_final

    if roi_method == 'auto':
        data = df_ROI_final

    fig=plot_umap(df_ROI_final=data, features_options=features,
                     n_components=dimensions, color=color,init='random',random_state=0,method=roi_method)

    return fig

