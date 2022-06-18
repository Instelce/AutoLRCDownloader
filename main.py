import os
import json
import lyricsgenius


def read_json_file(path):
    with open(path, 'r') as f:
        cache = f.read()
        data = json.loads(cache)
    return data


def write_json_file(path, data):
    json_object = json.dumps(data, indent=4)
    with open(path, 'w') as f:
        f.write(json_object)
    return data


def create_txt_file(path, data):
    if not os.path.exists(path):
        with open(path, 'w', encoding="utf-8") as f:
            f.write(data)
            print(f"File created at {path} !")
        return data


def get_artist_album_from_path(start_path):
    dir_path = os.path.dirname(start_path)
    dir_name = dir_path.split('\\')[-1]

    if not '-' in dir_name:
        get_artist_album_from_path(dir_path)
        # print("Oh no", dir_path)
    else:
        # print("Good", dir_path)
        artist = dir_name.split(' - ')[0]
        album = dir_name.split(' - ')[1]
        return (artist, album)


def scan_directory(path):
    content = os.scandir(path)
    songs_data = read_json_file('songs.json')

    for entry in content:
        if entry.is_dir():
            scan_directory(path +'/' + entry.name)

            if '-' in entry.name:
                artist = entry.name.split(' - ')[0]
                album = entry.name.split(' - ')[1]
                
                if not artist in songs_data.keys():
                    print("Create new artist")
                    songs_data[artist] = {}
                    if not album in songs_data[artist].keys():
                        print("Create new album")
                        songs_data[artist][album] = {}
        if entry.is_file():
            songs_data = read_json_file('songs.json')
            name, ext = os.path.splitext(entry.name)

            if ext == '.mp3':
                before_name, real_name = name.split(' - ')
                print(before_name, path)

                real_path = os.path.realpath(path + '/' + entry.name)
                dir_path = os.path.dirname(real_path)
                
                if any(chr.isdigit() for chr in before_name):
                    print("In album")
                    artist, album = get_artist_album_from_path(dir_path)
                else:
                    print("Single")
                    artist = before_name
                    album = 'single'

                # Add artist and album to songs data
                if not artist in songs_data.keys():
                    print("Create new artist")
                    songs_data[artist] = {}
                    songs_data[artist]['single'] = {}
                    if not album in songs_data[artist].keys():
                        print("Create new album")
                        songs_data[artist][album] = {}
                
                songs_data[artist][album][real_name] = path + "/"

                write_json_file('songs.json', songs_data)

# Scan the directory and get all data in songs.json
main_dir = input("Main directory : ")
write_json_file('songs.json', {})
scan_directory(main_dir)

genius = lyricsgenius.Genius("vbJ6FBsP92A5FXgvRbdTzR0325PZ5Xp1JY2B7tjzTzZqjSsmCaJeH1ITiFabGNqw")

songs_data = read_json_file('songs.json')

for artist in songs_data:
    # Get artist
    genius_artist = genius.search_artist(artist, max_songs=1, sort="title", include_features=True)
    for album in songs_data[artist]:
        for track_name, path in songs_data[artist][album].items():
            # Get the song
            song = genius.search_song(track_name, genius_artist.name)

            # Create the .lrc file lyrics 
            if not song is None:
                create_txt_file(str(path+track_name+'.lrc'), str(song.lyrics))