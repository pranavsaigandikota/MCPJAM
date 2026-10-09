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


# The manifest is enumerated from the bundled SoundFont, not a guessed GM list.
_MANIFEST = json.loads((Path(__file__).resolve().parent / "soundfonts/GeneralUser-GS/presets.json").read_text(encoding="utf-8"))
PRESETS = {preset["id"]: preset for preset in _MANIFEST["presets"]}
ALIASES = dict(INSTRUMENTS)
INSTRUMENTS.update({name: preset["midi_program"] for name, preset in PRESETS.items()})


def instrument_preset(instrument: str, drums: bool = False) -> dict:
    # Older projects stored piano on the drum track while actually using Standard Kit.
    if drums and instrument == "piano":
        return PRESETS["gs_128_0"]
    name = f"gs_0_{ALIASES[instrument]}" if instrument in ALIASES else instrument
    if name not in PRESETS:
        raise ValueError("Unknown instrument; read music://instruments/catalog")
    preset = PRESETS[name]
    if (preset["kind"] == "drum_kit") != drums:
        raise ValueError("Use a drum kit on channel 10 and a melodic preset on other channels")
    return preset


def instrument_catalog() -> dict:
    soundfont = Path(__file__).resolve().parent / "soundfonts/GeneralUser-GS/GeneralUser-GS.sf2"
    return {
        "sound_library": "GeneralUser GS",
        "soundfont_installed": soundfont.is_file(),
        "soundfont_sha256": _MANIFEST["soundfont_sha256"],
        "scope": "All 287 presets enumerated from the bundled SoundFont, including 13 drum kits",
        "program_numbering": "MIDI programs/channels are zero-based; percussion uses channel 9",
        "instruments": list(PRESETS.values()),
        "aliases": {name: f"gs_0_{number}" for name, number in ALIASES.items()},
        "usage": {
            "tool": "set_song_track or create_song_from_score (music server)",
            "instrument_argument": "Use a preset id or a legacy named alias",
            "drums": "Select a drum_kit preset for MIDI channel 9",
            "modern808": "Sampled bass/drums override GS timbres; instrument edits disable the corresponding override",
        },
    }


def register_instrument_catalog(mcp) -> None:
    @mcp.resource(CATALOG_URI, name="instrument_catalog",
                  description="Read the supported GeneralUser GS instrument names and MIDI programs. No playback changes.",
                  mime_type="application/json")
    def read_instrument_catalog() -> str:
        return json.dumps(instrument_catalog(), indent=2)
