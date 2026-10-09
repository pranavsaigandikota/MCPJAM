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
Slide 19 compares direct CLI/API adapters with the shared MCP contract: a database,
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
