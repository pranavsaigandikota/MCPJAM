# MCPJAM on macOS

Use the same starter, exercises and tool names as Windows. Only installation,
executable paths and shell commands differ. Complete setup before class.

## 1. Install Python with Tk

For a new installation, use the standard **Python 3.13 universal2 macOS
installer** from [Python's macOS downloads](https://www.python.org/downloads/macos/).
The installer runs on Intel and Apple Silicon and includes native Tk; see
[Python's macOS installation guide](https://docs.python.org/3/using/mac.html).
The [pygame release files](https://pypi.org/project/pygame/#files) include Python
3.13 wheels for both Mac architectures. Use a normal build for this workshop.

After installation, run `Install Certificates.command` in the matching
`/Applications/Python 3.13` folder, as described in Python's installation guide.
Open a new Terminal window:

```bash
python3.13 --version
python3.13 -m tkinter
```

A small Tk window should open; close it. If you already have Python 3.10–3.13
with working Tk, use its versioned command instead of `python3.13`. Avoid
Apple's `/usr/bin/python3` for this class. If using Homebrew or another
distribution, Tk must be installed for the same interpreter; it cannot be
installed with pip. The python.org installer is the documented class route.

## 2. Clone or extract, then install

Clone from Terminal:

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

If Git is unavailable on your Mac, use the downloadable
[student zip](https://github.com/pranavsaigandikota/MCPJAM/raw/refs/heads/main/workshop_delivery/MCPJAM-Student-Code.zip)
instead. Extract it so the inner package is named **MCPJAM**, then open Terminal
in that folder. The directory must contain `requirements.txt` and `app.py`.

From inside the cloned or extracted folder:

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python workshop_preflight.py
./.venv/bin/python -m tkinter
```

Close the Tk test window. Create a fresh venv on your Mac instead of copying
one from Windows. These commands select the interpreter without activation.

## 3. Start the music application

From inside `MCPJAM`, move to its parent and run the package:

```bash
cd ..
./MCPJAM/.venv/bin/python -m MCPJAM
```

Keep the Terminal window and DAW open. Run the package this way because the
application uses relative imports. `__main__.py` supplies the entry point.
Every playback path uses the bundled GeneralUser GS SoundFont through FluidSynth.
For optional audio, run `brew install fluid-synth` and install
`requirements-audio.txt`. Core-only participants verify state visually.
There is no built-in synthesized fallback:
if audio initialization fails, the app reports an audio error and cannot play.
For automated Homebrew setup, run `bash setup.sh --core-only` inside MCPJAM, then
`bash run_app.sh`. Windows has been tested; Mac runtime still needs verification.

## 4. Connect a host using your Mac's paths

Follow [the live lab](../workshop/README.md) for the JSON walkthrough and existing MCP demo.

In a second Terminal window, inside the `MCPJAM` folder:

```bash
./.venv/bin/python workshop_preflight.py --vscode-config
```

Copy the printed interpreter and script paths into your host's configuration.
This prints JSON only and does not edit your host. It uses the VS Code
`servers` structure; `--host-config` prints an `mcpServers` example for other hosts. Keep spaces
inside one JSON string and use absolute paths rather than `~`.
Restart/reconnect the host connection after configuration or code edits. The
host launches the stdio server; you do not launch a second server manually.

## 5. Make explicit calls

With the DAW running, from inside `MCPJAM`:

```bash
./.venv/bin/python workshop_client.py
./.venv/bin/python workshop_client.py --tool set_tempo --arguments '{"bpm":120}'
./.venv/bin/python workshop_client.py --tool get_state
```

After implementing `set_swing` in `workshop/starter/mcp_server_sdk.py`:

```bash
./.venv/bin/python workshop_client.py --tool set_swing --arguments '{"amount":35}'
./.venv/bin/python workshop_client.py --tool get_state
./.venv/bin/python workshop_client.py --tool set_swing --arguments '{"amount":100}'
```

The invalid call should print `isError: true` and exit with code 1. Writes are
queued; allow the UI to process them before checking state. The starter has
two tools; swing and mute are student additions. To run the completed solution,
add `--server workshop/solutions/mcp_server_solution.py` to the client command.

## Mac troubleshooting

| Symptom | Action |
| --- | --- |
| `python3.13` not found | Install the documented Python and reopen Terminal. |
| `_tkinter` missing or no Tk window | Use Python with native Tk, then recreate the venv with that interpreter. |
| pip certificate error | Run the matching `Install Certificates.command`; keep certificate verification enabled. |
| pygame attempts a source build | Check Python version/architecture; the documented 3.13 route has Mac wheels. |
| `No module named MCPJAM` | Run from the parent of the folder named exactly `MCPJAM`. |
| Port 8765 already in use | Close the extra DAW instance; keep one backend running. |
| Tools missing | Check the absolute paths, SDK version, and restart the connection. |
| Connection refused | Start the DAW; discovery alone does not connect to the backend. |
| No MIDI output or no sound | MIDI is optional; verify state visually. Check Mac volume/output device if audio is needed. |

## Validation scope

The protocol code is shared across platforms. Windows protocol and slide checks
do not replace a native Mac rehearsal. Before class, run this guide on a Mac
used by participants, demonstrate 120 BPM, and verify valid and invalid swing
calls. Preflight checks imports and SDK version, not GUI/audio or host behavior.


## Chat-only music and live Mac verification

With Homebrew installed, from the cloned MCPJAM folder:

```bash
bash setup.sh
bash verify_mac.sh
bash run_music_chat.sh
```

Close any running MCPJAM instance before verify_mac.sh. The check starts its own
background CoreAudio player and tests GeneralUser GS, exact duration, held notes,
pause/resume, edits, invalid-input rejection, and WAV export without an API key.
Music chat starts a background player automatically. Type pause, play, stop, or
exit; no visual window is required. Generation requires your Gemini API key.

The Mac scripts and library discovery have been reviewed on Windows. A passing
verify_mac.sh run on the target Mac is still required to confirm actual audio
hardware and runtime compatibility.
