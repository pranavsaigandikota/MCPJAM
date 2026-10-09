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
    # App adapter: reuse rendering for a saved song, or the optional GUI socket.
    # This routing is application logic; MCP messages are handled by FastMCP.
    # A generated song is rendered to MP3; the GUI socket remains the core-only fallback.
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
    """Read the generated workshop song's tempo and MP3 path, or the running app state."""
    return call_daw({"cmd": "get_state"})


@mcp.tool()
def get_instrument_catalog(query: str = '', kind: str = 'all', offset: int = 0, limit: int = 40) -> dict:
    """Find actual available instrument ids; choose sounds for the user's description."""
    from mcp_server_music import get_instrument_catalog as search
    return search(query, kind, offset, limit)


@mcp.tool()
def create_song_from_score(title: str, tracks: list[ScoreTrack], notes: list[ScoreNote],
                           genre: str = 'original', time_signature_numerator: int = 4,
                           time_signature_denominator: int = 4) -> dict:
    """Render an original 30-second MP3 at the default 120 BPM. Choose tracks and notes;
    no fixed melody or instrument palette is inserted. There is no tempo input yet.
    All notes must fit within 60 quarter-note beats. Never autoplay the result.
    """
    return create_default_song(title, tracks, notes, genre,
                               time_signature_numerator, time_signature_denominator)


# YOUR EDIT GOES HERE: add set_tempo(bpm: int), above the startup block.
# BEFORE YOUR EDIT: get_state works, but set_tempo is absent from discovery.
# An explicit set_tempo call must fail because the tool has not been registered.
# 1. REGISTER: @mcp.tool() makes your function discoverable by the MCP client.
# 2. CONTRACT: bpm: int defines the input type; -> dict describes returned data.
# 3. DESCRIBE: a docstring tells the host/model what the tool does and its range.
# 4. VALIDATE: reject values outside 40–240 BEFORE calling the backend.
# 5. ERROR: raise ValueError; FastMCP returns a tool error to the client.
# 6. ADAPTER + RESULT: call_daw delegates to existing app logic; return its data.
# AFTER YOUR EDIT: save, restart the MCP server, and discover set_tempo.
# Repeat the SAME call with bpm=150; get_state must report bpm=150.
# Test boundaries 40 and 240 and invalid 300; invalid input must not reach the app.
# Production pattern: validate inputs and verify state instead of trusting "queued".
# Optional extension: add set_swing with amount 0–75 after completing tempo.


# The host launches this file and talks over stdin/stdout (stdio).
# Never print debug text to stdout here: it would corrupt protocol messages.
# Send diagnostics to stderr instead. Reconnect the host after changing tools.
if __name__ == "__main__":
    mcp.run()
