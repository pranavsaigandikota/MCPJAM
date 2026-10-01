# MCPJAM Studio: build an MCP server

MCPJAM is a small Python DAW used as the backend for an MCP workshop. By the
end, students will have built and tested a real MCP server with the official
Python SDK.

The revised slides, speaker notes, checkpoints, and one-hour teaching plan are
in [Instructor-Guide.md](Instructor-Guide.md).

## What students build

The important file is `mcp_server_sdk.py`. It is an intentionally small
starter server:

- `FastMCP` creates the MCP server.
- `@mcp.tool()` exposes a Python function as an MCP tool.
- `call_daw()` sends the tool's action to the music application.
- `mcp.run()` starts the MCP transport.

Students do not need to implement JSON-RPC by hand. The SDK handles
initialization, tool discovery, request IDs, and tool-call responses. The
older `mcp_server.py` file is available as an optional protocol-inspection
example.

## Setup

Clone this repository (the same command works in PowerShell and Mac Terminal):

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

Or download the [student pack](MCPJAM-Student-Code.zip), then
extract it so the inner package folder is named `MCPJAM`. Both routes contain
the same starter and completed solution. Read
[Student Quick Start](Student-Quick-Start.md), or follow the
platform commands below. The
[workshop slides](MCPJAM-Workshop-Windows-and-Mac.pptx) and
[PDF](MCPJAM-Workshop-Windows-and-Mac.pdf) are also included.

Keep the package folder named `MCPJAM`. Install dependencies before
class, from inside that folder. The code requires Python 3.10+; for a new Mac
installation use the standard Python **3.13** macOS installer from
[python.org](https://www.python.org/downloads/macos/). See
[Mac setup and troubleshooting](MAC_SETUP.md) for the full path.

**Windows / PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Check the workshop environment, then start the DAW from the package's parent:

```powershell
.\.venv\Scripts\python.exe workshop_preflight.py
cd ..
.\MCPJAM\.venv\Scripts\python.exe -m MCPJAM
```

**macOS / Terminal (zsh or bash)**

```bash
# Inside MCPJAM; python3.13 is the installed Python.
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python workshop_preflight.py
./.venv/bin/python -m tkinter
# Close the Tk test window, then start the DAW from the parent folder.
cd ..
./MCPJAM/.venv/bin/python -m MCPJAM
```

Activation is optional: these commands select the interpreter explicitly.
Create `.venv` on each computer; do not copy a Windows environment to a Mac.
Keep the DAW terminal open during the lab.

The MCP host launches `mcp_server_sdk.py` as a stdio subprocess. Configure
the host as below; a separate manually launched server is not that connection.

The DAW must be running before students call tools because the SDK server
connects to `127.0.0.1:8765`.

## Connect an MCP host

Configure your host with absolute paths to the virtual-environment Python and
SDK server. The `mcpServers` structure below is a host-specific example; adapt
it to your host's configuration format. Keep paths containing spaces in one
JSON string. Do not use `~` in these paths.

**Windows example**

```json
{
  "mcpServers": {
    "mcpjam": {
      "command": "C:/path/to/MCPJAM/.venv/Scripts/python.exe",
      "args": ["C:/path/to/MCPJAM/mcp_server_sdk.py"]
    }
  }
}
```

**macOS example** (replace `YOUR_USERNAME` and the project directory):

```json
{
  "mcpServers": {
    "mcpjam": {
      "command": "/Users/YOUR_USERNAME/Documents/MCPJAM/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/Documents/MCPJAM/mcp_server_sdk.py"]
    }
  }
}
```

Print JSON with your actual paths from inside `MCPJAM`:

```bash
# macOS
./.venv/bin/python workshop_preflight.py --host-config
```

```powershell
# Windows
.\.venv\Scripts\python.exe workshop_preflight.py --host-config
```

Restart the host, then ask it to set the tempo or read the DAW state. The host
will discover `get_state` and `set_tempo` from the server.

Test through the supplied SDK client without an AI host, from inside `MCPJAM`
with the DAW running:

```bash
# macOS
./.venv/bin/python workshop_client.py
./.venv/bin/python workshop_client.py --tool set_tempo --arguments '{"bpm":120}'
./.venv/bin/python workshop_client.py --tool get_state
```

```powershell
# Windows: an input file avoids native JSON quoting differences.
Set-Content -LiteralPath tempo-input.json -Value '{"bpm":120}' -Encoding UTF8
.\.venv\Scripts\python.exe workshop_client.py --tool set_tempo --arguments-file tempo-input.json
.\.venv\Scripts\python.exe workshop_client.py --tool get_state
```

## Student exercise

Start with the two working tools and add these tools one at a time:

```python
@mcp.tool()
def set_swing(amount: int) -> str:
    """Set the groove swing from 0 to 75 percent."""
    if not 0 <= amount <= 75:
        raise ValueError("amount must be between 0 and 75")
    result = call_daw({"cmd": "set_swing", "amount": amount})
    return f"Swing command queued: {result}. Read get_state to verify."
```

Then add `mute_track(track: str, muted: bool)` using the DAW command
`{"cmd": "mute_track", "track": track, "muted": muted}`.

The starter intentionally contains only `get_state` and `set_tempo`. See
[mcp_server_solution.py](mcp_server_solution.py) after attempting the exercise.
To test the completed version, add `--server mcp_server_solution.py` to a
`workshop_client.py` command. Do not configure the older manual protocol sketch
as the workshop server.

This means students really do build an MCP server: they define tools, give
them descriptions and typed inputs, validate arguments, call a backend, and
return a useful result. The SDK supplies the protocol plumbing around their
code.

## One-hour workshop

Install dependencies and rehearse host setup **before class**. Basic Python
functions and dictionaries are assumed; no previous MCP experience is needed.

1. **0-12 minutes:** Demo, architecture, capabilities.
2. **12-20 minutes:** Connect, observe/act/verify, protocol lifecycle.
3. **20-30 minutes:** Read a tool, validation, exercise briefing.
4. **30-45 minutes:** Build `set_swing`, test, troubleshoot.
5. **45-57 minutes:** Guided `mute_track`, security, remote and advanced concepts.
6. **57-60 minutes:** Demonstrate and explain the server.

One implemented new tool is required; `mute_track` is a guided/stretch task.
The backend acknowledges writes when queued, so read `get_state` after the UI
processes the command to verify the change. The demo socket is unauthenticated
and should remain on loopback. It is not a production MCP endpoint.

The workshop pins the official MCP Python SDK to **1.19.0** for its `FastMCP`
API. Newer major versions may use different APIs. `mcp_server.py` is an older,
incomplete protocol sketch, not the workshop or production server.

## The protocol connection

The project contains two different connections:

1. `mcp_server_sdk.py` speaks MCP through the SDK over stdin/stdout.
2. `app.py` accepts simple newline-delimited JSON over the local socket.

The second connection is only the demo backend. It is not MCP. The SDK server
is the adapter between the AI host and the DAW.
