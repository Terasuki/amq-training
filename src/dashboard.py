"""
Statistics behind the Home page, computed from the whole play history.
"""

import sqlite3
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.utilities import BLANK_ANSWER, flag_repeat_confusions, to_records

# Months with fewer chances than this are left off the repeat confusion trend,
# since a handful of replays swings the rate wildly.
MIN_MONTHLY_CONFUSION_CHANCES = 20

TOP_K = 10


def number_or_none(value: float) -> Optional[float]:
    """NaN (e.g. the mean of no values) as None, so it serializes to JSON null."""
    return None if pd.isna(value) else float(value)


def load_history(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
        SELECT timestamp, difficulty, guess_time, correct, self_answer, name, artist,
            romaji_title
        FROM amq_data
        ORDER BY timestamp ASC
    """
    return pd.read_sql_query(query, conn, parse_dates=["timestamp"])


def classify(data: pd.DataFrame) -> pd.Series:
    """Correct / Incorrect / Spectated, as split in the outcome chart."""
    spectated = data["guess_time"].isna() & data["self_answer"].isna()
    outcome = np.select(
        [spectated, data["correct"] == 1], ["Spectated", "Correct"], "Incorrect"
    )
    return pd.Series(outcome, index=data.index)


def confusion_rate(rows: pd.DataFrame) -> Dict:
    return {
        "repeats": int(rows["repeat_confusion"].sum()),
        "chances": int(rows["confusion_chance"].sum()),
    }


def repeat_confusion_kpi(data: pd.DataFrame) -> Dict:
    """
    Replays of previously confused songs where the same wrong anime was
    answered again, all time and over the last 30 days.
    """
    recent = data.loc[
        data["timestamp"] >= data["timestamp"].max() - pd.Timedelta(days=30)
    ]
    return {"allTime": confusion_rate(data), "last30Days": confusion_rate(recent)}


def repeat_confusion_trend(data: pd.DataFrame) -> List[Dict]:
    monthly = (
        data.set_index("timestamp")[["repeat_confusion", "confusion_chance"]]
        .resample("MS")
        .sum()
    )
    monthly = monthly.loc[
        monthly["confusion_chance"] >= MIN_MONTHLY_CONFUSION_CHANCES
    ].reset_index()
    monthly["rate"] = monthly["repeat_confusion"] / monthly["confusion_chance"] * 100
    monthly["month"] = monthly["timestamp"].dt.strftime("%Y-%m")
    monthly = monthly.rename(
        columns={"repeat_confusion": "repeats", "confusion_chance": "chances"}
    )
    return to_records(monthly[["month", "repeats", "chances", "rate"]])


def top_repeat_confusions(data: pd.DataFrame) -> List[Dict]:
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
    return to_records(
        confusions.head(TOP_K)[["name", "artist", "anime", "answer", "times"]]
    )


def guess_time_by_difficulty(data: pd.DataFrame) -> List[Dict]:
    bins = list(range(0, 101, 10))
    labels = [f"{i}-{i + 10}" for i in bins[:-1]]
    difficulty_bin = pd.cut(
        data["difficulty"], bins=bins, labels=labels, include_lowest=True, right=False
    )
    difficulty_time = (
        data.groupby(difficulty_bin, observed=False)["guess_time"]
        .mean()
        .rename("guessTime")
        .rename_axis("difficulty")
        .reset_index()
    )
    return to_records(difficulty_time)


def songs_per_day(data: pd.DataFrame) -> List[Dict]:
    daily_counts = (
        data.set_index("timestamp").resample("D").size().reset_index(name="songs")
    )
    daily_counts["date"] = daily_counts["timestamp"].dt.strftime("%Y-%m-%d")
    return to_records(daily_counts[["date", "songs"]])


def song_stats(data: pd.DataFrame) -> pd.DataFrame:
    """Plays of each song, split into correct / wrong / spectated."""
    is_correct = data["correct"] == 1
    is_wrong = (data["correct"] == 0) & ~(data["self_answer"] == BLANK_ANSWER)

    song = [data["name"], data["artist"]]
    stats = pd.concat(
        [
            data.groupby(song).size().rename("total"),
            is_correct.groupby(song).sum().rename("correct"),
            is_wrong.groupby(song).sum().rename("wrong"),
        ],
        axis=1,
    ).reset_index()
    stats["spectated"] = stats["total"] - stats["correct"] - stats["wrong"]
    return stats


def get_dashboard(data: pd.DataFrame) -> Optional[Dict]:
    """
    Everything the Home page shows, or None when no songs are recorded yet.

    Parameters
    ----------
    data : pd.DataFrame
        From load_history.

    Returns
    -------
    dashboard : dict or None
    """
    if data.empty:
        return None

    spec_count = data.loc[data["guess_time"].isna() & data["self_answer"].isna()].shape[
        0
    ]
    songs_played = data.shape[0] - spec_count

    data = flag_repeat_confusions(data)

    outcome_counts = classify(data).value_counts()
    outcomes = [
        {"outcome": outcome, "count": int(outcome_counts.get(outcome, 0))}
        for outcome in ["Correct", "Incorrect", "Spectated"]
    ]

    stats = song_stats(data)

    return {
        "kpis": {
            "songsPlayed": songs_played,
            "songsSpectated": spec_count,
            "guessRate": number_or_none(data["correct"].mean() * 100),
            "avgGuessTime": number_or_none(data["guess_time"].mean()),
            "repeatConfusion": repeat_confusion_kpi(data),
        },
        "outcomes": outcomes,
        "guessTimeByDifficulty": guess_time_by_difficulty(data),
        "songsPerDay": songs_per_day(data),
        "repeatConfusionTrend": repeat_confusion_trend(data),
        "topListened": to_records(stats.nlargest(TOP_K, "total")),
        "topMissed": to_records(stats.nlargest(TOP_K, "wrong")),
        "topConfusions": top_repeat_confusions(data),
    }
