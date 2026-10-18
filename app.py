import json
import sqlite3

from datetime import datetime
from pathlib import Path
from typing import Tuple

from flask import (
    Flask,
    abort,
    request,
    jsonify,
    redirect,
    Response,
    send_from_directory,
)

from src.api import DB_PATH, api

# The React UI, built by `npm run build` in frontend/.
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

app = Flask(__name__, static_folder=None)
app.register_blueprint(api)


def init_db():
    """
    Function to start a database table if one does not exist yet.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS amq_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                game_mode TEXT,
                name TEXT,
                artist TEXT,
                english_title TEXT,
                romaji_title TEXT,
                ann_id INTEGER,
                type TEXT,
                difficulty REAL,
                anime_type TEXT,
                vintage TEXT,
                tags TEXT,
                genre TEXT,
                alt_answers TEXT,
                site_ids TEXT,
                start_sample REAL,
                video_length REAL,
                correct BOOLEAN,
                self_answer TEXT,
                guess_time REAL,
                position INTEGER,
                rig_type TEXT,
                rig_score INTEGER
            );
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["POST"])
def receive_data() -> Tuple[Response, int]:
    """
    Helper function that receives data from the Tampermonkey script and processes it to the database.

    Returns
    -------
    response : flask.Response
    status_code : int
    """
    data = request.json
    timestamped_data = {"timestamp": datetime.now().isoformat(), **data}
    raw_vintage = timestamped_data.get("vintage")
    season = raw_vintage.get("key", "").split(".")[-1].capitalize()
    year = raw_vintage.get("data", {}).get("year")
    vintage = f"{season} {year}" if year else season
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO amq_data (
            timestamp, game_mode, name, artist, english_title, romaji_title,
            ann_id, type, difficulty, anime_type, vintage, tags, genre,
            alt_answers, site_ids, start_sample, video_length, correct, self_answer, guess_time,
            position, rig_type, rig_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
            (
                timestamped_data["timestamp"],
                timestamped_data["gameMode"],
                timestamped_data["name"],
                timestamped_data["artist"],
                timestamped_data["anime"].get("english"),
                timestamped_data["anime"].get("romaji"),
                timestamped_data["annId"],
                timestamped_data["type"],
                timestamped_data["difficulty"],
                timestamped_data["animeType"],
                vintage,
                json.dumps(timestamped_data.get("tags", [])),
                json.dumps(timestamped_data.get("genre", [])),
                json.dumps(timestamped_data.get("altAnswers", [])),
                json.dumps(timestamped_data.get("siteIds", {})),
                timestamped_data.get("startSample"),
                timestamped_data.get("videoLength"),
                timestamped_data.get("correct"),
                timestamped_data.get("selfAnswer"),
                timestamped_data.get("guessTime"),
                timestamped_data.get("position"),
                timestamped_data.get("rig_type"),
                timestamped_data.get("rig_score"),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "success", "message": "Data saved"}), 200


@app.route("/main/", defaults={"page": ""})
@app.route("/main/<path:page>")
def legacy_page(page: str) -> Response:
    """
    Pages lived under /main/ when the UI was a Dash app; keeps old bookmarks working.
    """
    return redirect(f"/{page}")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path: str) -> Response:
    """
    Serves the built React app. Any other path without a file extension gets
    index.html, so the UI's own routes (e.g. /last-song) work on reload.
    """
    if (FRONTEND_DIR / path).is_file():
        return send_from_directory(FRONTEND_DIR, path)
    if path.startswith("api/") or "." in Path(path).name:
        abort(404)
    if not (FRONTEND_DIR / "index.html").is_file():
        return Response(
            "The UI hasn't been built yet: run `npm install` and `npm run build` in frontend/.",
            status=503,
            mimetype="text/plain",
        )
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8888, debug=True)
