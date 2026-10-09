# Description-driven music through MCP

The optional full music server now has **two composition paths**:

- `create_song_from_score`: the AI authors pitches, rhythm, chords, orchestration,
  dynamics and sections as structured note data. No fixed melody or chord progression
  is inserted. A genre is a description, not a pop/rnb/edm enum.
- The older `create_pop_song`, funk, bossa, EDM and orchestral tools use coded
  arrangement patterns. They remain available to explicit clients for fast, repeatable demonstrations.
  Music chat excludes these preset creation tools; its compositions use the free
  score interface and caller-selected sounds, with no default instrument palette.

The beginner workshop still uses workshop/starter/mcp_server_sdk.py. Keep this
richer music demonstration outside the protected student exercise.

## Start on Windows or Mac

Run full audio setup (omit the classroom core-only flag):

```powershell
# Windows, inside MCPJAM
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\run_music_chat.ps1
```

```bash
# Mac with Homebrew, inside MCPJAM
bash setup.sh
bash run_music_chat.sh
```

Enter your own Gemini API key at the hidden prompt. It is not saved to the repo.
Generation returns a playable 192-kbps stereo MP3 location and never autoplays.
No running app or background player is needed. Windows rendering has been exercised;
Mac needs a native rehearsal. Model access/quotas depend on your API account.
Use GEMINI_MODEL or gemini_host.py --model to choose an available model.

For an external AI host, configure `.vscode/mcp.json` with this clone's .venv
Python and change `args` to `${workspaceFolder}/mcp_server_music.py`. Reconnect the server and enable its tools. Launch the app separately only
when you explicitly want live playback controls. The full
music server exposes the composition tools; the beginner server does not.

All classroom prompts and default generated clips are **30 seconds**. The host
only changes length when explicitly asked. The score interface retains bounded
length support for future uses, but students do not need longer clips.

## Prompts to try

- “Compose an original 30-second contemporary R&B instrumental at 104 BPM.
  Use electric piano ninth chords, a syncopated bass conversation, light 808-kit
  percussion and a saxophone answer. Build a contrasting middle and gentle ending.
  Use create_song_from_score and compose the notes yourself.”
- “Compose a jazz waltz in 3/4: walking acoustic bass, brushed drums, piano
  voicings and a muted-trumpet phrase. Let the melody breathe and vary each repeat.”
- “Create a 30-second cinematic piece in 6/8, with a restrained cello opening,
  layered violins and French horn, then a crescendo and quiet resolution.”
- “Write an original fast drum-and-bass instrumental: break-like syncopation,
  moving synth bass, sparse pads and a new lead motif. Avoid a four-on-the-floor groove.”
- “Compose a bossa nova with nylon guitar offbeats, flute phrases, soft bass
  and brush percussion. Give the second section different chord voicings.”
- “Make the lead staccato, then rewrite its second phrase; lower bass volume,
  replace the lead with a different bank variant, and return the updated MP3 location.”

The host should search instruments, compose a score, call the tool and verify
the returned MP3 file. Open it yourself when ready, then ask for specific changes. Quality
is determined by the AI's score and the sampled sound library, not the genre label.
This is MIDI/sample composition: no vocals, neural audio generation or recording
transcription. It cannot guarantee a convincing rendition of every genre.

## Every bundled SoundFont preset is exposed

`music://instruments/catalog` contains all **287 actual presets**: 274 melodic
sounds and 13 drum kits, with exact bank/program numbers and canonical ids such
as gs_8_4. The manifest is enumerated from the bundled GeneralUser GS SoundFont
and records its SHA-256. Existing aliases (piano, violin, etc.) continue working.
`get_instrument_catalog` searches by name/id, filters melodic/drum_kit and pages
results; publishing a resource alone does not ensure an AI reads it.

`set_song_track` supports compatible melodic sounds or drum kits. In modern808
preset songs, selecting a GS bass/drum sound disables that corresponding sample
override so the selected timbre actually sounds. Individual WAV hits in the
modern808 pack remain the sample-layer sounds, not additional GS presets.
Bank and program selections carry through live playback and the rendered MP3 (MIDI/WAV are backend files).

## Score contract

- 1–16 tracks with unique zero-based MIDI channels; channel 9 is percussion.
- Each track has a name, channel, instrument id/alias, volume 0–100 and mute state.
- Each note has a track, MIDI pitch 0–127, onset/duration in quarter-note beats,
  velocity 1–127, and optional repeats/every_beats to compact a motif.
- 40–240 BPM; 5–180 seconds; time signatures 1–12 over 2, 4, 8 or 16.
- Up to 5,000 expanded notes. Use different durations for articulation, velocities
  for dynamics and chord overlaps for polyphony. Conflicting same-pitch overlaps
  on one track are rejected; join them into a longer held note instead.
- `replace_song_notes` rewrites melody/rhythm/chords without changing tracks.
  `set_song_track` changes sound/mute/volume. `edit_song` changes an AI score's
  title, tempo or duration; preset-style controls are rejected for AI scores.

The server validates the score before saving, renders it and encodes the MP3
before returning success. Creation, edits and export never start playback. Prompts,
resources, tools, validation, the adapter and observed state each have a role.

## Repeatable original demo without a model key

After audio setup, run the client in a terminal; no app needs to be running:

```powershell
.\.venv\Scripts\python.exe workshop_client.py --server mcp_server_music.py --tool create_song_from_score --arguments-file workshop/examples/original-rnb-score.json
```

```bash
./.venv/bin/python workshop_client.py --server mcp_server_music.py --tool create_song_from_score --arguments-file workshop/examples/original-rnb-score.json
```

The JSON is an original example score, not a transcription of a released song.
It demonstrates the same score interface an AI host uses. Its music data is
supplied by the caller, rather than baked into the generation backend.

Run `verify_score.py` with your .venv Python and the app closed for the complete
preset-selection, rendering, real MCP composition/edit/export and invalid-score
checks. `verify_music.py` exercises the older music paths. Explicit tests do not
call Gemini. Natural-language Gemini integration still needs a valid key and
has not been exercised in the current keyless verification session.
