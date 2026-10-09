# Intro to MCP Servers with MCPJAM

Use the [current Figma deck](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ/MCP-Servers-Slides)
and [matching instructor guide](workshop_delivery/Instructor-Guide.md).

Students generate a song at default 120 BPM, observe the missing set_tempo capability, then add it and verify the same 150 BPM request succeeds.
Plan 55 minutes and reserve minutes 55–60 for delays or Q&A.
Start installation at minute 1: 0–8 setup, 8–18 theory and MCP choices,
18–25 demo and activity map, 25–40 hands-on build/test, 40–47 security,
47–52 advanced awareness, enterprise and production practices, 52–55 hackathon transfer and exit check.
The 15-minute activity includes a three-minute guided build and twelve minutes
of audience testing/adaptation. Pair blocked learners before the activity.
Fresh Python/Homebrew installs may exceed the setup window; advance preparation helps.

Activity navigation: slide 14 traces MCP versus the backend; slide 16 explains
the client’s discovery metadata and returned tool result, with separate host/client/server roles; slide 20 shows the edit in workshop/starter/mcp_server_sdk.py; slide 21 shows the Copilot JSON; slides 22–23
show discovery, explicit tests, and get_state verification. Slide 15 maps these steps.
Slides 17–18 pair the read/act/observe concept with the maze example; keep each brief.
FAQ slides 5, 19 and 29 cover prompts, standard MCP versus custom tools,
AI testing without MCP, and a concrete hackathon use. Slide 19 compares direct CLI/API adapters with the shared MCP contract: a database,
filesystem and Jira still need adapters, while MCP standardizes discovery and calls.
Figma/GitHub share the protocol but differ in capabilities and may use different transports.
JSON-RPC is the message format; stdio and Streamable HTTP are standard transports.
Slide 11 compares SDKs,
standalone FastMCP, Zapier MCP and the adjacent Databutton app-builder category.

[README.md](README.md) is the maintained setup, VS Code Copilot connection, and exercise reference.
Full GeneralUser GS/FluidSynth setup is required for the lab MP3. The separate
mcp_server_music.py is an optional instructor showcase; the supplied song generator works at 120 BPM; students add set_tempo.
Slide 27 shows the separate music server and compose_music prompt, producing a 30-second MP3 without autoplay. Copilot supplies web access when available. Use .vscode/mcp.music.example.json for this connection; keep the starter connection for the lab.

Follow the [live FastMCP/configuration walkthrough](workshop/README.md) for starter/solution folders, VS Code JSON and the existing-server demo.

The live Figma deck is maintained; PowerPoint/PDF exports are archived snapshots. Slide 16 shows abbreviated discovery/result payloads and distinguishes the host from the client. No Gemini API key is required for the workshop route.

## MCP server walkthrough: transfer the pattern to your own project

Use the existing slides; this adds explanation within the guided three minutes,
not another activity. Begin with slides 4, 6 and 9–10 for the standard, roles,
primitives and discovery. Then walk through these project-building slides:

| Slide | Title | What students should carry into their own app |
|---|---|---|
| 14 | MCP ACTIVITY · trace the call | Keep host/client, MCP server and app backend separate. |
| 16 | What the MCP client sees | The client discovers schemas, calls tools and receives data/errors. |
| 20 | MCP BUILD · add set_tempo | Register, type, describe, validate, delegate and return. |
| 21 | Copilot connection: .vscode/mcp.json | Point a host at the server using the correct interpreter/transport. |
| 22 | MCP TEST · discover, call, verify | Save/restart, discover, retry and observe real results. |
| 23 | MCP TEST · evidence of success | Check valid inputs, boundaries, errors and unchanged state. |
| 24–26 | Security risks and controls | Authorize actions, scope access and distrust external content. |
| 28 | Enterprise: identity + production rules | Add identity, auditability and reliable operations for production. |
| 29 | Where can I use this at the hackathon? | Choose a useful action in your own project and wrap existing logic. |

Explain on slide 20: replace set_tempo with a narrow project action such as
search_inventory or create_draft_ticket, bpm with its typed inputs, and call_daw
with an existing function/API adapter. Keep the MCP registration and result
contract, use that app's validation and permissions, and supply a read/state tool
to verify the effect. Never treat the decorator alone as a security policy.

The current workshop has a default-tempo song before the edit, a missing-tool
error before registration, and a successful 150 BPM result afterwards. Students
add the capability in workshop/starter; workshop/solutions is the commented answer.
