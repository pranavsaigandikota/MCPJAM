"""Small educational MCP server for MCPJAM.

This file intentionally shows the protocol boundary instead of hiding it in
an SDK. MCP messages arrive on stdin as JSON-RPC 2.0 requests. The server
turns tools/call requests into the DAW's simple localhost socket commands.
"""

import json
import socket
import sys
from typing import Any

HOST = "127.0.0.1"
PORT = 8765
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "get_state",
        "description": "Read the current tempo, pattern, and playback state.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_tempo",
        "description": "Set the DAW tempo in beats per minute.",
        "inputSchema": {
            "type": "object",
            "properties": {"bpm": {"type": "integer", "minimum": 40, "maximum": 240}},
            "required": ["bpm"],
        },
    },
    {
        "name": "set_chords",
        "description": "Set a repeating chord progression.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chords": {"type": "array", "items": {"type": "string"}},
                "song_ref": {"type": "string"},
            },
            "required": ["chords"],
        },
    },
    {
        "name": "set_pattern",
        "description": "Replace one 16-step drum or instrument pattern.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track": {"type": "string"},
                "steps": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 1}},
            },
            "required": ["track", "steps"],
        },
    },
    {
        "name": "playback",
        "description": "Start, pause, or stop the sequencer.",
        "inputSchema": {
            "type": "object",
            "properties": {"action": {"type": "string", "enum": ["play", "pause", "stop"]}},
            "required": ["action"],
        },
    },
]


def write_message(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def call_daw(command: dict[str, Any]) -> dict[str, Any]:
    """Send one legacy command to the DAW and return its acknowledgement."""
    with socket.create_connection((HOST, PORT), timeout=5) as connection:
        connection.sendall(json.dumps(command).encode("utf-8") + b"\n")
        reply = connection.makefile("rb").readline()
    if not reply:
        raise RuntimeError("The DAW closed the connection without a response")
    return json.loads(reply.decode("utf-8"))


def tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "get_state":
        return call_daw({"cmd": "get_state"})
    if name == "set_tempo":
        return call_daw({"cmd": "set_tempo", "bpm": arguments.get("bpm")})
    if name == "set_chords":
        return call_daw({"cmd": "set_chords", "chords": arguments.get("chords", []), "song_ref": arguments.get("song_ref", "")})
    if name == "set_pattern":
        return call_daw({"cmd": "set_pattern", "track": arguments.get("track"), "steps": arguments.get("steps", [])})
    if name == "playback":
        return call_daw({"cmd": arguments.get("action")})
    raise ValueError(f"Unknown tool: {name}")


def handle_request(request: dict[str, Any]) -> None:
    request_id = request.get("id")
    method = request.get("method")

    if request.get("jsonrpc") != "2.0" or not method:
        if request_id is not None:
            write_message(error_response(request_id, -32600, "Expected a JSON-RPC 2.0 request"))
        return

    if method == "initialize":
        write_message(response(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "mcpjam-teaching-server", "version": "1.0.0"},
        }))
        return
    if method == "tools/list":
        write_message(response(request_id, {"tools": TOOLS}))
        return
    if method == "tools/call":
        params = request.get("params", {})
        try:
            result = tool_call(params.get("name", ""), params.get("arguments", {}))
            write_message(response(request_id, {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "structuredContent": result,
                "isError": not result.get("ok", True),
            }))
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            write_message(response(request_id, {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True,
            }))
        return
    if method == "notifications/initialized":
        return
    if request_id is not None:
        write_message(error_response(request_id, -32601, f"Method not found: {method}"))


def main() -> None:
    for line in sys.stdin:
        if line.strip():
            try:
                handle_request(json.loads(line))
            except json.JSONDecodeError as exc:
                write_message(error_response(None, -32700, f"Invalid JSON: {exc.msg}"))


if __name__ == "__main__":
    main()
