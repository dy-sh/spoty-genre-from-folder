from spoty.utils import SpotyContext
import spoty.audio_files
import click
from pathlib import Path

GENRES = [
    '90-th',
    'Bel',
    'Breakbeat',
    'Classical',
    'Country',
    'Drum',
    'Electronic',
    'Ethnic',
    'HipHop',
    'Indie',
    'Instrumental',
    'Jazz',
    'Lounge',
    'Old',
    'Opera',
    'Orchestral',
    'Pop',
    'Rap',
    'Rock',
    'Russian',
    'Techno',
]

MOODS = [
    'Angry',
    'Calm',
    'Energetic',
    'Happy',
    'Morose',
    'Nutral',
    'Punchy',
    'Relaxed',
    'Sad',
]


def get_genre(file_name: str):
    path = Path(file_name)
    folder = str(path.parent.absolute())
    for genre in GENRES:
        if genre.upper() in folder.upper():
            return genre
    return None


def get_mood(file_name: str):
    path = Path(file_name)
    folder = str(path.parent.absolute())
    for mood in MOODS:
        if mood.upper() in folder.upper():
            return mood
    return None


@click.group("genre-from-folder")
def genre_from_folder():
    """
The plugin updates Genre and Mood tags in audio files by the name of the parent folder.
To use this plugin, you need to provide a list of genres and moods that are encountered in your library.
If the specified word is found in the folder name, it will be used as a genre or mood.
Edit the plugin code to change the genre and mood list.
    """
    pass


@genre_from_folder.command()
@click.option('--audio', '--a', multiple=True,
              help='Get audio files located at the specified local path. You can specify the audio file name as well.')
@click.option('--no-recursive', '-r', is_flag=True,
              help='Do not search in subdirectories from the specified path.')
def write(
        audio,
        no_recursive
):
    """
Update Genre and Mood tag in audio files from parent folder name.
    """

    all_tags_list = []

    # get csv

    audio_files = []
    tags_list_from_audio = []

    # get audio

    if len(audio) > 0:
        audio_paths = []
        for path in audio:
            if spoty.audio_files.is_audio_file(path):
                if spoty.utils.is_valid_file(path):
                    audio_files.append(path)
            elif spoty.utils.is_valid_path(path):
                audio_paths.append(path)
            else:
                click.echo(f'Cant find path or file: "{path}"', err=True)
                exit()

        file_names = spoty.audio_files.find_audio_files_in_paths(audio_paths, not no_recursive)
        audio_files.extend(file_names)

        tags_list = spoty.audio_files.read_audio_files_tags(audio_files, True, False)
        tags_list = spoty.utils.add_playlist_index_from_playlist_names(tags_list)
        tags_list_from_audio.extend(tags_list)
        all_tags_list.extend(tags_list)

    # genre

    replace_list = []
    for tags in all_tags_list:
        file_name = tags['SPOTY_FILE_NAME']
        genre = get_genre(file_name)
        if genre is None:
            click.echo(f"Cant get genre for file: {file_name}", err=True)
            exit()
        if 'GENRE' not in tags or ('GENRE' in tags and genre != tags['GENRE']):
            replace_list.append(tags)

    if len(replace_list) > 0:
        click.echo()
        click.echo('--------------------------------------------------------------')
        for tags in replace_list:
            file_name = tags['SPOTY_FILE_NAME']
            genre = get_genre(file_name)
            click.echo(f'NEW GENRE: "{genre}" in "{file_name}"')
        if click.confirm(f'Do you want to write GENRE tag in {len(replace_list)} audio files?'):
            for tags in replace_list:
                file_name = tags['SPOTY_FILE_NAME']
                genre = get_genre(file_name)
                new_tags = {}
                new_tags['GENRE'] = genre
                spoty.audio_files.write_audio_file_tags(file_name, new_tags)
                tags['GENRE'] = new_tags['GENRE']

    # mood

    replace_list = []
    for tags in all_tags_list:
        file_name = tags['SPOTY_FILE_NAME']
        mood = get_mood(file_name)
        if mood is not None:
            if 'MOOD' not in tags or ('MOOD' in tags and mood != tags['MOOD']):
                replace_list.append(tags)

    if len(replace_list) > 0:
        click.echo()
        click.echo('--------------------------------------------------------------')
        for tags in replace_list:
            file_name = tags['SPOTY_FILE_NAME']
            mood = get_mood(file_name)
            click.echo(f'NEW MOOD: "{mood}" in "{file_name}"')
        if click.confirm(f'Do you want to write MOOD tag in {len(replace_list)} audio files?'):
            for tags in replace_list:
                file_name = tags['SPOTY_FILE_NAME']
                mood = get_mood(file_name)
                new_tags = {}
                new_tags['MOOD'] = mood
                spoty.audio_files.write_audio_file_tags(file_name, new_tags)
                tags['MOOD'] = new_tags['MOOD']