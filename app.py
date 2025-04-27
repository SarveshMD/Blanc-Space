import sqlite3
import json
from os import listdir

conn = sqlite3.connect("data.sqlite")
cursor = conn.cursor()

def ms_to_hours_minutes(ms):
    minutes = (ms // 60000) % 60
    hours = ms // 3600000
    return hours, minutes

# drop existing tables and create new tables
def reset_tables():
    with open("setup.sql") as script:
        cursor.executescript(script.read())

reset_tables()

files = []

ls = listdir("./extended_streaming_history")
print("JSON Files Read: ")
for item in ls:
    if item.endswith(".json"):
        path = f"extended_streaming_history/{item}"
        print(f"  - {path}")
        files.append(path)

if input("\nSample Data? "):
    files = ["extended_streaming_history/sample.json"]

total_streaming_history = []
for file in files:
    sample = json.loads(open(file, encoding="utf8").read())
    for track in sample:
        total_streaming_history.append(track)

total_artists = total_albums = total_tracks = total_stream_count = total_ms_played = 0

for line in total_streaming_history:
    artist = line['master_metadata_album_artist_name']
    database_artist = cursor.execute("SELECT name FROM artists WHERE name IS ?", (artist, )).fetchone()
    if database_artist is None:
        # print("New Artist", artist)
        total_artists += 1
        cursor.execute("INSERT INTO artists (name) VALUES (?)", (artist,))

    album = line['master_metadata_album_album_name']
    database_album = cursor.execute("SELECT name FROM albums WHERE name IS ?", (album, )).fetchone()
    if database_album is None:
        artist_id = cursor.execute("SELECT id FROM artists WHERE name IS ?", (artist, )).fetchone()[0]
        # print("New Album", album)
        total_albums += 1
        cursor.execute("INSERT INTO albums (name, artist_id) VALUES (?, ?)", (album, artist_id,))

    track = line['master_metadata_track_name']
    try:
        uri = line['spotify_track_uri'].split(':')[2]
    except AttributeError:
        uri = "None"
    database_track = cursor.execute("SELECT name FROM tracks WHERE name IS ?", (track, )).fetchone()
    if database_track is None:
        album_id, artist_id = cursor.execute("SELECT id, artist_id FROM albums WHERE name IS ?", (album, )).fetchone()
        # print("New Track", track)
        total_tracks += 1
        cursor.execute("INSERT INTO tracks (name, album_id, artist_id,  spotify_uri) VALUES (?, ?, ?, ?)", (track, album_id, artist_id, uri,))

    timestamp = line['ts']
    ms_played = line['ms_played']
    track_id, album_id, artist_id,  track_stream_count, track_ms_played = cursor.execute("SELECT id, album_id, artist_id, stream_count, ms_played FROM tracks WHERE name IS ?", (track, )).fetchone()
    album_stream_count, album_ms_played = cursor.execute("SELECT stream_count, ms_played FROM albums WHERE id IS ?", (album_id, )).fetchone()
    artist_stream_count, artist_ms_played = cursor.execute("SELECT stream_count, ms_played FROM artists WHERE id IS ?", (artist_id, )).fetchone()
    if ms_played >= 30000:
        total_stream_count += 1
        track_stream_count += 1
        album_stream_count += 1
        artist_stream_count += 1
        total_ms_played += ms_played
        track_ms_played += ms_played
        album_ms_played += ms_played
        artist_ms_played += ms_played
        cursor.execute("UPDATE tracks SET stream_count = ?, ms_played = ? WHERE id IS ?", (track_stream_count, track_ms_played, track_id))
        cursor.execute("UPDATE albums SET stream_count = ?, ms_played = ? WHERE id IS ?", (album_stream_count, album_ms_played, album_id))
        cursor.execute("UPDATE artists SET stream_count = ?, ms_played = ? WHERE id IS ?", (artist_stream_count, artist_ms_played, artist_id))
    skipped = line['skipped']
    shuffle = line['shuffle']
    cursor.execute('''INSERT INTO stream (timestamp, ms_played, track_id, skipped, shuffle)
                   VALUES (?, ?, ?, ?, ?)''', (timestamp, ms_played, track_id, skipped, shuffle))

conn.commit()

print(f"Total Artists: {total_artists}")
print(f"Total Albums: {total_albums}")
print(f"Total Tracks: {total_tracks}")
print(f"Total Stream Count: {total_stream_count}")
total_hours, total_minutes = ms_to_hours_minutes(total_ms_played)
print(f"Total Stream Time: {total_hours} hours, {total_minutes} minutes")

tracks = cursor.execute("SELECT id, ms_played FROM tracks WHERE ms_played > 0").fetchall()
for track_id, ms_played in tracks:
    hours, minutes = ms_to_hours_minutes(ms_played)
    cursor.execute("UPDATE tracks SET hours = ?, minutes = ? WHERE id IS ?", (hours, minutes, track_id))

albums = cursor.execute("SELECT id, ms_played FROM albums WHERE ms_played > 0").fetchall()
for album_id, ms_played in albums:
    hours, minutes = ms_to_hours_minutes(ms_played)
    cursor.execute("UPDATE albums SET hours = ?, minutes = ? WHERE id IS ?", (hours, minutes, album_id))

artists = cursor.execute("SELECT id, ms_played FROM artists WHERE ms_played > 0").fetchall()
for artist_id, ms_played in artists:
    hours, minutes = ms_to_hours_minutes(ms_played)
    cursor.execute("UPDATE artists SET hours = ?, minutes = ? WHERE id IS ?", (hours, minutes, artist_id))

conn.commit()
