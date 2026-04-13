import dash_bootstrap_components as dbc
from dash import html


def card(title, content_id):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, style={"textAlign": "center"}, className="card-title"),
                html.Div(
                    id=content_id,
                    className="card-contents",
                ),
            ]
        ),
        className="shadow-sm mb-3",
    )
