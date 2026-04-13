from dash import html, register_page, Input, Output, callback, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from src.utilities import get_last_song_matches, get_previously_correct
import ast


register_page(__name__)


def last_song_song():
    return html.Div(id="last_song_song2")


def last_song_artist():
    return html.Div(id="last_song_artist2")


def last_song_possible_answers():
    return html.Div(id="last_song_possible_answers2")


def last_song_previously_correct():
    return html.Div(
        id="last_song_previously_correct2",
        style={"margin": "auto", "text-align": "center"},
    )


def last_song_previously_played():
    return html.Div(
        dash_table.DataTable(
            id="last_song_previously_played2",
            columns=[],
            data=[],
            style_as_list_view=True,
            style_table={
                "width": "100%",
                "overflowX": "auto",
                "overflowY": "auto",
                "border": "thin lightgrey solid",
            },
            style_cell={
                "textAlign": "center",
                "padding": "5px",
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
            style_data_conditional=[
                {
                    "if": {
                        "filter_query": "{correct} = 1",
                    },
                    "backgroundColor": "green",
                    "color": "white",
                },
                {
                    "if": {
                        "filter_query": "{correct} = 0",
                    },
                    "backgroundColor": "red",
                    "color": "white",
                },
                {
                    "if": {
                        "filter_query": "{correct} is nil",
                    },
                    "backgroundColor": "gray",
                    "color": "white",
                },
                {
                    "if": {
                        "filter_query": "{Guess time} is nil && {Answer} is blank",
                    },
                    "backgroundColor": "gray",
                    "color": "white",
                },
                {
                    "if": {
                        "column_id": "correct",
                    },
                    "display": "None",
                },
            ],
            style_header_conditional=[
                {
                    "if": {
                        "column_id": "correct",
                    },
                    "display": "None",
                }
            ],
        ),
        style={"margin": "auto", "text-align": "center"},
    )


@callback(
    Output("last_song_song2", "children"),
    Output("last_song_artist2", "children"),
    Output("last_song_possible_answers2", "children"),
    Output("last_song_previously_correct2", "children"),
    Output("last_song_previously_played2", "columns"),
    Output("last_song_previously_played2", "data"),
    Input("selected-song", "data"),
)
def display_song_details(data):
    name = data.get("name", "")
    artist = data.get("artist", "")
    data_df = pd.DataFrame(
        [
            [name, artist],
        ],
        columns=["name", "artist"],
    )
    conn = sqlite3.connect("data.db")
    ls_matches, alt_answers = get_last_song_matches(data_df, conn)
    conn.close()
    ls_song = html.P(name, style={"text-align": "center"}, className="card-text")
    ls_artist = html.P(artist, style={"text-align": "center"}, className="card-text")

    ls_possible_answers = html.Div(
        [
            html.P(answer, style={"text-align": "center", "margin": "2px 0"})
            for answer in sorted(ast.literal_eval(alt_answers), key=len)
        ],
        className="card-text",
    )

    correct_guesses, wrong_guesses, spec_guesses = get_previously_correct(ls_matches)
    ls_previously_correct = html.P(
        children=[
            html.Span(correct_guesses, style={"color": "green"}),
            "/",
            html.Span(wrong_guesses, style={"color": "red"}),
            "/",
            html.Span(spec_guesses, style={"color": "gray"}),
        ],
        style={"text-align": "center"},
        className="card-text",
    )

    ls_matches_data = ls_matches.to_dict("records")
    ls_matches_columns = [{"name": col, "id": col} for col in ls_matches.columns]

    return (
        ls_song,
        ls_artist,
        ls_possible_answers,
        ls_previously_correct,
        ls_matches_columns,
        ls_matches_data,
    )


layout = (
    dbc.Container(
        children=[
            html.H2("Selected Song", style={"text-align": "center"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Song",
                                            style={"text-align": "center"},
                                            className="card-title",
                                        ),
                                        last_song_song(),
                                    ]
                                ),
                                className="shadow-sm mb-1",
                            ),
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Artist",
                                            style={"text-align": "center"},
                                            className="card-title",
                                        ),
                                        last_song_artist(),
                                    ]
                                ),
                                className="shadow-sm mb-1",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Possible answers",
                                        style={"text-align": "center"},
                                        className="card-title",
                                    ),
                                    last_song_possible_answers(),
                                ]
                            ),
                            className="shadow-sm mb-1",
                            style={"height": "100%"},
                        ),
                        width=6,
                    ),
                ]
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(
                                    "History",
                                    style={"text-align": "center"},
                                    className="card-title",
                                ),
                                last_song_previously_correct(),
                                last_song_previously_played(),
                            ]
                        ),
                        className="shadow-sm mb-1",
                    ),
                    width=12,
                )
            ),
            dcc.Interval(id="interval", interval=5 * 6000, n_intervals=0),
        ],
        style={
            "padding": "0.5em",
        },
    ),
)
