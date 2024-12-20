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
from dash import Dash, html, dcc, callback, Output, Input, dash_table
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

def get_song_links(row):
    site_ids = json.loads(row.get('site_ids')[0])
    
    links = [
        {
            'name': 'AniList',
            'url': f"https://anilist.co/anime/{site_ids.get('aniListId')}"
        },
        {
            'name': 'MAL',
            'url': f"https://myanimelist.net/anime/{site_ids.get('malId')}"
        },
        {
            'name': 'Kitsu',
            'url': f"https://kitsu.io/anime/{site_ids.get('kitsuId')}"
        },
        {
            'name': 'ANN',
            'url': f"https://www.animenewsnetwork.com/encyclopedia/anime.php?id={site_ids.get('annId')}"
        }
    ]
    return links

def get_last_song_matches(row, conn):

    def format_seconds(seconds_raw):
        minutes = int(seconds_raw // 60)
        seconds = int(seconds_raw % 60)
        return f'{minutes}:{seconds:02}' 

    song_name = row['name'][0]
    song_artist = row['artist'][0]
    matches_query = """
            SELECT timestamp, game_mode, difficulty, self_answer, guess_time, start_sample, video_length, ann_id, correct
            FROM amq_data 
            WHERE name = ? AND artist = ?
            ORDER BY timestamp
        """
    matches = pd.read_sql_query(matches_query, conn, params=(song_name, song_artist))
    matches['timestamp'] = pd.to_datetime(matches['timestamp']).dt.strftime('%d/%m/%y, %H:%M')

    matches['Sample'] = matches['start_sample'].apply(format_seconds) + '/' + matches['video_length'].apply(format_seconds)
    matches = matches.drop(['start_sample', 'video_length'], axis=1).rename(columns={'timestamp':'Date', 
                                                                                     'game_mode':'Gamemode', 
                                                                                     'difficulty':'Diff.',
                                                                                     'self_answer':'Answer',
                                                                                     'guess_time':'Guess time',
                                                                                     'ann_id':'ANNID'})
    return matches

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
        id='last_song_links',
        style={
            'margin': 'auto',
            'text-align': 'center'
        }
    )

def last_song_difficulty():
    return html.Div(
        id='last_song_difficulty'
    )

def last_song_previously_played():
    return html.Div(
        dash_table.DataTable(
            id='last_song_previously_played',
            columns=[],
            data=[],
            style_table={
                'width': '100%', 
                'overflowX': 'auto',
                'overflowY': 'auto'
            },
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{correct} = 1',
                    },
                    'backgroundColor': 'green',
                    'color': 'black'
                },
                {
                    'if': {
                        'filter_query': '{correct} = 0',
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },
                {'if': {'column_id': 'correct',},
                'display': 'None',}
            ],
            style_header_conditional=[
                {'if': {'column_id': 'correct',},
                    'display': 'None',}]
        ),
        style={
            'margin': 'auto',
            'text-align': 'center'
        }
    )

@callback(Output('last_song_anime', 'children'), 
          Output('last_song_song', 'children'), 
          Output('last_song_artist', 'children'), 
          Output('last_song_type', 'children'), 
          Output('last_song_difficulty', 'children'), 
          Output('last_song_links', 'children'), 
          Output('last_song_previously_played', 'columns'), 
          Output('last_song_previously_played', 'data'), 
          Input('interval', 'n_intervals'))
def update(n):
    conn = sqlite3.connect('data.db')
    query = 'SELECT * FROM amq_data ORDER BY timestamp DESC LIMIT 1'
    last_song = pd.read_sql_query(query, conn)
    ls_matches = get_last_song_matches(last_song, conn)
    conn.close()

    links = get_song_links(last_song)
    ls_anime = html.P(last_song.romaji_title, style={'margin-left':'3%', 'text-align':'center'})
    ls_song = html.P(last_song.name, style={'margin-left':'3%', 'text-align':'center'})
    ls_artist = html.P(last_song.artist, style={'margin-left':'3%', 'text-align':'center'})
    ls_type = html.P(last_song.type, style={'margin-left':'3%', 'text-align':'center'})
    ls_difficulty = html.P(last_song.difficulty, style={'margin-left':'3%', 'text-align':'center'})
    ls_song_links = html.P([html.A(link['name'], href=link['url'], target='_blank', style={'margin-left': '15px', 'text-align':'center'}) for link in links])
    ls_matches_data = ls_matches.to_dict('records')
    ls_matches_columns = [{'name': col, 'id': col} for col in ls_matches.columns]

    return ls_anime, ls_song, ls_artist, ls_type, ls_difficulty, ls_song_links, ls_matches_columns, ls_matches_data

dashboard.layout = dbc.Container(
    [
        dbc.Col(children=[
            html.H2('Last Song Played', style={'text-align': 'center'},),
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
            last_song_links(),
            html.P('Difficulty', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_difficulty(),
            html.P('Previously played', style={'margin-left':'3%', 'text-align':'center'}),
            last_song_previously_played(),
        ], style={
            'position':'fixed',
            'left':'0',
            'width':'30%',
            'height':'100%',
            'background-color':'#B8B8B8'
        }),
        dbc.Col([
            app_description(),
        ], style={
            'width':'70%',
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
    