from umap import UMAP
import plotly_express as px
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, minmax_scale
from plotly.express.colors import sample_colorscale

GENERIC_FEATURES = ['min_t', 'max_t', 'min_f', 'max_f',
                    'dt', 'df', 'centroid_f',
                    'centroid_t', 'duration_t', 'bandwidth_f', 'area_tf']

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

def plot_umap(df_ROI_final, features_options='basic', color='species', n_components=2, init='random', random_state=42,method='manual'):
    df = df_ROI_final.copy()
    df = df.reset_index(drop=True)

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
        features = SPECTRAL_FEATURES+TEMPORAL_FEATURES+GENERIC_FEATURES
    if method == 'auto':
        features = features.remove('df')
        features = features.remove('dt')

    #Info about Umaps + easy code example: https://umap-learn.readthedocs.io/en/latest/basic_usage.html
    
    scaled_data = StandardScaler().fit_transform(df[features])
    
    umap_2d = UMAP(n_components=n_components,
                   init=init, random_state=random_state)

    proj_2d = umap_2d.fit_transform(scaled_data)

    colors_ = np.linspace(0, 1, len(df[color].unique()))
    discrete_colors = sample_colorscale('Rainbow', minmax_scale(colors_))

    fig_2d = px.scatter(proj_2d, x=0, y=1, width=1000, height=800, color=df[color], color_discrete_sequence=discrete_colors,
                        labels={'color': str(color)})

    return fig_2d
