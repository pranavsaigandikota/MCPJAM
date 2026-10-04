"""Check real song creation, edits, invalid inputs, playback and sampled export."""
import asyncio
import json
from pathlib import Path
import sys
import wave

import mido
import numpy as np
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from gemini_host import state_from
from music_arranger import read_project, arrangement

ROOT = Path(__file__).resolve().parent


def result_data(result):
    assert not result.isError, result
    if result.structuredContent:
        return result.structuredContent
    return json.loads(next(p.text for p in result.content if p.type == 'text'))


async def main():
    checks = 0
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT/'mcp_server_music.py')])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            assert {t.name for t in (await session.list_tools()).tools} == {
                'get_state', 'create_pop_song', 'edit_song', 'set_song_track', 'play_song', 'stop_song', 'export_song'}
            checks += 1
            state = state_from(await session.call_tool('get_state', {}))
            assert state['audio_engine'] == 'generaluser_gs' and not state['soundfont_error']
            checks += 1
            original_bpm = state['bpm']
            try:
                song = result_data(await session.call_tool('create_pop_song', {'title':'MCPJAM Integration Test','bpm':112,'key':'D','bars':8}))
                song_id = song['song_id']
                assert song['playback'] == 'observed' and song['event_count'] > 200
                assert {s['name'] for s in song['sections']} == {'intro','verse','chorus','bridge','outro'}
                checks += 2
                state = state_from(await session.call_tool('get_state', {}))
                assert state['song_id'] == song_id and state['timeline_active'] and state['bpm'] == 112
                checks += 1
                midi = mido.MidiFile(song['midi_path'])
                assert len(midi.tracks) == 6 and 17 <= midi.length <= 18
                checks += 1
                edited = result_data(await session.call_tool('edit_song', {'song_id':song_id,'bpm':128,'swing':15}))
                assert edited['revision'] == 2 and edited['bpm'] == 128
                state = state_from(await session.call_tool('get_state', {}))
                assert state['song_revision'] == 2 and state['bpm'] == 128
                checks += 2
                changed = result_data(await session.call_tool('set_song_track', {'track':'lead','instrument':'flute','volume':65}))
                assert changed['tracks']['lead']['instrument'] == 'flute'
                checks += 1
                result_data(await session.call_tool('set_song_track', {'track':'drums','muted':True}))
                events, _ = arrangement(read_project(song_id))
                assert not any(e['type']=='note_on' and e['channel']==9 for e in events)
                checks += 1
                before = read_project(song_id)
                for name, args in [('edit_song',{'bpm':500}), ('set_song_track',{'track':'lead','instrument':'invalid'}),
                                   ('set_song_track',{'track':'drums','instrument':'piano'}),
                                   ('set_song_track',{'track':'lead','volume':101}), ('play_song',{'song_id':'../README'})]:
                    assert (await session.call_tool(name,args)).isError
                    assert read_project(song_id) == before
                    checks += 1
                exported = result_data(await session.call_tool('export_song', {}))
                with wave.open(exported['wav_path']) as wav:
                    assert wav.getnchannels()==2 and wav.getframerate()==44100
                    samples = np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype('int32')
                    assert 0 < np.max(np.abs(samples)) < 32767
                checks += 2
                result_data(await session.call_tool('stop_song', {}))
                assert not state_from(await session.call_tool('get_state', {}))['timeline_active']
                checks += 1
                print(f'PASS: {checks} live music checks; sampled engine, MIDI, edits, rejection, WAV, and stop.')
            finally:
                await session.call_tool('stop_song', {})
                from mcp_server_sdk import call_daw
                call_daw({'cmd':'set_tempo','bpm':original_bpm})


if __name__ == '__main__':
    asyncio.run(main())
