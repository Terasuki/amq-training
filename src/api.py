"""
JSON API read by the React UI in frontend/.
"""

import json
import sqlite3
from contextlib import closing
from typing import Tuple

import pandas as pd
from flask import Blueprint, Response, jsonify, request

from src.dashboard import get_dashboard, load_history
from src.utilities import (
    PLAY_FIELDS,
    classify_plays,
    get_song_links,
    get_song_plays,
    song_history,
)

DB_PATH = "data.db"

# Database column -> API field, for a row of the All Songs table.
SONG_FIELDS = {
    "romaji_title": "anime",
    "name": "name",
    "artist": "artist",
    "type": "type",
    "anime_type": "animeType",
    "vintage": "vintage",
    **PLAY_FIELDS,
}

api = Blueprint("api", __name__, url_prefix="/api")


def connect() -> closing:
    return closing(sqlite3.connect(DB_PATH))


@api.get("/dashboard")
def dashboard() -> Response:
    with connect() as conn:
        data = load_history(conn)
    return jsonify(get_dashboard(data))


@api.get("/last-song")
def last_song() -> Response:
    """The most recently played song, or null when none are recorded yet."""
    with connect() as conn:
        last = conn.execute("""
            SELECT romaji_title, name, artist, type, difficulty, site_ids
            FROM amq_data
            ORDER BY timestamp DESC
            LIMIT 1
        """).fetchone()
        if last is None:
            return jsonify(None)
        anime, name, artist, song_type, difficulty, site_ids = last
        plays = get_song_plays(name, artist, conn)

    return jsonify(
        {
            "anime": anime,
            "name": name,
            "artist": artist,
            "type": song_type,
            "difficulty": difficulty,
            "links": get_song_links(site_ids),
            "history": song_history(plays),
        }
    )


@api.get("/song")
def song() -> Response | Tuple[Response, int]:
    """A song picked from a table, identified by its name and artist."""
    name = request.args.get("name", "")
    artist = request.args.get("artist", "")
    with connect() as conn:
        plays = get_song_plays(name, artist, conn)
    if plays.empty:
        return jsonify({"error": "No plays recorded for this song"}), 404

    alt_answers = json.loads(plays.iloc[-1]["alt_answers"] or "[]") or []
    return jsonify(
        {
            "name": name,
            "artist": artist,
            "altAnswers": sorted(alt_answers, key=len),
            "history": song_history(plays),
        }
    )


@api.get("/songs")
def songs() -> Response:
    """Every play, most recent first."""
    query = """
        SELECT id, timestamp, game_mode, romaji_title, name, artist, type, anime_type,
            vintage, difficulty, self_answer, guess_time, start_sample, video_length,
            ann_id, correct
        FROM amq_data
        ORDER BY timestamp DESC
    """
    with connect() as conn:
        data = pd.read_sql_query(query, conn)
    data["outcome"] = classify_plays(data)
    data = data.rename(columns=SONG_FIELDS)[list(SONG_FIELDS.values())]
    # Serialized straight from pandas: it's every row, so skip the jsonify round trip.
    return Response(
        data.to_json(orient="records", force_ascii=False), mimetype="application/json"
    )
