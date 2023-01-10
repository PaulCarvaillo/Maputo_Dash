from dash import html
from dash import dcc
from dash import dash_table


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
                            html.Div(
                                [
                                    html.H4("CDAC app"),
                                ],
                                className="product",
                            ),
                            html.Div([get_menu()]),
                            html.Br([]),
                        ],
                        className="row",
                    ),])

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
                className="tab",
            ),
        ],
        className="column",
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


def interactive_datatable(df):
    return dash_table.DataTable(id='datatable-interactivity',
                                columns=[
                                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                                ],
                                data=df.to_dict(
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
                                page_size=5,
                                ),
