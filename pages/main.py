from dash import (
    html,
    register_page,
    Input,
    Output,
    callback,
    dcc,
    dash_table,
    no_update,
    ctx,
    State,
)
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import io
import plotly.express as px
from src.objects import card
from src.utilities import flag_repeat_confusions
from src.theme import (
    SUCCESS_CHART,
    DANGER_CHART,
    NEUTRAL_CHART,
    INK,
    table_style_table,
    table_style_cell,
    table_style_header,
    table_style_data,
)

register_page(__name__, path="/")

# Months with fewer chances than this are left off the repeat confusion trend,
# since a handful of replays swings the rate wildly.
MIN_MONTHLY_CONFUSION_CHANCES = 20


def classify(row):
    if pd.isna(row["guess_time"]) and pd.isna(row["self_answer"]):
        return "Spectated"
    elif row["correct"] == 1:
        return "Correct"
    else:
        return "Incorrect"


def chart_card(title, graph_id, tint=0):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, style={"textAlign": "center"}, className="card-title"),
                dcc.Graph(
                    id=graph_id,
                    config={"responsive": True},
                    style={"minHeight": "360px", "flex": "1"},
                ),
            ],
            className="d-flex flex-column",
        ),
        className=f"h-100 card-tint-{tint}",
    )


def table_card(title, table, tint=0):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, style={"textAlign": "center"}, className="card-title"),
                table,
            ]
        ),
        className=f"h-100 card-tint-{tint}",
    )


def song_stats_datatable(table_id):
    return dash_table.DataTable(
        id=table_id,
        columns=[
            {"name": "Song name", "id": "name"},
            {"name": "Artist", "id": "artist"},
            {"name": "History", "id": "stats", "presentation": "markdown"},
        ],
        style_table={**table_style_table(), "tableLayout": "fixed"},
        style_cell={
            **table_style_cell(),
            "overflowWrap": "break-word",
            "wordBreak": "break-word",
        },
        style_cell_conditional=[
            {"if": {"column_id": "name"}, "width": "40%"},
            {"if": {"column_id": "artist"}, "width": "30%"},
            {"if": {"column_id": "stats"}, "width": "30%"},
        ],
        style_header=table_style_header(),
        style_data={"cursor": "pointer", **table_style_data()},
        row_selectable=False,
        markdown_options={"html": True},
        page_size=10,
    )


def generate_table_data(stats_list):
    data_list = []
    for s in stats_list:
        stat_str = (
            f"<div style='text-align: center;'>"
            f"<span class='text-success-light'>{s['c']}</span> / "
            f"<span class='text-danger-light'>{s['w']}</span> / "
            f"<span class='text-neutral-light'>{s['s']}</span> "
            f"(<span style='color: {INK};font-weight: bold;'>{s['total']}</span>)"
            f"</div>"
        )
        data_list.append({"name": s["name"], "artist": s["artist"], "stats": stat_str})
    return data_list


def confusions_datatable(table_id):
    return dash_table.DataTable(
        id=table_id,
        columns=[
            {"name": "Song name", "id": "name"},
            {"name": "Anime", "id": "anime"},
            {"name": "Your answer", "id": "answer"},
            {"name": "Times", "id": "times"},
        ],
        style_table={**table_style_table(), "tableLayout": "fixed"},
        style_cell={
            **table_style_cell(),
            "overflowWrap": "break-word",
            "wordBreak": "break-word",
        },
        style_cell_conditional=[
            {"if": {"column_id": "name"}, "width": "30%"},
            {"if": {"column_id": "anime"}, "width": "30%"},
            {"if": {"column_id": "answer"}, "width": "28%"},
            {"if": {"column_id": "times"}, "width": "12%"},
        ],
        style_header=table_style_header(),
        style_data={"cursor": "pointer", **table_style_data()},
        row_selectable=False,
        page_size=10,
    )


def top_repeat_confusions(data, top_k=10):
    """
    Songs most often answered with the same wrong anime, most recent first on ties.
    Rows keep `artist` (not shown) so a click can open the song's details.
    """
    wrong = data.loc[data["confused_with"].notna()]
    confusions = (
        wrong.groupby(["name", "artist", "confused_with"])
        .agg(
            times=("timestamp", "size"),
            last_seen=("timestamp", "max"),
            anime=("romaji_title", "last"),
            answer=("self_answer", "last"),
        )
        .reset_index()
    )
    confusions = confusions.loc[confusions["times"] > 1].sort_values(
        ["times", "last_seen"], ascending=False
    )
    confusions["answer"] = confusions["answer"].str.strip()
    return confusions.head(top_k)[
        ["name", "artist", "anime", "answer", "times"]
    ].to_dict("records")


def repeat_confusion_kpi(data):
    """
    Share of replays of previously confused songs where the same wrong anime
    was answered again, all time, with the last 30 days underneath.
    """

    def rate(rows, show_counts=False):
        repeats = rows["repeat_confusion"].sum()
        chances = rows["confusion_chance"].sum()
        if chances == 0:
            return "–"
        text = f"{repeats / chances * 100:.1f} %"
        return f"{text} ({repeats}/{chances})" if show_counts else text

    recent = data.loc[
        data["timestamp"] >= data["timestamp"].max() - pd.Timedelta(days=30)
    ]

    return [
        html.Div(rate(data)),
        html.Div(
            f"Last 30 days: {rate(recent, show_counts=True)}",
            className="card-subtext",
        ),
    ]


def repeat_confusion_trend(data):
    monthly = (
        data.set_index("timestamp")[["repeat_confusion", "confusion_chance"]]
        .resample("MS")
        .sum()
    )
    monthly = monthly.loc[
        monthly["confusion_chance"] >= MIN_MONTHLY_CONFUSION_CHANCES
    ].reset_index()
    monthly["rate"] = monthly["repeat_confusion"] / monthly["confusion_chance"] * 100

    fig = px.line(
        monthly,
        x="timestamp",
        y="rate",
        custom_data=["repeat_confusion", "confusion_chance"],
        labels={"rate": "Same wrong answer repeated (%)", "timestamp": "Month"},
    )
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=8),
        hovertemplate=(
            "%{x|%b %Y}<br><b>%{y:.1f} %</b>"
            "<br>%{customdata[0]} of %{customdata[1]} replays of confused songs"
            "<extra></extra>"
        ),
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))
    return fig


layout = dbc.Container(
    [
        html.H2("Home", style={"textAlign": "center", "marginBottom": "1em"}),
        dcc.Location(id="url", refresh=True),
        dcc.Store(id="dashboard_data_store", storage_type="session"),
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
            color="primary",
            type="border",
            fullscreen=False,
            spinner_style={"width": "5rem", "height": "5rem", "borderWidth": "0.5rem"},
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            card("Songs played", "songs_played", tint=0),
                            xs=6,
                            md=4,
                            lg=True,
                        ),
                        dbc.Col(
                            card("Guess rate", "guess_rate", tint=0),
                            xs=6,
                            md=4,
                            lg=True,
                        ),
                        dbc.Col(
                            card("Average guess time", "guess_time", tint=0),
                            xs=6,
                            md=4,
                            lg=True,
                        ),
                        dbc.Col(
                            card("Songs spectated", "songs_spec", tint=0),
                            xs=6,
                            md=4,
                            lg=True,
                        ),
                        dbc.Col(
                            card("Repeat confusions", "repeat_confusions", tint=0),
                            xs=12,
                            md=4,
                            lg=True,
                        ),
                    ],
                    className="g-4 mb-4 kpi-row",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            chart_card(
                                "",
                                "correct_incorrect_chart",
                                tint=1,
                            ),
                            xs=12,
                            lg=6,
                        ),
                        dbc.Col(
                            chart_card(
                                "",
                                "guess_time_difficulty_chart",
                                tint=1,
                            ),
                            xs=12,
                            lg=6,
                        ),
                    ],
                    className="g-4 mb-4",
                ),
                dbc.Row(
                    dbc.Col(
                        chart_card(
                            "Songs played over time", "songs_over_time_chart", tint=2
                        ),
                        xs=12,
                    ),
                    className="g-4 mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            chart_card(
                                "Repeat confusions over time",
                                "repeat_confusions_chart",
                                tint=2,
                            ),
                            xs=12,
                            lg=6,
                        ),
                        dbc.Col(
                            table_card(
                                "Top repeat confusions",
                                confusions_datatable("confusions_table"),
                                tint=2,
                            ),
                            xs=12,
                            lg=6,
                        ),
                    ],
                    className="g-4 mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            table_card(
                                "Top listened songs",
                                song_stats_datatable("common_songs_table"),
                                tint=3,
                            ),
                            xs=12,
                            lg=6,
                        ),
                        dbc.Col(
                            table_card(
                                "Top missed songs",
                                song_stats_datatable("wrong_songs_table"),
                                tint=3,
                            ),
                            xs=12,
                            lg=6,
                        ),
                    ],
                    className="g-4 mb-4",
                ),
            ],
        ),
    ],
    fluid=True,
    style={"padding": "1em"},
)


@callback(
    Output("dashboard_data_store", "data"),
    Input("update_btn", "n_clicks"),
    State("dashboard_data_store", "data"),
)
def refresh_dashboard_data(n_clicks, cached_data):
    if ctx.triggered_id != "update_btn" and cached_data is not None:
        return no_update

    conn = sqlite3.connect("data.db")
    query = """
        SELECT timestamp, difficulty, guess_time, correct, self_answer, name, artist,
            romaji_title
        FROM amq_data
        ORDER BY timestamp ASC
    """
    data = pd.read_sql_query(query, conn, parse_dates=["timestamp"])
    conn.close()

    return data.to_json(date_format="iso", orient="split")


@callback(
    Output("songs_played", "children"),
    Output("guess_rate", "children"),
    Output("guess_time", "children"),
    Output("songs_spec", "children"),
    Output("repeat_confusions", "children"),
    Output("correct_incorrect_chart", "figure"),
    Output("guess_time_difficulty_chart", "figure"),
    Output("songs_over_time_chart", "figure"),
    Output("repeat_confusions_chart", "figure"),
    Output("common_songs_table", "data"),
    Output("wrong_songs_table", "data"),
    Output("confusions_table", "data"),
    Input("dashboard_data_store", "data"),
)
def update_dashboard(stored_data):
    if not stored_data:
        return (no_update,) * 12

    data = pd.read_json(io.StringIO(stored_data), orient="split")
    data["timestamp"] = pd.to_datetime(data["timestamp"])

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

    data = flag_repeat_confusions(data)
    kpi_confusions = repeat_confusion_kpi(data)
    confusion_fig = repeat_confusion_trend(data)

    data["outcome"] = data.apply(classify, axis=1)
    outcome_counts = data["outcome"].value_counts()

    pie_fig = px.pie(
        values=outcome_counts.values,
        names=outcome_counts.index,
        color=outcome_counts.index,
        color_discrete_map={
            "Correct": SUCCESS_CHART,
            "Incorrect": DANGER_CHART,
            "Spectated": NEUTRAL_CHART,
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
    is_correct = data["correct"] == 1
    is_wrong = (data["correct"] == 0) & ~(
        data["self_answer"] == "\n\t\t\t\t\t\n\t\t\t\t"
    )

    grouped = data.groupby(["name", "artist"])
    song_stats = pd.concat(
        [
            grouped.size().rename("total"),
            is_correct.groupby([data["name"], data["artist"]]).sum().rename("c"),
            is_wrong.groupby([data["name"], data["artist"]]).sum().rename("w"),
        ],
        axis=1,
    ).reset_index()
    song_stats["s"] = song_stats["total"] - song_stats["c"] - song_stats["w"]

    common_list = song_stats.nlargest(top_k, "total").to_dict("records")
    wrong_list = song_stats.nlargest(top_k, "w").to_dict("records")

    return (
        kpi_songs,
        kpi_rate,
        kpi_avg_time,
        kpi_spec,
        kpi_confusions,
        pie_fig,
        bar_fig,
        line_fig,
        confusion_fig,
        generate_table_data(common_list),
        generate_table_data(wrong_list),
        top_repeat_confusions(data),
    )


@callback(
    Output("url", "pathname"),
    Output("selected-song", "data", allow_duplicate=True),
    Input("common_songs_table", "active_cell"),
    Input("wrong_songs_table", "active_cell"),
    Input("confusions_table", "active_cell"),
    State("common_songs_table", "data"),
    State("wrong_songs_table", "data"),
    State("confusions_table", "data"),
    prevent_initial_call=True,
)
def handle_row_click(
    active_common,
    active_wrong,
    active_confusions,
    data_common,
    data_wrong,
    data_confusions,
):
    triggered_id = ctx.triggered_id

    if triggered_id == "common_songs_table":
        active_cell = active_common
        data = data_common
    elif triggered_id == "wrong_songs_table":
        active_cell = active_wrong
        data = data_wrong
    elif triggered_id == "confusions_table":
        active_cell = active_confusions
        data = data_confusions
    else:
        return no_update, no_update

    if active_cell and data:
        row_index = active_cell["row"]
        song_info = data[row_index]

        payload = {"name": song_info["name"], "artist": song_info["artist"]}
        return "/main/song-details", payload

    return no_update, no_update
