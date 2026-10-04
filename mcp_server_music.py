"""Optional song-making MCP server; the beginner starter remains separate."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

from mcp.server.fastmcp import FastMCP

from mcp_server_sdk import call_daw
from music_arranger import INSTRUMENTS, new_project, read_project, save_project, render_wav, arrangement, validate

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
    call_daw({'cmd': 'play_midi_raw', 'events': events, 'title': spec['title'],
              'song_id': spec['song_id'], 'revision': spec['revision'], 'bpm': spec['bpm'],
              'duration_seconds': spec['bars']*4*60/spec['bpm'], 'song_tracks': spec['tracks']})
    deadline = time.monotonic()+5
    while time.monotonic() < deadline:
        state = get_state()
        if state.get('song_id') == spec['song_id'] and state.get('song_revision') == spec['revision'] and state.get('timeline_active'):
            return {'playback': 'observed', 'audio_engine': state['audio_engine'], 'song_id': spec['song_id'], 'revision': spec['revision']}
        time.sleep(.05)
    raise RuntimeError('Song was queued but playback was not observed; inspect get_state before retrying')


@mcp.tool()
def create_pop_song(title: str = 'MCPJAM Pop', bpm: int = 112, key: str = 'C', bars: int = 32) -> dict:
    """Create and play an original instrumental pop arrangement with intro, verse, chorus, bridge, and outro. Major key note C/D/F#/Bb etc; 8–64 bars, 40–240 BPM. Uses sampled piano, guitar, bass, strings, drums. Returns an editable song_id and MIDI file. Requires running GeneralUser GS app; no vocals are synthesized."""
    spec = new_project(title, bpm, key, bars)
    result = save_project(spec)
    result.update(play_project(spec))
    return result


@mcp.tool()
def edit_song(song_id: str = '', bpm: int | None = None, key: str | None = None,
              bars: int | None = None, swing: int | None = None, title: str | None = None) -> dict:
    """Edit the current or supplied song: tempo, major key, length, swing, title. Rebuild the MIDI and restart playback with the changes. Empty song_id means the current app song. Valid ranges: BPM 40–240, bars 8–64, swing 0–75."""
    spec = copy.deepcopy(current_project(song_id))
    for field, value in [('bpm', bpm), ('key', key), ('bars', bars), ('swing', swing), ('title', title)]:
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
def export_song(song_id: str = '') -> dict:
    """Export the current/supplied arrangement as MIDI and a stereo WAV rendered with GeneralUser GS. Does not change playback. Returns local files."""
    spec = current_project(song_id)
    result = save_project(spec)
    rendered = subprocess.run([sys.executable, str(Path(__file__).with_name('render_song.py')), spec['song_id']],
                              capture_output=True, text=True, timeout=60)
    if rendered.returncode:
        raise RuntimeError('WAV render failed: ' + rendered.stderr[-1000:])
    result.update(json.loads(rendered.stdout))
    return result


if __name__ == '__main__':
    mcp.run()
