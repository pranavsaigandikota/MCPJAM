"""Optional song-making MCP server; the beginner starter remains separate."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

from mcp.server.fastmcp import FastMCP

from mcp_server_sdk import call_daw
from music_arranger import INSTRUMENTS, new_project, read_project, save_project, render_wav, arrangement, validate, song_duration

mcp = FastMCP('mcpjam-music')


@mcp.tool()
def get_state() -> dict:
    """Read observed app state, current song ID/revision, playback, and soundfont engine."""
    return call_daw({'cmd': 'get_state'})


def current_project(song_id):
    return read_project(song_id or get_state().get('song_id', ''))


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


@mcp.tool()
def create_pop_song(title: str = 'MCPJAM Pop', bpm: int = 112, key: str = 'C', bars: int = 32,
                    duration_seconds: float | None = None, articulation: str = 'legato', style: str = 'pop') -> dict:
    """Create and play original instrumental music with phrases, dynamics, and held notes. Style pop or rnb (minor seventh chords and a syncopated half-time groove). Set duration_seconds (5–180) for exact length, e.g. 30; otherwise bars (8–64). BPM 40–240, tonic C/D/F#/Bb etc. Articulation legato/normal/staccato. Uses GeneralUser GS piano, guitar, bass, strings, drums. Returns editable song_id and MIDI; no vocals."""
    spec = new_project(title, bpm, key, bars, duration_seconds, articulation, style)
    result = save_project(spec)
    result.update(play_project(spec))
    return result


@mcp.tool()
def create_808_song(title: str = 'Blackout', bpm: int = 128, key: str = 'D',
                    duration_seconds: float = 30, energy: int = 80) -> dict:
    """Create a restrained dark dance beat using the modern808 hard-trap WAV pack for tuned sub bass and drums, with GS piano/strings atmosphere. No GS synth lead or electric-guitar lead. Requires background player. Duration 5–180, energy 0–100, BPM 40–240. Live playback and export use the same rendered sample mix."""
    spec = new_project(title,bpm,key,32,duration_seconds,'normal','edm')
    spec.update(sample_pack='modern808',energy=energy,variation=0,swing=0)
    spec['tracks']['lead']['muted'] = True
    spec['tracks']['keys']['volume'] = 38
    spec['tracks']['pad']['volume'] = 30
    validate(spec)
    result = save_project(spec)
    result.update(play_project(spec))
    return result


@mcp.tool()
def create_edm_song(title: str = 'Midnight Pursuit', bpm: int = 132, key: str = 'D',
                    duration_seconds: float = 30, energy: int = 85, variation: int = 0) -> dict:
    """Create/play original cinematic EDM: minor-key riffs, four-on-floor kick, syncopated bass, tom layers, snare builds, drops and breakdown. All sounds GeneralUser GS. Duration 5–180 seconds (subject to 64-bar limit), BPM 40–240, energy/variation 0–100. Variation changes melodic accents; energy controls drum density. No copied melody or vocals."""
    spec = new_project(title, bpm, key, 32, duration_seconds, 'normal', 'edm')
    spec.update(energy=energy, variation=variation, swing=0)
    spec['tracks']['bass']['instrument'] = 'synth_bass'
    spec['tracks']['lead']['instrument'] = 'electric_guitar'
    validate(spec)
    result = save_project(spec)
    result.update(play_project(spec))
    return result


@mcp.tool()
def edit_song(song_id: str = '', bpm: int | None = None, key: str | None = None,
              bars: int | None = None, swing: int | None = None, title: str | None = None,
              duration_seconds: float | None = None, articulation: str | None = None, style: str | None = None,
              energy: int | None = None, variation: int | None = None) -> dict:
    """Edit tempo, key, duration_seconds (5-180), bars (8-64), swing (0-75), title, articulation (legato/normal/staccato), style (pop/rnb/edm), or EDM energy/variation (0-100). Rebuild MIDI and restart. Empty song_id uses current song. A bars edit clears exact duration; tempo edits preserve it. BPM 40-240."""
    spec = copy.deepcopy(current_project(song_id))
    if bars is not None and duration_seconds is None:
        spec['duration_seconds'] = None
    for field, value in [('bpm', bpm), ('key', key), ('bars', bars), ('swing', swing), ('title', title),
                         ('duration_seconds', duration_seconds), ('articulation', articulation), ('style', style),
                         ('energy', energy), ('variation', variation)]:
        if value is not None:
            spec[field] = value
    validate(spec)
    spec['revision'] += 1
    result = save_project(spec)
    result.update(play_project(spec))
    return result


@mcp.tool()
def set_song_track(track: str, song_id: str = '', instrument: str | None = None,
                   muted: bool | None = None, volume: int | None = None) -> dict:
    """Edit keys/bass/pad/lead/drums in a song; then rebuild and play. Volume 0–100. Melodic instruments: piano, electric_piano, acoustic_guitar, electric_guitar, finger_bass, synth_bass, strings, choir, trumpet, saxophone, flute, synth_lead, warm_pad. Drums use the sampled GM drum kit and accept mute/volume edits only."""
    spec = copy.deepcopy(current_project(song_id))
    if track not in spec['tracks']:
        raise ValueError('track must be keys, bass, pad, lead, or drums')
    if instrument is not None:
        if track == 'drums' or instrument not in INSTRUMENTS:
            raise ValueError('Choose a listed melodic instrument for a non-drum track')
        spec['tracks'][track]['instrument'] = instrument
    if muted is not None:
        spec['tracks'][track]['muted'] = muted
    if volume is not None:
        spec['tracks'][track]['volume'] = volume
    validate(spec)
    spec['revision'] += 1
    result = save_project(spec)
    result.update(play_project(spec))
    return result


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
    """Export the current/supplied arrangement as MIDI and a stereo WAV rendered with GeneralUser GS. Does not change playback. Returns local files."""
    spec = current_project(song_id)
    result = save_project(spec)
    rendered = subprocess.run([sys.executable, '-u', str(Path(__file__).with_name('render_song.py')), spec['song_id']],
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parent, timeout=60)
    if rendered.returncode:
        raise RuntimeError('WAV render failed: ' + rendered.stderr[-1000:])
    result.update(json.loads(rendered.stdout))
    return result


if __name__ == '__main__':
    mcp.run()
