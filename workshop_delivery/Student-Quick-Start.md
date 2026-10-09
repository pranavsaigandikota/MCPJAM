# Student quick start

Clone from GitHub, or unzip so the package folder is called MCPJAM:

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

Basic Python is assumed; no MCP knowledge is required.
Prepare before class if possible; installation also starts near the beginning.
Mac users should first follow [MAC_SETUP.md](../MAC_SETUP.md)
for Python with Tk, certificates, and host configuration. Both platforms use the
same Python files, tool names, validations, and exercises.

## Windows / PowerShell setup

From inside MCPJAM:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

## macOS / Terminal setup

With Homebrew installed, from inside MCPJAM:

```bash
bash setup.sh
bash run_app.sh
```

Full setup installs the MP3 renderer and configures FluidSynth. If native audio setup
is blocked, use core-only setup to verify tempo through the GUI and get_state, and
pair with an audio-ready learner for the MP3. GeneralUser GS and its license are bundled.
Use Play/Pause, Stop, or Space in the desktop app. It starts paused.
Windows has been tested; Mac runtime has not yet been verified.
Create a new virtual environment on each computer.

The host launches the stdio server with absolute paths to this interpreter and
workshop/starter/mcp_server_sdk.py. Do not launch another server manually for the host connection.
Configuration layout is host-specific; see [the live lab](../workshop/README.md).
Print host JSON with your actual paths from inside MCPJAM using
`./.venv/bin/python workshop_preflight.py --vscode-config` on Mac or
`.\.venv\Scripts\python.exe workshop_preflight.py --vscode-config` on Windows.

## VS Code + GitHub Copilot

Open the whole clone, sign into Copilot, open .vscode/mcp.json, and enter your
absolute .venv Python path. MCP: List Servers → mcpjam → Start. Enable its tools.
Use the starter connection throughout the activity. Full audio setup is required
to generate MP3s; omit the core-only option from the setup commands above.

## Student exercise: add set_tempo

The supplied starter can generate an original **30-second MP3 at 120 BPM**.
It already exposes get_instrument_catalog, create_song_from_score and get_state,
plus compose_music instructions. The tempo input is absent from creation;
set_tempo is intentionally unregistered. AI still selects sounds and writes notes.

Full audio setup is required for MP3 rendering: run setup.ps1 without -CoreOnly
on Windows or bash setup.sh without --core-only on Mac. Prepare before class
where possible. Core-only learners can use the running app to verify the same
tempo tool without rendering; pair them with an audio-ready learner for the MP3.

1. Start the starter connection in VS Code. Use / → compose_music with an
   original genre description. Request a 30-second song; creation uses 120 BPM.
   Return the MP3 path, without autoplay. Use get_state to confirm bpm=120.
2. Ask: **“Use only MCPJAM tools to set this song to 150 BPM. Do not edit code,
   use the terminal, another server, or regenerate it. Then verify with get_state.”**
   Copilot should explain that set_tempo is unavailable. An explicit call below
   must return a tool error/exit 1. This expected failure proves missing capability.
3. Edit workshop/starter/mcp_server_sdk.py at YOUR EDIT GOES HERE. Add:

```python
@mcp.tool()
def set_tempo(bpm: int) -> dict:
    """Change tempo from 40 to 240 BPM."""
    if not 40 <= bpm <= 240:
        raise ValueError("Use 40–240 BPM")
    return call_daw({"cmd": "set_tempo", "bpm": bpm})
```

4. Save. Run MCP: List Servers → mcpjam → Restart and refresh/enable tools.
   Confirm set_tempo appears. Repeat the **same 150 BPM request**.
5. get_state must now report bpm=150. For a rendered song, use the returned new
   MP3 path; the file is re-rendered, not merely relabeled. No autoplay.
6. Test 40 and 240, then invalid 300. Invalid input must fail before the backend
   changes. Explain registration, schema, validation, adapter and verification.

For a song, slower tempo crops notes beyond the 30-second endpoint; faster tempo
can leave a longer outro. Pitches and beat spacing stay unchanged. The original
notes are retained so a later tempo increase can restore them. The supplied
adapter routes song edits to rendering, or to the local GUI for the core-only lab.

Windows, **before adding the tool**, with the app/song ready:

```powershell
Set-Content -LiteralPath tempo-input.json -Value '{"bpm":150}' -Encoding UTF8
.\.venv\Scripts\python.exe workshop_client.py --tool set_tempo --arguments-file tempo-input.json
```

Expect exit 1. Run that exact command again after adding the function: expect
success. Read state with `.\.venv\Scripts\python.exe workshop_client.py --tool get_state`.

Mac:

```bash
./.venv/bin/python workshop_client.py --tool set_tempo --arguments '{"bpm":150}'
./.venv/bin/python workshop_client.py --tool get_state
```

The explicit client starts a fresh server each invocation; VS Code requires a
restart after edits. Test invalid 300 with the explicit client, since an LLM may
refuse without actually invoking validation. Compare workshop/solutions only
after your attempt. Swing and mute are optional extensions, not the required lab.

## Instructor music showcase

After full audio setup, use [.vscode/mcp.music.example.json](../.vscode/mcp.music.example.json)
for a separate **mcpjam-music** connection. Add its server entry to the existing
`servers` object, keeping the interpreter input and valid JSON. Start that server
and enable its tools. In Copilot chat, type `/` and select `compose_music`.
Provide a description; the host researches if web tools are available, matches
sounds to the catalog, writes notes and requests a 30-second MP3.
If search is unavailable, supply a source URL for fetching or compose from the
description. Generation returns a local path without autoplay. This is an
instructor showcase, not an extra requirement in the 15-minute student lab.
