# MCPJAM workshop: start here

Build one MCP tool in VS Code + GitHub Copilot. The starter makes a **30-second
MP3 at 120 BPM**. You add `set_tempo`, then change the same song to 150 BPM.

## 1. Clone

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

## 2. Install — choose your operating system

**Windows / PowerShell**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

**Mac / Terminal** — Homebrew required; [Mac help](MAC_SETUP.md).

```bash
bash setup.sh
```

Setup is chat-only by default: Python 3.10–3.13 plus offline audio rendering.
No Tk, Pygame, app window, MIDI hardware or Gemini key is needed.
Use the normal command above; core-only mode cannot generate MP3s.
If audio setup is blocked, pair with someone whose setup works.

## 3. Connect in VS Code

Open the **MCPJAM folder**, sign into Copilot and open `.vscode/mcp.json`.
Find your Python path with the command for your OS:

```powershell
# Windows
.\.venv\Scripts\python.exe workshop_preflight.py --vscode-config
```

```bash
# Mac
./.venv/bin/python workshop_preflight.py --vscode-config
```

Copy the printed `command` path into the Python-path prompt.
**MCP: List Servers → mcpjam → Start**, then enable its tools in Copilot agent chat.
Keep the starter connection for this activity. No Gemini API key is needed.

## 4. Make a song, then try the missing tool

Choose `/` → `compose_music` in Copilot and ask:

> Make an original energetic 30-second rock instrumental. Return its MP3 path
> without autoplay. Use get_state to verify the default 120 BPM.

Then ask:

> Use only MCPJAM tools to change this existing song to 150 BPM. Do not edit
> files, use the terminal, another server, or regenerate it. Verify with get_state.

**Expected: the tempo tool is unavailable.** Song generation works; `set_tempo`
has intentionally not been registered yet.

## 5. Student exercise: add set_tempo

Edit **`workshop/starter/mcp_server_sdk.py`** at `YOUR EDIT GOES HERE`, above
`if __name__`. Wait for the workshop snippet:

The instructor will provide the commented `set_tempo` snippet during the workshop.
It is intentionally omitted from this repository.

## 6. Restart and retry

Save → **MCP: List Servers → mcpjam → Restart** → refresh/enable tools.
Confirm `set_tempo` appears, then repeat the **same 150 BPM request**.

**Expected:** `get_state` reports 150 BPM and a new MP3 revision. Nothing autoplays.
Test 40 and 240; 300 must fail without changing state.

For your own project, replace the action, typed inputs and backend call. Keep
validation, permissions, clear results and a way to verify the effect.

## More help

- [Detailed lab and explicit terminal tests](workshop/README.md)
- [Optional swing/mute reference — tempo is supplied in class](workshop/solutions/mcp_server_solution.py)
- [Music capabilities](MUSIC_GENERATOR.md)
- [Live Figma slides](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ/MCP-Servers-Slides)

Windows has been tested. Mac instructions are provided; native Mac execution
still needs rehearsal. Prepare audio setup before class where possible.
