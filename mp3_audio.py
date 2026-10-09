"""Encode a rendered PCM WAV to a portable MP3; MIDI/WAV remain backend files."""
from pathlib import Path
import wave


def encode_mp3(wav_path):
    import lameenc
    path = Path(wav_path)
    output = path.with_suffix('.mp3')
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(192)
    encoder.set_quality(2)
    encoder.silence()
    with wave.open(str(path), 'rb') as wav:
        if wav.getsampwidth() != 2:
            raise ValueError('MP3 encoding requires 16-bit PCM')
        encoder.set_in_sample_rate(wav.getframerate())
        encoder.set_channels(wav.getnchannels())
        duration = wav.getnframes() / wav.getframerate()
        with output.open('wb') as target:
            while True:
                block = wav.readframes(8192)
                if not block:
                    break
                target.write(encoder.encode(block))
            target.write(encoder.flush())
    if output.stat().st_size < 1000:
        raise RuntimeError('MP3 encoder produced an empty/incomplete file')
    return {'mp3_path': str(output), 'file_path': str(output), 'mime_type': 'audio/mpeg',
            'duration_seconds': duration, 'bitrate_kbps': 192}
