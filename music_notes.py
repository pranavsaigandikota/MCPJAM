"""Pitch and chord helpers; no audio generation or playback."""
from .constants import SEMI_MAP, CHORD_FORMULAS, ROOT_TO_BASS_NOTE

def parse_chord_frequencies(chord_name: str):
    """Parse any chord name (e.g. 'Am', 'Fmaj7', 'C#m', 'Bb', 'Gsus4') into audio frequencies."""
    clean = chord_name.strip().upper().replace("MIN", "M").replace("MAJOR", "MAJ")
    if len(clean) > 1 and clean[1] in ("#", "B"):
        root = clean[:2]
        quality = clean[2:]
    elif clean:
        root = clean[:1]
        quality = clean[1:]
    else:
        root = "C"
        quality = ""

    semi = SEMI_MAP.get(root, 0)
    intervals = CHORD_FORMULAS.get(quality, [0, 4, 7])

    # Base root in octave 3/4 (C4 = 261.63 Hz)
    root_f = 261.63 * (2.0 ** (semi / 12.0))
    if root_f > 380:
        root_f /= 2.0  # Keep in comfortable mid octave

    freqs = [root_f * (2.0 ** (iv / 12.0)) for iv in intervals]
    bass_note = ROOT_TO_BASS_NOTE.get(root, "A1")
    return root, quality, freqs, bass_note

def parse_note_frequency(note_str: str) -> float:
    """Parse a note string like 'C4', 'Eb5', 'A#4', 'F#5' to Hz."""
    note = note_str.strip().upper()
    if not note:
        return 440.0
    # Extract octave if present
    if note[-1].isdigit():
        octave = int(note[-1])
        pitch = note[:-1]
    else:
        octave = 5
        pitch = note

    semi = SEMI_MAP.get(pitch, 0)
    # C4 = 261.6256 Hz
    return (440.0 / (2.0 ** (9 / 12.0))) * (2.0 ** (octave - 4)) * (2.0 ** (semi / 12.0))
