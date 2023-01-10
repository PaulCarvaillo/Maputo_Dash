import matplotlib.pyplot as plt
from utils import utils
from app import app
import pandas as pd
from dash import dash_table, dcc, html
from dash import dcc, callback_context
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.tools as tls
from plotly import optional_imports
from controller.ROI.ROI import ROI_and_centroid, find_ROIs_soundfile, compute_Sxx_dB_nonoise_smooth
import plotly_express as px
import plotly.graph_objects as go
import base64
from pathlib import Path
from loaded_data import df_annot_final

import matplotlib
matplotlib.use('Agg')

centroids_annot = df_annot_final
df_data = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_datapaths.csv')


def create_layout(app, df_metafiles_xenocanto):
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
                                    # FILEPATH/SPECIES/FREQUENCY SELECTOR PARAMETERS:
                                    html.H5(
                                        ["Find .wav to analyze"], style={
                                            'marginLeft': '30px'}
                                    ),

                                    html.H6(
                                        ["Select gen:"], className="subtitle padded"
                                    ),
                                    dcc.Dropdown(df_data.gen.unique(
                                    ), id='gen_dropdown', placeholder='GEN SELECTION', searchable=True),
                                    html.H6(
                                        ["Select species:"], className="subtitle padded"
                                    ),
                                    dcc.Dropdown(df_data.species.unique(
                                    ), id='species_dropdown', placeholder='SPECIES SELECTION'),
                                    html.H6(
                                        ["Select file:"], className="subtitle padded"
                                    ),
                                    dcc.Dropdown(df_data.fullfilename.unique(
                                    ), id='wav_dropdown', value=[], placeholder='.wav SELECTION'),

                                    dcc.Graph(id='spectrogram'),
                                    html.Audio(id='audio', controls=True)

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
                                        ["ROI detection params"], style={
                                            'marginLeft': '30px'}
                                    ),
                                    html.H6(
                                        ["Select frequency band:"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.RangeSlider(0, 20000, marks=None, value=[
                                                    0, 20000], id='frequency_selection', tooltip={"placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Bin mode :"], style={
                                            'marginLeft': '30px'}, className="subtitle padded"
                                    ),
                                    dcc.Dropdown(
                                        ['relative', 'absolute'], value='relative', id='mode_bin', style={
                                            'marginLeft': '10px'}),
                                    html.H6(
                                        ["Smoothing coefficient (0.5 -- 3):"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(0.5, 3, marks=None,
                                               value=0.5, id='smoothing', tooltip={"placement": "bottom", "always_visible": True}),

                                    html.H6(
                                        ["Mask threshold: Values above certain dB selected"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),

                                    dcc.Slider(0, 30, marks=None, id="param1", value=18, tooltip={
                                               "placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Relative cluster threshold: '%' difference to be considered linked to pixel"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(0, 1, id="param2", value=0.9, tooltip={
                                               "placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Max frequency of ROI (dashed line)"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(0, 20000, id="roi_max_f", value=20000, tooltip={
                                               "placement": "bottom", "always_visible": True}),
                                    html.H6(
                                        ["Min frequency of ROI (blue line)"], className="subtitle padded", style={
                                            'marginLeft': '30px'}
                                    ),
                                    dcc.Slider(0, 20000, id="roi_min_f", value=100, tooltip={
                                               "placement": "bottom", "always_visible": True}),

                                    html.Button('SAVE PARAMETERS', id='save_params', n_clicks=0, style={
                                        'marginLeft': '30px'}),
                                    html.Br(),
                                    html.Button('BATCH ANALYSE', id='plot_ROI', n_clicks=0, style={
                                        'marginLeft': '30px'}),
                                    html.Button('UPDATE ANNOTATIONS', id='read_annot', n_clicks=0, style={
                                        'marginLeft': '30px'}),
                                ]),
                        ],
                        className="three columns",
                    ),
                    dcc.Store(id='datastore', storage_type='local'),
                    dcc.Store(id='datastore_spectro', storage_type='memory'),
                    dcc.Store(id='datastore_spectro_fn',
                              storage_type='local'),
                    dcc.Store(id='datastore_spectro_tn',
                              storage_type='local'),
                    dcc.Store(id='datastore_spectro_ext',
                              storage_type='local'),
                    dcc.Store(id='datastore_ROI_centroid',
                              storage_type='memory'),
                    dcc.Store(id='datastore_annot',
                              storage_type='memory'),
                    html.Div([
                    ],
                        className="twelve columns")
                ])
        ]),
# callbacks
# callbacks


@ app.callback(Output('datastore_spectro', 'data'),
               Output('datastore_spectro_fn', 'data'),
               Output('datastore_spectro_tn', 'data'),
               Output('datastore_spectro_ext', 'data'),

               [Input('wav_dropdown', 'value'),
                Input('smoothing', 'value'),
                Input('frequency_selection', 'value')])
def update_spectro_data(wav_dropdown, smoothing, frequency_selection):
    if isinstance(wav_dropdown, str) == False:
        raise PreventUpdate
    else:
        fmin = frequency_selection[0]
        fmax = frequency_selection[1]
        Sxx, tn, fn, ext = compute_Sxx_dB_nonoise_smooth(
            path=wav_dropdown, fmin=fmin, fmax=fmax, smoothing=smoothing)
        df_Sxx = pd.DataFrame(Sxx).to_dict('records')
        df_fn = pd.DataFrame(fn, columns=['fn']).to_dict('records')
        df_tn = pd.DataFrame(tn, columns=['tn']).to_dict('records')
        df_ext = pd.DataFrame([ext]).to_dict('records')

    return df_Sxx, df_fn, df_tn, df_ext


@ app.callback(Output('datastore_annot', 'data'), Input('wav_dropdown', 'value'))
def get_annot__data(wav_dropdown):
    centroids_annot_dff = centroids_annot.copy()
    if isinstance(wav_dropdown, str):
        id = Path(wav_dropdown).parts[-1][:-4]
        print(id)
        centroids_annot_dff = centroids_annot[centroids_annot['sound_id'].astype(
            str) == id]
        print(centroids_annot_dff.shape)
    else:
        PreventUpdate
    return centroids_annot_dff.to_dict('records')


@ app.callback(Output('datastore', 'data'), [Input('gen_dropdown', 'value')])
def filter_data_by_gen(gen_dropdown):
    data = df_data[df_data['gen'] == gen_dropdown]
    return data.to_dict('records')


@ app.callback(Output('species_dropdown', 'options'), Output('species_dropdown', 'value'), Input('datastore', 'data'))
def species_dropdown_update(data):
    if data:
        dff = pd.DataFrame.from_dict(data)
        options = dff.species.unique()
        values = dff.fullfilename
    else:
        values = []
        options = []
    return options, values


@ app.callback(Output('wav_dropdown', 'options'), Output('wav_dropdown', 'value'), [Input('datastore', 'data'), Input('species_dropdown', 'value')])
def wav_dropdown_update(data, species_dropdown):
    if data:
        dff = pd.DataFrame.from_dict(data)
        dff = dff[dff['species'] == species_dropdown]
        options = dff.fullfilename.unique()
        values = dff.fullfilename
    else:
        values = []
        options = []
    return options, values


@ app.callback(Output('datastore_ROI_centroid', 'data'),

               [Input('datastore_spectro', 'data'),
               Input('datastore_spectro_fn', 'data'),
               Input('datastore_spectro_tn', 'data'),
               Input('datastore_spectro_ext', 'data'),


               Input('param1', 'value'),
               Input('param2', 'value'),
               Input('mode_bin', 'value')])
def compute_and_update_ROI_datastore(spectro, fn, tn, ext, param1, param2, mode_bin='relative'):
    if spectro:
        Sxxt = pd.DataFrame.from_dict(spectro).to_numpy()
        fn = pd.DataFrame.from_dict(fn)['fn'].to_numpy()
        tn = pd.DataFrame.from_dict(tn)['tn'].to_numpy()
        ext = list(pd.DataFrame.from_dict(ext).to_numpy())

        _, _, centroid = ROI_and_centroid(
            Sxx_db_noNoise_smooth=Sxxt, tn=tn, fn=fn, ext=ext, mode_bin=mode_bin, param1=param1, param2=param2, display=False)
        centroid_json = centroid.to_dict('records')
    else:
        raise PreventUpdate

    return centroid_json


@ app.callback([Output('spectrogram', 'figure')],

               [Input('datastore_spectro', 'data'),
               Input('datastore_spectro_fn', 'data'),
               Input('datastore_spectro_tn', 'data'),
               Input('datastore_spectro_ext', 'data'),
               Input('datastore_ROI_centroid', 'data'),
               Input('datastore_annot', 'data'),

               Input('roi_max_f', 'value'),
               Input('roi_min_f', 'value')])
def plot_spectrogram_and_ROI_and_annot(spectro, fn, tn, ext, centroid, annot, roi_max_f, roi_min_f):
    if spectro:
        Sxxt = pd.DataFrame.from_dict(spectro).to_numpy()
        fn = pd.DataFrame.from_dict(fn)['fn'].to_numpy()
        tn = pd.DataFrame.from_dict(tn)['tn'].to_numpy()
        ext = list(pd.DataFrame.from_dict(ext).to_numpy())
        centroids_annot = pd.DataFrame.from_dict(annot).reset_index(drop=True)

        fig_kwargs = {'vmax': Sxxt.max(),
                      'vmin': -20,
                      'figsize': (4, 13),
                      'xlabel': 'Time [sec]',
                      'ylabel': 'Frequency [Hz]',
                      'cmap': 'viridis'
                      }
        fig = px.imshow(Sxxt, color_continuous_scale='viridis', origin='lower',
                        labels=dict(x="Time (sec)",
                                    y="Frequency (Hz)", color="Level (dB"),
                        x=tn,
                        y=fn,
                        aspect='auto')

        for i in range(0, len(centroids_annot), 1):
            fig.add_shape(type='rect', x0=centroids_annot.min_t[i], x1=centroids_annot.max_t[i], y0=centroids_annot.min_f[i], y1=centroids_annot.max_f[i], line=dict(
                color="Red",
                width=1,
            ),)

        if centroid:
            centroid2 = pd.DataFrame.from_dict(centroid)
            filtered_centroids = centroid2.copy()
            filtered_centroids = filtered_centroids[filtered_centroids['min_f'] < roi_max_f]
            filtered_centroids = filtered_centroids[filtered_centroids['max_f'] > roi_min_f]
            filtered_centroids = filtered_centroids.reset_index(drop=True)

            for i in range(0, len(filtered_centroids), 1):
                fig.add_shape(type='rect', x0=filtered_centroids.min_t[i], x1=filtered_centroids.max_t[i], y0=filtered_centroids.min_f[i], y1=filtered_centroids.max_f[i], line=dict(
                    color="Yellow",
                    width=1,
                ),)

                fig.add_shape(type="line",
                              x0=1, y0=roi_min_f, x1=filtered_centroids.max_t.max(), y1=roi_min_f,
                              line=dict(
                                  color="Red",
                                  width=3,
                                  dash="dashdot",
                              ))
                fig.add_shape(type="line",
                              x0=1, y0=roi_max_f, x1=filtered_centroids.max_t.max(), y1=roi_max_f,
                              line=dict(
                                  color="LightSeaGreen",
                                  width=3,
                                  dash="dashdot",
                              ))

    else:
        raise PreventUpdate

    return [go.Figure(data=fig)]


# @app.callback([Output('audio', 'children')],
#               [Input('wav_dropdown', 'value')])
# def load_audio(wav_dropdown):
#     if wav_dropdown == []:
#         raise PreventUpdate
#     elif wav_dropdown:
#         # Encode the local sound file.
#         sound_filename = wav_dropdown
#         encoded_sound = base64.b64encode(open(sound_filename, 'rb').read())
#         url = 'data:audio/mpeg;base64,{}'.format(encoded_sound.decode())
#         # url = 'file:///'+wav_dropdown
#     return src=f"{sound_filename}",type="audio/wav"
