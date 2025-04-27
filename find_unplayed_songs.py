import requests
import json
import sqlite3

search_endpoint_url = "https://api.spotify.com/v1/search/"
artist_endpoint_url = "https://api.spotify.com/v1/artists/"
album_endpoint_url  = "https://api.spotify.com/v1/albums/"

headers = {"Content-Type": "application/x-www-form-urlencoded"}

token = json.loads(open("token.json").read())
headers["Authorization"] = "Bearer  " + token["access_token"]


def get_artist(query):
    params = {
        "q": query,
        "type": "artist",
        "limit": 1
    }
    response = requests.get(search_endpoint_url, headers=headers, params=params)
    results = json.loads(response.text)["artists"]["items"][0]
    return {
        "name": results["name"],
        "id": results["uri"].split(":")[-1],
        "pfp": results["images"][0]["url"]
    }

def request_albums(artist_id):
    params = {
        "include_groups": "album, single",
        "market": "IN",
        "limit": 50
    }
    response = requests.get(f"{artist_endpoint_url}{artist_id}/albums", headers=headers, params=params)
    results = json.loads(response.text)
    return results["items"]
    # with open("albums.json", "w") as file:
    #     file.write(json.dumps(results, indent=4))

# all albums available in json["items"]
# tracks of album url = f"{album_endpoint_url}{album_id}/tracks""

def request_tracks(album_id):
    params = {
        "market": "IN",
        "limit": 50
    }
    response = requests.get(f"{album_endpoint_url}{album_id}/tracks", headers=headers, params=params)
    results = json.loads(response.text)
    if results["next"] != None:
        print("Not all songs included...")
    return results["items"]


def ignore(name):
    ignored_phrases = [
        "live" ,
        "memo" ,
        "karaoke" ,
        "long pond studio sessions" ,
    ]
    for phrase in ignored_phrases:
        if phrase in name.lower():
            return True
    return False


def refresh_all_tracks():
    artist = get_artist("Taylor")
    albums = request_albums(artist["id"])
    all_tracks = []
    for album in albums:
        if ignore(album["name"]):
            continue
        album_id = album["uri"].split(":")[-1]
        print(f"Album Name: {album["name"]}")
        tracks = request_tracks(album_id)
        for track in tracks:
            if ignore(track["name"]):
                continue
            if track["name"] not in all_tracks:
                all_tracks.append(track["name"])
            # print(f"  - {track["name"]}")
    with open("tracks.json", "w") as file:
        file.write(json.dumps(all_tracks, indent=4))
    return all_tracks

# all_tracks = refresh_all_tracks()
with open("tracks.json") as file:
    all_tracks = json.loads(file.read())

conn = sqlite3.connect("data.sqlite")
cursor = conn.cursor()

for track in all_tracks:
    search_db = cursor.execute("SELECT name FROM tracks WHERE name IS ?", (track, )).fetchall()
    if not search_db:
        print(track)