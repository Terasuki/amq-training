import json
import sqlite3
import webbrowser

from datetime import datetime
from threading import Timer
from typing import Tuple

import dash_bootstrap_components as dbc

from flask import Flask, request, jsonify, redirect, Response
from flask_cors import cross_origin
from dash import Dash, html, page_container, callback, Input, Output
from dash_bootstrap_templates import load_figure_template

app = Flask(__name__)

dashboard = Dash(
    __name__,
    server=app,
    url_base_pathname='/main/',
    external_stylesheets=[dbc.themes.SLATE, '/assets/styles.css'],
    update_title=None,
    use_pages=True
)

dashboard.title = 'AMQ Song List'
load_figure_template('DARKLY')

def open_browser() -> None:
    """
    Function to start the game and the dashboard.
    """
    webbrowser.open_new('http://127.0.0.1:8888/main/')
    webbrowser.open_new_tab('https://animemusicquiz.com/')

def init_db():
    """
    Function to start a database table if one does not exist yet.
    """
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['POST'])
@cross_origin(origin='*')
def receive_data() -> Tuple[Response, int]:
    """
    Helper function that receives data from the Tampermonkey script and processes it to the database.

    Returns
    -------
    response : flask.Response
    status_code : int
    """
    data = request.json
    timestamped_data = {
        'timestamp': datetime.now().isoformat(),
        **data
    }

    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
        INSERT INTO amq_data (
            timestamp, game_mode, name, artist, english_title, romaji_title,
            ann_id, type, difficulty, anime_type, vintage, tags, genre,
            alt_answers, site_ids, start_sample, video_length, correct, self_answer, guess_time,
            position, rig_type, rig_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
            (
        timestamped_data['timestamp'],
        timestamped_data['gameMode'],
        timestamped_data['name'],
        timestamped_data['artist'],
        timestamped_data['anime'].get('english'),
        timestamped_data['anime'].get('romaji'),
        timestamped_data['annId'],
        timestamped_data['type'],
        timestamped_data['difficulty'],
        timestamped_data['animeType'],
        timestamped_data['vintage'],
        json.dumps(timestamped_data.get('tags', [])),
        json.dumps(timestamped_data.get('genre', [])),
        json.dumps(timestamped_data.get('altAnswers', [])),
        json.dumps(timestamped_data.get('siteIds', {})),
        timestamped_data.get('startSample'),
        timestamped_data.get('videoLength'),
        timestamped_data.get('correct'),
        timestamped_data.get('selfAnswer'),
        timestamped_data.get('guessTime'),
        timestamped_data.get('position'),
        timestamped_data.get('rig_type'),
        timestamped_data.get('rig_score')
    )
        )
        conn.commit()

    return jsonify({'status': 'success', 'message': 'Data saved'}), 200

@app.route('/')
def index():
    return redirect('/main')

dropdown = html.Div(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    'Last Song', href='/main/last-song'
                ),
                dbc.DropdownMenuItem(
                    'All Songs', href='/main/all-songs'
                ),
            ],
            label='Navigation',
        ),
        
    ],
    style={
        'margin': 'auto',
        'text-align': 'center'
    }
)

dashboard.layout = html.Div([
    dropdown,
    page_container
])

if __name__ == '__main__':

    init_db()
    # Timer(1, open_browser).start() 
    app.run(host='127.0.0.1', port=8888, debug=True)
    