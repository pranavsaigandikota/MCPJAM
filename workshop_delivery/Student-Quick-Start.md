# Student quick start

Clone from GitHub, or unzip so the package folder is called MCPJAM:

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

Basic Python is assumed; no MCP knowledge is required.
Complete setup before class. Mac users should first follow [MAC_SETUP.md](MAC_SETUP.md)
for Python with Tk, certificates, and host configuration. Both platforms use the
same Python files, tool names, validations, and exercises.

## Windows / PowerShell setup

From inside MCPJAM:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe workshop_preflight.py
```

Start the DAW from the parent folder:

```powershell
.\MCPJAM\.venv\Scripts\python.exe -m MCPJAM
```

## macOS / Terminal setup

From inside MCPJAM, using the documented Python 3.13 installation:

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python workshop_preflight.py
./.venv/bin/python -m tkinter
```

Close the Tk test window, then start the DAW from the parent folder:

```bash
cd ..
./MCPJAM/.venv/bin/python -m MCPJAM
```

Do not transfer virtual environments between computers; create one on each.
Activation is optional because commands use the venv interpreter directly.

The host launches the stdio server with absolute paths to this interpreter and
mcp_server_sdk.py. Do not launch another server manually for the host connection.
Configuration layout is host-specific; see README.md.
Print host JSON with your actual paths from inside MCPJAM using
`./.venv/bin/python workshop_preflight.py --host-config` on Mac or
`.\.venv\Scripts\python.exe workshop_preflight.py --host-config` on Windows.

## Exercise

Edit mcp_server_sdk.py above its main guard. Implement set_swing(amount: int):
register it, describe it, validate 0–75, send the set_swing backend command,
return the actual acknowledgement. Restart the host connection and rediscover.

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
To inspect the solution through the SDK client, add --server mcp_server_solution.py.
The local DAW socket is not MCP and has no authentication. Keep it on loopback.
