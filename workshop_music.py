"""Ready-made music backend for the beginner lab; students expose its tempo control.

The starter fixes creation at 120 BPM. Instrument selection and notes still come
from the AI's score. Rendering and changing tempo never start playback.
"""
import copy
import json
import math
import os
from pathlib import Path

DEFAULT_BPM = 120
POINTER = Path(os.environ.get('MCPJAM_WORKSHOP_SONG_POINTER',
                             str(Path(__file__).with_name('generated_music') / 'workshop-latest.json')))


def current_song():
    if not POINTER.exists():
        return None
    from music_arranger import read_project
    return read_project(json.loads(POINTER.read_text(encoding='utf-8'))['song_id'])


def remember(result, source_notes=None):
    POINTER.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(POINTER.read_text(encoding='utf-8')) if POINTER.exists() else {}
    if source_notes is None and previous.get('song_id') == result['song_id']:
        source_notes = previous.get('source_notes')
    POINTER.write_text(json.dumps({'song_id': result['song_id'], 'mp3_path': result['mp3_path'],
                                   'source_notes': source_notes}), encoding='utf-8')
    return result


def create_default_song(title, tracks, notes, genre='original',
                        time_signature_numerator=4, time_signature_denominator=4):
    # Reuse the capable renderer, without exposing its tempo parameter to the host.
    from mcp_server_music import create_song_from_score
    return remember(create_song_from_score(
        title=title, bpm=DEFAULT_BPM, tracks=tracks, notes=notes,
        duration_seconds=30, genre=genre,
        time_signature_numerator=time_signature_numerator,
        time_signature_denominator=time_signature_denominator),
        source_notes=[note.model_dump() for note in notes])


def song_state():
    spec = current_song()
    if spec is None:
        return None
    pointer = json.loads(POINTER.read_text(encoding='utf-8'))
    return {'ok': True, 'bpm': spec['bpm'], 'song_id': spec['song_id'],
            'song_revision': spec['revision'], 'duration_seconds': spec['duration_seconds'],
            'mp3_path': pointer['mp3_path'], 'playing': False,
            'state_source': 'rendered_workshop_song', 'tracks': list(spec['tracks'])}


def change_tempo(bpm):
    # Enforce this again at the backend boundary, even if a caller bypasses the tool.
    if type(bpm) is not int or not 40 <= bpm <= 240:
        raise ValueError('bpm must be an integer between 40 and 240')
    spec = copy.deepcopy(current_song())
    if spec is None:
        raise ValueError('Create a workshop song first')
    # Keep a 30-second output. At slower tempi, crop events past the new endpoint;
    # leave pitches and beat spacing unchanged so this is a real tempo change.
    end = 30 * bpm / 60
    cropped = []
    pointer = json.loads(POINTER.read_text(encoding='utf-8'))
    for entry in pointer.get('source_notes') or spec['notes']:
        for repeat in range(entry.get('repeats', 1)):
            beat = entry['beat'] + repeat * entry.get('every_beats', 4)
            if beat >= end:
                continue
            note = dict(entry, beat=beat, duration=min(entry['duration'], end-beat), repeats=1)
            cropped.append(note)
    spec.update(bpm=bpm, duration_seconds=30, bars=max(1, math.ceil(bpm/8)),
                notes=cropped, revision=spec['revision']+1)
    from music_arranger import validate
    from mcp_server_music import deliver_song
    validate(spec)
    return dict(remember(deliver_song(spec)), ok=True, bpm=bpm)
