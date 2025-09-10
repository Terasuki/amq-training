from dash import html, register_page, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3


register_page(__name__, path="/")


def songs_played():
    return html.Div(id="songs_played")


def guess_rate():
    return html.Div(id="guess_rate")


def guess_time():
    return html.Div(id="guess_time")


def songs_spec():
    return html.Div(
        id="songs_spec",
    )

@callback(
    Output("songs_played", "children"),
    Output("guess_rate", "children"),
    Output("guess_time", "children"),
    Output("songs_spec", "children"),
    Input("interval", "n_intervals"),
)
def update(n):
    conn = sqlite3.connect("data.db")
    query = """
            SELECT timestamp, game_mode, difficulty, guess_time, correct, alt_answers, type, anime_type, vintage, self_answer
            FROM amq_data 
            ORDER BY timestamp DESC
        """
    data = pd.read_sql_query(query, conn)
    conn.close()
    spec_count = data.loc[data["guess_time"].isna() & data["self_answer"].isna()].shape[0]
    total_count = data.shape[0]
    song_count = html.P(total_count-spec_count, style={"text-align": "center"}, className="card-text")
    guess_time = html.P(f"{data['guess_time'].mean():.2f} ms", style={"text-align": "center"}, className="card-text")
    guess_rate = html.P(f"{(data['correct'].mean()*100):.2f} %", style={"text-align": "center"}, className="card-text")
    songs_spec = html.P(spec_count, style={"text-align": "center"}, className="card-text")

    return (
        song_count,
        guess_rate,
        guess_time,
        songs_spec,
    )


layout = (
    dbc.Container(
        children=[
            html.H2("Home", style={"text-align": "center"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Songs recorded",
                                            style={"text-align": "center"},
                                            className="card-title",
                                        ),
                                        songs_played(),
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
                                        guess_rate(),
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
                                        "Average guess time",
                                        style={"text-align": "center"},
                                        className="card-title",
                                    ),
                                    guess_time(),
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
                                songs_spec(),
                            ]
                        ),
                        className="shadow-sm mb-1",
                    ),
                    width=12,
                )
            ),
            dcc.Interval(id="interval", interval=500, n_intervals=0),
        ],
        style={
            "padding": "0.5em",
        },
    ),
)
