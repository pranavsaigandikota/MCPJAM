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
INSTRUMENTS = {'piano': 0, 'electric_piano': 4, 'acoustic_guitar': 25,
               'electric_guitar': 27, 'finger_bass': 33, 'synth_bass': 38,
               'strings': 48, 'choir': 52, 'trumpet': 56, 'saxophone': 65,
               'flute': 73, 'synth_lead': 81, 'warm_pad': 89}
PITCHES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5,
           'F#': 6, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
CHANNELS = {'keys': 0, 'bass': 1, 'pad': 2, 'lead': 3, 'drums': 9}


def validate(spec):
    if spec.get('style', 'pop') not in ('pop', 'rnb'):
        raise ValueError('style must be pop or rnb')
    if spec.get('articulation', 'legato') not in ('legato', 'normal', 'staccato'):
        raise ValueError('articulation must be legato, normal, or staccato')
    if spec.get('duration_seconds') is not None:
        duration = spec['duration_seconds']
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 5 <= duration <= 180:
            raise ValueError('duration_seconds must be 5–180 seconds')
        spec['bars'] = max(8, math.ceil(duration * spec['bpm'] / 240))
    if spec['key'] not in PITCHES:
        raise ValueError('key must be a supported note name, such as C, D, F#, or Bb')
    for field, low, high in [('bpm', 40, 240), ('bars', 8, 64), ('swing', 0, 75)]:
        if type(spec[field]) is not int or not low <= spec[field] <= high:
            raise ValueError(f'{field} must be an integer from {low} to {high}')
    if not 1 <= len(spec['title']) <= 120:
        raise ValueError('title must contain 1–120 characters')
    for track, setting in spec['tracks'].items():
        if track not in CHANNELS or setting['instrument'] not in INSTRUMENTS:
            raise ValueError('Unknown track or instrument')
        if not 0 <= setting['volume'] <= 100 or type(setting['muted']) is not bool:
            raise ValueError('volume must be 0–100 and muted must be a boolean')


def project_path(song_id):
    if not isinstance(song_id, str) or len(song_id) != 32 or any(c not in '0123456789abcdef' for c in song_id):
        raise ValueError('Use the song_id returned by create_pop_song')
    return OUTPUT / f'{song_id}.json'


def song_duration(spec):
    return spec.get('duration_seconds') or spec['bars'] * 240 / spec['bpm']


def new_project(title='MCPJAM Pop', bpm=112, key='C', bars=32, duration_seconds=None, articulation='legato', style='pop'):
    spec = {'song_id': uuid.uuid4().hex, 'title': title, 'bpm': bpm, 'key': key,
            'bars': bars, 'duration_seconds': duration_seconds, 'articulation': articulation, 'style': style,
            'swing': 8, 'revision': 1, 'tracks': {}}
    for track, instrument, volume in [('keys', 'piano', 80), ('bass', 'finger_bass', 90),
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
    rng = random.Random(spec['song_id'])
    root = PITCHES[spec['key']]
    rnb = spec.get('style', 'pop') == 'rnb'
    total_beats = song_duration(spec) * spec['bpm'] / 60
    musical_bars = math.ceil(total_beats / 4)
    events = []
    for track, ch in CHANNELS.items():
        if ch != 9:
            events.append({'beat': 0.0, 'type': 'program_change', 'channel': ch,
                           'program': INSTRUMENTS[spec['tracks'][track]['instrument']]})

    def note(track, pitch, beat, duration, velocity):
        settings = spec['tracks'][track]
        if settings['muted'] or settings['volume'] == 0:
            return
        swing = spec['swing'] / 100 * .12 if int(beat * 2) % 2 else 0
        onset = max(0, beat + swing + rng.uniform(-.008, .008))
        if onset >= total_beats:
            return
        if track == 'lead':
            duration *= {'legato': 1.03, 'normal': .9, 'staccato': .48}[spec.get('articulation', 'legato')]
        duration = min(duration, total_beats - onset)
        vel = max(1, min(127, round((velocity + rng.randint(-5, 5)) * settings['volume'] / 100)))
        events.extend([{'beat': onset, 'type': 'note_on', 'channel': CHANNELS[track], 'note': pitch, 'velocity': vel},
                       {'beat': onset + duration, 'type': 'note_off', 'channel': CHANNELS[track], 'note': pitch, 'velocity': 0}])

    sections = []
    for bar in range(musical_bars):
        progress = bar / musical_bars
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


def save_project(spec):
    events, sections = arrangement(spec)
    OUTPUT.mkdir(exist_ok=True)
    path = project_path(spec['song_id'])
    path.write_text(json.dumps(spec, indent=2), encoding='utf-8')
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage('track_name', name=spec['title']))
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(spec['bpm'])))
    meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    midi.tracks.append(meta)
    for name, channel in CHANNELS.items():
        track = mido.MidiTrack()
        track.append(mido.MetaMessage('track_name', name=name))
        previous = 0
        for event in events:
            if event['channel'] != channel:
                continue
            tick = round(event['beat'] * 480)
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
            'event_count': len(events), 'midi_path': str(midi_path)}


def render_wav(spec):
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
                    synth.program_change(ch, event['program'])
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
