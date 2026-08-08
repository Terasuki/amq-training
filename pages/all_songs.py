import sqlite3
import pandas as pd

import dash_bootstrap_components as dbc

from dash import (
    html,
    dcc,
    callback,
    Output,
    Input,
    dash_table,
    register_page,
    no_update,
    State,
)

from src.utilities import clean_full_data
from src.theme import (
    SUCCESS,
    SUCCESS_TEXT,
    DANGER,
    DANGER_TEXT,
    NEUTRAL,
    NEUTRAL_TEXT,
    table_style_table,
    table_style_cell,
    table_style_header,
    table_header_conditional_correct,
)

register_page(__name__)


def main_table():
    return html.Div(
        dash_table.DataTable(
            id="main_table",
            columns=[],
            data=[],
            filter_action="native",
            filter_options={"placeholder_text": "", "case": "insensitive"},
            sort_action="native",
            page_action="native",
            page_size=50,
            style_as_list_view=True,
            style_table=table_style_table(),
            style_cell=table_style_cell(),
            style_header=table_style_header(),
            style_data_conditional=[
                {
                    "if": {"filter_query": "{correct} = 1"},
                    "backgroundColor": SUCCESS,
                    "color": SUCCESS_TEXT,
                },
                {
                    "if": {"filter_query": "{correct} = 0"},
                    "backgroundColor": DANGER,
                    "color": DANGER_TEXT,
                },
                {
                    "if": {"filter_query": "{correct} is nil"},
                    "backgroundColor": NEUTRAL,
                    "color": NEUTRAL_TEXT,
                },
                {
                    "if": {
                        "filter_query": "{Guess time} is nil && {Answer} is blank",
                    },
                    "backgroundColor": NEUTRAL,
                    "color": NEUTRAL_TEXT,
                },
                {
                    "if": {
                        "column_id": "correct",
                    },
                    "display": "None",
                },
            ],
            style_header_conditional=table_header_conditional_correct(),
            style_data={"cursor": "pointer"},
        ),
        style={"margin": "auto", "text-align": "center"},
    )


@callback(
    Output("main_table", "columns"),
    Output("main_table", "data"),
    Input("interval", "n_intervals"),
)
def update(n):
    conn = sqlite3.connect("data.db")
    query = """
    SELECT timestamp, game_mode, romaji_title, name, artist, type, anime_type, vintage, difficulty, self_answer, guess_time, start_sample, video_length, ann_id, correct 
    FROM amq_data
    ORDER BY timestamp DESC"""
    raw_data = pd.read_sql_query(query, conn)
    conn.close()

    data = clean_full_data(raw_data)
    table_data = data.to_dict("records")
    table_columns = [{"name": col, "id": col} for col in data.columns]
    return table_columns, table_data


@callback(
    Output("selected-song", "data", allow_duplicate=True),
    Output("row-click-redirect", "pathname"),
    Input("main_table", "active_cell"),
    State("main_table", "derived_viewport_data"),
    prevent_initial_call=True,
)
def row_click(active_cell, viewport_data):
    if active_cell and viewport_data:
        row_index = active_cell["row"]
        song = viewport_data[row_index].get("Song name")
        artist = viewport_data[row_index].get("Artist")

        return {"name": song, "artist": artist}, "/main/song-details"
    return no_update, no_update


layout = dbc.Container(
    children=[
        html.H2("All songs", style={"text-align": "center"}),
        main_table(),
        dcc.Interval(id="interval", interval=5 * 6000, n_intervals=0),
        dcc.Location(id="row-click-redirect", refresh=True),
    ]
)
