import os
from utils import utils
from app import app
import xenopy as xeno
import pandas as pd
from loaded_data import datasets_path

from dash import dcc, html, State
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly_express as px
from controller.extract_xenocanto.xenocanto_utils import download_files

table_visible_columns = ['id', 'rec', 'loc', 'gen', 'sp', 'lat',
                         'lng', 'alt', 'type', 'q', 'length', 'bird-seen', 'file', 'en']

# Layout--------------------------------------------------------------------------------------------------------------------


def create_layout(app, df_metafiles_xenocanto):
    # Page layouts
    return html.Div([
        html.Div([utils.get_header(app)]),
        # page 1
        html.Div(
            [
                html.H5(
                    ["Create / Select Project"], style={
                        'marginLeft': '30px'}
                ),
                dcc.Input(value="my_project_name", placeholder='projectname', id='project_name', type='text', style={
                    'marginLeft': '30px'}),

                html.Button('Create project directory', title='Creates a folder in : ../datasets/projectname/', id='new_project_button', n_clicks=0, style={
                    'marginLeft': '30px'}),

                dcc.Dropdown(id='project_selector', placeholder='Select project...', options=[], value='',
                             style={'width': '40%', 'marginLeft': '15px'}),

                html.H5(
                    ["Query Xenocanto"], style={
                        'marginLeft': '30px'}
                ),
                html.Section(
                    [
                        'Send query to xenocanto and retrieve recording informations (metadata).', html.Br(
                        )
                    ],
                    style={'width': '60%',
                           'marginLeft': '30px',
                           'marginBottom': '5px'}
                ),
                html.A(
                    html.Button(
                        "Query instructions",
                        id="query_instructions",
                        style={"margin-left": "30px", 'marginBottom': '30px'},
                    ),
                    href="https://xeno-canto.org/help/search",
                    title="https://xeno-canto.org/help/search",
                    target="_blank"
                ),

                html.Br(),

                dcc.Input(value="cnt:mozambique", placeholder='query_text', id='XC_query', type='text', style={
                    'marginLeft': '30px'}),

                html.Button('Query Xeno-Canto', id='query_button', title='Sends your query to Xenocanto.org and updates metadata.', n_clicks=0, style={
                    'marginLeft': '30px'}),

                dcc.Loading(id="loading-1", children=[
                    # elements of your app that should be displayed during the download process
                ], type="default"),

                dcc.Textarea(id='query_log', placeholder='Query Log',
                             readOnly=True, style={'width': '90%',
                                                   'marginLeft': '30px',
                                                   'marginRight': '30px'
                                                   }),

                html.H5(
                    ["Filter metadata"], style={
                        'marginLeft': '30px'}
                ),

                html.Section(
                    [
                        'In this step we filter the query results to the needs of our project.', html.Br(), html.Br(),
                        "Dataset can be filtered by entering text in the second row of the datatable. Operators such as '>' , '<' , '=', '!=' can be used under the column names for conditional filtering.", html.Br(), html.Br(),
                        "Usage examples:", html.Br(),
                        "'<C' in the q (quality) column would remove all C, D and E quality recordings.", html.Br(
                        ),
                        "'!=John Noisy' in the rec column would remove all recordings made by John Noisy.", html.Br(),
                        "'Maputo' in the loc column will keep all locations containing the word Maputo.", html.Br(), html.Br(),
                        "CAUTION : You can add/remove conditions as much as you want, but removing line using X button cannot be undone.", html.Br(),
                        "When you are satisfied with study data, save filtered data to .csv. Download button will retrieve sounds on Xenocanto, then download and organize them in project_folder.This step might take a while, double-check your filtered dataset !"
                    ],
                    style={'width': '100%',
                           'marginLeft': '30px',
                           'marginBottom': '20px'}
                ),

                utils.get_interactive_datatable(df_metafiles_xenocanto),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    id='recordings_leaflet_map'),
                                dcc.Graph(
                                    id='species_classification_sunburst_graph'),
                                dcc.Graph(
                                    id='wave_length_and_quality_graph'),
                                dcc.Graph(id='recorder_bar_graph'),
                            ]),
                    ],
                    className="twelve columns",
                ),
                dcc.Store(id='metadata_storage', storage_type='memory'),
                html.Button(
                    "Save Filtered Dataset in csv", title='Saves your current table in /../datasets/tables/projectname/filtered_df.csv',
                    id="save_button"),
                html.Button(
                    "Download .wav files", title='Downloads all recordings from filtered_df.csv, output folder structure is labeled as ..datasets/wav/projectname/genus_species/id.wav',
                    id="download_button", style={
                        'marginLeft': '30px'}),
                dcc.Loading(id="loading-2", children=[], type="default"),
                dcc.Textarea(id='error-log2', placeholder='Error Log',
                             readOnly=True, style={'width': '100%'}),
                html.Div([
                ],
                    className="twelve columns")
            ])
    ]),

# callbacks


def get_project_options():
    options = [{'label': project, 'value': os.path.join(datasets_path, project)}
               for project in os.listdir(datasets_path) if os.path.isdir(os.path.join(datasets_path, project))]
    return options


@ app.callback(
    Output('project_selector', 'options'),
    [Input('new_project_button', 'n_clicks')],
    [State('project_name', 'value')])
def create_project_directory(n_clicks, project_name):
    if n_clicks:
        path = f"/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/{project_name}/"
        path2 = f"/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/{project_name}/tables/"
        path3 = f"/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/{project_name}/wav/"
        os.makedirs(path, exist_ok=True)
        os.makedirs(path2, exist_ok=True)
        os.makedirs(path3, exist_ok=True)
    # Add the project to the options list
    options = [{'label': project_name, 'value': project_name}]
    options = get_project_options()

    return options


@ app.callback(Output("metadata_storage", "data"), Output("loading-1", "children"), Output("query_log", "value"),
               Input("query_button", "n_clicks"), State('XC_query', 'value'), [State("loading-1", "children"), Input('project_selector', 'value')])
def query_xeno_button(n, user_query, children, projectdir_path):
    if projectdir_path == '':
        raise PreventUpdate
    elif projectdir_path != '':
        csv_path = os.path.join(
            projectdir_path, 'tables/metadata_filtered.csv')
        try:
            df_metafiles = pd.read_csv(csv_path)
            log = f'reading metadata from {projectdir_path}'
            return df_metafiles.to_dict('records'), children, log
        except:
            log = f'New project: {projectdir_path}'

    if n:
        q = xeno.Query(user_query)
        try:
            metadata = q.retrieve_meta(verbose=True)
        except Exception as e:
            return children, e

        if metadata != []:
            df_metafiles = pd.DataFrame(metadata['recordings'])
            df_metafiles.to_csv(os.path.join(
                projectdir_path, 'tables/metadata_raw_all_columns.csv'))

            df_metafiles = df_metafiles.loc[:, table_visible_columns]
            df_metafiles.to_csv(os.path.join(
                projectdir_path, 'tables/metadata_raw.csv'))
            print('Metadata saved')
            log = f'Successfully queried Xenocanto, there are {len(df_metafiles)} recordings'
        else:
            log = '/!!\ :  Invalid / empty query.'
            return _, _, log
    else:
        raise PreventUpdate

    return df_metafiles.to_dict('records'), children, log


@ app.callback(
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


@ app.callback(Output('datatable-interactivity', 'style_data_conditional'),
               Input('datatable-interactivity', 'selected_columns'))
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@ app.callback(Output('recordings_leaflet_map', "children"),
               Input('datatable-interactivity', "derived_virtual_data"),
               Input('datatable-interactivity',
                     "derived_virtual_selected_rows"),
               Input("save_button", "n_clicks"),
               State("project_selector", "value"),
               )
def update_graphs(rows, derived_virtual_selected_rows, n, projectdir_path):
    if projectdir_path == '':
        raise PreventUpdate

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    df_metafiles_xenocanto = pd.read_csv(
        os.path.join(
            projectdir_path, 'tables/metadata_raw.csv')
    )
    df_metafiles_all_col = pd.read_csv(
        os.path.join(
            projectdir_path, 'tables/metadata_raw_all_columns.csv')
    )

    dff = df_metafiles_xenocanto if rows is None else pd.DataFrame(rows)
    dff2 = df_metafiles_all_col if rows is None else pd.DataFrame(rows)

    if n:  # save filtered data on click
        dff.to_csv(
            os.path.join(
                projectdir_path, 'tables/metadata_filtered.csv')
        )
        dff2.to_csv(
            os.path.join(
                projectdir_path, 'tables/metadata_filtered_all_columns.csv')
        )

    return utils.get_leaflet_map(dff, heigth=500)


@ app.callback(Output("wave_length_and_quality_graph", "figure"),
               Output("species_classification_sunburst_graph", "figure"),
               Output("recorder_bar_graph", "figure"),
               [Input("datatable-interactivity", "derived_virtual_data")])
def generate_graphs(data):

    data = pd.DataFrame.from_dict(data)
    if data.shape != 0:
        try:
            data[['length_min', 'length_sec']
                 ] = data['length'].str.split(':', expand=True)
            data['file_length'] = data['length_sec'].astype(
                int)+data['length_min'].astype(int)*60
            data['birds'] = 'Birds'
        except:
            raise PreventUpdate

        sunburst = px.sunburst(data,
                               path=['birds', 'gen', 'sp'],
                               height=800,
                               title="Genus & Species distribution amongst files <br><sup>Areas represent number of files, hover for info.</sup>"
                               )
        scatter = px.scatter(data, x='file_length', facet_col='q', labels={'file_length': 'file length (s)', 'y': 'ID of file'},
                             title='Length and quality of files', category_orders={"q": ["A", "B", "C", "D", "E"]})
        bar = px.bar(data, barmode='group', x='rec', labels={
            'rec': 'Recorder Name', 'count': 'Number of recordings'})
    else:
        raise PreventUpdate

    return scatter, sunburst, bar


prev_n_clicks = 0


@ app.callback(
    Output("loading-2", "children"),
    [Input("download_button", "n_clicks")],
    [State("loading-2", "children"), State('project_selector', 'value')
     ])
def download_files_and_update_loading_state(n_clicks, children, projectdir_path):
    global prev_n_clicks
    if n_clicks:
        if n_clicks > prev_n_clicks:
            prev_n_clicks = n_clicks
            df_recordings = pd.read_csv(os.path.join(
                projectdir_path, 'tables/metadata_filtered.csv'))
            try:
                download_files(df_recordings=df_recordings,
                               root_dir=os.path.join(
                                   projectdir_path, 'wav'))
            except Exception as e:
                print(e)
        return children

# Graveyard:

# @app.callback(
#     Output("metadata_storage", "data"),
#     [Input("project_selector", "value")]
# )
# def update_metadata_storage(projectdir_path):
#     if projectdir_path == '':
#         raise PreventUpdate
#     else:
#         csv_path = os.path.join(
#             projectdir_path, 'tables/metadata_filtered.csv')
#         df = pd.read_csv(csv_path)
#         return df.to_dict('records')


# @ app.callback(
#     Output("loading-2", "children"),
#     [Input("download_button", "n_clicks")],
#     [State("loading-2", "children"), State('project_selector', 'value')
#      ])
# def download_files_and_update_loading_state(n_clicks, children, projectdir_path):
#     if n_clicks:
#         df_recordings = pd.read_csv(os.path.join(
#             projectdir_path, 'tables/metadata_filtered.csv'))
#         try:
#             download_files(df_recordings=df_recordings,
#                            root_dir=os.path.join(
#                                projectdir_path, 'wav'))
#         except Exception as e:
#             return children, e
#     return children


# @ app.callback(Output('error-log2', 'value'), [Input("loading-2", "children"), Input('download_button', 'n_clicks'), State('project_selector', 'value')])
# def update_error_log(children, n_clicks, projectdir_path):

#     if n_clicks:
#         df_recordings = pd.read_csv(os.path.join(
#             projectdir_path, 'tables/metadata_filtered.csv'))
#         try:
#             download_files(df_recordings=df_recordings,
#                            root_dir=os.path.join(
#                                projectdir_path, 'wav'))
#             return ''
#         except Exception as e:
#             return str(e)
