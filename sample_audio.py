"""Modern 808 WAV sample layer; no oscillator fallback."""
import copy
import json
import hashlib
from pathlib import Path
import wave
import numpy as np

PACK = Path(__file__).resolve().parent / 'samples' / 'modern808'


def read_audio(path):
    with wave.open(str(path)) as wav:
        if wav.getsampwidth() != 2:
            raise RuntimeError('Sample pack requires 16-bit PCM WAV')
        audio = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2').astype(np.float32) / 32768
        audio = audio.reshape(-1, wav.getnchannels())
        if audio.shape[1] == 1:
            audio = np.repeat(audio, 2, axis=1)
        if wav.getframerate() != 44100:
            raise RuntimeError('Sample pack requires 44100 Hz')
        return audio


def render_sample_song(spec):
    from music_arranger import arrangement, render_wav, project_path
    path = project_path(spec['song_id']).with_suffix('.wav')
    cache = path.with_suffix('.mix.json')
    signature = hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()
    if cache.is_file() and path.is_file():
        stored = json.loads(cache.read_text())
        if stored['signature'] == signature:
            return stored['result']
    accompaniment = copy.deepcopy(spec)
    accompaniment.pop('sample_pack', None)
    overridden = (['bass'] if spec.get('sample_bass', True) else []) + (['drums'] if spec.get('sample_drums', True) else [])
    for track in overridden:
        accompaniment['tracks'][track]['muted'] = True
    result = render_wav(accompaniment)
    mix = read_audio(result['wav_path']) * .7
    samples = {name: read_audio(PACK / (name + '.wav')) for name in
               ('bass','kick','snare','clap','hat','open_hat','tom','crash')}
    bass = samples['bass'].mean(axis=1)
    # Estimate the recorded sample's sustained fundamental, then tune it.
    window = bass[4410:22050]
    spectrum = np.abs(np.fft.rfft(window * np.hanning(len(window))))
    frequencies = np.fft.rfftfreq(len(window), 1/44100)
    spectrum[(frequencies < 25) | (frequencies > 150)] = 0
    fundamental = float(frequencies[np.argmax(spectrum)])
    events, _ = arrangement(spec)
    drum_names = {36:'kick',38:'snare',39:'clap',42:'hat',46:'open_hat',49:'crash'}
    for event in events:
        if event['type'] != 'note_on' or event['channel'] not in (1,9):
            continue
        if event['channel'] == 1:
            if not spec.get('sample_bass', True):
                continue
            target = 440 * 2 ** ((event['note'] - 69)/12)
            ratio = target / fundamental
            source = samples['bass']
            positions = np.arange(0, len(source)-1, ratio)
            clip = np.column_stack([np.interp(positions, np.arange(len(source)), source[:,ch]) for ch in range(2)])
            level = .85
        else:
            if not spec.get('sample_drums', True):
                continue
            clip = samples[drum_names.get(event['note'], 'tom')]
            level = .65 if event['note'] == 36 else .28
        start = round(event['time_sec'] * 44100)
        count = min(len(clip), len(mix)-start)
        if count > 0:
            mix[start:start+count] += clip[:count] * event['velocity']/127 * level
    # Soft saturation catches stacked transients; final headroom avoids clipping.
    mix = np.tanh(mix * 1.2)
    peak = float(np.max(np.abs(mix)))
    if peak > .89:
        mix *= .89/peak
    fade = min(11025, len(mix))
    mix[-fade:] *= np.linspace(1,0,fade)[:,None]
    path = project_path(spec['song_id']).with_suffix('.wav')
    pcm = (mix * 32767).astype('<i2')
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(44100)
        wav.writeframes(pcm.tobytes())
    result = {'wav_path':str(path),'sample_rate':44100,'channels':2,
            'peak':int(np.max(np.abs(pcm.astype('int32')))),
            'audio_engine':('modern808_samples_with_generaluser_gs' if spec.get('sample_bass', True) and spec.get('sample_drums', True) else 'modern_bass_with_generaluser_gs' if spec.get('sample_bass', True) else 'modern_drums_with_generaluser_gs')}
    cache.write_text(json.dumps({'signature':signature,'result':result}))
    return result
