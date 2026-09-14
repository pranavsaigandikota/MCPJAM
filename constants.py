HOST, PORT = "127.0.0.1", 8765
STEPS = 16

# The 8 Tracks across the 4 Pillars
TRACKS = ["kick", "snare", "hihat", "clap", "bass", "keys", "lead", "pad"]

TRACK_PILLARS = {
    "kick":  "DRUMS",
    "snare": "DRUMS",
    "hihat": "DRUMS",
    "clap":  "DRUMS",
    "bass":  "BASS",
    "keys":  "HARMONY (MIDS)",
    "lead":  "SYNTHS",
    "pad":   "SYNTHS",
}

COLORS = {
    "kick":  "#ff5370",  # Coral Punch Red
    "snare": "#ffcb6b",  # Amber Snare Gold
    "hihat": "#89ddff",  # Ice Cyan Closed Hat
    "clap":  "#f78c6c",  # Warm Orange Handclap
    "bass":  "#c792ea",  # Electric Purple Groove Bass
    "keys":  "#2ee59d",  # Emerald Fender Rhodes / Piano Chords
    "lead":  "#00e5ff",  # Electric Cyan Pop Synth Lead
    "pad":   "#bb9af7",  # Lush Lavender Atmospheric Pad
}

TRACK_LABELS = {
    "kick":  "KICK 808",
    "snare": "POP SNARE",
    "hihat": "HI-HAT 16th",
    "clap":  "CLAP / PERC",
    "bass":  "GROOVE BASS",
    "keys":  "KEYS / CHORDS",
    "lead":  "SYNTH LEAD",
    "pad":   "LUSH PAD",
}

# Musical Pitch & Scale Mathematics (12-Tone Equal Temperament)
SEMI_MAP = {
    "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3,
    "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8,
    "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11
}

# All 12 Chromatic Bass Frequencies (Hz) for sub bass
BASS_FREQS = {
    "C1": 32.70, "C#1": 34.65, "DB1": 34.65,
    "D1": 36.71, "D#1": 38.89, "EB1": 38.89,
    "E1": 41.20,
    "F1": 43.65, "F#1": 46.25, "GB1": 46.25,
    "G1": 49.00, "G#1": 51.91, "AB1": 51.91,
    "A1": 55.00, "A#1": 58.27, "BB1": 58.27,
    "B1": 61.74, "C2": 65.41,
}

ROOT_TO_BASS_NOTE = {
    "C": "C1", "C#": "C#1", "DB": "C#1",
    "D": "D1", "D#": "D#1", "EB": "D#1",
    "E": "E1",
    "F": "F1", "F#": "F#1", "GB": "F#1",
    "G": "G1", "G#": "G#1", "AB": "G#1",
    "A": "A1", "A#": "A#1", "BB": "A#1",
    "B": "B1"
}

CHORD_FORMULAS = {
    "":       [0, 4, 7],      # Major Triad (1, 3, 5)
    "MAJ":    [0, 4, 7],
    "MAJOR":  [0, 4, 7],
    "M":      [0, 3, 7],      # Minor Triad (1, b3, 5)
    "MIN":    [0, 3, 7],
    "MINOR":  [0, 3, 7],
    "5":      [0, 7, 12],     # Heavy Rock Power Chord (Root, 5th, Octave)
    "POWER":  [0, 7, 12],
    "7":      [0, 4, 7, 10],  # Dominant 7th (1, 3, 5, b7)
    "DOM7":   [0, 4, 7, 10],
    "MAJ7":   [0, 4, 7, 11],  # Major 7th (1, 3, 5, 7) - J-Fusion / Pop staple
    "M7":     [0, 3, 7, 10],  # Minor 7th (1, b3, 5, b7)
    "MIN7":   [0, 3, 7, 10],
    "MAJ9":   [0, 4, 7, 11, 14], # Jazz / J-Fusion Major 9th
    "MIN9":   [0, 3, 7, 10, 14], # Jazz / J-Fusion Minor 9th
    "M9":     [0, 3, 7, 10, 14],
    "9":      [0, 4, 7, 10, 14], # Dominant 9th
    "11":     [0, 4, 7, 10, 14, 17], # Jazz 11th
    "M11":    [0, 3, 7, 10, 14, 17], # Minor 11th
    "13":     [0, 4, 7, 10, 14, 21], # Jazz 13th
    "MAJ13":  [0, 4, 7, 11, 14, 21],
    "M7B5":   [0, 3, 6, 10],  # Half-Diminished (J-Fusion staple)
    "HALF-DIM": [0, 3, 6, 10],
    "6":      [0, 4, 7, 9],   # Major 6th
    "M6":     [0, 3, 7, 9],   # Minor 6th
    "6/9":    [0, 4, 7, 9, 14],
    "7#9":    [0, 4, 7, 10, 15], # Hendrix Rock/Jazz chord
    "7B9":    [0, 4, 7, 10, 13],
    "SUS4":   [0, 5, 7],      # Suspended 4th
    "SUS2":   [0, 2, 7],      # Suspended 2nd
    "DIM":    [0, 3, 6],      # Diminished
    "DIM7":   [0, 3, 6, 9],
    "ADD9":   [0, 4, 7, 14],  # Add 9
}
