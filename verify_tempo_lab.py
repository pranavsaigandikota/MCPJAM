"""Verify the student activity using real MCP and real 30-second audio rendering.

Requires the full audio setup. Creates test songs without starting playback.
"""
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import wave

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from music_arranger import read_project, project_path

ROOT = Path(__file__).resolve().parent
SNIPPET = '''@mcp.tool()
def set_tempo(bpm: int) -> dict:
    """Change tempo from 40 to 240 BPM."""
    if not 40 <= bpm <= 240:
        raise ValueError("Use 40–240 BPM")
    return call_daw({"cmd": "set_tempo", "bpm": bpm})

'''


def data(result):
    assert not result.isError, result
    return result.structuredContent or json.loads(next(c.text for c in result.content if c.type == 'text'))


def check_audio(result, bpm):
    assert Path(result['mp3_path']).stat().st_size > 10000
    spec = read_project(result['song_id'])
    assert spec['bpm'] == bpm and spec['duration_seconds'] == 30
    with wave.open(str(project_path(result['song_id']).with_suffix('.wav'))) as wav:
        assert abs(wav.getnframes() / wav.getframerate() - 30) < .01
    return spec


async def run_server(path, pointer, completed=False):
    params = StdioServerParameters(command=sys.executable, args=[str(path)],
                                  env={**os.environ, 'MCPJAM_WORKSHOP_SONG_POINTER': str(pointer)})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            assert ('set_tempo' in {t.name for t in tools}) == completed
            if not completed:
                schema = next(t.inputSchema for t in tools if t.name == 'create_song_from_score')
                assert 'bpm' not in schema['properties'] and 'duration_seconds' not in schema['properties']
                catalog = data(await session.call_tool('get_instrument_catalog',{'query':'distortion','kind':'melodic'}))
                preset = catalog['instruments'][0]['id']
                song = data(await session.call_tool('create_song_from_score', {
                    'title': 'Tempo lab verification', 'genre': 'rock',
                    'tracks': [{'name':'guitar','channel':0,'instrument':preset}],
                    'notes': [{'track':'guitar','pitch':52,'beat':0,'duration':.5,'repeats':30,'every_beats':2}]}))
                check_audio(song,120)
                before = data(await session.call_tool('get_state',{}))
                assert (await session.call_tool('set_tempo',{'bpm':150})).isError
                assert data(await session.call_tool('get_state',{})) == before
                print('PASS: default 120 BPM MP3; missing tempo call fails; state unchanged.')
            else:
                for bpm in (150,40,240):
                    song = data(await session.call_tool('set_tempo',{'bpm':bpm}))
                    spec = check_audio(song,bpm)
                    state = data(await session.call_tool('get_state',{}))
                    assert state['bpm'] == bpm and not state['playing']
                    if bpm == 240:
                        assert len(spec['notes']) == 30, 'Slower crop must not permanently remove source notes'
                before = data(await session.call_tool('get_state',{}))
                assert (await session.call_tool('set_tempo',{'bpm':300})).isError
                assert data(await session.call_tool('get_state',{})) == before
                print('PASS: copied slide code registers; 150/40/240 render 30-second MP3s; 300 rejected.')


async def main():
    starter = ROOT/'workshop/starter/mcp_server_sdk.py'
    latest = ROOT/'generated_music/latest.json'
    previous = latest.read_bytes() if latest.exists() else None
    with tempfile.TemporaryDirectory() as temp:
        pointer = Path(temp)/'song.json'
        fd, name = tempfile.mkstemp(prefix='_tempo_verification_',suffix='.py',dir=starter.parent)
        os.close(fd)
        copied = Path(name)
        try:
            copied.write_text(starter.read_text(encoding='utf-8').replace('if __name__ == "__main__":',
                              SNIPPET+'if __name__ == "__main__":'),encoding='utf-8')
            await run_server(starter,pointer)
            await run_server(copied,pointer,True)
        finally:
            copied.unlink(missing_ok=True)
            if previous is not None:
                latest.write_bytes(previous)
    print('PASS: complete before/after workshop activity; no autoplay.')


if __name__ == '__main__':
    asyncio.run(main())
