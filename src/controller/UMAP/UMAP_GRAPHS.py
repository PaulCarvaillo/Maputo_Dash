import numpy as np
import pandas as pd
import plotly_express as px
from plotly.express.colors import sample_colorscale
from sklearn.preprocessing import StandardScaler, minmax_scale
from umap import UMAP

from assets.features import (
    GENERIC_FEATURES,
    SHAPE_FEATURES,
    SPECTRAL_FEATURES,
    TEMPORAL_FEATURES,
)


def plot_umap(
    df_ROI_final,
    features_options="basic",
    color="species",
    n_components=2,
    init="random",
    random_state=42,
    method="manual",
):
    df = df_ROI_final.copy()
    df = df.reset_index(drop=True)

    if features_options == "basic":
        features = GENERIC_FEATURES
    if features_options == "shapes":
        features = SHAPE_FEATURES
    if features_options == "shapes+basic":
        features = SHAPE_FEATURES + GENERIC_FEATURES
    if features_options == "spectral":
        features = SPECTRAL_FEATURES
    if features_options == "spectral+basic":
        features = SPECTRAL_FEATURES + GENERIC_FEATURES
    if features_options == "temporal":
        features = TEMPORAL_FEATURES
    if features_options == "temporal+basic":
        features = TEMPORAL_FEATURES + GENERIC_FEATURES
    if features_options == "all":
        features = SPECTRAL_FEATURES + TEMPORAL_FEATURES + GENERIC_FEATURES
    if method == "auto":
        features = features.remove("df")
        features = features.remove("dt")

    # Info about Umaps + easy code example: https://umap-learn.readthedocs.io/en/latest/basic_usage.html

    scaled_data = StandardScaler().fit_transform(df[features])

    umap_2d = UMAP(n_components=n_components, init=init, random_state=random_state)

    proj_2d = umap_2d.fit_transform(scaled_data)

    colors_ = np.linspace(0, 1, len(df[color].unique()))

    discrete_colors = sample_colorscale("Rainbow", minmax_scale(colors_))

    df_proj_2d = pd.DataFrame(proj_2d)
    proj_2d_with_categories = pd.concat(
        [
            df_proj_2d,
            df[["order", "family", "genus", "species", "sound_id", "biotope"]],
        ],
        axis=1,
    )
    fig_2d = px.scatter(
        proj_2d_with_categories,
        x=0,
        y=1,
        width=1000,
        height=800,
        color=df[color].astype("category"),
        color_discrete_sequence=discrete_colors,
        custom_data=["order", "family", "genus", "species", "sound_id", "biotope"],
        labels={"color": str(color)},
    )
    fig_2d.update_traces(
        hovertemplate="<br>".join(
            [
                "UMAP_X: %{x}",
                "UMAP_Y: %{y}",
                "Order: %{customdata[0]}",
                "Family: %{customdata[1]}",
                "Genus: %{customdata[2]}",
                "Species: %{customdata[3]}",
                "Sound_ID: %{customdata[4]}",
                "Biotope: %{customdata[5]}",
            ]
        )
    )

    return fig_2d
