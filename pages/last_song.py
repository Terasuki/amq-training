import sqlite3
import pandas as pd

import dash_bootstrap_components as dbc

from dash import html, dcc, callback, Output, Input, dash_table, register_page

from src.utilities import get_song_links, get_last_song_matches, get_previously_correct
from src.objects import card

register_page(__name__)


layout = dbc.Container(
    children=[
        html.H2("Last Song", style={"textAlign": "center"}),
        dbc.Row(
            [
                dbc.Col(card("Anime", "last_song_anime"), width=4),
                dbc.Col(card("Song", "last_song_song"), width=4),
                dbc.Col(card("Artist", "last_song_artist"), width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(card("Type", "last_song_type"), width=4),
                dbc.Col(card("Links", "last_song_links"), width=4),
                dbc.Col(card("Difficulty", "last_song_difficulty"), width=4),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(
                                "History",
                                style={"textAlign": "center"},
                                className="card-title",
                            ),
                            html.Div(
                                id="last_song_previously_correct",
                                style={"textAlign": "center"},
                            ),
                            dash_table.DataTable(
                                id="last_song_previously_played",
                                columns=[],
                                data=[],
                                style_as_list_view=True,
                                style_table={
                                    "width": "100%",
                                    "overflowX": "auto",
                                    "border": "thin lightgrey solid",
                                },
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "5px",
                                    "whiteSpace": "normal",
                                },
                                style_header={
                                    "backgroundColor": "rgb(30, 30, 30)",
                                    "color": "white",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"filter_query": "{correct} = 1"},
                                        "backgroundColor": "green",
                                        "color": "white",
                                    },
                                    {
                                        "if": {"filter_query": "{correct} = 0"},
                                        "backgroundColor": "red",
                                        "color": "white",
                                    },
                                    {
                                        "if": {"filter_query": "{correct} is nil"},
                                        "backgroundColor": "gray",
                                        "color": "white",
                                    },
                                    {"if": {"column_id": "correct"}, "display": "None"},
                                ],
                                style_header_conditional=[
                                    {"if": {"column_id": "correct"}, "display": "None"}
                                ],
                            ),
                        ]
                    ),
                    className="shadow-sm mb-1",
                ),
                width=12,
            )
        ),
        dcc.Interval(id="interval", interval=500, n_intervals=0),
    ],
    style={"padding": "0.5em"},
)


@callback(
    Output("last_song_anime", "children"),
    Output("last_song_song", "children"),
    Output("last_song_artist", "children"),
    Output("last_song_type", "children"),
    Output("last_song_difficulty", "children"),
    Output("last_song_links", "children"),
    Output("last_song_previously_correct", "children"),
    Output("last_song_previously_played", "columns"),
    Output("last_song_previously_played", "data"),
    Input("interval", "n_intervals"),
)
def update_dashboard(n):
    with sqlite3.connect("data.db") as conn:
        query = "SELECT * FROM amq_data ORDER BY timestamp DESC LIMIT 1"
        last_song = pd.read_sql_query(query, conn)
        ls_matches, _alt_answers = get_last_song_matches(last_song, conn)

    links = get_song_links(last_song)
    ls_links_html = [
        html.A(link["name"], href=link["url"], target="_blank", style={"margin": "7px"})
        for link in links
    ]

    correct, wrong, spec = get_previously_correct(ls_matches)
    history_summary = html.P(
        [
            html.Span(correct, style={"color": "green"}),
            "/",
            html.Span(wrong, style={"color": "red"}),
            "/",
            html.Span(spec, style={"color": "gray"}),
        ],
        className="card-text",
    )

    cols = [{"name": i, "id": i} for i in ls_matches.columns]
    data = ls_matches.to_dict("records")

    return (
        last_song.romaji_title,
        last_song.name,
        last_song.artist,
        last_song.type,
        last_song.difficulty,
        ls_links_html,
        history_summary,
        cols,
        data,
    )
