from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from pages.info_about_data.layout import create_layout
from pages.study_of_ROI.layout import create_layout as cl2
from pages.PCA.layout import create_layout as cl3
from pages.UMAPs.layout import create_layout as cl4
from pages.tSNE.layout import create_layout as cl5
from pages.features.layout import create_layout as cl6
from loaded_data import df_metafiles_xenocanto, df_ROI_final

# --------------------Layout of first page, links to different pages---
df_metafiles_xenocanto_reduced = df_metafiles_xenocanto.loc[:, [
    'id', 'rec', 'loc', 'gen', 'sp', 'lat', 'lng', 'alt', 'type', 'q', 'length', 'bird-seen', 'file','en']]

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
# -------------------Callback used to change page on click ------------

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app1':
        return create_layout(app, df_metafiles_xenocanto=df_metafiles_xenocanto_reduced)
    elif pathname == '/pages/info_about_data':
        return create_layout(app, df_metafiles_xenocanto=df_metafiles_xenocanto_reduced)
    elif pathname == '/pages/ROI':
        return cl2(app, df_metafiles_xenocanto=df_metafiles_xenocanto_reduced)
    elif pathname == '/pages/PCA':
        return cl3(app, df_ROI_final=df_ROI_final)
    elif pathname == '/pages/UMAPs':
        return cl4(app, df_ROI_final=df_ROI_final)
    elif pathname == '/pages/tSNE':
        return cl5(app, df_ROI_final=df_ROI_final)
    elif pathname == '/pages/features':
        return cl6(app, df_ROI_final=df_ROI_final)
    else:
        return create_layout(app, df_metafiles_xenocanto=df_metafiles_xenocanto_reduced)


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
