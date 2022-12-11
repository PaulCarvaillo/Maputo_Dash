from app import app
import numpy as np
import pandas as pd
import plotly_express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from plotly.express.colors import sample_colorscale
from sklearn.preprocessing import minmax_scale


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


def compute_PCA(df_ROI_final, features_options='basic', dimensions=2, color="species"):

    df = df_ROI_final.copy()
    df = df.reset_index()

    if features_options == 'basic':
        features = GENERIC_FEATURES
    if features_options == 'shapes':
        features = SHAPE_FEATURES
    if features_options == 'shapes+basic':
        features = SHAPE_FEATURES+GENERIC_FEATURES
    if features_options == 'spectral':
        features = SPECTRAL_FEATURES
    if features_options == 'spectral+basic':
        features = SPECTRAL_FEATURES+GENERIC_FEATURES
    if features_options == 'temporal':
        features = TEMPORAL_FEATURES
    if features_options == 'temporal+basic':
        features = TEMPORAL_FEATURES+GENERIC_FEATURES
    if features_options == 'all':
        features = GENERIC_FEATURES+SPECTRAL_FEATURES+TEMPORAL_FEATURES

    df = df.dropna(how='all')
    # Scale Features
    data_scaled = pd.DataFrame(preprocessing.scale(
        df[features]), columns=df[features].columns)
    # PCA
    pca = PCA(n_components=dimensions)
    components = pca.fit_transform(data_scaled)
    total_var = pca.explained_variance_ratio_.sum() * 100
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Dump components relations with features:
    weights = (pd.DataFrame(pca.components_,
               columns=data_scaled.columns, index=[f'PC-{i+1}' for i in range(dimensions)]))
    weights = weights.reset_index()

    # figures-----------------------
    labels = {
        str(i): f"PC {i+1} ({var1:.1f}%) - EV = {var2:.1f}" for i, (var1, var2) in enumerate(zip(pca.explained_variance_ratio_ * 100, pca.explained_variance_))
    }

    colors_ = np.linspace(0, 1, len(df[color].unique()))
    discrete_colors = sample_colorscale('Rainbow', minmax_scale(colors_))

    fig = px.scatter_matrix(
        components,
        height=1000,
        labels=labels,
        dimensions=range(dimensions),
        color=df[color].astype('category'),
        color_discrete_sequence=discrete_colors,
        title=f'Principal component analysis of ROIs ---Total Explained Variance: {total_var:.2f}%',
    )
    fig.update_traces(diagonal_visible=False)

    # stacked plots of weigths-----------------------
    fig2 = make_subplots(cols=1, rows=dimensions, subplot_titles=(
        [f'PC-{i+1}: abs weight of features' for i in range(dimensions)]))
    for i in range(dimensions):
        fig2.append_trace(go.Bar(
            x=features, y=weights[features].loc[i, :], text=features, textposition="inside"), col=1, row=i+1)
        fig2.update_xaxes({'categoryorder': 'total descending'})
        # fig2.update_xaxes(visible=False)

    fig2.update_layout(barmode='stack', height=600,
                       width=1300, showlegend=False)

    # LOADINGS GRAPH
    loadings_graph = go.Figure()
    loadings_graph.add_shape(type='circle', x0=-1, x1=1, y0=-1, y1=1)

    for i, feature in enumerate(features):
        loadings_graph.add_shape(
            type='line',
            x0=0, y0=0,
            x1=loadings[i, 0],
            y1=loadings[i, 1]
        )
        loadings_graph.add_annotation(
            x=loadings[i, 0],
            y=loadings[i, 1],
            ax=0, ay=0,
            xanchor="center",
            yanchor="bottom",
            text=feature,
        )
    loadings_graph.update_layout(yaxis_range=[-1, 1])
    loadings_graph.update_layout(xaxis_range=[-1, 1], height=400, width=400,
                                 title='PCA Correlation circle', xaxis_title='PC1', yaxis_title='PC2')

    return fig, fig2, loadings_graph
