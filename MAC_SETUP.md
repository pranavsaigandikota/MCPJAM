# MCPJAM on Mac — Copilot chat only

The workshop generates 30-second MP3 files through MCP. No app window, Tk,
Pygame, MIDI hardware or Gemini API key is required.

## 1. Clone and install

Install [Homebrew](https://brew.sh) before class if it is not already installed.
Then, in Terminal:

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
bash setup.sh
```

The script reuses compatible Python 3.10–3.13 or installs Python 3.13. It installs
FluidSynth and the Python MCP/audio packages and
checks the bundled soundfont. It creates a local `.venv`; do not copy a Windows venv.
Core-only mode skips audio and cannot generate MP3s.

## 2. Connect in VS Code

Open the whole **MCPJAM** folder, sign into Copilot and run:

```bash
./.venv/bin/python workshop_preflight.py --vscode-config
```

Use the printed absolute Python path in `.vscode/mcp.json`'s input prompt.
Run **MCP: List Servers → mcpjam → Start**, then enable its tools in agent chat.
If VS Code says the session runtime has not been created, send a chat message
first, then start the server again.

## 3. Create a song and do the activity

Choose `/` → `compose_music` and ask for an original 30-second instrumental.
Request its MP3 path without autoplay. Generate a song before calling `get_state`.
The starter uses 120 BPM. `set_tempo` is deliberately absent until you add the
snippet supplied during the workshop. Save, restart the MCP server, refresh tools,
then retry 150 BPM and verify the new MP3 path. 300 BPM must be rejected.

See the [student instructions](README.md) and [detailed lab](workshop/README.md).

## Optional graphical app

Only for people choosing the GUI: run `bash setup.sh --with-gui`, then
`bash run_app.sh`. This additionally installs Tk and Pygame.

## Troubleshooting

| Problem | Action |
| --- | --- |
| Homebrew missing | Install it before class, or pair with an audio-ready learner. |
| FluidSynth library missing | Run `brew install fluid-synth`, then rerun setup. |
| Wrong Python path | Use the absolute `.venv/bin/python` path printed by preflight. |
| Connection refused from get_state | Create a song first; the empty-song path can fall back to the optional GUI. |
| set_tempo unavailable | Expected before the activity; after editing, restart and refresh tools. |

The Mac scripts are reviewed; a native Mac rehearsal is still required.
