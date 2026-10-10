import json
import pandas as pd
import sqlite3
import math
from typing import List, Dict, Tuple


def format_seconds(seconds_raw: float) -> str:
    """
    Formats raw seconds into minutes:seconds format.

    Parameters
    ----------
    seconds_raw : float
        Raw seconds to be converted.

    Returns
    -------
    time : str
        The time equivalent in minutes:seconds format.
    """
    if seconds_raw is None or math.isnan(seconds_raw):
        return "0:00"
    minutes = int(seconds_raw // 60)
    seconds = int(seconds_raw % 60)
    return f"{minutes}:{seconds:02}"


def get_song_links(row: pd.DataFrame) -> List[Dict]:
    site_ids = json.loads(row.get("site_ids")[0])

    links = [
        {
            "name": "AniList",
            "url": f"https://anilist.co/anime/{site_ids.get('aniListId')}",
        },
        {
            "name": "MAL",
            "url": f"https://myanimelist.net/anime/{site_ids.get('malId')}",
        },
        {"name": "Kitsu", "url": f"https://kitsu.io/anime/{site_ids.get('kitsuId')}"},
        {
            "name": "ANN",
            "url": f"https://www.animenewsnetwork.com/encyclopedia/anime.php?id={site_ids.get('annId')}",
        },
    ]

    return links


def get_last_song_matches(row: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    song_name = row["name"][0]
    song_artist = row["artist"][0]
    matches_query = """
            SELECT timestamp, game_mode, difficulty, self_answer, guess_time, start_sample, video_length, ann_id, correct, alt_answers
            FROM amq_data 
            WHERE name = ? AND artist = ?
            ORDER BY timestamp DESC
        """
    matches = pd.read_sql_query(matches_query, conn, params=(song_name, song_artist))
    matches["timestamp"] = pd.to_datetime(matches["timestamp"]).dt.strftime(
        "%Y/%m/%d, %H:%M"
    )

    matches["Sample"] = (
        matches["start_sample"].apply(format_seconds)
        + "/"
        + matches["video_length"].apply(format_seconds)
    )
    matches = matches.drop(["start_sample", "video_length"], axis=1).rename(
        columns={
            "timestamp": "Date",
            "game_mode": "Mode",
            "difficulty": "Diff.",
            "self_answer": "Answer",
            "guess_time": "Guess time",
            "ann_id": "ANNID",
        }
    )
    alt_answers = matches.iloc[-1]["alt_answers"]
    matches = matches[
        ["Date", "Mode", "ANNID", "Diff.", "Sample", "Guess time", "Answer", "correct"]
    ]

    return matches, alt_answers


def get_previously_correct(
    matches: pd.DataFrame, correct: str = "correct", selfAnswer: str = "Answer"
) -> Tuple[int, int, int]:
    """
    Finds correctness of user's guesses from a song list in pd.DataFrame form.

    Parameters
    ----------
    matches : pd.DataFrame
        User's guesses.

    Returns
    -------
    correct_guesses : int
    wrong_guesses : int
    spec_guesses : int
    """
    n_guesses = matches.shape[0]
    correct_guesses = matches.loc[matches[correct] == 1].shape[0]
    wrong_guesses = matches.loc[
        (matches[correct] == 0) & ~(matches[selfAnswer] == "\n\t\t\t\t\t\n\t\t\t\t")
    ].shape[0]
    spec_guesses = n_guesses - correct_guesses - wrong_guesses
    return correct_guesses, wrong_guesses, spec_guesses


def flag_repeat_confusions(data: pd.DataFrame) -> pd.DataFrame:
    """
    Flags plays where the user repeated an earlier wrong answer for the same song,
    i.e. kept confusing the song with the same (wrong) anime.

    Expects `data` sorted by timestamp ascending, with name, artist, correct and
    self_answer columns. Answers are compared case-insensitively; blank and "..."
    (no answer typed) never count as a confusion.

    Parameters
    ----------
    data : pd.DataFrame
        Play history.

    Returns
    -------
    data : pd.DataFrame
        Same data with three columns added:
        `confused_with` - the normalized wrong answer typed, or NA when the play
        was correct, spectated or left unanswered.
        `confusion_chance` - the user played a song they had previously typed a
        wrong answer for (participated, not spectated).
        `repeat_confusion` - the user typed a wrong answer they had already given
        for this song before.
    """
    song = [data["name"], data["artist"]]
    answer = data["self_answer"].astype("string").str.strip().str.casefold()
    typed_wrong = (data["correct"] == 0) & answer.notna() & ~answer.isin(["", "..."])

    data["confused_with"] = answer.where(typed_wrong)

    prior_wrongs = typed_wrong.groupby(song).cumsum() - typed_wrong
    data["confusion_chance"] = data["correct"].notna() & (prior_wrongs > 0)

    wrong = data.loc[typed_wrong]
    seen_before = wrong.groupby(["name", "artist", answer[typed_wrong]]).cumcount() > 0
    data["repeat_confusion"] = seen_before.reindex(data.index, fill_value=False)
    return data


def clean_full_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw data into user-friendly format.

    Parameters
    ----------
    raw_data : pd.DataFrame
        Raw data.

    Returns
    -------
    clean_data : pd.DataFrame
        Clean data.
    """
    raw_data["timestamp"] = pd.to_datetime(raw_data["timestamp"]).dt.strftime(
        "%Y/%m/%d, %H:%M"
    )
    raw_data["Sample"] = (
        raw_data["start_sample"].apply(format_seconds)
        + "/"
        + raw_data["video_length"].apply(format_seconds)
    )
    clean_data = raw_data.drop(["start_sample", "video_length"], axis=1).rename(
        columns={
            "timestamp": "Date",
            "name": "Song name",
            "artist": "Artist",
            "type": "Type",
            "anime_type": "Anime Type",
            "vintage": "Vintage",
            "romaji_title": "Anime",
            "game_mode": "Mode",
            "difficulty": "Diff.",
            "self_answer": "Answer",
            "guess_time": "Guess time",
            "ann_id": "ANNID",
        }
    )
    return clean_data
