"""Workshop MCP server built with the official Python MCP SDK.

Students can add tools below without implementing JSON-RPC themselves.
The DAW remains a separate local backend so the MCP boundary is easy to see.
"""

import json
import socket
from typing import Any

# FastMCP in the pinned official SDK builds tool schemas and handles MCP messages.
# This is not the separate package imported with "from fastmcp import FastMCP".
from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path

# Find shared app helpers from either Windows or Mac, even when the host starts here.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from instrument_catalog import register_instrument_catalog
from music_score import ScoreTrack, ScoreNote
from music_prompts import register_music_prompts
from workshop_music import create_default_song, song_state, change_tempo

# Local app backend: this socket speaks app JSON, not MCP. Keep it on loopback.
HOST = "127.0.0.1"
PORT = 8765

# One server groups the tools that compatible AI hosts can discover and call.
mcp = FastMCP("mcpjam-workshop")
# Resources provide read-only context; tools below expose actions.
register_instrument_catalog(mcp)
register_music_prompts(mcp, default_bpm=120)


def call_daw(command: dict[str, Any]) -> dict[str, Any]:
    state = song_state()
    if state is not None and command['cmd'] == 'get_state':
        return state
    if state is not None and command['cmd'] == 'set_tempo':
        return change_tempo(command['bpm'])
    return call_app(command)


def call_app(command: dict[str, Any]) -> dict[str, Any]:
    # The adapter sends a validated command to the app; MCP transport stays separate.
    # Production pattern: bound waiting time and reply size instead of trusting a backend.
    with socket.create_connection((HOST, PORT), timeout=5) as connection:
        connection.sendall(json.dumps(command).encode("utf-8") + b"\n")
        with connection.makefile("rb") as stream:
            reply = stream.readline(1_048_577)
    if not reply:
        raise RuntimeError("The DAW did not return a response")
    if len(reply) > 1_048_576 or not reply.endswith(b"\n"):
        raise RuntimeError("The DAW response exceeded the limit or was incomplete")
    result = json.loads(reply.decode("utf-8"))
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise RuntimeError(f"DAW rejected the command: {result}")
    return result


# The decorator exposes this Python function as an MCP tool.
# Its name, annotations and docstring form the tool contract the host sees.
@mcp.tool()
def get_state() -> dict[str, Any]:
    """Read the current tempo, playback state, chords, and patterns."""
    return call_daw({"cmd": "get_state"})


# REFERENCE ANSWER: this is the set_tempo tool students add to the starter.
@mcp.tool()
def set_tempo(bpm: int) -> dict[str, Any]:
    """Set tempo from 40 to 240 BPM."""
    # Enforce the range in code: a description alone cannot prevent an unsafe input.
    if type(bpm) is not int or not 40 <= bpm <= 240:
        raise ValueError("bpm must be between 40 and 240")
    # A write acknowledgement can mean queued, so read actual state afterwards.
    return call_daw({"cmd": "set_tempo", "bpm": bpm})


@mcp.tool()
def get_instrument_catalog(query: str = '', kind: str = 'all', offset: int = 0, limit: int = 40) -> dict:
    """Find available instrument ids for the user's description."""
    from mcp_server_music import get_instrument_catalog as search
    return search(query, kind, offset, limit)


@mcp.tool()
def create_song_from_score(title: str, tracks: list[ScoreTrack], notes: list[ScoreNote],
                           genre: str = 'original', time_signature_numerator: int = 4,
                           time_signature_denominator: int = 4) -> dict:
    """Render an original 30-second MP3 at default 120 BPM without autoplay."""
    return create_default_song(title, tracks, notes, genre,
                               time_signature_numerator, time_signature_denominator)


# OPTIONAL EXTENSIONS: set_swing and mute_track are implemented below.
# 1. Use @mcp.tool() and a short docstring explaining the 0–75 range.
# 2. Reject invalid input with ValueError BEFORE calling the app.
# 3. call_daw({"cmd": "set_swing", "amount": amount}), then return its acknowledgement.
# 4. Test 35, 0, 75 and invalid 100; use get_state to verify the outcome.
# Student exercise: add a tool that calls {"cmd": "mute_track", "track": track, "muted": muted}.


@mcp.tool()
def set_swing(amount: int) -> str:
    """Set groove swing from 0 to 75 percent."""
    # Reject out-of-range input before it reaches the backend.
    if not 0 <= amount <= 75:
        raise ValueError("amount must be between 0 and 75")
    result = call_daw({"cmd": "set_swing", "amount": amount})
    return f"Swing command queued: {result}. Read get_state to verify."


@mcp.tool()
def mute_track(track: str, muted: bool) -> str:
    """Mute or unmute one known DAW track."""
    allowed = {"kick", "snare", "hihat", "clap", "bass", "keys", "lead", "pad"}
    if track not in allowed:
        raise ValueError("Unknown track: " + track)
    result = call_daw({"cmd": "mute_track", "track": track, "muted": muted})
    return f"Mute command queued: {result}. Read get_state to verify."


# The host launches this file and talks over stdin/stdout (stdio).
# Never print debug text to stdout here: it would corrupt protocol messages.
# Send diagnostics to stderr instead. Reconnect the host after changing tools.
if __name__ == "__main__":
    mcp.run()
