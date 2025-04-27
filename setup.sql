DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS albums;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS stream;

CREATE TABLE artists
            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            name STRING,
            stream_count INTEGER DEFAULT 0,
            ms_played INTEGER DEFAULT 0,
            hours INTEGER DEFAULT 0,
            minutes INTEGER DEFAULT 0);
CREATE TABLE albums
            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            artist_id INTEGER REFERENCES artists(id),
            name STRING,
            stream_count INTEGER DEFAULT 0,
            ms_played INTEGER DEFAULT 0,
            hours INTEGER DEFAULT 0,
            minutes INTEGER DEFAULT 0);
CREATE TABLE tracks
            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            album_id INTEGER REFERENCES albums(id),
            artist_id INTEGER REFERENCES artists(id),
            name STRING,
            spotify_uri STRING,
            stream_count INTEGER DEFAULT 0,
            ms_played INTEGER DEFAULT 0,
            hours INTEGER DEFAULT 0,
            minutes INTEGER DEFAULT 0);
CREATE TABLE stream
            (timestamp STRING,
            ms_played INTEGER,
            track_id INTEGER REFERENCES tracks(id),
            skipped INTEGER,
            shuffle INTEGER);
