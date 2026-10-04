"""GeneralUser GS configuration shared by live playback and WAV rendering."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOUNDFONT = ROOT / 'soundfonts' / 'GeneralUser-GS' / 'GeneralUser-GS.sf2'
_DLL_HANDLES = []


def load_fluidsynth():
    if sys.platform == 'darwin' and not os.environ.get('HOMEBREW_PREFIX'):
        for prefix in ('/opt/homebrew', '/usr/local'):
            if (Path(prefix) / 'lib' / 'libfluidsynth.dylib').is_file():
                os.environ['HOMEBREW_PREFIX'] = prefix
                break
    if sys.platform == 'win32':
        runtime = ROOT / '.audio_runtime'
        for dll in runtime.rglob('libfluidsynth*.dll'):
            directory = str(dll.parent)
            _DLL_HANDLES.append(os.add_dll_directory(directory))
            os.environ['PATH'] = directory + os.pathsep + os.environ.get('PATH', '')
            break
    import fluidsynth
    return fluidsynth


def create_synth(live=False):
    if not SOUNDFONT.is_file():
        raise RuntimeError(f'GeneralUser GS soundfont is missing: {SOUNDFONT}')
    fluidsynth = load_fluidsynth()
    synth = fluidsynth.Synth(samplerate=44100, gain=0.5)
    try:
        # A damped room adds space without the metallic modulation of chorus.
        synth.setting('synth.reverb.active', 1)
        synth.setting('synth.chorus.active', 0)
        synth.set_reverb(roomsize=0.72, damping=0.65, width=80.0, level=0.32)
        if live:
            driver = 'dsound' if sys.platform == 'win32' else ('coreaudio' if sys.platform == 'darwin' else 'pulseaudio')
            synth.setting('audio.driver', driver)
            # Feed MIDI from the app directly; do not open a hardware MIDI input.
            synth.audio_driver = fluidsynth.new_fluid_audio_driver(synth.settings, synth.synth)
            if not synth.audio_driver:
                raise RuntimeError(f'FluidSynth could not start the {driver} audio driver')
        sfid = synth.sfload(str(SOUNDFONT))
        if sfid < 0:
            raise RuntimeError('FluidSynth could not load GeneralUser GS')
        # Select the bank on every channel; MIDI channel 10 uses the drum bank.
        for channel in range(16):
            if synth.program_select(channel, sfid, 128 if channel == 9 else 0, 0) < 0:
                raise RuntimeError(f'Soundfont bank/program selection failed on channel {channel}')
            # Keep bass/drums dry; put piano, strings and melody in the room.
            synth.cc(channel, 91, {0: 85, 1: 12, 2: 70, 3: 60, 9: 20}.get(channel, 45))
            synth.cc(channel, 93, 0)
        return synth
    except Exception:
        synth.delete()
        raise
