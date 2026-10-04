"""Read-only music theory reference exposed by the music MCP server."""
import json

THEORY_URI = "music://theory/reference"
THEORY_REFERENCE = {
    "keys_and_scales": {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "natural_minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    },
    "triads": {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "diminished": [0, 3, 6],
    },
    "seventh_chords": {
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "dominant7": [0, 4, 7, 10],
        "min7_flat5": [0, 3, 6, 10],
    },
    "common_progressions": {
        "pop_major": ["I", "V", "vi", "IV"],
        "rnb_minor_seventh": ["i7", "VImaj7", "IIImaj7", "VII7"],
        "jazz_ii_v_i": ["ii7", "V7", "Imaj7"],
        "jazz_turnaround": ["Imaj7", "vi7", "ii7", "V7"],
    },
    "arrangement_guidance": {
        "held_notes": "Use legato articulation and longer note durations for connected melodic phrases; keep drum notes short.",
        "dynamics": "Use a crescendo to build, decrescendo to release, or swell for a rise-and-fall phrase.",
        "piano_motion": "Use up_down for a scalar/arpeggiated single-note piano figure instead of block chords.",
        "velocity": "Track volume sets the base level; dynamics shape velocity over the song timeline.",
    },
    "mcp_edit_values": {
        "articulation": ["legato", "normal", "staccato"],
        "dynamics": ["flat", "crescendo", "decrescendo", "swell"],
        "piano_motion": ["chords", "up_down"],
    },
}


def register_music_theory(mcp) -> None:
    @mcp.resource(
        THEORY_URI,
        name="music_theory_reference",
        description="Read-only scales, chords, progressions, and arrangement guidance used by the music tools.",
        mime_type="application/json",
    )
    def read_music_theory() -> str:
        return json.dumps(THEORY_REFERENCE, indent=2)
