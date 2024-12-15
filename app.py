import json
import sqlite3
import pandas as pd
import numpy as np
import webbrowser

from datetime import datetime
from threading import Timer

import plotly.express as px
import dash_bootstrap_components as dbc

from flask import Flask, request, jsonify, redirect
from flask_cors import cross_origin
from dash import Dash, html, dcc, callback, Output, Input
from dash_bootstrap_templates import load_figure_template

app = Flask(__name__)

dashboard = Dash(
    __name__,
    server=app,
    url_base_pathname='/main/',
    external_stylesheets=[dbc.themes.DARKLY],
    update_title=None
)

dashboard.title = 'AMQ Song List'
load_figure_template('DARKLY')

def open_browser():

    webbrowser.open_new('http://127.0.0.1:8888/main/')
    webbrowser.open_new_tab('https://animemusicquiz.com/')

def init_db():
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
                position INTEGER,
                rig_type TEXT,
                rig_score INTEGER
            );
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['POST'])
@cross_origin(origin='*')
def receive_data():
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
            alt_answers, site_ids, start_sample, video_length, correct, self_answer,
            position, rig_type, rig_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

def app_description():
    return html.Div(
        id='app-description',
        children=[
            html.H2('Ranked Statistics'),
        ]
    )

def last_song_anime():
    return html.Div(
        id='last_song_anime'
    )

def last_song_song():
    return html.Div(
        id='last_song_song'
    )

def last_song_artist():
    return html.Div(
        id='last_song_artist'
    )

def last_song_type():
    return html.Div(
        id='last_song_type'
    )

def last_song_links():
    return html.Div(
        id='last_song_links'
    )

def last_song_difficulty():
    return html.Div(
        id='last_song_difficulty'
    )

def last_song_previously_played():
    return html.Div(
        id='last_song_previously_played'
    )

@callback(Output('last_song_anime', 'children'), 
          Output('last_song_song', 'children'), 
          Output('last_song_artist', 'children'), 
          Output('last_song_type', 'children'), 
          Output('last_song_difficulty', 'children'), 
          Output('last_song_previously_played', 'children'), 
          Input('interval', 'n_intervals'))
def update(n):
    conn = sqlite3.connect('data.db')
    query = 'SELECT * FROM amq_data ORDER BY timestamp DESC LIMIT 1'
    last_song = pd.read_sql_query(query, conn)
    conn.close()
    ls_anime = html.P(last_song.romaji_title, style={'margin-left':'3%', 'text-align':'center'})
    ls_song = html.P(last_song.name, style={'margin-left':'3%', 'text-align':'center'})
    ls_artist = html.P(last_song.artist, style={'margin-left':'3%', 'text-align':'center'})
    ls_type = html.P(last_song.type, style={'margin-left':'3%', 'text-align':'center'})
    ls_difficulty = html.P(last_song.difficulty, style={'margin-left':'3%', 'text-align':'center'})
    ls_previously_played = html.P(last_song.difficulty, style={'margin-left':'3%', 'text-align':'center'})
    return ls_anime, ls_song, ls_artist, ls_type, ls_difficulty, ls_previously_played

dashboard.layout = dbc.Container(
    [
        dbc.Col(children=[
            html.H2('Last Song Played', style={'margin-left':'3%'},),
            html.Hr(),
            html.P('Anime', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_anime(),
            html.P('Song', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_song(),
            html.P('Artist', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_artist(),
            html.P('Type', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_type(),
            html.P('Links', style={'margin-left':'3%', 'text-align':'center'}),
            html.P('Difficulty', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_difficulty(),
            html.P('Previously played', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_previously_played(),
        ], style={
            'position':'fixed',
            'left':'0',
            'width':'20%',
            'height':'100%',
            'background-color':'#B8B8B8'
        }),
        dbc.Col([
            app_description(),
        ], style={
            'width':'80%',
            'float':'right',
            'margin-top':'10px'
        }),
        dcc.Interval(
            id='interval',
            interval=500, # in milliseconds
            n_intervals=0
        )
    ]
)

if __name__ == '__main__':

    init_db()
    # Timer(1, open_browser).start() 
    app.run(host='127.0.0.1', port=8888, debug=True)
    