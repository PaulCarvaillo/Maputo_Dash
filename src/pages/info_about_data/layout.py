import os
from sre_parse import State
from utils import utils
from app import app
import xenopy as xeno
import pandas as pd

from dash import dash_table, dcc, html, State
from dash import dcc, callback_context
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import dash_leaflet as dl
import dash_leaflet.express as dlx
import plotly_express as px
from controller.extract_xenocanto.xenocanto_utils import download_files
from loaded_data import df_metafiles_xenocanto


def create_layout(app, df_metafiles_xenocanto):
    # Page layouts
    return html.Div(
        [
            html.Div([utils.get_header(app)]),
            # page 1
            html.Div(
                [
                    html.H5(
                        ["Query Xenocanto"], style={
                            'marginLeft': '30px'}
                    ),
                    dcc.Input(value="cnt:mozambique", placeholder='query_text', id='XC_query', type='text', style={
                        'marginLeft': '30px'}),
                    html.Button('Query Xeno-Canto', id='query_button', n_clicks=0, style={
                        'marginLeft': '30px'}),

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
                    html.Button(
                        "Save Filtered Dataset in csv",
                        id="save_button"),
                    html.Button('Add additional categorical data', id='add_data', n_clicks=0, style={
                        'marginLeft': '30px'}),
                    html.Button(
                        "Download .wav files",
                        id="download_button", style={
                            'marginLeft': '30px'}),
                    dcc.Loading(id="loading-1", children=[
                        # elements of your app that should be displayed during the download process
                    ], type="default"),
                    dcc.Textarea(id='error-log', placeholder='Error Log',
                                 readOnly=True, style={'width': '100%'}),

                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Graph(id='descriptive_graph'),
                                    dcc.Graph(id='descriptive_graph2'),
                                ]),
                        ],
                        className="six columns",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        id='datatable-interactivity-container'),


                                    dcc.Graph(id='descriptive_graph3'),
                                ]),
                        ],
                        className="six columns",
                    ),
                    dcc.Store(id='metadata_storage', storage_type='session'),
                    html.Div([
                    ],
                        className="twelve columns")
                ])
        ]),
# callbacks


@app.callback(
    Output('datatable-interactivity', 'data'),
    Output('datatable-interactivity', 'columns'),
    Input('metadata_storage', 'data')
)
def update_metadata_table(data):
    metadata = data
    df_metafiles_xenocanto = pd.DataFrame.from_dict(data)
    columns = [{"name": i, "id": i, "deletable": True, "selectable": True}
               for i in df_metafiles_xenocanto.columns]
    return metadata, columns


@app.callback(Output('datatable-interactivity', 'style_data_conditional'),
              Input('datatable-interactivity', 'selected_columns'))
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(Output('datatable-interactivity-container', "children"),
              Input('datatable-interactivity', "derived_virtual_data"),
              Input('datatable-interactivity',
                    "derived_virtual_selected_rows"),
              Input("save_button", "n_clicks"))
def update_graphs(rows, derived_virtual_selected_rows, n):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df_metafiles_xenocanto if rows is None else pd.DataFrame(rows)
    birds_positions = dff.loc[:, ['gen', 'lat', 'lng']]
    birds_positions.columns = ['name', 'lat', 'lon']
    birds_positions = birds_positions.to_dict('records')
    # Creating a geojson from the input points
    geojson_birds = dlx.dicts_to_geojson(
        [{**bird, **dict(tooltip=bird['name'])} for bird in birds_positions])

    if n:
        dff.to_csv(
            '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv')

    return [dl.Map([dl.TileLayer(), dl.GeoJSON(data=geojson_birds, id="geojson", zoomToBounds=True, cluster=True)],
                   style={"width": "600px",
                          "height": "750px"}), html.H6('Number of .wav files: ' + str(dff.id.count()), style={'marginLeft': '30px'}),
            html.H6('Number of recorders: ' + str(dff['rec'].nunique()), style={'marginLeft': '30px'}), ]


@app.callback(Output("descriptive_graph", "figure"),
              Output("descriptive_graph2", "figure"),
              Output("descriptive_graph3", "figure"),
              [Input("datatable-interactivity", "derived_virtual_data")])
def generate_graphs(data):

    data = pd.DataFrame.from_dict(data)
    if data.shape != 0:
        data[['length_min', 'length_sec']
             ] = data['length'].str.split(':', expand=True)
        data['file_length'] = data['length_sec'].astype(
            int)+data['length_min'].astype(int)*60
        data['birds'] = 'Birds'

        sunburst = px.sunburst(data,
                               path=['birds', 'gen', 'sp'],
                               width=750,
                               height=650,
                               title="Genus & Species distribution amongst files <br><sup>Areas represent number of files, hover for info.</sup>"
                               )
        scatter = px.scatter(data, x='file_length', facet_col='q', labels={'file_length': 'file length (s)', 'y': 'ID of file'},
                             title='Length and quality of files', category_orders={"q": ["A", "B", "C", "D", "E"]})
        bar = px.bar(data, barmode='group', x='rec', labels={
                     'rec': 'Recorder Name', 'count': 'Number of recordings'})
    else:
        raise PreventUpdate

    # save figures in a dictionary for sending to the dcc.Store
    return scatter, sunburst, bar


@app.callback(Output("metadata_storage", "data"),
              Input("query_button", "n_clicks"), State('XC_query', 'value'))
def query_xeno_button(n, user_query):
    tables_path = '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables'
    if n:
        q = xeno.Query(user_query)
        metadata = q.retrieve_meta(verbose=True)
        df_metafiles = pd.DataFrame(metadata['recordings'])
        df_metafiles.to_csv(tables_path+'/metafiles_xenocanto.csv')
        print('Metadata saved')
        # # retrieve recordings
        # datapath_wav='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/project'
        # q.retrieve_recordings(multiprocess=True, nproc=10, attempts=10, outdir=datapath_wav)
    else:
        raise PreventUpdate

    return df_metafiles.to_dict('records')


# @app.callback(Output("download_button", "children"),
#               Input("download_button", "n_clicks"), State('XC_query', 'value'))
# def download_filtered_metadata_to_wav_directory(n, user_query):

#     wav_path = '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_dash/datasets/wav/xenocanto2/'
#     filtered_dataset_path = '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv'

#     if n:
#         q = xeno.Query(user_query)
#         cur_dir = os.getcwd()
#         os.chdir(wav_path)
#         q.filtered__multi_dl(input_csv=filtered_dataset_path,
#                              nproc=10, attempts=10, outdir=wav_path)
#         # q.retrieve_recordings(multiprocess=True, nproc=10, attempts=10, outdir=datapath_wav)
#         os.chdir(cur_dir)

#         return 'Downloaded files to wav/xenocanto/'
#     return 'Click to download'
# %%
@app.callback(Output("loading-1", "children"), [Input("download_button", "n_clicks")], [State("loading-1", "children")])
def download_files_and_update_loading_state(n_clicks, children):
    if n_clicks:
        df_recordings = pd.read_csv(
            '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv')
        try:
            download_files(df_recordings=df_recordings,root_dir='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/wav/TEST')
        except Exception as e:
            return children, e
    return children


@app.callback(Output('error-log', 'value'), [Input("loading-1", "children"), Input('download_button', 'n_clicks')])
def update_error_log(children, n_clicks):
    if n_clicks:
        df_recordings = pd.read_csv(
            '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv')
        try:
            download_files(df_recordings=df_recordings,root_dir='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/wav/TEST')
            return ''
        except Exception as e:
            return str(e)

# df_recordings = pd.read_csv('/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/filtered_df.csv')
# download_files(df_recordings=df_recordings,root_dir='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/wav/TEST')
