# Live lab: build a server, connect it, use an existing server

Run commands from the cloned **MCPJAM** folder. Use Python 3.10–3.13 with Tk.
For AI chat, use an MCP-capable VS Code/Copilot installation and account. The
explicit Python client works without an AI account or API key.

## 1. Clone and launch (start installation at the beginning)

Windows / PowerShell:

```powershell
git clone https://github.com/pranavsaigandikota/MCPJAM.git
Set-Location MCPJAM
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

Mac / Terminal with Homebrew:

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
bash setup.sh
bash run_app.sh
```

Without Homebrew, follow [MAC_SETUP.md](../MAC_SETUP.md)'s manual core setup.
Keep the app open. Core-only setup is enough to inspect UI/state and use MCP;
FluidSynth/audio and Gemini chat are optional. Use one app instance (port 8765).
Windows has been tested locally; native Mac execution still needs rehearsal.
If Git is unavailable, extract the student ZIP and open its MCPJAM folder.

## 2. Show the FastMCP server

Open [starter/mcp_server_sdk.py](starter/mcp_server_sdk.py). **Students edit
this file**, not the compatibility launcher at the repository root.
[solutions/mcp_server_solution.py](solutions/mcp_server_solution.py) contains
optional swing/mute examples. The instructor supplies the tempo tool in class.

```text
AI host → MCP client → FastMCP server → call_daw → music app
          MCP/stdio                     local app JSON socket
```

Explain these five parts before changing code:

- `FastMCP(...)`: creates the server using the pinned official Python SDK.
- `@mcp.tool()`: registers a function so a host can discover it.
- Function name, typed inputs and docstring: describe the callable contract.
- Validation and `call_daw`: enforce limits, then adapt to the existing app.
- `mcp.run()`: starts stdio transport; the host launches it. Keep stdout for MCP.

This lab uses `from mcp.server.fastmcp import FastMCP` with `mcp==1.19.0`.
Standalone FastMCP uses `from fastmcp import FastMCP`; do not mix installation
or examples from the two packages. The SDK handles protocol plumbing; your
app still needs validation, authorization and outcome verification.

## 3. Show the JSON where the host adds MCP

Open [../.vscode/mcp.json](../.vscode/mcp.json) in VS Code. The supplied entry
launches the **starter** server. When prompted, enter the absolute path of
this clone's virtual-environment Python. Find it in a second terminal:

Windows:

```powershell
.\.venv\Scripts\python.exe workshop_preflight.py --vscode-config
```

Mac:

```bash
./.venv/bin/python workshop_preflight.py --vscode-config
```

The output is a complete machine-specific JSON example. Copy its `command`
value into the prompt, or replace `.vscode/mcp.json` with that output if you
prefer fixed paths. Fixed paths are for your computer; do not commit them.

```json
{
  "servers": {
    "mcpjam": {
      "type": "stdio",
      "command": "ABSOLUTE_PATH_TO_YOUR_VENV_PYTHON",
      "args": ["ABSOLUTE_PATH_TO/workshop/starter/mcp_server_sdk.py"]
    }
  }
}
```

The checked-in version uses `${input:mcpjamPython}` for `command` and
`${workspaceFolder}` in `args`, so no instructor's Windows path is bundled.

- `servers`: VS Code's list of connections; `mcpjam` is a local label.
- `type: stdio`: start a local process and exchange MCP messages over its streams.
- `command`: Python from **this clone's .venv**, not an unrelated system Python.
- `args`: the server file to execute; each argument is a separate JSON string.

Open the whole MCPJAM folder in VS Code. Use **MCP: List Servers**, start
`mcpjam`, and inspect its output/tools. Complete the host's trust/approval
flow after reviewing the server. In an MCP-capable agent chat, enable this
server's tools. Generate a song using compose_music at default 120 BPM, then
try the missing set_tempo tool before implementing it. See the activity below.
The host starts the server; you start the music app separately.

Other hosts can use different schemas. `--host-config` prints an `mcpServers`
example; it is **not** the same schema as VS Code's `servers` file. Do not copy
JSON between hosts without checking their documentation.

## 4. Add and test set_tempo (15 minutes total)

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
3. Edit workshop/starter/mcp_server_sdk.py at YOUR EDIT GOES HERE, using the snippet supplied in class:

The instructor will provide the commented `set_tempo` snippet during the workshop.
It is intentionally omitted from this repository.

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

## 5. Connect an existing MCP server (instructor demonstration)

“Built-in tools” (file editing, shell or browser tools supplied by a host)
are not automatically MCP. A preinstalled/managed MCP integration may hide
its setup UI. **Existing MCP servers** still connect through the same discovery
and invocation model; you do not have to write FastMCP to use them.

For a complete optional two-server JSON, see
[examples/mcp-existing.vscode.json](examples/mcp-existing.vscode.json). Review
it and copy it into .vscode/mcp.json only for the prepared demo.

For a quick second-server demo, add this entry **inside the same `servers`
object** in `.vscode/mcp.json`, alongside `mcpjam` (keep valid JSON commas):

```json
"context7": {
  "type": "http",
  "url": "https://mcp.context7.com/mcp"
}
```

This HTTP example is documented in the [VS Code MCP reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).
It uses a URL instead of a local Python command. Start it with MCP: List Servers,
inspect the discovered tools, enable only the tools needed for your demo, and
ask for current library documentation. Provider access/rate limits may apply;
prepare it before class and keep the local lab as the required activity.

For other existing servers, use **MCP: Add Server** or **MCP: Browse MCP Servers**.
Choose the provider's official configuration, complete its login if required,
and inspect the available actions before using them. GitHub can expose repository
actions; Figma can expose design context; Zapier MCP can expose configured app
actions. Accounts, permissions and host support vary. Do not assume every host
ships these integrations or that every tool is safe to enable.

Keep tokens out of the repository. Production methods to remember: least
privilege, validation before actions, approvals for consequential writes,
untrusted tool output handling, and verifying outcomes rather than trusting
queued acknowledgements. MCP does not provide those policies automatically.

## Instructor pacing

During the existing demo/build segment, show the starter (2 min), the JSON and
host discovery (2 min), then an already-prepared existing server (1 min).
Use these in place of the longer tempo/code walkthrough; do not add time to
the 55-minute plan. Protect the 15-minute audience lab and 5-minute spare window.
Slides 20–21 show the build: navigate to the starter folder; 22–23 show tests.

Sources: [VS Code setup](https://code.visualstudio.com/docs/agent-customization/mcp-servers),
[configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration),
[official Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## Optional music showcase

See [MUSIC_GENERATOR.md](../MUSIC_GENERATOR.md) for 30-second AI-authored scores,
all 287 SoundFont presets, editable notes, and description-driven prompts.
Keep this outside the beginner lab so setup and student practice fit the hour.

The full music server also exposes the optional `compose_music` MCP prompt.
Use `workshop_client.py --server mcp_server_music.py --list-prompts` to demonstrate
prompt discovery, then `--prompt compose_music --arguments-file
workshop/examples/music-prompt.json` to retrieve its reusable instructions.
Retrieval alone runs no AI or audio. This is an optional instructor example;
the protected starter lab remains focused on tools. See [Music guide](../MUSIC_GENERATOR.md).

## Copilot music showcase (slide 27)

The classroom AI host is VS Code GitHub Copilot. Keep `.vscode/mcp.json` pointing
to the starter during the student lab. For the prepared music showcase, add the
`mcpjam-music` server entry from [.vscode/mcp.music.example.json](../.vscode/mcp.music.example.json)
to its `servers` object; both entries can share the existing mcpjamPython input.
Use **MCP: List Servers** to start the music server and enable its tools in chat.
Type `/` and select `compose_music`, then enter an original music description.
Copilot supplies web fetching/search when available, matches catalog sounds,
writes a score and requests a 30-second MP3. Source URL fetching is different
from web search; use a prepared link or disclose unavailable research. No Gemini
key is required. Generation returns a path and never autoplays. The instructor
prepares full audio dependencies; this does not expand the 15-minute core lab.
