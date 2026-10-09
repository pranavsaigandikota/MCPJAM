"""AI-authored scores: no fixed genre, chord progression or melody template."""
import math
from pydantic import BaseModel, ConfigDict, Field
from instrument_catalog import instrument_preset


class ScoreTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    channel: int = Field(ge=0, le=15, strict=True, description="Unique zero-based MIDI channel; 9 is percussion")
    instrument: str = Field(description="Preset id from get_instrument_catalog, or a named alias")
    volume: int = Field(default=80, ge=0, le=100, strict=True)
    muted: bool = False


class ScoreNote(BaseModel):
    model_config = ConfigDict(extra="forbid")
    track: str
    pitch: int = Field(ge=0, le=127, strict=True, description="MIDI note number; on percussion, selects a drum sound")
    beat: float = Field(ge=0, allow_inf_nan=False)
    duration: float = Field(gt=0, allow_inf_nan=False, description="Length in beats; use overlaps for legato")
    velocity: int = Field(default=90, ge=1, le=127, strict=True)
    repeats: int = Field(default=1, ge=1, le=128, strict=True)
    every_beats: float = Field(default=4, gt=0, allow_inf_nan=False, description="Spacing between repetitions; vary notes to develop the motif")


def score_channels(spec):
    return {name: setting["channel"] for name, setting in spec["tracks"].items()}


def validate_score(spec):
    numerator = spec.get("time_signature_numerator", 4)
    denominator = spec.get("time_signature_denominator", 4)
    if type(numerator) is not int or not 1 <= numerator <= 12 or denominator not in (2, 4, 8, 16):
        raise ValueError("Use a time signature of 1–12 over 2, 4, 8 or 16")
    tracks = spec["tracks"]
    if not 1 <= len(tracks) <= 16:
        raise ValueError("Supply 1–16 tracks with unique MIDI channels")
    channels = []
    for name, setting in tracks.items():
        track = ScoreTrack(name=name, **setting)
        instrument_preset(track.instrument, track.channel == 9)
        channels.append(track.channel)
    if len(set(channels)) != len(channels):
        raise ValueError("Each track needs a unique MIDI channel")
    notes = spec.get("notes", [])
    if not 1 <= len(notes) <= 5000:
        raise ValueError("Supply 1–5000 note entries")
    expanded = 0
    end = spec["duration_seconds"] * spec["bpm"] / 60
    intervals = {}
    for entry in notes:
        note = ScoreNote.model_validate(entry)
        if note.track not in tracks:
            raise ValueError("A note refers to an unknown track")
        expanded += note.repeats
        if expanded > 5000:
            raise ValueError("Expanded score exceeds 5000 notes")
        for i in range(note.repeats):
            onset = note.beat + i * note.every_beats
            if onset >= end or onset + note.duration > end + 1e-6:
                raise ValueError("Notes must fit inside duration_seconds at this tempo")
            key = (note.track, note.pitch)
            intervals.setdefault(key, []).append((onset, onset + note.duration))
    # A second same-pitch note-on before note-off would cut off the first note.
    for ranges in intervals.values():
        ranges.sort()
        if any(b[0] < a[1] - 1e-6 for a, b in zip(ranges, ranges[1:])):
            raise ValueError("Overlapping notes of the same pitch/track are ambiguous; merge them")


def score_events(spec):
    events = []
    for setting in spec["tracks"].values():
        preset = instrument_preset(setting["instrument"], setting["channel"] == 9)
        events.append({"beat": 0.0, "type": "program_change", "channel": setting["channel"],
                       "program": preset["midi_program"], "bank": preset["bank"]})
    for entry in spec["notes"]:
        note = ScoreNote.model_validate(entry)
        setting = spec["tracks"][note.track]
        if setting["muted"] or setting["volume"] == 0:
            continue
        for i in range(note.repeats):
            beat = note.beat + i * note.every_beats
            velocity = max(1, min(127, round(note.velocity * setting["volume"] / 100)))
            events.extend([
                {"beat": beat, "type": "note_on", "channel": setting["channel"], "note": note.pitch, "velocity": velocity},
                {"beat": beat + note.duration, "type": "note_off", "channel": setting["channel"], "note": note.pitch, "velocity": 0},
            ])
    events.sort(key=lambda e: (e["beat"], 0 if e["type"] == "program_change" else 1 if e["type"] == "note_off" else 2))
    for event in events:
        event["time_sec"] = round(event["beat"] * 60 / spec["bpm"], 6)
    return events, [{"name": "ai_score", "start_bar": 1}]
