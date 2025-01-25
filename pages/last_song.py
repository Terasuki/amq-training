import sqlite3
import pandas as pd

import dash_bootstrap_components as dbc

from dash import html, dcc, callback, Output, Input, dash_table, register_page

from utilities import get_song_links, get_last_song_matches, get_previously_correct

register_page(__name__)

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

def last_song_previously_correct():
    return html.Div(
        id='last_song_previously_correct',
        style={
            'margin': 'auto',
            'text-align': 'center'
        }
    )

def last_song_previously_played():
    return html.Div(
        dash_table.DataTable(
            id='last_song_previously_played',
            columns=[],
            data=[],
            style_as_list_view=True,
            style_table={
                'width': '100%', 
                'overflowX': 'auto',
                'overflowY': 'auto',
                'border': 'thin lightgrey solid',
            },
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'whiteSpace': 'normal',
                'height': 'auto',
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
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{correct} = 0',
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{correct} is nil',
                    },
                    'backgroundColor': 'gray',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Guess time} is nil && {Answer} is blank',
                    },
                    'backgroundColor': 'gray',
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
          Output('last_song_previously_correct', 'children'), 
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
    ls_anime = html.P(last_song.romaji_title, style={'text-align':'center'}, className='card-text')
    ls_song = html.P(last_song.name, style={'text-align':'center'}, className='card-text')
    ls_artist = html.P(last_song.artist, style={'text-align':'center'}, className='card-text')
    ls_type = html.P(last_song.type, style={'text-align':'center'}, className='card-text')
    ls_difficulty = html.P(last_song.difficulty, style={'text-align':'center'}, className='card-text')
    ls_song_links = html.P([html.A(link['name'], href=link['url'], target='_blank', style={'margin-left': '7px', 'margin-right': '7px', 'text-align':'center'}) for link in links], className='card-text')
    correct_guesses, wrong_guesses, spec_guesses = get_previously_correct(ls_matches)
    ls_previously_correct = html.P(children=[html.Span(correct_guesses, style={'color':'green'}), 
                                             '/',
                                             html.Span(wrong_guesses, style={'color':'red'}),
                                             '/',
                                             html.Span(spec_guesses, style={'color':'gray'})], style={'text-align':'center'}, className='card-text')
    ls_matches_data = ls_matches.to_dict('records')
    ls_matches_columns = [{'name': col, 'id': col} for col in ls_matches.columns]

    return ls_anime, ls_song, ls_artist, ls_type, ls_difficulty, ls_song_links, ls_previously_correct, ls_matches_columns, ls_matches_data

layout = dbc.Container(children=[

            html.H2('Last Song', style={'text-align': 'center'}),

            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Anime', style={'text-align':'center'}, className='card-title'),
                last_song_anime(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Song', style={'text-align':'center'}, className='card-title'),
                last_song_song(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Artist', style={'text-align':'center'}, className='card-title'),
                last_song_artist(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Type', style={'text-align':'center'}, className='card-title'),
                last_song_type(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Links', style={'text-align':'center'}, className='card-title'),
                last_song_links(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('Difficulty', style={'text-align':'center'}, className='card-title'),
                last_song_difficulty(),
            ]), className="shadow-sm mb-1",))),
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5('History', style={'text-align':'center'}, className='card-title'),
                last_song_previously_correct(),   
                last_song_previously_played(),
            ]), className="shadow-sm mb-1",))),
            dcc.Interval(
                id='interval',
                interval=500,
                n_intervals=0
            )
        ], style={
            'padding': '0.5em'
        }),
