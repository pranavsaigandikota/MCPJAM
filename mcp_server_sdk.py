"""Workshop MCP server built with the official Python MCP SDK.

Students can add tools below without implementing JSON-RPC themselves.
The DAW remains a separate local backend so the MCP boundary is easy to see.
"""

import json
import socket
from typing import Any

from mcp.server.fastmcp import FastMCP

HOST = "127.0.0.1"
PORT = 8765

mcp = FastMCP("mcpjam-workshop")


def call_daw(command: dict[str, Any]) -> dict[str, Any]:
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


@mcp.tool()
def get_state() -> dict[str, Any]:
    """Read the current tempo, playback state, chords, and patterns."""
    return call_daw({"cmd": "get_state"})


@mcp.tool()
def set_tempo(bpm: int) -> str:
    """Set the DAW tempo from 40 to 240 beats per minute."""
    if not 40 <= bpm <= 240:
        raise ValueError("bpm must be between 40 and 240")
    result = call_daw({"cmd": "set_tempo", "bpm": bpm})
    return f"Tempo command queued for {bpm} BPM: {result}. Read get_state to verify."


# Student exercise: add a tool that calls {"cmd": "set_swing", "amount": amount}.
# Student exercise: add a tool that calls {"cmd": "mute_track", "track": track, "muted": muted}.


if __name__ == "__main__":
    mcp.run()
