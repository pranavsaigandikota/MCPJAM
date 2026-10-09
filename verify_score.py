"""Verify full SoundFont selection and the AI-authored score path over real MCP."""
import asyncio
import copy
import hashlib
import json
from pathlib import Path
import sys
import wave
import mido
import numpy as np
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from instrument_catalog import PRESETS
from music_arranger import validate, read_project, arrangement, project_path
from soundfont_audio import create_synth, SOUNDFONT

ROOT = Path(__file__).resolve().parent


def data(result):
    assert not result.isError, result
    return result.structuredContent or json.loads(next(c.text for c in result.content if c.type == 'text'))


def presets_check():
    manifest = json.loads((ROOT/'soundfonts/GeneralUser-GS/presets.json').read_text())
    assert hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest() == manifest['soundfont_sha256']
    synth = create_synth(False)
    try:
        synth.setting('synth.reverb.active', 0)
        for preset in PRESETS.values():
            ch = 9 if preset['kind'] == 'drum_kit' else 0
            synth.cc(ch, 120, 0)
            assert synth.program_select(ch, synth.soundfont_id, preset['bank'], preset['midi_program']) == 0
            assert synth.program_info(ch)[1:] == (preset['bank'], preset['midi_program'])
            peaks = []
            for pitch in (36,60,84):
                synth.cc(ch, 120, 0)
                synth.noteon(ch, pitch, 100)
                peaks.append(int(np.abs(synth.get_samples(11025).astype('int32')).max()))
                synth.noteoff(ch, pitch)
            assert max(peaks) > 0, preset
        print(f'PASS: {len(PRESETS)} actual SoundFont presets select and render nonzero audio', flush=True)
    finally:
        synth.delete()


async def live_check():
    params = StdioServerParameters(command=sys.executable,args=[str(ROOT/'mcp_server_music.py')])
    score = json.loads((ROOT/'workshop/examples/original-rnb-score.json').read_text(encoding='utf-8'))
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            names = {t.name for t in (await session.list_tools()).tools}
            assert {'create_song_from_score','replace_song_notes','get_instrument_catalog'} <= names
            found = []
            for offset in range(0,287,100):
                page = data(await session.call_tool('get_instrument_catalog',{'offset':offset,'limit':100}))
                found.extend(p['id'] for p in page['instruments'])
            assert set(found)==set(PRESETS) and len(found)==287
            song = data(await session.call_tool('create_song_from_score',{k:v for k,v in score.items() if k != 'duration_seconds'}))
            assert song['status']=='generated' and song['composer']=='ai_score'
            assert 'playback' not in song and Path(song['mp3_path']).is_file()
            spec = read_project(song['song_id'])
            assert spec['notes'] == score['notes'] # No fixed backend melody inserted.
            midi = mido.MidiFile(project_path(song['song_id']).with_suffix('.mid'))
            assert abs(midi.length-30)<.01 and len(midi.tracks)==6
            # Arbitrary track names, all 16 channels and a non-4/4 meter.
            ensemble={'title':'Sixteen Voices','bpm':120,'duration_seconds':5,'genre':'chamber waltz',
                      'time_signature_numerator':3,'time_signature_denominator':4,
                      'tracks':[{'name':f'part_{ch}','channel':ch,'instrument':'gs_128_40' if ch==9 else 'gs_0_48','volume':35} for ch in range(16)],
                      'notes':[{'track':f'part_{ch}','pitch':36 if ch==9 else 48+ch,'beat':0,'duration':1,'velocity':45} for ch in range(16)]}
            voices=data(await session.call_tool('create_song_from_score',ensemble))
            ensemble_midi=mido.MidiFile(project_path(voices['song_id']).with_suffix('.mid'))
            assert len(ensemble_midi.tracks)==17
            assert next(m for m in ensemble_midi.tracks[0] if m.type=='time_signature').numerator==3
            for track in midi.tracks[1:]:
                assert any(m.type=='control_change' and m.control==0 for m in track)
                assert any(m.type=='control_change' and m.control==32 for m in track)
            revision = spec['revision']
            assert (await session.call_tool('edit_song',{'song_id':song['song_id'],'key':'D'})).isError
            assert read_project(song['song_id'])['revision']==revision
            bad_cases=[]
            for mutate in [lambda s:s['notes'][0].update(pitch=128),
                           lambda s:s['notes'][0].update(beat=999),
                           lambda s:s['notes'][0].update(track='unknown'),
                           lambda s:s['tracks'][0].update(channel=9),
                           lambda s:s['tracks'][1].update(channel=0),
                           lambda s:s['tracks'][0].update(instrument='gs_999_0'),
                           lambda s:s.update(time_signature_denominator=3),
                           lambda s:s['notes'].append(copy.deepcopy(s['notes'][0])),
                           lambda s:s['notes'][0].update(repeats=128,every_beats=.001),
                           lambda s:s.update(notes=[{'track':'keys','pitch':i,'beat':0,'duration':.001,'velocity':80,'repeats':128,'every_beats':.002} for i in range(40)])]:
                bad=copy.deepcopy(score);mutate(bad);bad_cases.append(bad)
            for bad in bad_cases:
                assert (await session.call_tool('create_song_from_score',bad)).isError
                assert read_project(song['song_id'])['revision']==revision
            # Select a bank variant and a percussion kit over MCP, and rewrite pitches.
            changed = data(await session.call_tool('set_song_track',{'song_id':song['song_id'],'track':'keys','instrument':'gs_8_4'}))
            events,_ = arrangement(read_project(song['song_id']))
            assert next(e for e in events if e['type']=='program_change' and e['channel']==0)['bank']==8
            data(await session.call_tool('set_song_track',{'song_id':song['song_id'],'track':'drums','instrument':'gs_128_8'}))
            replacement=copy.deepcopy(score['notes']);replacement[0]['pitch']+=1
            rewritten=data(await session.call_tool('replace_song_notes',{'song_id':song['song_id'],'notes':replacement}))
            assert read_project(song['song_id'])['notes']==replacement
            # Restore the original score and export the audible original demo.
            data(await session.call_tool('replace_song_notes',{'song_id':song['song_id'],'notes':score['notes']}))
            data(await session.call_tool('set_song_track',{'song_id':song['song_id'],'track':'keys','instrument':'gs_0_4'}))
            data(await session.call_tool('set_song_track',{'song_id':song['song_id'],'track':'drums','instrument':'gs_128_25'}))
            exported=data(await session.call_tool('export_song',{'song_id':song['song_id']}))
            assert Path(exported['mp3_path']).stat().st_size > 100000
            assert 'midi_path' not in song and 'wav_path' not in exported
            with wave.open(str(Path(exported['mp3_path']).with_suffix('.wav'))) as wav:
                assert wav.getnchannels()==2 and wav.getframerate()==44100
                assert abs(wav.getnframes()/44100-30)<.01
                audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype('int32')
                assert 0 < np.abs(audio).max() < 32767
            receipt={'song_id':song['song_id'],'mp3_path':exported['mp3_path'],
                     'preset_count':len(PRESETS),'invalid_cases':len(bad_cases),'composer':'ai_score'}
            (ROOT/'.workshop_slide_edit/music-score-verification.json').write_text(json.dumps(receipt,indent=2))
            print('PASS: real MCP discovery, 287-preset paging, original score file generation without a player, 16 voices, 3/4 meter, MIDI bank export, 10 rejected scores, sound edits, note rewrite, no autoplay and user-facing MP3',flush=True)
            print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    presets_check()
    asyncio.run(live_check())
