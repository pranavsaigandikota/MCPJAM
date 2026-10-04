"""Install the pinned official FluidSynth runtime locally on Windows."""
import hashlib
import io
from pathlib import Path
import platform
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = '2.6.1'
URL = ('https://github.com/FluidSynth/fluidsynth/releases/download/v2.6.1/'
       'fluidsynth-v2.6.1-win10-x64-cpp11.zip')
SHA256 = 'fab7a2e4b85675b66970f97a39bbc239729c5e0f237198b5922a6a73cbc8677c'


def main():
    if platform.system() != 'Windows':
        print('Install FluidSynth using your OS package manager (macOS: brew install fluid-synth).')
        return
    if platform.machine().lower() not in ('amd64', 'x86_64'):
        raise RuntimeError('This installer supplies the Windows x64 runtime only')
    destination = ROOT / '.audio_runtime'
    print(f'Downloading official FluidSynth {VERSION} Windows x64 runtime...')
    with urllib.request.urlopen(URL, timeout=60) as response:
        data = response.read(20_000_001)
    if len(data) > 20_000_000 or hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError('FluidSynth download failed its size/checksum verification')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            target = (destination / item.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise RuntimeError('Archive contains an unsafe path')
        archive.extractall(destination)
    print(f'PASS: verified runtime installed in {destination}')


if __name__ == '__main__':
    main()
