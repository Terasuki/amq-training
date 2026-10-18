import json
import sqlite3
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# What AMQ records as your answer when the answer box was never touched.
BLANK_ANSWER = "\n\t\t\t\t\t\n\t\t\t\t"

# Database column -> API field, for a row of a play history table.
PLAY_FIELDS = {
    "id": "id",
    "timestamp": "timestamp",
    "game_mode": "mode",
    "ann_id": "annId",
    "difficulty": "difficulty",
    "start_sample": "startSample",
    "video_length": "videoLength",
    "guess_time": "guessTime",
    "self_answer": "answer",
    "outcome": "outcome",
}


def to_records(data: pd.DataFrame) -> List[Dict]:
    """
    Converts a DataFrame to JSON-safe records, with NaN as None.

    Parameters
    ----------
    data : pd.DataFrame

    Returns
    -------
    records : list of dict
    """
    return json.loads(data.to_json(orient="records", force_ascii=False))


def get_song_links(site_ids_json: str) -> List[Dict]:
    """
    Links to an anime's page on each tracking site.

    Parameters
    ----------
    site_ids_json : str
        A play's `site_ids` column, a JSON object of the anime's site ids.

    Returns
    -------
    links : list of dict
        Each with the site `name` and the anime's `url` on it.
    """
    site_ids = json.loads(site_ids_json or "{}")

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


def get_song_plays(name: str, artist: str, conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Every play of a song, most recent first.

    Parameters
    ----------
    name : str
    artist : str
    conn : sqlite3.Connection

    Returns
    -------
    plays : pd.DataFrame
    """
    query = """
        SELECT id, timestamp, game_mode, difficulty, self_answer, guess_time,
            start_sample, video_length, ann_id, correct, alt_answers
        FROM amq_data
        WHERE name = ? AND artist = ?
        ORDER BY timestamp DESC
    """
    return pd.read_sql_query(query, conn, params=(name, artist))


def get_previously_correct(
    matches: pd.DataFrame, correct: str = "correct", selfAnswer: str = "self_answer"
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
        (matches[correct] == 0) & ~(matches[selfAnswer] == BLANK_ANSWER)
    ].shape[0]
    spec_guesses = n_guesses - correct_guesses - wrong_guesses
    return correct_guesses, wrong_guesses, spec_guesses


def classify_plays(data: pd.DataFrame) -> pd.Series:
    """
    Outcome of each play as tinted in the tables: "correct", "wrong" or
    "spectated". A play marked wrong with no guess time and a blank answer
    counts as spectated.

    Parameters
    ----------
    data : pd.DataFrame
        Plays, with correct, guess_time and self_answer columns.

    Returns
    -------
    outcome : pd.Series
    """
    blank_answer = data["self_answer"].fillna("").astype(str).str.strip().eq("")
    unanswered = data["guess_time"].isna() & blank_answer
    outcome = np.select(
        [data["correct"] == 1, (data["correct"] == 0) & ~unanswered],
        ["correct", "wrong"],
        default="spectated",
    )
    return pd.Series(outcome, index=data.index)


def song_history(plays: pd.DataFrame) -> Dict:
    """
    A song's history card: correct/wrong/spectated counts and one row per play.

    Parameters
    ----------
    plays : pd.DataFrame
        From get_song_plays.

    Returns
    -------
    history : dict
    """
    correct, wrong, spectated = get_previously_correct(plays)
    rows = plays.assign(outcome=classify_plays(plays)).rename(columns=PLAY_FIELDS)
    return {
        "correct": correct,
        "wrong": wrong,
        "spectated": spectated,
        "plays": to_records(rows[list(PLAY_FIELDS.values())]),
    }


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
