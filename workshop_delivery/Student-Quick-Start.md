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
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -CoreOnly
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

## macOS / Terminal setup

With Homebrew installed, from inside MCPJAM:

```bash
bash setup.sh --core-only
bash run_app.sh
```

Core-only setup installs the workshop dependencies; verify changes in the app UI
and through get_state. For optional sampled audio, omit the core-only flag to also
configure FluidSynth. GeneralUser GS and its license are bundled.
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

1. Open the whole MCPJAM folder and sign into Copilot with agent/MCP access.
2. Open `.vscode/mcp.json`. Keep its starter connection for the lab.
3. Run `workshop_preflight.py --vscode-config` using your .venv Python to find
   its absolute path; enter that path when VS Code prompts for mcpjamPython.
4. Run **MCP: List Servers**, start **mcpjam**, then enable its tools in Copilot
   agent chat. Ask: “Use set_tempo to set 120 BPM, then get_state to verify.”
5. After adding set_swing, save and restart mcpjam; confirm the new tool appears.
   Test 35, 0, 75 and invalid 100. Verify state after each call.

Copilot uses your account; a Gemini API key is not part of this route.
If Copilot is unavailable, use the explicit calls below.

## Exercise

Edit workshop/starter/mcp_server_sdk.py above its main guard. Implement set_swing(amount: int):
register it, describe it, validate 0–75, send the set_swing backend command,
return the actual acknowledgement. Restart the host connection and rediscover.
AI may generate the short function. You must explain the contract, scope,
validation and outcome checks. The main workshop emphasizes theory and application;
full implementations remain in the repository. The current presentation has 29 slides.
Slide 15 maps the activity: 14 traces MCP versus the backend, 16 explains the
contract, 20 is MCP BUILD, 21 is the Copilot connection, and 22–23 are MCP TEST. Edit workshop/starter/mcp_server_sdk.py;
test with workshop_client.py and verify actual state with get_state.
The protected activity is 15 minutes, including a short guided build.
See the repository README.md for the 55-minute plan plus 5 minutes spare and the VS Code Copilot walkthrough.

Call 35, 0, 75, and 100 explicitly. Invalid 100 must produce a tool error before
the backend call. Read the `swing` key in get_state's result and allow the UI to
process queued commands. A natural-language refusal does not prove validation.

## Explicit calls without a host UI

From inside MCPJAM (the DAW must already be running), **macOS**:

```bash
./.venv/bin/python workshop_client.py
./.venv/bin/python workshop_client.py --tool set_tempo --arguments '{"bpm":120}'
./.venv/bin/python workshop_client.py --tool set_swing --arguments '{"amount":35}'
./.venv/bin/python workshop_client.py --tool set_swing --arguments '{"amount":100}'
./.venv/bin/python workshop_client.py --tool get_state
```

**Windows / PowerShell**:

```powershell
.\.venv\Scripts\python.exe workshop_client.py
.\.venv\Scripts\python.exe workshop_client.py --tool set_tempo --arguments '{"bpm":120}'
.\.venv\Scripts\python.exe workshop_client.py --tool set_swing --arguments '{"amount":35}'
.\.venv\Scripts\python.exe workshop_client.py --tool set_swing --arguments '{"amount":100}'
.\.venv\Scripts\python.exe workshop_client.py --tool get_state
```

Client exits with code 1 for a tool error; that is expected for invalid inputs.
For a call that avoids native JSON quoting differences across PowerShell versions:

```powershell
Set-Content -LiteralPath swing-input.json -Value '{"amount":35}' -Encoding UTF8
.\.venv\Scripts\python.exe workshop_client.py --tool set_swing --arguments-file swing-input.json
```

Starter has two tools; the completed solution adds swing and mute.
To inspect the solution through the SDK client, add --server workshop/solutions/mcp_server_solution.py.
The local DAW socket is not MCP and has no authentication. Keep it on loopback.


Follow the [live FastMCP/configuration walkthrough](../workshop/README.md) for starter/solution folders, VS Code JSON and the existing-server demo.

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
