import json
import pandas as pd
import sqlite3
from typing import List, Dict, Tuple

def format_seconds(seconds_raw: float) -> str:
        minutes = int(seconds_raw // 60)
        seconds = int(seconds_raw % 60)
        return f'{minutes}:{seconds:02}' 

def get_song_links(row: pd.DataFrame) -> List[Dict]:
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

def get_last_song_matches(row: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:

    song_name = row['name'][0]
    song_artist = row['artist'][0]
    matches_query = """
            SELECT timestamp, game_mode, difficulty, self_answer, guess_time, start_sample, video_length, ann_id, correct
            FROM amq_data 
            WHERE name = ? AND artist = ?
            ORDER BY timestamp DESC
        """
    matches = pd.read_sql_query(matches_query, conn, params=(song_name, song_artist))
    matches['timestamp'] = pd.to_datetime(matches['timestamp']).dt.strftime('%d/%m/%y, %H:%M')

    matches['Sample'] = matches['start_sample'].apply(format_seconds) + '/' + matches['video_length'].apply(format_seconds)
    matches = matches.drop(['start_sample', 'video_length'], axis=1).rename(columns={'timestamp':'Date', 
                                                                                     'game_mode':'Mode', 
                                                                                     'difficulty':'Diff.',
                                                                                     'self_answer':'Answer',
                                                                                     'guess_time':'Guess time',
                                                                                     'ann_id':'ANNID'})
    
    matches = matches[['Date', 'Mode', 'ANNID', 'Diff.', 'Guess time', 'Answer', 'correct']]
    return matches

def get_previously_correct(matches: pd.DataFrame) -> Tuple[int, int, int]:

    n_guesses = matches.shape[0]
    correct_guesses = matches.loc[matches['correct'] == 1].shape[0]
    spec_matches = matches.loc[(matches['correct'] == None) | ((matches['Guess time'] == None) & (matches['Answer'] == '\n\t\t\t\t\t\n\t\t\t\t'))]
    spec_guesses = spec_matches.shape[0]
    wrong_guesses = n_guesses - correct_guesses - spec_guesses
    return correct_guesses, wrong_guesses, spec_guesses
