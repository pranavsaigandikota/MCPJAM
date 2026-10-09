"""Optional song-making MCP server; the beginner starter remains separate."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
import math
import uuid

from mcp.server.fastmcp import FastMCP
from instrument_catalog import register_instrument_catalog, instrument_catalog, instrument_preset
from music_theory import register_music_theory

from mcp_server_sdk import call_daw
from music_arranger import INSTRUMENTS, new_project, read_project, save_project, render_wav, arrangement, validate, song_duration

mcp = FastMCP('mcpjam-music')
register_instrument_catalog(mcp)
register_music_theory(mcp)
from music_score import ScoreTrack, ScoreNote



@mcp.tool()
def get_state() -> dict:
    """Read observed app state, current song ID/revision, playback, and soundfont engine."""
    return call_daw({'cmd': 'get_state'})


@mcp.tool()
def get_instrument_catalog(query: str = '', kind: str = 'all', offset: int = 0, limit: int = 40) -> dict:
    """Search all 287 GeneralUser GS presets by name/id. kind: all, melodic, drum_kit. Page with offset and limit 1–100. Use returned preset id for score tracks or set_song_track; aliases remain supported."""
    if kind not in {'all', 'melodic', 'drum_kit'} or offset < 0 or not 1 <= limit <= 100:
        raise ValueError('Use a valid kind, nonnegative offset and limit 1–100')
    catalog = instrument_catalog()
    matches = [p for p in catalog['instruments'] if (kind == 'all' or p['kind'] == kind)
               and query.casefold() in (p['name'] + ' ' + p['id']).casefold()]
    return {'total': len(matches), 'offset': offset, 'instruments': matches[offset:offset+limit],
            'aliases': catalog['aliases'], 'next_offset': offset+limit if offset+limit < len(matches) else None}


@mcp.tool()
def create_song_from_score(title: str, bpm: int, tracks: list[ScoreTrack], notes: list[ScoreNote],
                           duration_seconds: float = 30, genre: str = 'original',
                           time_signature_numerator: int = 4, time_signature_denominator: int = 4) -> dict:
    """Generate an original AI-authored instrumental MP3 for any genre description. YOU choose every pitch, rhythm, chord, track and preset; no preset melody/progression is inserted. Duration 5–180 sec, BPM 40–240, 1–16 unique channels (9 is drums), at most 5000 expanded notes. Notes use quarter-note beats and durations; time signature supports 1–12 over 2/4/8/16; repeats/every_beats compact a motif. Develop contrasting sections by adding notes at later beats. Same-pitch overlaps on one track are rejected. Search get_instrument_catalog for sounds. No vocals/audio cloning. Return the MP3 path; never autoplay. MIDI/WAV remain internal."""
    spec = {'song_id': uuid.uuid4().hex, 'title': title, 'bpm': bpm, 'key': 'C',
            'bars': max(1, math.ceil(duration_seconds * bpm / 240)),
            'duration_seconds': duration_seconds, 'style': 'pop', 'genre': genre,
            'score': 'custom', 'swing': 0, 'revision': 1,
            'time_signature_numerator': time_signature_numerator, 'time_signature_denominator': time_signature_denominator,
            'tracks': {track.name: track.model_dump(exclude={'name'}) for track in tracks},
            'notes': [note.model_dump() for note in notes]}
    if len(spec['tracks']) != len(tracks):
        raise ValueError('Track names must be unique')
    if not 1 <= len(genre) <= 120:
        raise ValueError('genre must contain 1–120 characters')
    validate(spec)  # Reject the entire score before saving or changing playback.
    return deliver_song(spec)


@mcp.tool()
def replace_song_notes(notes: list[ScoreNote], song_id: str = '') -> dict:
    """Rewrite an AI-authored score's notes while retaining tracks, tempo and duration. Use for changes to melody, chords, rhythm, structure or phrasing; notes are beat-based. Preset songs use edit_song instead. Rejects invalid notes before changing the saved project or playback."""
    spec = copy.deepcopy(current_project(song_id))
    if spec.get('score') != 'custom':
        raise ValueError('Use create_song_from_score first for freely editable notes')
    spec['notes'] = [note.model_dump() for note in notes]
    validate(spec)
    spec['revision'] += 1
    return deliver_song(spec)


def current_project(song_id):
    if not song_id:
        latest = Path(__file__).with_name('generated_music') / 'latest.json'
        if not latest.is_file():
            raise ValueError('Generate a song first or supply song_id')
        song_id = json.loads(latest.read_text(encoding='utf-8'))['song_id']
    return read_project(song_id)


def play_project(spec):
    state = get_state()
    if state.get('audio_engine') != 'generaluser_gs':
        raise RuntimeError('GeneralUser GS is not active. Install requirements-audio.txt, run setup_audio.py, then restart the app.')
    events, _ = arrangement(spec)
    if spec.get('sample_pack') == 'modern808':
        rendered = subprocess.run([sys.executable, '-u', str(Path(__file__).with_name('render_song.py')), spec['song_id']],
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                  cwd=Path(__file__).resolve().parent, timeout=60)
        if rendered.returncode:
            raise RuntimeError('Sample render failed: ' + rendered.stderr[-1000:])
        audio = json.loads(rendered.stdout)
        call_daw({'cmd':'play_wav','wav_path':audio['wav_path'],'title':spec['title'],
                  'song_id':spec['song_id'],'revision':spec['revision'],
                  'duration_seconds':song_duration(spec),'bpm':spec['bpm'],
                  'song_tracks':spec['tracks'],'song_engine':audio['audio_engine']})
        state = get_state()
        if state.get('song_id') != spec['song_id'] or not state.get('timeline_active'):
            raise RuntimeError('Sample playback was not observed. Use background music chat.')
        return {'playback':'observed','audio_engine':audio['audio_engine'],'song_id':spec['song_id'],'revision':spec['revision']}
    call_daw({'cmd': 'play_midi_raw', 'events': events, 'title': spec['title'],
              'song_id': spec['song_id'], 'revision': spec['revision'], 'bpm': spec['bpm'],
              'duration_seconds': song_duration(spec), 'articulation': spec.get('articulation', 'legato'),
              'song_tracks': spec['tracks']})
    deadline = time.monotonic()+5
    while time.monotonic() < deadline:
        state = get_state()
        if state.get('song_id') == spec['song_id'] and state.get('song_revision') == spec['revision'] and state.get('timeline_active'):
            return {'playback': 'observed', 'audio_engine': state['audio_engine'], 'song_id': spec['song_id'], 'revision': spec['revision']}
        time.sleep(.05)
    raise RuntimeError('Song was queued but playback was not observed; inspect get_state before retrying')



def render_mp3(spec):
    rendered = subprocess.run([sys.executable, '-u', str(Path(__file__).with_name('render_song.py')), spec['song_id'], '--mp3'],
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parent, timeout=60)
    if rendered.returncode:
        raise RuntimeError('MP3 render failed: ' + rendered.stderr[-1000:])
    return json.loads(rendered.stdout)


def deliver_song(spec):
    # Save MIDI for internal sequencing, then render and encode before claiming success.
    result = save_project(spec)
    result.pop('midi_path', None)
    result.update(render_mp3(spec))
    # Generating or editing a file never starts the audio player.
    result['status'] = 'generated'
    result['file_size_bytes'] = Path(result['mp3_path']).stat().st_size
    latest = Path(__file__).with_name('generated_music') / 'latest.json'
    latest.write_text(json.dumps({'song_id': spec['song_id']}), encoding='utf-8')
    return result


@mcp.tool()
def create_pop_song(title: str = 'MCPJAM Pop', bpm: int = 112, key: str = 'C', bars: int = 32,
                    duration_seconds: float | None = 30, articulation: str = 'legato', style: str = 'pop',
                    hold_notes: bool = False, dynamics: str = 'flat') -> dict:
    """Generate an original instrumental MP3 with phrases, dynamics, and held notes. Style pop or rnb (minor seventh chords and a syncopated half-time groove). Set duration_seconds (5–180) for exact length, e.g. 30; otherwise bars (8–64). BPM 40–240, tonic C/D/F#/Bb etc. Articulation legato/normal/staccato. Set hold_notes true for longer connected melodic notes. Set dynamics to flat, crescendo, decrescendo, or swell. Uses GeneralUser GS piano, guitar, bass, strings, drums. Returns editable song_id and MP3 path; no vocals or autoplay."""
    spec = new_project(title, bpm, key, bars, duration_seconds, articulation, style, hold_notes, dynamics)
    return deliver_song(spec)


@mcp.tool()
def create_bossa_song(title: str = 'Seaside Circuit', bpm: int = 112, key: str = 'C', duration_seconds: float = 30) -> dict:
    """Generate an MP3 of original playful racing-game-style bossa nova: nylon guitar syncopation, piano melody, light shaker/rim percussion and quiet root/fifth finger bass. Uses GeneralUser GS. No copied game melody. Exact duration 5–180, BPM 40–240, supported tonic key. Bass defaults to 35/100; edit with set_song_track."""
    spec=new_project(title,bpm,key,16,duration_seconds,'normal','pop')
    spec.update(score='bossa',swing=0)
    for track,instrument,volume in [('keys','piano',58),('lead','piano',68),('pad','nylon_guitar',74),('bass','finger_bass',35),('drums','piano',52)]:
        spec['tracks'][track].update(instrument=instrument,volume=volume,muted=False)
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def create_funk_song(title: str = 'Gold Rush', bpm: int = 112, key: str = 'E', duration_seconds: float = 30) -> dict:
    """Generate an MP3 of original upbeat funk-pop with soft sampled finger bass, syncopated electric piano, clipped acoustic guitar chords, brass call/response and modern sampled drums. No copied song melody/lyrics. Duration 5–180 seconds, BPM 40–240, supported tonic key. No player is required for MP3 generation."""
    spec = new_project(title,bpm,key,16,duration_seconds,'normal','pop')
    spec.update(score='funk_pop',sample_pack='modern808',sample_bass=False,swing=4)
    for track,instrument,volume in [('keys','electric_piano',68),('lead','trumpet',55),('pad','acoustic_guitar',52),('bass','finger_bass',38),('drums','piano',78)]:
        spec['tracks'][track].update(instrument=instrument,volume=volume,muted=False)
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def create_composed_song(title: str = 'Nightfall', bpm: int = 128, key: str = 'D') -> dict:
    """Generate an MP3 of a deliberately scored original 16-bar dark piano/808 arrangement: connected chord voicings, question/answer melody, rests, dynamics, restrained dance groove and breakdown. GS piano/strings plus modern808 samples. 30 seconds at 128 BPM; tempo changes adjust duration. BPM 40–240, supported tonic key. No player is required for MP3 generation."""
    spec = new_project(title,bpm,key,16,None,'normal','edm')
    spec.update(sample_pack='modern808',score='dark_piano_16',energy=75,swing=0)
    for track,instrument,volume in [('keys','piano',65),('lead','piano',66),('pad','strings',38),('bass','finger_bass',40),('drums','piano',82)]:
        spec['tracks'][track].update(instrument=instrument,volume=volume,muted=False)
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def create_orchestral_song(title: str = 'Feral Ascent', bpm: int = 155, key: str = 'D', duration_seconds: float = 30, mood: str = 'dramatic') -> dict:
    """Generate an MP3 of an original cinematic orchestral instrumental with layered violin, cello, piano ostinato, sustained strings, and dynamic climax. Mood can be dramatic or happy. Duration 5-180 seconds, BPM 40-240."""
    spec = new_project(title, bpm, key, 32, duration_seconds, 'legato', 'pop', True, 'swell')
    spec.update(score='orchestral', sample_pack='generaluser_gs', swing=0, mood=mood)
    for track, instrument, volume in [('keys', 'piano', 68), ('lead', 'violin', 74),
                                      ('pad', 'strings', 64), ('bass', 'cello', 56),
                                      ('drums', 'piano', 68)]:
        spec['tracks'][track].update(instrument=instrument, volume=volume, muted=False)
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def create_808_song(title: str = 'Blackout', bpm: int = 128, key: str = 'D',
                    duration_seconds: float = 30, energy: int = 80) -> dict:
    """Create a restrained dark dance beat using the modern808 hard-trap WAV pack for tuned sub bass and drums, with GS piano/strings atmosphere. No GS synth lead or electric-guitar lead. No player is required for MP3 generation. Duration 5–180, energy 0–100, BPM 40–240. Live playback and export use the same rendered sample mix."""
    spec = new_project(title,bpm,key,32,duration_seconds,'normal','edm')
    spec.update(sample_pack='modern808',energy=energy,variation=0,swing=0)
    spec['tracks']['lead']['muted'] = True
    spec['tracks']['keys']['volume'] = 38
    spec['tracks']['pad']['volume'] = 30
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def create_edm_song(title: str = 'Midnight Pursuit', bpm: int = 132, key: str = 'D',
                    duration_seconds: float = 30, energy: int = 85, variation: int = 0) -> dict:
    """Generate an MP3 of original cinematic EDM: minor-key riffs, four-on-floor kick, syncopated bass, tom layers, snare builds, drops and breakdown. All sounds GeneralUser GS. Duration 5–180 seconds (subject to 64-bar limit), BPM 40–240, energy/variation 0–100. Variation changes melodic accents; energy controls drum density. No copied melody or vocals."""
    spec = new_project(title, bpm, key, 32, duration_seconds, 'normal', 'edm')
    spec.update(energy=energy, variation=variation, swing=0)
    spec['tracks']['bass']['instrument'] = 'synth_bass'
    spec['tracks']['lead']['instrument'] = 'electric_guitar'
    validate(spec)
    return deliver_song(spec)


@mcp.tool()
def edit_song(song_id: str = '', bpm: int | None = None, key: str | None = None,
              bars: int | None = None, swing: int | None = None, title: str | None = None,
              duration_seconds: float | None = None, articulation: str | None = None, style: str | None = None,
              energy: int | None = None, variation: int | None = None,
              piano_motion: str | None = None, hold_notes: bool | None = None,
              dynamics: str | None = None, mood: str | None = None,
              melody_style: str | None = None) -> dict:
    """Edit tempo, key, duration_seconds (5-180), bars (8-64), swing (0-75), title, articulation (legato/normal/staccato), style (pop/rnb/edm), EDM energy/variation (0-100), funk piano_motion (chords/up_down), hold_notes, dynamics (flat/crescendo/decrescendo/swell), orchestral mood (dramatic/happy), or melody_style (smooth/jumpy). Render an updated MP3 without autoplay. For AI scores, only tempo, title and duration apply; use replace_song_notes for musical changes."""
    spec = copy.deepcopy(current_project(song_id))
    if spec.get("score") == "custom" and any(value is not None for value in (key, bars, swing, articulation, style, energy, variation, piano_motion, hold_notes, dynamics, mood, melody_style)):
        raise ValueError("For an AI score, edit note pitches/timing/velocity with replace_song_notes; preset controls do not change its music")
    if bars is not None and duration_seconds is None:
        spec['duration_seconds'] = None
    for field, value in [('bpm', bpm), ('key', key), ('bars', bars), ('swing', swing), ('title', title),
                         ('duration_seconds', duration_seconds), ('articulation', articulation), ('style', style),
                         ('energy', energy), ('variation', variation), ('piano_motion', piano_motion),
                         ('hold_notes', hold_notes), ('dynamics', dynamics), ('mood', mood),
                         ('melody_style', melody_style)]:
        if value is not None:
            spec[field] = value
    validate(spec)
    spec['revision'] += 1
    return deliver_song(spec)


@mcp.tool()
def set_song_track(track: str, song_id: str = '', instrument: str | None = None,
                   muted: bool | None = None, volume: int | None = None) -> dict:
    """Edit an existing song track, render an updated MP3 without autoplay. Preset songs use keys/bass/pad/lead/drums; AI scores use their supplied track names. Select any compatible preset id from get_instrument_catalog, including drum kits on channel 9; named aliases remain valid. Volume 0–100, mute true/false. Changing sampled bass/drums to a GS preset disables that sample override so your selected sound is audible."""
    spec = copy.deepcopy(current_project(song_id))
    if track not in spec['tracks']:
        raise ValueError('Choose a track name from the saved song')
    if instrument is not None:
        drums = spec['tracks'][track].get('channel', 9 if track == 'drums' else 0) == 9
        if drums and instrument == 'piano':
            raise ValueError('Select a drum_kit preset, not a melodic piano alias')
        instrument_preset(instrument, drums)
        if spec.get('sample_pack') and track in {'bass', 'drums'}:
            spec['sample_bass' if track == 'bass' else 'sample_drums'] = False
            if not spec.get('sample_bass', True) and not spec.get('sample_drums', True):
                spec.pop('sample_pack')
        spec['tracks'][track]['instrument'] = instrument
    if muted is not None:
        spec['tracks'][track]['muted'] = muted
    if volume is not None:
        spec['tracks'][track]['volume'] = volume
    validate(spec)
    spec['revision'] += 1
    return deliver_song(spec)


@mcp.tool()
def play_song(song_id: str = '') -> dict:
    """Replay a saved song from the start using GeneralUser GS. Empty ID uses the current song."""
    return play_project(current_project(song_id))


@mcp.tool()
def stop_song() -> dict:
    """Stop song playback and verify that the app is stopped."""
    call_daw({'cmd': 'stop'})
    deadline = time.monotonic()+5
    while time.monotonic() < deadline:
        state = get_state()
        if not state.get('timeline_active') and not state['playing']:
            return {'stopped': True}
        time.sleep(.05)
    raise RuntimeError('Stop was queued but not observed')


@mcp.tool()
def pause_song() -> dict:
    """Pause the current song and silence held notes. Resume with resume_song."""
    call_daw({'cmd': 'pause'})
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = get_state()
        if state.get('timeline_paused') or not state.get('timeline_active'):
            return {'paused': True, 'position_seconds': state.get('song_position_seconds', 0)}
        time.sleep(.05)
    raise RuntimeError('Pause was not observed')


@mcp.tool()
def resume_song() -> dict:
    """Resume a paused song at its position, including notes held at the pause."""
    if not get_state().get('timeline_active'):
        return play_song()
    call_daw({'cmd': 'play'})
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = get_state()
        if state.get('timeline_active') and not state.get('timeline_paused'):
            return {'playing': True, 'position_seconds': state.get('song_position_seconds', 0)}
        time.sleep(.05)
    raise RuntimeError('Resume was not observed')


@mcp.tool()
def export_song(song_id: str = '') -> dict:
    """Export the current/supplied song as a playable 192-kbps stereo MP3. MIDI and WAV are internal backend files. Does not change playback. Returns the local MP3 file path."""
    spec = current_project(song_id)
    result = save_project(spec)
    result.pop('midi_path', None)
    result.update(render_mp3(spec))
    return result


if __name__ == '__main__':
    mcp.run()
