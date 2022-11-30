from utils import utils
from app import app

import pandas as pd

from dash import dash_table, dcc, html
from dash import dcc, callback_context
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pages.info_about_data.info_about_data import df_metafiles_xenocanto


# import processed data from datasets
# %%
df_metafiles_xenocanto = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/metafiles_xenocanto.csv')
df_metafiles_xenocanto_reduced = df_metafiles_xenocanto.loc[:, [
    'id', 'gen', 'sp', 'lat', 'lng', 'alt', 'type', 'q', 'length', 'bird-seen']]

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def create_layout(app, df_metafiles_xenocanto):
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
                    # Row 4
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["First, let's load and check data and Metafiles from XenoCanto:"], className="subtitle padded"
                                    ),
                                    # this contains the map (return of callback):
                                    html.Div(
                                        id='datatable-interactivity-container'),

                                    # INTERACTIVE DATATABLE:
                                    dash_table.DataTable(id='datatable-interactivity',
                                                         columns=[
                                                             {"name": i, "id": i, "deletable": True, "selectable": True} for i in df_metafiles_xenocanto.columns
                                                         ],
                                                         data=df_metafiles_xenocanto.to_dict(
                                                             'records'),
                                                         editable=True,
                                                         filter_action="native",
                                                         sort_action="native",
                                                         sort_mode="multi",
                                                         column_selectable="single",
                                                         row_selectable="multi",
                                                         row_deletable=True,
                                                         selected_columns=[],
                                                         selected_rows=[],
                                                         page_action="native",
                                                         page_current=0,
                                                         page_size=10,
                                                         ),
                                    dbc.Button(
                                        "Save Filtered Dataset in csv",
                                        color="primary",
                                        id="save_button",
                                        className="mb-4",
                                    ),
                                    # TABS AND GRAPHS:
                                    html.Div([dbc.Container([dcc.Store(id="store"),

                                                             dbc.Button(
                                        "Compute acoustic data",
                                        color="primary",
                                        id="button",
                                        className="mb-4",
                                    ),
                                        dbc.Tabs(
                                        [
                                            dbc.Tab(label="Histograms",
                                                    tab_id="histogram"),
                                            dbc.Tab(label="Scatter",
                                                    tab_id="scatter"),
                                            dbc.Tab(label="file length",
                                                    tab_id="length"),
                                        ],
                                        id="tabs",
                                        active_tab="Histograms",
                                    ),
                                        html.Div(id="tab-content",
                                                 className="p-4"),
                                    ]),
                                    ]
                                    )
                                ]),
                        ],
                        className="twelve columns",
                    ),
                ])
        ]),
# callbacks


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"),
    Input("save_button", "n_clicks"))
def update_graphs(rows, derived_virtual_selected_rows, n):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df_metafiles_xenocanto if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    birds_positions = dff.loc[:, ['gen', 'lat', 'lng']]
    birds_positions.columns = ['name', 'lat', 'lon']
    birds_positions = birds_positions.to_dict('records')
    # Creating a geojson from the input points
    geojson_birds = dlx.dicts_to_geojson(
        [{**bird, **dict(tooltip=bird['name'])} for bird in birds_positions])

    if n:
        dff.to_csv(
            '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv')

    return [html.H6('Current number of files: ' + str(dff.id.count())),
            dl.Map([dl.TileLayer(), dl.GeoJSON(data=geojson_birds, id="geojson", zoomToBounds=True, cluster=True)],
                   style={"width": "1500px",
                          "height": "400px"},
                   ), ]


# callbacks

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """

    if active_tab and data is not None:
        if active_tab == "scatter":
            return dcc.Graph(figure=data["scatter"])
        if active_tab == "length":
            return dcc.Graph(figure=data["hist_3"])
        elif active_tab == "histogram":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["hist_1"]), width=12),
                    dbc.Col(dcc.Graph(figure=data["hist_2"]), width=12),
                ]
            )
    return "No tab selected"


@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
    """
    This callback generates three simple graphs from random data.
    """
    if not n:
        # generate empty graphs when app loads
        return {k: go.Figure(data=[]) for k in ["scatter", "hist_1", "hist_2", "hist_3"]}

    data = df_metafiles_xenocanto
    scatter = go.Figure(
        data=[go.Scatter(x=data.loc[:, 'lat'],
                         y=data.loc[:, 'lng'], mode="markers")]
    )
    hist_1 = go.Figure(data=[go.Histogram(x=data.loc[:, 'rec'])])
    hist_2 = go.Figure(
        data=[go.Histogram(x=data.loc[:, 'q'], hoverinfo='all')])
    hist_3 = go.Figure(
        data=[go.Histogram(x=data.loc[:, 'length'], xbins=dict(
            start='00:00',
            end=max(data.loc[:, 'length']),
            size='10s'
        ), hoverinfo='all')])

    hist_1.update_layout(xaxis={'categoryorder': 'total ascending'})
    # hist_2.update_layout(xaxis={'categoryorder': 'total ascending'})
    hist_3.update_layout(xaxis={'categoryorder': 'total ascending'})

    # save figures in a dictionary for sending to the dcc.Store
    return {"scatter": scatter, "hist_1": hist_1, "hist_2": hist_2, "hist_3": hist_3}

# %%
