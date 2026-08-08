import dash_bootstrap_components as dbc
from dash import html


def card(title, content_id, tint=0):
    """
    Parameters
    ----------
    title : str
        Card heading.
    content_id : str
        id assigned to the card's content Div, for callbacks to target.
    tint : int, optional
        Index into the pastel palette (see assets/styles.css `.card-tint-*`)
        used for this card's background, so a row of cards can rotate
        through the palette instead of repeating one color.
    """
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
        className=f"mb-3 card-tint-{tint}",
    )
