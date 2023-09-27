import plotly_express as px
from sklearn.manifold import TSNE


def compute_tSNE_2d(
    df_ROI_final,
    features_options="basic",
    perplexity=15,
    color="species",
    early_exag=12,
    learning_rate=200,
    n_iter=1000,
    method="barnes_hut",
):
    # 2D tSNE-----------------------------------------------
    df = df_ROI_final.copy()
    df = df.reset_index()
    if features_options == "basic":
        features = ["min_t", "max_t", "min_f", "max_f"]
    if features_options == "shapes":
        features = [col for col in df if col.startswith("shp")]
    if features_options == "advanced":
        features = [col for col in df if col.startswith("shp")]
    df = df.dropna()

    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        early_exaggeration=early_exag,
        learning_rate=learning_rate,  # [10-1000]
        n_iter=n_iter,  # [250-5000]
        method=method,
    )

    projections = tsne.fit_transform(df[features])

    fig = px.scatter(
        projections, x=0, y=1, color=df[color], labels={"color": "species"}
    )
    return fig


def compute_tSNE_3d(
    df_ROI_final, features_options="basic", dimensions=2, color="species"
):
    # --------------3D tSNE----------------------------------
    df = df_ROI_final.copy()
    df = df.reset_index()
    if features_options == "basic":
        features = ["min_t", "max_t", "min_f", "max_f"]
    if features_options == "shapes":
        features = [col for col in df if col.startswith("shp")]
    if features_options == "advanced":
        features = [col for col in df if col.startswith("shp")]
    df = df.dropna()

    tsne = TSNE(n_components=3, random_state=0)
    projections = tsne.fit_transform(
        features,
    )

    fig2 = px.scatter_3d(
        projections, x=0, y=1, z=2, color=df.species, labels={"color": "species"}
    )
    fig2.update_traces(marker_size=8)

    return fig2
