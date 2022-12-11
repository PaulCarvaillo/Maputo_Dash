from sklearn.manifold import TSNE
from utils import utils
from app import app
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from controller.tSNE.tSNE_GRAPHS import compute_tSNE_2d

import matplotlib
matplotlib.use('Agg')


df_ROI_final = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_ROI_final.csv')


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
                                    html.H4("CDAC app"),
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
                                    # FILEPATH/SPECIES/FREQUENCY SELECTOR PARAMETERS:
                                    html.H5(
                                        ["t-distributed Stochastic Neighbor Embedding (t-SNE) of ROI"], style={
                                            'marginLeft': '30px'}
                                    ),
                                    html.Button('COMPUTE AND PLOT t-SNE', id='button', n_clicks=0, style={
                                        'marginLeft': '30px'}),

                                    dcc.Graph(id='t-SNE'),

                                ]),
                        ],
                        className="nine columns",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    # ROI PARAMETERS:
                                    html.H5(
                                        ["t-SNE parameters "], style={
                                            'marginLeft': '30px'}
                                    ),
                                   
                                    html.H6(
                                        ["Color grouping :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['species', 'biotopes','gen'], value='species', id='color', style={
                                            'marginLeft': '10px'}),
                                    
                                    
                                    html.H6(
                                        ["features :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['basic', 'shapes'], value='basic', id='features', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["Roi detection method:"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['Manual annotation', 'Automatic detection'], value='basic', id='roi_method', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["t-SNE method:"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['exact', 'barnes_hut'], value='barnes_hut', id='method', style={
                                            'marginLeft': '10px'}),
                                    
                                    html.H6(
                                        ["Perplexity:"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(5, 50, marks=None,
                                               value=15, id='perplexity', tooltip={"placement": "bottom", "always_visible": True}),
                                    
                                    html.H6(
                                        ["Early exageration:"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(1, 50, marks=None,
                                               value=12, id='early_exag', tooltip={"placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Learning rate:"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(10, 1000, marks=None,
                                               value=200, id='learning_rate', tooltip={"placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Number of iterations:"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(250, 5000, marks=None,
                                               value=1000, id='n_iter', tooltip={"placement": "bottom", "always_visible": True}),
                                    
                                    html.H6(
                                        ["Dimensions"], className="subtitle padded", style={
                                            'marginLeft': '30px'},
                                    ),
                                    dcc.Input(id="dimensions", type="number",value=2, placeholder="dimensions", style={'marginLeft':'30px'})
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

df_ROI_final = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_ROI_final.csv')


@app.callback(Output("t-SNE", "figure"), [Input("button", "n_clicks"), Input("features","value"), Input("perplexity","value"),Input("color","value"),Input("early_exag","value"),Input("learning_rate","value"), Input("n_iter","value"),Input("method","value")])
def generate_graphs(n,features_options,perplexity,color,early_exag,learning_rate,n_iter,method):
    if n == 0:
        raise PreventUpdate

    fig2 = compute_tSNE_2d(df_ROI_final,
                           features_options=features_options,
                            perplexity=perplexity,
                            color=color,
                            early_exag=early_exag ,
                            learning_rate=learning_rate,
                            n_iter=n_iter,
                            method=method)


    return fig2
