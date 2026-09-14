"""
mcpjam/midi_importer.py

Parses any Standard MIDI File (.mid) and produces a list of raw MIDI events
that can be directly dispatched to the MCPJAM Studio socket as a
{"cmd": "play_midi_raw", "events": [...]} command.

Each output event:
    {
        "time_sec": float,       # absolute time in seconds from start
        "type": "note_on" | "note_off" | "program_change",
        "channel": int,          # 0-15  (9 = drums)
        "note": int,             # 0-127
        "velocity": int,         # 0-127
        "program": int,          # GM program number (0-127)
    }
"""

import mido


def midi_note_to_name(note_num: int) -> str:
    """Convert a MIDI note number to a human-readable note name (e.g. 60 -> 'C4')."""
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_num // 12) - 1
    name = NOTE_NAMES[note_num % 12]
    return f"{name}{octave}"


def parse_midi_file(path: str, max_seconds: float = 20.0) -> dict:
    """
    Parse a MIDI file and return a dict with:
        {
            "bpm": int,
            "events": [ {time_sec, type, channel, note, velocity, program}, ... ]
        }
    Only the first max_seconds of the file are returned.

    Args:
        path: Absolute path to the .mid file.
        max_seconds: How many seconds of the file to import (default 20).
    """
    mid = mido.MidiFile(path)

    # Current tempo in microseconds per beat (default 120 BPM = 500000 µs/beat)
    tempo = 500000
    ticks_per_beat = mid.ticks_per_beat

    events = []
    channel_programs = {}  # channel -> current program number

    def ticks_to_sec(ticks):
        beats = ticks / ticks_per_beat
        return beats * (tempo / 1_000_000)

    # Merge all tracks into one absolute-time event stream
    absolute_events = []
    for track in mid.tracks:
        abs_tick = 0
        running_tempo = 500000
        for msg in track:
            abs_tick += msg.time
            absolute_events.append((abs_tick, running_tempo, msg))
            if msg.type == 'set_tempo':
                running_tempo = msg.tempo

    # Sort by absolute tick
    absolute_events.sort(key=lambda x: x[0])

    # Re-walk with proper tempo map
    tempo = 500000
    last_tick = 0
    elapsed_sec = 0.0
    tempo_map = []  # (abs_tick, tempo, elapsed_sec_at_that_tick)

    # Build a proper tempo map first
    raw_tempo_changes = [(0, 500000)]
    for _, _, msg in absolute_events:
        if msg.type == 'set_tempo':
            # We need the actual absolute tick for this, so re-do it properly
            pass

    # Proper approach: iterate each track separately to get tempo map
    tempo_map = [(0, 500000)]
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if msg.type == 'set_tempo':
                tempo_map.append((abs_tick, msg.tempo))

    tempo_map.sort(key=lambda x: x[0])
    # Deduplicate
    seen = set()
    clean_tempo = []
    for t in tempo_map:
        if t[0] not in seen:
            seen.add(t[0])
            clean_tempo.append(t)
    tempo_map = clean_tempo

    def tick_to_seconds(tick: int) -> float:
        """Convert an absolute tick to seconds using the tempo map."""
        elapsed = 0.0
        prev_tick = 0
        prev_tempo = 500000
        for map_tick, map_tempo in tempo_map:
            if map_tick >= tick:
                break
            elapsed += (map_tick - prev_tick) * prev_tempo / (ticks_per_beat * 1_000_000)
            prev_tick = map_tick
            prev_tempo = map_tempo
        elapsed += (tick - prev_tick) * prev_tempo / (ticks_per_beat * 1_000_000)
        return elapsed

    # Now parse all messages into absolute-time events
    channel_programs = {ch: 0 for ch in range(16)}
    merged = []

    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            merged.append((abs_tick, msg))

    merged.sort(key=lambda x: x[0])

    parsed_events = []
    for abs_tick, msg in merged:
        t = tick_to_seconds(abs_tick)
        if t > max_seconds:
            break

        if msg.type == 'program_change':
            channel_programs[msg.channel] = msg.program
            parsed_events.append({
                "time_sec": t,
                "type": "program_change",
                "channel": msg.channel,
                "program": msg.program,
                "note": 0,
                "velocity": 0
            })

        elif msg.type == 'note_on' and msg.velocity > 0:
            prog = 0 if msg.channel == 9 else channel_programs.get(msg.channel, 0)
            parsed_events.append({
                "time_sec": t,
                "type": "note_on",
                "channel": msg.channel,
                "note": msg.note,
                "velocity": msg.velocity,
                "program": prog
            })

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            parsed_events.append({
                "time_sec": t,
                "type": "note_off",
                "channel": msg.channel,
                "note": msg.note,
                "velocity": 0,
                "program": channel_programs.get(msg.channel, 0)
            })

    # Estimate BPM from the first tempo event
    bpm = 120
    for map_tick, map_tempo in tempo_map:
        if map_tempo > 0:
            bpm = round(60_000_000 / map_tempo)
            break

    return {
        "bpm": bpm,
        "events": parsed_events,
        "duration_sec": max(e["time_sec"] for e in parsed_events) if parsed_events else 0.0,
        "total_events": len(parsed_events),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python midi_importer.py path/to/song.mid [max_seconds]")
        sys.exit(1)
    path = sys.argv[1]
    max_sec = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
    result = parse_midi_file(path, max_sec)
    print(f"Parsed {result['total_events']} events | BPM: {result['bpm']} | Duration: {result['duration_sec']:.1f}s")
    for ev in result["events"][:20]:
        print(f"  {ev['time_sec']:.3f}s  {ev['type']:15s}  ch={ev['channel']}  note={ev['note']}  vel={ev['velocity']}  prog={ev['program']}")
