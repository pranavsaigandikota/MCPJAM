# Intro to MCP Servers with MCPJAM

**Understand MCP, trace a tool call, and implement and test a tool in a starter MCP server.**

MCPJAM is a small Python music application used as the backend for a beginner
workshop. Students extend the supplied Python SDK server with one swing tool.
Basic Python functions and dictionaries are assumed.

- [Current 27-slide Figma presentation](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ)
- [Slide-by-slide instructor guide](workshop_delivery/Instructor-Guide.md)
- [Student quick start](workshop_delivery/Student-Quick-Start.md)
- [Gemini API keys](https://aistudio.google.com/api-keys)

The Figma deck is the current workshop. Older PPTX/PDF files in workshop_delivery
are historical exports and do not reflect this 27-slide revision.

## Copy-and-paste setup and playback

After cloning, run these commands inside **MCPJAM**. The setup scripts create
the local environment and install the dependencies listed in requirements-audio.txt.
GeneralUser GS is bundled with its license; FluidSynth supplies its playback engine.

Windows 64-bit / PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\run_music_chat.ps1
```

The Windows helper uses an existing Python 3.10–3.13 with Tk or installs Python
3.13 through winget if necessary. If winget is absent, install 64-bit Python
3.13 from python.org first.

macOS / Terminal (requires [Homebrew](https://brew.sh)):

```bash
bash setup.sh
bash run_app.sh
```

The Mac helper installs Python 3.13, Tk, FluidSynth, and Python dependencies.
This repository supports the same application and MCP tools on both platforms;
Windows has been exercised locally, while macOS execution remains unverified.

Music chat automatically starts a **background audio player with no window**.
Enter a Gemini key at the hidden prompt, then ask:

> Make a 30-second original R&B instrumental in C at 98 BPM with legato phrases,
> held notes, and acoustic GeneralUser GS instruments.

Type **pause**, **play** (resume), **stop**, or **exit**. These exact transport
commands run locally without a Gemini API request. Natural-language requests
create/edit songs through Gemini and MCP. Pause preserves the position and
resumes held notes. Exact durations of 5–180 seconds are supported. Articulation
can be legato, normal, or staccato; styles are pop or rnb.

For the workshop's visual sequencer, run `run_app.ps1` on Windows (or
`run_app.sh` on Mac) separately. Close it before starting background music chat.
The player and sequencer share the local backend port; run one at a time.

**Acoustic playback uses GeneralUser GS; modern808 mode uses WAV samples for bass/drums and GS for piano/strings.** There is no built-in DSP
or default-MIDI fallback. If the soundfont or native engine cannot load, the
app shows an audio error and disables sound. The default pop preset selects
piano, acoustic guitar, finger bass, strings, and sampled drums; its former
synth lead/bass/pad patches have been replaced. Other explicitly selected
General MIDI patches still come from the same GeneralUser bank.

Live playback and WAV export share a damped room reverb. Piano has a stronger
reverb send; bass and drums stay drier. Chorus is disabled to avoid a modulated,
metallic texture. The default piano accompaniment is more prominent.

To start music chat directly:

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File .\run_music_chat.ps1
```

```bash
# macOS
bash run_music_chat.sh
```

Enter your own Gemini API key at the hidden prompt. Keys are not bundled or
committed. The explicit workshop client needs no key.

## Files and responsibilities

| File | Purpose |
|---|---|
| README.md | Setup, launch commands, and exercises |
| app.py | Music application, UI, audio, and local backend socket |
| mcp_server_sdk.py | Starter MCP server with get_state, set_tempo, and call_daw |
| workshop_client.py | Discover tools and test explicit arguments without a model |
| mcp_server_solution.py | Completed reference implementation |
| gemini_host.py | Optional Gemini AI host with an MCP client |
| verify_workshop.py | MCP integration checks with a controlled mock backend |
| verify_live.py | MCP checks against the running music application |

The architecture has these connections:

1. Host/client ↔ mcp_server_sdk.py: **MCP over stdio**.
2. Tool function → call_daw(): **Python function call**.
3. call_daw() ↔ app.py: **newline-delimited JSON over 127.0.0.1:8765**.

The local socket is a demo backend, not an MCP endpoint. Keep it on loopback.
The SDK handles protocol messages and dispatches tool calls. You implement
useful behavior, validation, backend integration, and any required authorization.

## Setup

Keep the package folder named MCPJAM. Python 3.10+ with Tk is required.
Create a separate virtual environment on each computer. No MIDI hardware,
external soundfont, or Gemini key is needed for explicit tool tests.

```bash
git clone https://github.com/pranavsaigandikota/MCPJAM.git
cd MCPJAM
```

### Windows / PowerShell

Run inside MCPJAM:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

Launch the music application from the package's parent directory:

```powershell
cd ..
.\MCPJAM\.venv\Scripts\python.exe -m MCPJAM
```

Keep it running. Open a second PowerShell terminal inside MCPJAM for the client.
You can also launch from inside the repository with `powershell -ExecutionPolicy Bypass -File .\run_app.ps1`.

### macOS / Terminal

Use Python with Tk, such as the standard Python 3.13 installer from python.org.
See [Mac setup](MAC_SETUP.md).

```bash
python3.13 -m venv .venv
brew install fluid-synth
./.venv/bin/python -m pip install -r requirements-audio.txt
./.venv/bin/python workshop_preflight.py
./.venv/bin/python -m tkinter
# Close the Tk test window.
cd ..
./MCPJAM/.venv/bin/python -m MCPJAM
```

Open a second terminal inside MCPJAM for the client. Do not run app.py directly:
it uses package-relative imports. Activation is optional because the commands
select the environment's interpreter explicitly.

## Rehearse the explicit client first

The client starts a fresh stdio server on every invocation, so saved edits
are loaded automatically. An existing AI host connection must be restarted
or reconnected after a server edit.

Windows, inside MCPJAM:

```powershell
.\.venv\Scripts\python.exe workshop_client.py
Set-Content -LiteralPath tempo-input.json -Value '{"bpm":120}' -Encoding UTF8
.\.venv\Scripts\python.exe workshop_client.py --tool set_tempo --arguments-file tempo-input.json
.\.venv\Scripts\python.exe workshop_client.py --tool get_state
```

macOS:

```bash
./.venv/bin/python workshop_client.py
./.venv/bin/python workshop_client.py --tool set_tempo --arguments '{"bpm":120}'
./.venv/bin/python workshop_client.py --tool get_state
```

Expect discovery of get_state and set_tempo. Start the demo at a tempo other
than 120. A successful write says **queued**: read get_state to verify bpm=120.
If it still shows the previous value, read again after the UI processes the queue.

## Gemini AI demo

The supplied gemini_host.py discovers the MCP tools, sends their definitions
to Gemini, prints the model's selected tool and arguments, executes through
the MCP client, and reads application state to verify the effect.

Create a key at https://aistudio.google.com/api-keys. The key is needed only for
this AI host demo. Use hidden input so it is not stored in shell history:

```powershell
# Windows, inside MCPJAM; keep the music application running.
.\.venv\Scripts\python.exe gemini_host.py --ask-key "Set the tempo to 120 BPM."
```

```bash
# macOS
./.venv/bin/python gemini_host.py --ask-key "Set the tempo to 120 BPM."
```

Alternatively, supply GEMINI_API_KEY through your environment. The host does
not save the key or forward it to the MCP server. It sends tool definitions,
your request, and tool results to Google's Gemini API.

The tested default model is gemini-3.8-flash. Override it with --model or
GEMINI_MODEL if account availability changes. Free-tier quotas and availability
depend on the account/model; see [Google's pricing](https://ai.google.dev/gemini-api/docs/pricing).
Do not enable billing merely to complete this workshop. On quota, network, or
model errors, use the explicit client commands above.

The model proposes a call; the host coordinates it. Keep this demo to about
three minutes and save set_swing for student work.

Other MCP hosts can use the configuration printed by:

```powershell
.\.venv\Scripts\python.exe workshop_preflight.py --host-config
```

On macOS, use ./.venv/bin/python instead. The printed mcpServers JSON is a
host-specific example, not an MCP standard. Use the actual absolute paths.

## Student exercise: add a swing tool

Edit mcp_server_sdk.py. Use the existing set_tempo function as the example:

- Define set_swing(amount: int) and register it with @mcp.tool().
- Give the tool a clear description.
- Accept integers from 0 to 75 and reject out-of-range values.
- Call the existing adapter with command set_swing and field amount.
- Return a useful result; distinguish queued from completed.
- Put the tool definition before the server startup block.

Save, restart/reconnect the client, and confirm set_swing appears in discovery.
Then test explicit values and read get_state:

| Test | Expected evidence |
|---|---|
| Discovery | set_swing appears in available tools |
| 35 | Accepted; get_state reports swing=35 |
| 0 and 75 | Both boundary values accepted and observed |
| 100 | Tool error; application state unchanged |

Windows test, after implementing the tool:

```powershell
.\.venv\Scripts\python.exe workshop_client.py
Set-Content -LiteralPath swing-input.json -Value '{"amount":35}' -Encoding UTF8
.\.venv\Scripts\python.exe workshop_client.py --tool set_swing --arguments-file swing-input.json
.\.venv\Scripts\python.exe workshop_client.py --tool get_state
# Repeat with amount 0, 75, and 100. For 100, expect exit code 1.
```

macOS:

```bash
./.venv/bin/python workshop_client.py --tool set_swing --arguments '{"amount":35}'
./.venv/bin/python workshop_client.py --tool get_state
```

A model may refuse or modify an invalid natural-language request, so use
explicit client arguments to test validation. Success means showing one valid
call, one rejected call, and explaining registration, validation, and the backend.

After attempting the exercise, compare with mcp_server_solution.py.
To rehearse the reference version, add --server mcp_server_solution.py to a
client command. Do not overwrite the starter with the solution for students.

Early finishers may try a natural-language request or optionally implement
mute_track(track: str, muted: bool). A second tool is not required.

## Exact 60-minute plan

| Time | Activity |
|---|---|
| Before the clock | Check-in and installation readiness |
| 0–15 | Introduction, MCP theory, APIs, real-world examples, discovery, SDK |
| 15–25 | Links, demo, architecture, code walkthrough, exercise briefing |
| 25–30 | Flexible setup/help buffer; ready students begin early |
| 30–50 | Protected student implementation and testing |
| 50–55 | Security risks and defenses |
| 55–58 | Advanced capabilities, multiple servers, enterprise overview |
| 58–60 | Apply the pattern elsewhere, check understanding, close |

35 minutes guided teaching/demo + 20 minutes practical work + 5 minutes buffer.
There is no appendix in the current deck.

## Instructor verification

With the music app **closed**, run the controlled-backend tests (they use port 8765):

```powershell
.\.venv\Scripts\python.exe verify_workshop.py
```

With the music app **running**, run the real application checks:

```powershell
.\.venv\Scripts\python.exe verify_live.py
```

Use ./.venv/bin/python on macOS. The live check temporarily changes tempo,
swing, and kick mute, tests invalid inputs, and restores those settings.
It checks both the starter and completed reference. Run it before students
add set_swing to the starter, because it checks the starter's two-tool inventory.
Audio-enabled status confirms device initialization; listen during rehearsal
to confirm the selected output is audible.

The workshop pins MCP SDK 1.19.0 and constrains its Pydantic dependencies to
the tested compatible range. The older mcp_server.py is an optional manual
protocol sketch, not the workshop server.

## Security and scope

Range validation checks a value; authorization checks who may perform an
action. This trusted-local-machine demo does not implement production user
authentication. A production integration must check access, limit permissions,
treat documents/tool results as untrusted, and review server code and updates.
The host coordinates workflows across servers; servers do not automatically
cooperate just because they use MCP.

## Sampled instruments and song-making chat (optional demo)

GeneralUser GS v2.0.3 is bundled under soundfonts/GeneralUser-GS, together with
its original license. It contains sampled General MIDI instruments and drums.
The app loads it through FluidSynth instead of relying on the mathematical
synth or a computer's default MIDI output.

Windows, inside MCPJAM:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-audio.txt
.\.venv\Scripts\python.exe setup_audio.py
```

The installer downloads the pinned official FluidSynth 2.6.1 Windows x64
runtime into .audio_runtime and verifies its SHA-256 checksum. The native
runtime stays local and is excluded from Git. Restart the music app after setup.
On macOS, install FluidSynth with brew install fluid-synth, then install
requirements-audio.txt using the workshop environment. Linux users need their
system FluidSynth library and an available audio driver.

For the richer demonstration, use the separate mcp_server_music.py server:

```powershell
.\.venv\Scripts\python.exe gemini_host.py --server mcp_server_music.py --ask-key --chat
```

Keep the music application running in its own window. For the same chat command,
you can run `powershell -ExecutionPolicy Bypass -File .\run_music_chat.ps1`.

Example conversation:

- Create a 32-bar pop instrumental in D at 116 BPM with piano, acoustic guitar,
  finger bass, strings, and drums.
- Make it 124 BPM, change the lead instrument to flute, and lower its volume to 65.
- Mute the drums, then play it again.
- Export the song as MIDI and WAV.

The host retains conversation context. The server saves editable projects in
 generated_music, rebuilds the MIDI after edits, and plays it in the running app.
WAV export uses the same GeneralUser GS soundfont in an isolated renderer.
get_state reports audio_engine, soundfont_path, the current song ID/revision,
track settings, and playback state. The music tools require
 audio_engine=generaluser_gs and report an error if sampled playback is unavailable.
Song edits restart playback from the beginning.

These are original instrumental arrangements with an intro, verse, chorus,
bridge, and outro. They do not generate sung vocals or reproduce commercial
recordings. This optional music server does not change the workshop starter:
students still implement only set_swing in mcp_server_sdk.py.

Any compatible local MCP host can launch mcp_server_music.py with the same
virtual-environment Python. Use that server path for a music demo, or
mcp_server_sdk.py for the student workshop. Gemini is the included host;
configuration for another chat application's local MCP support depends on that host.


## Cinematic EDM through MCP

`create_edm_song` creates original minor-key dance arrangements with four-on-the-floor
kicks, syncopated bass, layered tom percussion, snare builds, drops, a breakdown,
and a final drop. Sounds remain entirely GeneralUser GS, including electronic
patches from that bank. Reverb applies to both live audio and exports.

Example chat request: "Make a 30-second dark cinematic EDM beat in D at 132 BPM,
energy 92, variation 17. Export the WAV." Follow up with "lower energy to 70" or
"change variation to 35"; `edit_song` exposes both controls. Energy controls drum
density; variation changes deterministic melodic accents. This is a MIDI arranger,
not a model that copies recordings or produces vocals.

`verify_music.py` includes EDM structure and invalid-energy rejection checks.


## Modern sample-based 808 mode

Ask music chat: "Use create_808_song to make a serious 30-second dark beat at
128 BPM." This replaces GS bass/drums with the bundled hard-trap WAV sample kit,
removes the bright lead, and uses restrained GS piano/strings over a minor drone.
There is no oscillator fallback. The background player uses the rendered mix for
playback, so its sound matches the WAV export; pause, resume and live edits work.
The MIDI export contains note data and does not embed the sample pack.

Source: https://github.com/Boochi44/free-drum-samples (CC0 as declared by its author).
Original licensing statement and per-file source URLs/checksums are bundled in
samples/modern808. Importing a different private pack is not yet exposed as an MCP tool.


## Deliberately composed demo

Ask music chat to call `create_composed_song`, title Nightfall, BPM 128, key D.
This is an original written 16-bar score (30 seconds at 128 BPM), using connected
piano voicings, a recurring question/answer melody, rests, held strings, modern
808 samples and a resolving ending. It does not randomly jump octaves or add
constant tom fills. This is one authored score, not a general-purpose AI composer.
Tempo and track/instrument edits are supported; its structure is designed for 16 bars.
