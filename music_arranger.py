"""Original pop MIDI arrangements, editable projects, and sampled WAV exports."""
import json
import math
from pathlib import Path
import random
import uuid
import wave

import mido

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'generated_music'
from instrument_catalog import INSTRUMENTS, instrument_preset
from music_score import validate_score, score_events, score_channels
PITCHES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5,
           'F#': 6, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
CHANNELS = {'keys': 0, 'bass': 1, 'pad': 2, 'lead': 3, 'drums': 9}


def validate(spec):
    if spec.get('style', 'pop') not in ('pop', 'rnb', 'edm'):
        raise ValueError('style must be pop, rnb, or edm')
    for field in ('energy', 'variation'):
        value = spec.get(field, 80 if field == 'energy' else 0)
        if type(value) is not int or not 0 <= value <= 100:
            raise ValueError(f'{field} must be an integer from 0 to 100')
    if spec.get('articulation', 'legato') not in ('legato', 'normal', 'staccato'):
        raise ValueError('articulation must be legato, normal, or staccato')
    if spec.get('dynamics', 'flat') not in ('flat', 'crescendo', 'decrescendo', 'swell'):
        raise ValueError('dynamics must be flat, crescendo, decrescendo, or swell')
    if type(spec.get('hold_notes', False)) is not bool:
        raise ValueError('hold_notes must be a boolean')
    if spec.get('duration_seconds') is not None:
        duration = spec['duration_seconds']
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 5 <= duration <= 180:
            raise ValueError('duration_seconds must be 5–180 seconds')
        spec['bars'] = max(8, math.ceil(duration * spec['bpm'] / 240))
    if spec['key'] not in PITCHES:
        raise ValueError('key must be a supported note name, such as C, D, F#, or Bb')
    for field, low, high in [('bpm', 40, 240), ('bars', 1 if spec.get('score') == 'custom' else 8, 180 if spec.get('score') == 'custom' else 64), ('swing', 0, 75)]:
        if type(spec[field]) is not int or not low <= spec[field] <= high:
            raise ValueError(f'{field} must be an integer from {low} to {high}')
    if not 1 <= len(spec['title']) <= 120:
        raise ValueError('title must contain 1–120 characters')
    if spec.get('score') == 'custom':
        validate_score(spec)
        return
    for track, setting in spec['tracks'].items():
        if track not in CHANNELS or setting['instrument'] not in INSTRUMENTS:
            raise ValueError('Unknown track or instrument')
        instrument_preset(setting['instrument'], track == 'drums')
        if not 0 <= setting['volume'] <= 100 or type(setting['muted']) is not bool:
            raise ValueError('volume must be 0–100 and muted must be a boolean')


def project_path(song_id):
    if not isinstance(song_id, str) or len(song_id) != 32 or any(c not in '0123456789abcdef' for c in song_id):
        raise ValueError('Use the song_id returned by create_pop_song')
    return OUTPUT / f'{song_id}.json'


def song_duration(spec):
    return spec.get('duration_seconds') or spec['bars'] * 240 / spec['bpm']


def new_project(title='MCPJAM Pop', bpm=112, key='C', bars=32, duration_seconds=None, articulation='legato', style='pop', hold_notes=False, dynamics='flat'):
    spec = {'song_id': uuid.uuid4().hex, 'title': title, 'bpm': bpm, 'key': key,
            'bars': bars, 'duration_seconds': duration_seconds, 'articulation': articulation, 'style': style,
            'hold_notes': hold_notes, 'dynamics': dynamics, 'swing': 8, 'revision': 1, 'tracks': {}}
    for track, instrument, volume in [('keys', 'piano', 88), ('bass', 'finger_bass', 42),
                                      ('pad', 'strings', 48), ('lead', 'acoustic_guitar', 82),
                                      ('drums', 'piano', 85)]:
        spec['tracks'][track] = {'instrument': instrument, 'volume': volume, 'muted': False}
    validate(spec)
    return spec


def read_project(song_id):
    spec = json.loads(project_path(song_id).read_text(encoding='utf-8'))
    validate(spec)
    return spec


def arrangement(spec):
    """Intro, verses, choruses, bridge, outro with a repeating melodic hook."""
    validate(spec)
    if spec.get('score') == 'custom':
        return score_events(spec)
    rng = random.Random(spec['song_id'] + str(spec.get('variation', 0)))
    root = PITCHES[spec['key']]
    rnb = spec.get('style', 'pop') == 'rnb'
    total_beats = song_duration(spec) * spec['bpm'] / 60
    musical_bars = math.ceil(total_beats / 4)
    events = []
    for track, ch in CHANNELS.items():
        preset = instrument_preset(spec['tracks'][track]['instrument'], ch == 9)
        events.append({'beat': 0.0, 'type': 'program_change', 'channel': ch,
                       'program': preset['midi_program'], 'bank': preset['bank']})

    def note(track, pitch, beat, duration, velocity):
        settings = spec['tracks'][track]
        if settings['muted'] or settings['volume'] == 0:
            return
        swing = spec['swing'] / 100 * .12 if int(beat * 2) % 2 else 0
        onset = max(0, beat + swing + rng.uniform(-.008, .008))
        if onset >= total_beats:
            return
        articulation = spec.get('articulation', 'legato')
        if track != 'drums':
            duration *= {'legato': 1.18, 'normal': 1.0, 'staccato': .48}[articulation]
            if spec.get('hold_notes', False):
                duration = max(duration, .85)
        duration = min(duration, total_beats - onset)
        progress = min(1.0, max(0.0, beat / max(total_beats, 1.0)))
        dynamics = spec.get('dynamics', 'flat')
        if dynamics == 'crescendo':
            dynamic_level = .68 + .44 * progress
        elif dynamics == 'decrescendo':
            dynamic_level = 1.12 - .44 * progress
        elif dynamics == 'swell':
            dynamic_level = .68 + .52 * math.sin(math.pi * progress)
        else:
            dynamic_level = 1.0
        vel = max(1, min(127, round((velocity + rng.randint(-5, 5)) * settings['volume'] / 100 * dynamic_level)))
        events.extend([{'beat': onset, 'type': 'note_on', 'channel': CHANNELS[track], 'note': pitch, 'velocity': vel},
                       {'beat': onset + duration, 'type': 'note_off', 'channel': CHANNELS[track], 'note': pitch, 'velocity': 0}])

    sections = []
    for bar in range(musical_bars):
        progress = bar / musical_bars
        if spec.get('score') == 'bossa':
            from bossa_score import bossa_bar
            section = 'intro' if progress<.14 else 'outro' if progress>.9 else 'theme'
            if not sections or sections[-1]['name'] != section:
                sections.append({'name':section,'start_bar':bar+1})
            bossa_bar(note,bar,root,section)
            continue
        if spec.get('score') == 'funk_pop':
            from funk_score import funk_bar
            section = ('intro' if progress<.14 else 'groove' if progress<.55 else
                       'breakdown' if progress<.7 else 'lift' if progress<.93 else 'outro')
            if not sections or sections[-1]['name'] != section:
                sections.append({'name':section,'start_bar':bar+1})
            funk_bar(note,bar,root,section,spec.get('piano_motion', 'chords'))
            continue
        if spec.get('score') == 'dark_piano_16':
            from composed_score import score_bar
            section = ('intro' if bar < 2 else 'pulse' if bar < 4 else 'groove' if bar < 8 else
                       'breakdown' if bar < 10 else 'drop' if bar < 14 else 'outro')
            if not sections or sections[-1]['name'] != section:
                sections.append({'name':section,'start_bar':bar+1})
            score_bar(note,bar,root,section)
            continue
        if spec.get('score') == 'orchestral':
            from orchestral_score import orchestral_bar
            section = 'intro' if progress < .12 else 'build' if progress < .45 else 'climax' if progress < .85 else 'outro'
            if not sections or sections[-1]['name'] != section:
                sections.append({'name': section, 'start_bar': bar + 1})
            orchestral_bar(note, bar, root, section, rng, spec.get('mood', 'dramatic'),
                           spec.get('melody_style', 'smooth'))
            continue
        if spec.get('style') == 'edm':
            section = ('outro' if bar == musical_bars - 1 else 'intro' if progress < .12 else
                       'build' if progress < .30 else 'drop' if progress < .62 else
                       'breakdown' if progress < .74 else 'final_drop')
            if not sections or sections[-1]['name'] != section:
                sections.append({'name': section, 'start_bar': bar + 1})
            edm_bar(note, bar, root, section, spec.get('energy', 80), rng, spec.get('sample_pack') == 'modern808')
            continue
        section = ('outro' if bar == musical_bars-1 else 'intro' if progress < .125 else 'verse' if progress < .375 else
                   'chorus' if progress < .625 else 'bridge' if progress < .75 else
                   'chorus' if progress < .9375 else 'outro')
        if not sections or sections[-1]['name'] != section:
            sections.append({'name': section, 'start_bar': bar + 1})
        # I–V–vi–IV; a vi–IV–I–V contrast for the bridge.
        progression = [(0, False), (7, False), (9, True), (5, False)]
        if rnb:
            progression = [(0, True), (8, False), (10, False), (5, True)]
        if section == 'bridge':
            progression = [progression[i] for i in (2, 3, 0, 1)]
        interval, minor = progression[bar % 4]
        chord_root = 48 + root + interval
        chord = [chord_root, chord_root + (3 if minor else 4), chord_root + 7]
        if rnb:
            chord.append(chord_root + (10 if minor else 11))
        beat = bar * 4
        # Soft rolled piano voicings, longer releases, and a rising chorus.
        for onset in ((0, 2) if section == 'chorus' else (0,)):
            for voice, pitch in enumerate(chord):
                note('keys', pitch + 12, beat + onset + voice * .035,
                     1.9 if section == 'chorus' else 3.8,
                     82 if section == 'chorus' else 58 + (bar % 4) * 3)
        if section in ('chorus', 'bridge', 'outro'):
            for pitch in chord:
                note('pad', pitch, beat, 3.85, 70)
        if section != 'intro':
            for offset in ((0, 1.75, 3) if rnb else (0, 1.5, 2, 3.5)):
                note('bass', chord_root - 12, beat + offset, 1.3 if rnb else (.42 if offset % 1 else .8), 88 if rnb else 95)
            for offset in ((0, 1.75, 3.5) if rnb else ((0, 1.5, 2, 2.75) if section == 'chorus' else (0, 2))):
                note('drums', 36, beat + offset, .12, 110)
            for offset in ((2,) if rnb else (1, 3)):
                note('drums', 38, beat + offset, .12, 100)
                if section == 'chorus':
                    note('drums', 39, beat + offset, .12, 65)
            for i in range(8):
                note('drums', 42, beat + i / 2, .08, 62 if i % 2 else 77)
            if section == 'chorus' and bar % 4 == 0:
                note('drums', 49, beat, .8, 85)
        if section in ('verse', 'chorus'):
            hook = [0, 4, 7, 4, 2, 4, 7, 9] if not minor else [0, 3, 7, 3, 2, 3, 7, 10]
            # Four-bar question/answer: pickups, breathing space, held endings.
            phrases = [
                [(0, 0, .75), (.75, 2, .75), (1.5, 4, 1.25), (3, 7, .75)],
                [(0, 4, 1.5), (2, 2, .75), (3, 0, .9)],
                [(0, 0, .5), (.5, 4, .5), (1, 7, 1), (2.5, 9, 1.25)],
                [(0, 7, .75), (1, 4, .75), (2, 0, 1.85)],
            ]
            for i, (offset, interval, length) in enumerate(phrases[bar % 4]):
                if minor and interval == 4:
                    interval = 3
                note('lead', chord_root + 12 + interval, beat + offset, length,
                     (90 if section == 'chorus' else 72) + (3 if i == 0 else -i * 2))
        if section == 'bridge':
            for i, pitch in enumerate(chord):
                note('lead', pitch + 12, beat + i, 1.8 if i == 2 else .95, 64 + i * 4)
        if section == 'outro':
            note('lead', chord_root + 12, beat, min(3.9, total_beats - beat), 62)
        if (bar + 1) % 8 == 0 and section != 'intro':
            for i in range(4):
                note('drums', 45 + i % 3, beat + 3 + i / 4, .1, 70 + i * 8)

    events.sort(key=lambda e: (e['beat'], 0 if e['type'] == 'program_change' else 1 if e['type'] == 'note_off' else 2))
    for event in events:
        event['time_sec'] = round(event['beat'] * 60 / spec['bpm'], 6)
    return events, sections


def edm_bar(note, bar, root, section, energy, rng, modern=False):
    """Original minor-key cinematic dance groove with builds and drum answers."""
    beat = bar * 4
    drop = section in ('drop', 'final_drop')
    chord_root = 48 + root + (0 if modern else (0, 0, 8, 10)[bar % 4])
    minor = modern or bar % 4 < 2
    chord = [chord_root, chord_root + (3 if minor else 4), chord_root + 7]
    intensity = .55 + energy / 220
    # Sustained strings supply atmosphere; piano adds clear sampled attacks.
    for pitch in chord:
        note('pad', pitch, beat, 3.9, 55 if not drop else 72)
    if section in ('intro', 'breakdown', 'outro'):
        for i, pitch in enumerate(chord + [chord[1] + 12]):
            note('keys', pitch + 12, beat + i * .75, 1.2, 62)
        note('lead', chord_root + 12, beat + .5, 2.8, 62)
        if section == 'intro':
            note('drums', 41, beat, .3, 90)
        return
    for offset in ((0, 1, 2, 3) if drop else (0, 2)):
        note('drums', 36, beat + offset, .15, round(118 * intensity))
    for offset in (1, 3):
        note('drums', 38, beat + offset, .12, 105)
        note('drums', 39, beat + offset + .012, .12, 78)
    for i in range(8 if energy < 85 else 16):
        spacing = .5 if energy < 85 else .25
        note('drums', 42, beat + i * spacing, .06, 72 if i % 2 == 0 else 45)
    for offset in (.5, 1.5, 2.5, 3.5):
        note('drums', 46, beat + offset, .22, 62)
        if not modern:
            note('bass', chord_root - 12, beat + offset, .32, 108)
    if modern:
        for offset in (0, 1.75, 3):
            note('bass', chord_root - 24, beat + offset, 1.15, 112)
    # A separate tom/percussion response gives the beat a cinematic pulse.
    for i, offset in enumerate((2.75,) if modern else (.75, 1.75, 2.75, 3.25, 3.5)):
        note('drums', (41, 45, 47, 43, 50)[i], beat + offset, .18, 82 + i * 4)
    if section == 'build':
        count = 8 if bar % 2 == 0 else 16
        for i in range(count):
            note('drums', 38, beat + i * 4 / count, .05, 40 + round(i / count * 60))
        for i, pitch in enumerate(chord):
            note('keys', pitch + 12, beat + i * .5, .35, 75)
    else:
        motif = [(0, 0, .65), (.75, 0, .35), (1.5, 3, .4), (2.25, 7, .6), (3, 5, .35)]
        if bar % 4 == 3:
            motif = [(0, 10, .7), (1, 7, .6), (2, 3, 1.6)]
        for offset, interval, length in motif:
            if rng.random() < .15:
                interval += 12
            note('lead', 60 + root + interval, beat + offset, length, 98)
        for offset in (0, 2):
            for pitch in chord:
                note('keys', pitch + 12, beat + offset, .35, 78)
        if bar % 4 == 0:
            note('drums', 49, beat, .7, 100)


def save_project(spec):
    events, sections = arrangement(spec)
    OUTPUT.mkdir(exist_ok=True)
    path = project_path(spec['song_id'])
    path.write_text(json.dumps(spec, indent=2), encoding='utf-8')
    midi = mido.MidiFile(type=1, ticks_per_beat=480, charset='utf-8')
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage('track_name', name=spec['title']))
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(spec['bpm'])))
    meta.append(mido.MetaMessage('time_signature', numerator=spec.get('time_signature_numerator', 4), denominator=spec.get('time_signature_denominator', 4)))
    midi.tracks.append(meta)
    for name, channel in (score_channels(spec) if spec.get("score") == "custom" else CHANNELS).items():
        track = mido.MidiTrack()
        track.append(mido.MetaMessage('track_name', name=name))
        previous = 0
        for event in events:
            if event['channel'] != channel:
                continue
            tick = round(event['beat'] * 480)
            if event['type'] == 'program_change':
                bank = event.get('bank', 128 if channel == 9 else 0)
                track.append(mido.Message('control_change', channel=channel, control=0, value=bank // 128, time=tick-previous))
                track.append(mido.Message('control_change', channel=channel, control=32, value=bank % 128, time=0))
                previous = tick
            kwargs = {'program': event['program']} if event['type'] == 'program_change' else {'note': event['note'], 'velocity': event['velocity']}
            track.append(mido.Message(event['type'], channel=channel, time=tick-previous, **kwargs))
            previous = tick
        track.append(mido.MetaMessage('end_of_track', time=max(0, round(song_duration(spec)*spec['bpm']/60*480)-previous)))
        midi.tracks.append(track)
    midi_path = path.with_suffix('.mid')
    midi.save(midi_path)
    return {'song_id': spec['song_id'], 'title': spec['title'], 'bpm': spec['bpm'], 'key': spec['key'],
            'bars': spec['bars'], 'revision': spec['revision'], 'tracks': spec['tracks'], 'sections': sections,
            'duration_seconds': round(song_duration(spec), 2), 'articulation': spec.get('articulation', 'legato'), 'style': spec.get('style', 'pop'),
            'genre': spec.get('genre', spec.get('style', 'pop')), 'composer': 'ai_score' if spec.get('score') == 'custom' else 'coded_pattern', 'event_count': len(events), 'midi_path': str(midi_path)}


def render_wav(spec):
    if spec.get('sample_pack') == 'modern808':
        from sample_audio import render_sample_song
        return render_sample_song(spec)
    from soundfont_audio import create_synth
    synth = create_synth(live=False)
    path = project_path(spec['song_id']).with_suffix('.wav')
    events, _ = arrangement(spec)
    cursor = 0
    peak = 0
    try:
        with wave.open(str(path), 'wb') as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(44100)
            def samples(until):
                nonlocal cursor, peak
                while cursor < until:
                    count = min(8192, until-cursor)
                    audio = synth.get_samples(count)
                    peak = max(peak, int(abs(audio.astype('int32')).max()))
                    output.writeframes(audio.astype('<i2').tobytes())
                    cursor += count
            for event in events:
                samples(round(event['time_sec']*44100))
                ch = event['channel']
                if event['type'] == 'program_change':
                    synth.program_select(ch, synth.soundfont_id, event.get('bank', 128 if ch == 9 else 0), event['program'])
                elif event['type'] == 'note_on':
                    synth.noteon(ch, event['note'], event['velocity'])
                else:
                    synth.noteoff(ch, event['note'])
            samples(round(song_duration(spec)*44100))
    finally:
        synth.delete()
    if peak == 0:
        raise RuntimeError('Soundfont rendered silent audio')
    return {'wav_path': str(path), 'sample_rate': 44100, 'channels': 2, 'peak': peak, 'audio_engine': 'generaluser_gs'}
