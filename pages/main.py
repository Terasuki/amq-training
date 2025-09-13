from dash import html, register_page, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px

register_page(__name__, path="/")


def classify(row):
    if pd.isna(row["guess_time"]) and pd.isna(row["self_answer"]):
        return "Spectated"
    elif row["correct"] == 1:
        return "Correct"
    else:
        return "Incorrect"


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
            [
                dbc.Col(make_card("Songs Recorded", "songs_played"), width=2),
                dbc.Col(make_card("Guess Rate", "guess_rate"), width=2),
                dbc.Col(make_card("Average Guess Time", "guess_time"), width=2),
                dbc.Col(make_card("Fastest Guess", "fastest_guess"), width=2),
                dbc.Col(make_card("Songs Spectated", "songs_spec"), width=2),
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
        dcc.Interval(id="interval", interval=5000, n_intervals=0),
    ],
    fluid=True,
    style={"padding": "1em"},
)


@callback(
    Output("songs_played", "children"),
    Output("guess_rate", "children"),
    Output("guess_time", "children"),
    Output("fastest_guess", "children"),
    Output("songs_spec", "children"),
    Output("correct_incorrect_chart", "figure"),
    Output("guess_time_difficulty_chart", "figure"),
    Output("songs_over_time_chart", "figure"),
    Input("interval", "n_intervals"),
)
def update_dashboard(n):
    conn = sqlite3.connect("data.db")
    query = """
        SELECT timestamp, difficulty, guess_time, correct, self_answer
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
    fastest_guess = data["guess_time"].min()
    guess_rate = data["correct"].mean() * 100

    kpi_songs = f"{songs_played}"
    kpi_rate = f"{guess_rate:.1f} %"
    kpi_avg_time = f"{avg_guess_time:.0f} ms"
    kpi_fastest = f"{fastest_guess:.0f} ms"
    kpi_spec = f"{spec_count}"

    data["outcome"] = data.apply(classify, axis=1)
    outcome_counts = data["outcome"].value_counts()

    pie_fig = px.pie(
        values=outcome_counts.values,
        names=outcome_counts.index,
        title="Songs distribution",
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
        title="Guess Time by Difficulty",
        labels={
            "guess_time": "Average Guess Time (ms)",
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
        title="Songs Played Over Time",
        labels={"songs": "Songs Played", "timestamp": "Date"},
    )
    line_fig.update_traces(mode="lines+markers")
    line_fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))

    return (
        kpi_songs,
        kpi_rate,
        kpi_avg_time,
        kpi_fastest,
        kpi_spec,
        pie_fig,
        bar_fig,
        line_fig,
    )
