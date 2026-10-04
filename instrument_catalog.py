"""Read-only MCP catalog of the instruments supported by MCPJAM."""
import json
from pathlib import Path

CATALOG_URI = "music://instruments/catalog"
INSTRUMENTS = {
    "piano": 0, "electric_piano": 4, "nylon_guitar": 24,
    "acoustic_guitar": 25, "electric_guitar": 27, "finger_bass": 33,
    "synth_bass": 38, "violin": 40, "viola": 41, "cello": 42, "contrabass": 43,
    "strings": 48, "choir": 52, "trumpet": 56,
    "saxophone": 65, "flute": 73, "synth_lead": 81, "warm_pad": 89,
}


def instrument_catalog() -> dict:
    """Describe supported presets without loading audio or contacting the app."""
    soundfont = Path(__file__).resolve().parent / "soundfonts" / "GeneralUser-GS" / "GeneralUser-GS.sf2"
    return {
        "sound_library": "GeneralUser GS",
        "soundfont_installed": soundfont.is_file(),
        "scope": "Presets supported by MCPJAM's song editor, not every preset in the SoundFont",
        "program_numbering": "MIDI program values are zero-based; display numbers are one-based",
        "instruments": [
            {"id": name, "name": name.replace("_", " ").title(),
             "bank": 0, "midi_program": program, "display_program": program + 1}
            for name, program in INSTRUMENTS.items()
        ],
        "usage": {
            "melodic_tracks": ["keys", "bass", "pad", "lead"],
            "tool": "set_song_track (music server only)",
            "instrument_argument": "Use an instrument id from this catalog",
            "drums": "MIDI channel 10 (zero-based 9); song editor permits drum volume/mute edits, not melodic preset selection",
            "modern808": "Songs using the modern808 sample layer can override bass/drum audio; this resource catalogs GeneralUser GS presets only",
        },
    }


def register_instrument_catalog(mcp) -> None:
    @mcp.resource(CATALOG_URI, name="instrument_catalog",
                  description="Read the supported GeneralUser GS instrument names and MIDI programs. No playback changes.",
                  mime_type="application/json")
    def read_instrument_catalog() -> str:
        return json.dumps(instrument_catalog(), indent=2)
