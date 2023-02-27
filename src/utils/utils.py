from dash import html
from dash import dcc
from dash import dash_table
import dash_leaflet as dl
import dash_leaflet.express as dlx

columns_visible_to_user = ['id', 'rec', 'loc', 'gen', 'sp',
                           'lat', 'lng', 'alt', 'type', 'q', 'length', 'bird-seen', 'en']


def Header(app):
    return html.Div([get_header(app), get_menu(), html.Br([])])


def get_header(app):
    header = html.Div(
        [
            html.Div(
                [

                    html.A(
                        html.Button(
                            "Paul Carvaillo",
                            id="learn-more-button",
                            style={"margin-left": "-10px"},
                        ),
                        href="https://www.linkedin.com/in/paul-c-65a72290/",

                    ),
                    html.A(
                        html.Button(
                            "Glenn le Floch",
                            id="learn-more-button",
                            style={"margin-left": "-10px"},
                        ),
                        href="https://www.linkedin.com/in/glennlefloch/?originalSubdomain=fr",

                    ),
                    html.A(
                        html.Button("Source Code", id="learn-more-button"),
                        href="https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-financial-report",
                    ),
                ],
                className="column",
            ),
            html.Div(
                [
                    # Row 3
                    html.Div(
                        [
                            html.Div([get_menu()]),
                            html.Div(
                                [
                                    html.H4(""),
                                ],
                                className="product",
                            ),
                        ],
                        className="row",
                    ), ])

        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link(
                "Clean and inspect data",
                href="/pages/info_about_data",
                className="tab first",
            ),
            dcc.Link(
                "Detect Regions of interest",
                href="/pages/ROI",
                className="tab",
            ),
            dcc.Link(
                "Analyse: Feature selection",
                href="/pages/features",
                className="tab",
            ),
            dcc.Link(
                "PCA",
                href="/pages/PCA",
                className="tab",
            ),
            dcc.Link(
                "tSNE",
                href="/pages/tSNE",
                className="tab",
            ),
            dcc.Link(
                "UMAPS",
                href="/pages/UMAPs",
                className="tablast",
            ),
        ],
        className="all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    table = [html.Tr([html.Th(col) for col in df.columns])] + table
    return table


def get_interactive_datatable(df_metafiles_xenocanto):
    return dash_table.DataTable(id='datatable-interactivity',
                                columns=[
                                    {"name": i, "id": i, "deletable": False, "selectable": False} for i in columns_visible_to_user
                                ],
                                data=df_metafiles_xenocanto.to_dict(
                                    'records'),
                                editable=True,
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                column_selectable=False,
                                row_selectable="multi",
                                row_deletable=True,
                                selected_columns=[],
                                selected_rows=[],
                                page_action="native",
                                page_current=0,
                                page_size=10
                                )


def get_leaflet_map(dff, heigth=750):

    # Creating a geojson from the input points
    birds_positions = dff.loc[:, ['gen', 'lat', 'lng']]
    birds_positions.columns = ['name', 'lat', 'lon']
    birds_positions = birds_positions.to_dict('records')
    geojson_birds = dlx.dicts_to_geojson(
        [{**bird, **dict(tooltip=bird['name'])} for bird in birds_positions])

    return [
        html.H6('Current number of .wav files in dataset: ' + str(dff.id.count()),
                style={'marginLeft': '30px'}),
        dl.Map([dl.TileLayer(),
                dl.GeoJSON(data=geojson_birds, id="geojson", zoomToBounds=True, cluster=True)],
               style={"width": '100%',
                      "height": f"{heigth}px"}),

    ]
