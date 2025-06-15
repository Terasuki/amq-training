import sqlite3
import pandas as pd

import dash_bootstrap_components as dbc

from dash import html, dcc, callback, Output, Input, dash_table, register_page

from utilities import clean_full_data

register_page(__name__)


def main_table():
    return html.Div(
        dash_table.DataTable(
            id="main_table",
            columns=[],
            data=[],
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_size=50,
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


layout = dbc.Container(
    children=[
        html.H2("All songs", style={"text-align": "center"}),
        main_table(),
        dcc.Interval(id="interval", interval=5 * 6000, n_intervals=0),
    ]
)
