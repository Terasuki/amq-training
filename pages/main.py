from dash import html, register_page, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
from utilities import get_previously_correct

register_page(__name__, path="/")


def classify(row):
    if pd.isna(row["guess_time"]) and pd.isna(row["self_answer"]):
        return "Spectated"
    elif row["correct"] == 1:
        return "Correct"
    else:
        return "Incorrect"


def generate_styled_table(stats_list):
    table_header = [
        html.Thead(
            html.Tr([html.Th("Song name"), html.Th("Artist"), html.Th("C/I/S (Total)")])
        )
    ]
    table_rows = []
    for s in stats_list:
        cell_content = html.Div(
            [
                html.Span(f"{s['c']}", style={"color": "green"}),
                html.Span(" / "),
                html.Span(f"{s['w']}", style={"color": "red"}),
                html.Span(" / "),
                html.Span(f"{s['s']}", style={"color": "gray"}),
                html.Span(f" ({s['total']})", style={"fontWeight": "bold"}),
            ]
        )
        table_rows.append(
            html.Tr([html.Td(s["name"]), html.Td(s["artist"]), html.Td(cell_content)])
        )

    return dbc.Table(
        table_header + [html.Tbody(table_rows)],
        bordered=True,
        striped=True,
        hover=True,
        className="mt-3",
    )


def make_card(title, content_id):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, style={"textAlign": "center"}, className="card-title"),
                html.Div(
                    id=content_id,
                    style={
                        "textAlign": "center",
                        "fontSize": "1.25em",
                        "fontWeight": "bold",
                    },
                ),
            ]
        ),
        className="shadow-sm mb-3",
    )


layout = dbc.Container(
    [
        html.H2("Home", style={"textAlign": "center", "marginBottom": "1em"}),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Update data", id="update_btn", color="primary", className="mb-4"
                ),
                width="auto",
            ),
            justify="center",
        ),
        dbc.Spinner(
            id="loading-spinner",
            color="white",
            type="border",
            fullscreen=False,
            spinner_style={"width": "5rem", "height": "5rem", "borderWidth": "0.5rem"},
            children=[
                dbc.Row(
                    [
                        dbc.Col(make_card("Songs played", "songs_played"), width=2),
                        dbc.Col(make_card("Guess rate", "guess_rate"), width=2),
                        dbc.Col(make_card("Average guess time", "guess_time"), width=2),
                        dbc.Col(make_card("Songs spectated", "songs_spec"), width=2),
                    ],
                    justify="center",
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="correct_incorrect_chart"), width=6),
                        dbc.Col(dcc.Graph(id="guess_time_difficulty_chart"), width=6),
                    ]
                ),
                dbc.Row(dbc.Col(dcc.Graph(id="songs_over_time_chart"), width=12)),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4(
                                    "Top listened songs",
                                    style={"textAlign": "center", "marginTop": "2em"},
                                ),
                                html.Div(id="common_songs_table"),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.H4(
                                    "Top missed songs",
                                    style={"textAlign": "center", "marginTop": "2em"},
                                ),
                                html.Div(id="wrong_songs_table"),
                            ],
                            width=6,
                        ),
                    ]
                ),
            ],
        ),
    ],
    fluid=True,
    style={"padding": "1em"},
)


@callback(
    Output("songs_played", "children"),
    Output("guess_rate", "children"),
    Output("guess_time", "children"),
    Output("songs_spec", "children"),
    Output("correct_incorrect_chart", "figure"),
    Output("guess_time_difficulty_chart", "figure"),
    Output("songs_over_time_chart", "figure"),
    Output("common_songs_table", "children"),
    Output("wrong_songs_table", "children"),
    Input("update_btn", "n_clicks"),
)
def update_dashboard(n_clicks):
    conn = sqlite3.connect("data.db")
    query = """
        SELECT timestamp, difficulty, guess_time, correct, self_answer, name, artist
        FROM amq_data
        ORDER BY timestamp ASC
    """
    data = pd.read_sql_query(query, conn, parse_dates=["timestamp"])
    conn.close()

    spec_count = data.loc[data["guess_time"].isna() & data["self_answer"].isna()].shape[
        0
    ]
    total_count = data.shape[0]
    songs_played = total_count - spec_count

    avg_guess_time = data["guess_time"].mean()
    guess_rate = data["correct"].mean() * 100

    kpi_songs = f"{songs_played}"
    kpi_rate = f"{guess_rate:.1f} %"
    kpi_avg_time = f"{avg_guess_time:.0f} ms"
    kpi_spec = f"{spec_count}"

    data["outcome"] = data.apply(classify, axis=1)
    outcome_counts = data["outcome"].value_counts()

    pie_fig = px.pie(
        values=outcome_counts.values,
        names=outcome_counts.index,
        color=outcome_counts.index,
        color_discrete_map={
            "Correct": "green",
            "Incorrect": "red",
            "Spectated": "gray",
        },
    )
    pie_fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))

    bins = list(range(0, 101, 10))
    labels = [f"{i}-{i + 10}" for i in bins[:-1]]
    data["difficulty_bin"] = pd.cut(
        data["difficulty"], bins=bins, labels=labels, include_lowest=True, right=False
    )
    difficulty_time = (
        data.groupby("difficulty_bin", observed=False)["guess_time"]
        .mean()
        .reset_index()
    )

    bar_fig = px.bar(
        difficulty_time,
        x="difficulty_bin",
        y="guess_time",
        labels={
            "guess_time": "Average guess time (ms)",
            "difficulty_bin": "Difficulty",
        },
    )
    bar_fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))

    daily_counts = (
        data.set_index("timestamp").resample("D").size().reset_index(name="songs")
    )
    line_fig = px.line(
        daily_counts,
        x="timestamp",
        y="songs",
        labels={"songs": "Songs played + spectated", "timestamp": "Date"},
    )
    line_fig.update_traces(mode="lines+markers")
    line_fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))

    top_k = 10
    song_groups = data.groupby(["name", "artist"])
    all_song_stats = []
    for (name, artist), group in song_groups:
        c, w, s = get_previously_correct(
            group, correct="correct", selfAnswer="self_answer"
        )
        total = len(group)
        all_song_stats.append(
            {"name": name, "artist": artist, "c": c, "w": w, "s": s, "total": total}
        )

    common_list = sorted(all_song_stats, key=lambda x: x["total"], reverse=True)[:top_k]
    common_songs_table = generate_styled_table(common_list)

    wrong_list = sorted(all_song_stats, key=lambda x: x["w"], reverse=True)[:top_k]
    wrong_songs_table = generate_styled_table(wrong_list)

    return (
        kpi_songs,
        kpi_rate,
        kpi_avg_time,
        kpi_spec,
        pie_fig,
        bar_fig,
        line_fig,
        common_songs_table,
        wrong_songs_table,
    )
