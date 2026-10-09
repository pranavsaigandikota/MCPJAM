# Intro to MCP Servers: instructor guide

Present [MCPJAM-Workshop-Copilot.pptx](MCPJAM-Workshop-Copilot.pptx) or its PDF.
The live Figma deck includes these Copilot updates and the client response example on slide 16.
The 29-slide deck teaches standard MCP using custom music tools; students extend
an existing server rather than build the music app from scratch.

## Run of show: 55 minutes plus 5 spare

| Time | Activity |
|---|---|
| 0–8 | Start installation at minute 1, readiness vote and goal |
| 8–18 | Foundations, one-shot prompts/APIs, hackathon servers, MCP options |
| 18–25 | Tempo demo, MCP/backend boundary, contract and activity map |
| 25–40 | Hands-on: 3-minute guided build + 12-minute audience testing/adaptation |
| 40–47 | Injection scenario, poisoning/rug pulls, security controls |
| 47–52 | 1 minute advanced awareness + 4 minutes enterprise/production methods |
| 52–55 | Hackathon action/state/permission pair exercise and exit check |
| 55–60 | True spare time for delays or Q&A |

Start installers while students check in. Fresh Python/Homebrew installs can run
long; ask students to prepare in advance and pair blocked learners before minute 25.
Use core-only setup for the lab. VS Code Copilot is the AI host; sampled audio
is instructor preparation; explicit tool tests need no API key and visual state can be verified
without audio. The check-in QR is an event QR; README/GitHub is the setup reference.

Keep the existing visual diagrams and two-column comparisons. Pair the read/act/observe concept on slide 17 with the maze illustration on slide 18.
Keep them to 20 and 30 seconds; the standalone transition was removed.
Use the concise recipe on slide 20: imports, server and transport already exist;
students add one tool and explain registration, validation, adapter and verification.
Slide 27 uses one minute for the prepared Copilot music prompt and MP3 result.
Long generation requests, a second student tool, detailed JSON-RPC plumbing and
installing multiple third-party servers are outside the clock. Security and enterprise stay live.

## Live files to show

Show workshop/starter/mcp_server_sdk.py, then .vscode/mcp.json and host discovery.
Use [the configuration walkthrough](../workshop/README.md) for the prepared
existing-server demonstration. These replace the longer code walkthrough; keep
the 15-minute lab. Slides show the server basename; navigate into the starter
folder. Root server files are compatibility launchers; students edit the starter.
Reference answers are in workshop/solutions.

## Activity navigation

| Slides | Students should understand/do |
|---|---|
| 14 | MCP over stdio reaches the server; local JSON socket reaches the backend |
| 15 | Map the files and next steps |
| 16 | Tool registration, input type and description |
| 20 | MCP BUILD: edit workshop/starter/mcp_server_sdk.py above startup |
| 21 | MCP CONNECT: .vscode/mcp.json, venv interpreter and server startup |
| 22–23 | MCP TEST: discover, call explicit inputs, verify via get_state |

Use README for exact Windows/Mac commands. Restart persistent hosts after edits;
workshop_client.py starts a fresh server per run. Test 35, 0, 75 and invalid 100.
Rejected input must leave state unchanged. Queued acknowledgement alone is insufficient.
AI-generated code is allowed; each learner should explain what it exposes and checks.

Interactive moments are inside each segment: readiness vote; classify tool/resource/
prompt; choose a custom SDK versus managed actions; predict set_swing(100); discuss
malicious tool-result instructions; discuss retrying a timed-out write; give a partner
one hackathon tool with input, permission and evidence of success.

## FAQ teaching points

A prompt supplies instructions. A host needs actual connected capabilities to act.
MCP supplies shared discovery and invocation for compatible hosts; prompts and MCP
work together. A coding agent may already have shell/browser/API tools and can test
an app without that app exposing MCP. Expose a thin MCP adapter when reusable live
capabilities across compatible hosts are valuable. A fixed single-client integration
can use a direct API. MCPJAM uses ordinary MCP with domain-specific tools.

Official SDK v1 FastMCP uses mcp.server.fastmcp; standalone FastMCP is a separate
package with from fastmcp import FastMCP. Zapier MCP provides managed app actions;
classic Zaps start with a trigger then actions. Databutton's app-builder documentation
is an adjacent category, not evidence of an interchangeable MCP SDK.


## Slide content and presenter notes

### Slide 1: Intro to MCP Servers

- Intro to MCP Servers

- Presented by Pranav

- X


Presenter notes:

55 minutes planned + 5 minutes spare. 00–08 install/check-in. 08–18 foundations, prompts/APIs and MCP options. 18–25 tempo demo, architecture, contract and paired feedback-loop/maze illustration. 25–40 protected build/test: 3 minutes guided + 12 audience testing/adaptation. 40–47 security. 47–52 advanced awareness, enterprise and production practices. 52–55 hackathon transfer and exit check. 55–60 spare. Start setup at minute 1 and pair blocked learners. Transition and duplicate exercise slide were cut. A one-minute music prompt showcase is included on slide 27; fuller music exploration stays outside the hour.



### Slide 2: Install now

- Install now

- SETUP · README.md

- Windows

- setup.ps1 -CoreOnly

- Mac

- bash setup.sh --core-only

- Pair if blocked

- QR: event check-in


Presenter notes:

00–08 min: installation starts now. Windows: powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -CoreOnly. Mac: bash setup.sh --core-only, with Homebrew available. Open README for clone and manual Python/Tk instructions. Core-only supports visual verification. Copilot agent chat is the workshop route; full audio is instructor preparation. Ask who is ready, installing, or blocked. Continue setup during theory, check readiness before minute 25, and pair blocked learners. Fresh Python/Homebrew installs may run long. Reserve 55–60 for spare time.



### Slide 3: Today’s workshop

- Today’s workshop

- 8 min setup · 10 theory · 7 demo · 15 practice

- 7 security · 5 enterprise · 3 exit · 5 spare

- UNDERSTAND

- Connect an AI Application to useful software capabilities.

- TRACE

- Follow a request from the host to the music Application.

- IMPLEMENT + TEST

- Extend the supplied server with one validated tool.


Presenter notes:

55 minutes planned + 5 minutes spare. 00–08 install/check-in. 08–18 foundations, prompts/APIs and MCP options. 18–25 tempo demo, architecture, contract and paired feedback-loop/maze illustration. 25–40 protected build/test: 3 minutes guided + 12 audience testing/adaptation. 40–47 security. 47–52 advanced awareness, enterprise and production practices. 52–55 hackathon transfer and exit check. 55–60 spare. Start setup at minute 1 and pair blocked learners. Transition and duplicate exercise slide were cut. A one-minute music prompt showcase is included on slide 27; fuller music exploration stays outside the hour. Security and enterprise are required live content.



### Slide 4: What MCP is

- What MCP is

- Model Context Protocol

- An open standard that connects AI Applications to tools, data, and reusable instructions.

- An MCP server is the program that exposes those capabilities.

- Today: extend an existing server using the Python SDK.


Presenter notes:

Explain the shared interface. The workshop extends an existing server using the Python SDK; it does not build an application or server from scratch.



Meme image source: https://imgflip.com/memetemplate/609042041/Tralalero-Tralala



### Slide 5: Why MCP instead of one prompt?

- Why MCP instead of one prompt?

- Workflow step

- What MCP adds

- One-shot prompt

- Gives instructions; tools still need a connection.

- Live capabilities

- The host discovers tools and input schemas.

- Act + observe

- Call an action, read state, then adjust.

- Reusable workflow

- Compatible hosts reuse the same tool interface.

- Me when the next

- compatible AI host

- uses the same server.

- MCP does not guarantee correctness. Test tools and verify outcomes.


Presenter notes:

08–18 segment, about 60 seconds. A one-shot prompt is instructions to a model. The host may already have shell, browser or API tools; MCP is one way to connect additional discoverable capabilities. Prompt + tools can be used together. MCP enables live action/observation and reuse across compatible hosts, not guaranteed reasoning or correctness. Ask: what evidence would you need after asking an AI to change the tempo? get_state verifies it.



### Slide 6: Host, client, server: the apps you know

- Host, client, server: the apps you know

- HOST · the AI Application you use

- VS Code + GitHub Copilot

- Agent chat coordinates model, tools and permissions.

- CLIENT · the MCP connection inside it

- Built into the VS Code host

- Discovers tools, sends calls, receives results.

- ↔

- MCP

- SERVER · exposes tools

- Lab: workshop/starter/mcp_server_sdk.py

- Built with SDK FastMCP

- get_state + set_tempo; you add set_swing

- Model ≠ host: the selected model reasons; VS Code coordinates the calls.

- Backend ≠ MCP server: app.py changes the music; the server exposes its controls.


Presenter notes:

VS Code is the workshop host, GitHub Copilot supplies agent chat and a selected model, and VS Code includes the MCP client. No standalone Gemini host or Gemini key is used. Core entry points to workshop/starter/mcp_server_sdk.py; the root compatibility launcher is not the student edit. Source: https://code.visualstudio.com/docs/agent-customization/mcp-servers .



### Slide 7: Where an API fits

- Where an API fits

- AI HOST

- Contains the MCP client

- MCP SERVER

- Exposes a useful tool

- EXISTING API

- Applies Application rules

- DATA / ACTION

- Reads or changes the app

- MCP request →

- API call →

- Read / write →

- An MCP tool can call an EXISTING API, Python function, or supported Application command.

- 1 / 3 · PRIZE QUESTION  ·  Hands up!

- Who chooses which MCP tool to call?

- A  The host       B  The server       C  JSON


Presenter notes:

08–18 segment. MCP can wrap an existing API or function. It is useful for shared discovery and tool schemas across compatible hosts. A direct API is often sufficient for one fixed integration. MCP does not replace app business rules or automatically enforce permissions. Prize question: host coordinates which tool to call; model proposes the call, server exposes and executes it. Allow 15 seconds within this segment.



### Slide 8: 12 AM. Your team’s MCP power tools.

- 12 AM. Your team’s MCP power tools.

- Start with the 2–3 servers your demo needs. Access and features depend on permissions and plans.

- Connect existing servers. Spend your time on the idea.

- Figma

- DESIGN

- Bring UI designs into your coding workflow.

- GitHub

- BUILD

- Inspect code, track issues and work with PRs.

- Supabase

- DATA

- Inspect schemas, query data and manage migrations.

- Playwright

- TEST

- Drive the browser and verify the demo flow.

- Vercel

- SHIP

- Manage deployments and inspect deployment logs.

- Sentry

- DEBUG

- Investigate errors before the judges find them.

- Stripe

- PAYMENTS

- Explore APIs and build a sandbox payment demo.

- Context7 · Upstash

- DOCS

- Pull current library docs and code examples.

- Design → build → connect data → test → deploy → fix

- Pick a compatible host → add a server → authorize → inspect tools → use it


Presenter notes:

08–18 segment, quick scan, 45 seconds. Choose only 2–3 useful servers. Design → build → data → test → ship → debug. Ask which capability would help this team most. Permissions, compatible host support and plans vary. Prefer read-only access where practical. Do not spend workshop time setting up every service. Sources: https://developers.figma.com/docs/figma-mcp-server/ ; https://github.com/github/github-mcp-server ; https://supabase.com/docs/guides/ai-tools/mcp ; https://playwright.dev/docs/getting-started-mcp ; https://vercel.com/docs/agent-resources/vercel-mcp ; https://mcp.sentry.dev/ ; https://docs.stripe.com/mcp ; https://github.com/upstash/context7 .



### Slide 9: Tools, resources, and prompts

- Tools, resources, and prompts

- TOOLS

- Callable operations

- Example: set_tempo or get_state

- RESOURCES

- Read-only context and data

- Our app: GeneralUser GS instrument catalog

- PROMPTS

- Reusable task instructions

- Music demo: compose_music(description)


Presenter notes:

Tools perform actions or return computed results. Resources supply context. MCP prompts supply user-selected reusable messages, not automatic execution. The optional music server registers compose_music(description, reference_song, rights_context); the beginner starter does not expose it.



### Slide 10: Discover → select → invoke

- Discover → select → invoke

- 1 · DISCOVER

- The client lists tools with their names, descriptions, and input schemas.

- 2 · SELECT

- The model proposes a tool and arguments; the host coordinates the call.

- 3 · INVOKE

- The client calls the tool. The server validates, executes, and returns a result.

- set_tempo accepts bpm, an integer.

- Python validation enforces the allowed range.


Presenter notes:

08–18 segment. Client lists tool schemas. Model proposes a tool and arguments; host checks policy and coordinates invocation. Server validates and executes, then returns results. Integer typing alone does not enforce 40–240; Python validation enforces the range. SDK v1 lab uses initialize, discovery and calls; protocol versions and negotiated capabilities matter.



### Slide 11: Ways to build or connect MCP

- Ways to build or connect MCP

- Option

- When to choose it

- SDK FASTMCP

- Official Python SDK v1; used in this workshop.

- Standalone FastMCP

- Separate Python package: from fastmcp import FastMCP.

- Other SDKs

- Official SDKs for your stack, including TypeScript.

- Zapier MCP

- Managed app actions via Zapier MCP; a Zap is trigger → actions.

- DATABUTTON · adjacent app builder

- An app builder is not itself an MCP framework.

- Choose by tools exposed, host support, auth and deployment.


Presenter notes:

08–18 min overview, about 60 seconds here. Workshop: mcp.server.fastmcp.FastMCP from pinned official Python SDK v1. Standalone FastMCP uses from fastmcp import FastMCP and is a separate package. Other official SDKs include TypeScript. Zapier MCP offers managed app actions; classic Zaps run a trigger followed by actions. Databutton documentation describes an AI app builder, not a verified interchangeable MCP framework. Ask: would your team build custom tools or connect managed actions? Sources: https://github.com/modelcontextprotocol/python-sdk ; https://gofastmcp.com/getting-started/welcome ; https://help.zapier.com/hc/en-us/articles/48308034391821-What-is-Zapier-MCP ; https://help.zapier.com/hc/en-us/articles/8496309697421-What-is-a-Zap ; https://docs.databutton.com/help-and-faq .



### Slide 12: VS Code Copilot: setup and readiness

- VS Code Copilot: setup and readiness

- github.com/pranavsaigandikota/MCPJAM

- Windows + Mac · Copilot account with agent access

- 1  Clone the repo; run the Windows or Mac setup.

- 2  Open the whole MCPJAM folder in VS Code.

- 3  Sign into Copilot; start the app for the lab.

- 4  Open .vscode/mcp.json; select your .venv Python.

- Copilot uses your account. Explicit CLI tests are the fallback.


Presenter notes:

00–08 setup, continue installs during theory. Windows: setup.ps1 -CoreOnly; Mac: bash setup.sh --core-only (Homebrew required). Open the whole repository, sign into GitHub Copilot with agent/MCP access and use the tools picker. Run run_app.ps1/run_app.sh for visual lab verification. The supplied .vscode/mcp.json prompts for an absolute interpreter path; use workshop_preflight.py --vscode-config to find it. Explicit workshop_client.py tests work if Copilot access is blocked. Full audio setup is instructor preparation for slide 27, not an added lab requirement.



### Slide 13: Copilot demo: tempo + verified state

- Copilot demo: tempo + verified state

- “Set tempo to 120, then verify it.”

- 1  Open Copilot agent chat; enable MCPJAM tools.

- 2  Inspect set_tempo(bpm=120) and its result.

- 3  Call get_state; check bpm is actually 120.


Presenter notes:

18–25 demo block. Start mcpjam from MCP: List Servers, open a tool-enabled Copilot agent chat and enable MCPJAM tools. Ask: Use set_tempo to set 120 BPM, then use get_state to verify. Inspect the actual call and bpm field; queued is not completed. This uses Copilot account access, not a Gemini API key. If account access fails, run the explicit CLI fallback. Source: https://code.visualstudio.com/docs/agents/run/tools .



### Slide 14: MCP ACTIVITY · trace the call

- MCP ACTIVITY · trace the call

- Host + MCP client

- VS Code Copilot · built-in MCP client

- starter/mcp_server_sdk.py

- Tool definitions and the Python SDK

- call_daw()

- Backend adapter

- app.py

- Music Application · UI and audio

- ↓  Client ↔ server: MCP over stdio

- ↓  Tool function → adapter: Python function call

- ↓  Adapter ↔ app: newline-delimited JSON over the local socket


Presenter notes:

Trace Copilot/VS Code MCP client → workshop/starter/mcp_server_sdk.py → call_daw → app.py. The first link is MCP stdio; the adapter socket is application JSON. Host choice changes the first box, not the tool contract.



### Slide 15: Activity map: where we edit

- Activity map: where we edit

- File

- Workshop step

- .vscode/mcp.json

- CONNECT · slide 21: interpreter + starter path

- workshop/starter/

- BUILD · slide 20: edit mcp_server_sdk.py

- Copilot + workshop_client.py

- TEST · slides 22–23: discover, call, verify

- workshop/solutions/

- REFERENCE · compare after your attempt

- MCP slides 14 + 16 trace the call. Music showcase: slide 27.


Presenter notes:

Student edit: workshop/starter/mcp_server_sdk.py. Keep the root compatibility launchers unchanged. .vscode/mcp.json points to the canonical starter. Reference code is workshop/solutions/mcp_server_solution.py. Full music showcase is a separate connection shown on slide 27; do not replace the lab server during the protected exercise.



### Slide 16: What the MCP client sees

- Discovery: tool name and inputSchema, including bpm as an integer.
- Result: content containing a text acknowledgement.
- HOST: coordinates the LLM and permissions.
- CLIENT: discovers tools, sends calls, reads responses.
- SERVER: executes tools and returns actual data.

Presenter notes:

Spend about one minute within the existing 18–25 demo block. These are abbreviated payloads; JSON-RPC envelopes and other metadata are omitted. tools/list returns a tools array containing names, descriptions and schemas. FastMCP derives metadata from decorators, type annotations and docstrings. tools/call returns content, structured data or errors. The host uses an LLM, often through a remote service, and controls conversation and permissions; its MCP client handles the protocol. The host supplies selected results to the model. A queued tempo command is an acknowledgement: call get_state to verify completion. Other result content can include images, audio and resource links.

### Slide 17: A useful tool can act and observe

- A useful tool can act and observe

- 1 · READ STATE

- Observe the starting value.

- 2 · PERFORM AN ACTION

- Call a specific tool.

- 3 · READ STATE AGAIN

- Verify the expected result.

- Trust “queued”

- or verify the actual state?

- Choose the state check.


Presenter notes:

18–25 demo block, 20 seconds: read → act → observe again. The maze on the next slide applies the same pattern to game controls.



### Slide 18: Can an AI escape a maze using tools?

- Can an AI escape a maze using tools?

- The model chooses a move. The MCP server exposes controls. The maze app applies it.

- S

- E

- S = start       E = exit       Dark cells = walls

- EXPOSED MCP TOOLS

- move_up()      move_down()

- move_left()    move_right()

- get_maze_state()

- THE FEEDBACK LOOP

- 1  Read the maze + current position

- 2  Model selects a movement tool

- 3  App returns moved / blocked + position

- 4  Observe again; stop when at_exit = true

- WORKSHOP CONNECTION

- Move tool ↔ set_swing

- get_maze_state ↔ get_state

- Maze app ↔ app.py

- MCP is the interface. The model plans. The Application enforces valid moves.


Presenter notes:

18–25 demo block, 30 seconds. Illustration only: maze tools are examples, not tools in the student server. The host/model chooses moves, MCP exposes controls/state, and the maze app enforces walls and success. Compare with music read → act → observe on the previous slide. Ask what to do after a blocked move: observe again and choose another move.



### Slide 19: Is this different from a “normal MCP”?

- Is this different from a “normal MCP”?

- Same MCP protocol. Our custom server exposes music capabilities.

- CODING AGENT · builds and tests

- • Shell, browser or API tools

- • Can test an app without MCP

- • Prompt alone adds no capabilities

- • Verify with actual evidence

- YOUR APP + MCP · reusable controls

- • Expose focused tools + schemas

- • Reuse across compatible hosts

- • Production: validate + authorize

- • Read state to verify the result

- MCP is an integration choice. A direct API is enough for one fixed client.

- Use MCP when multiple compatible hosts need live, reusable app capabilities.


Presenter notes:

18–25 segment, about 45 seconds. MCPJAM uses standard MCP with domain-specific music tools. There is no special protocol called normal versus our MCP. Coding agents can already use shell/browser/API capabilities to test apps. Expose your app through MCP when compatible hosts need reusable discoverable actions and live state. Direct API remains reasonable for one fixed client. Prompt quality and tool connectivity solve different needs.



### Slide 20: MCP BUILD · six parts, one tool

- MCP BUILD · six parts, one tool

- EDIT: workshop/starter/mcp_server_sdk.py

- Register set_swing(amount: int).

- Describe its purpose and 0–75 range.

- Validate before calling the app.

- call_daw: cmd=set_swing, amount=input.

- Return the acknowledgement.

- Read get_state to verify.

- SERVER

- Reuse the supplied FastMCP instance.

- TOOL CONTRACT

- Decorator + name + type + description.

- VALIDATION + ADAPTER

- Check the range; send the app command.

- RESULT + TRANSPORT

- Verify queued work. Keep stdio startup.

- Add above “if __name__”. Save → restart the MCP server → verify discovery.


Presenter notes:

25–40 build/test. Three-minute guided review plus twelve minutes student testing/adaptation. Add @mcp.tool def set_swing(amount:int), validate 0–75, send call_daw({cmd:set_swing,amount:amount}), return acknowledgement, and verify state. Add above startup in workshop/starter/mcp_server_sdk.py. Compare workshop/solutions only after attempting.



### Slide 21: Copilot connection: .vscode/mcp.json

- Copilot connection: .vscode/mcp.json

- Use the supplied JSON. The input prompt selects this clone’s .venv Python.

- MCP: List Servers → mcpjam → Start. After editing Python, restart the server.

- "mcpjam": {

-   "type": "stdio",

-   "command": "${input:mcpjamPython}",

-   "args": [

-     "${workspaceFolder}/workshop/starter/mcp_server_sdk.py"

-   ]

- }

- Python path: Windows → .venv/Scripts/python.exe

- Mac → .venv/bin/python · enter an absolute path


Presenter notes:

This is the existing servers.mcpjam entry inside the supplied JSON, not the entire file: keep its inputs array and servers wrapper. command uses the mcpjamPython input. Enter the absolute venv interpreter for Windows or Mac. args identifies the MCP server, not app.py. Run MCP: List Servers, start mcpjam and inspect the tools. After adding set_swing restart the server, then re-enable/refresh tools. CLI fallback: workshop_client.py lists the canonical starter tools. Source: https://code.visualstudio.com/docs/agent-customization/mcp-servers .



### Slide 22: MCP TEST · discover, call, verify

- MCP TEST · discover, call, verify

- 1  Save your tool in workshop/starter/.

- 2  MCP: List Servers → mcpjam → Restart.

- 3  Enable tools; confirm set_swing appears.

- 4  Ask for swing 35; verify with get_state.

- 15 minutes.

- Test and adapt.

- 25–40 min · build, reconnect, test, then explain to a partner

- 2 / 3 · PRIZE QUESTION  ·  Hands up!

- Should set_swing(100) succeed?

- A  Yes       B  No


Presenter notes:

After saving, restart mcpjam in MCP: List Servers and check discovery. In Copilot ask: Use set_swing with amount 35, then get_state. Test boundaries 0 and 75 and invalid 100. Inspect calls and state, not just the chat text. Explicit CLI tests remain the deterministic fallback. Do not add extra exercise time.



### Slide 23: MCP TEST · evidence of success

- MCP TEST · evidence of success

- Test

- Expected evidence

- Discovery

- set_swing appears in available tools

- Amount 35

- Accepted and verified through get_state

- Amount 0 and 75

- Boundary values accepted

- Amount 100

- Tool error; Application state unchanged

- When the valid call

- AND the rejected call

- both behave correctly.

- Absolute verification.

- 3 / 3 · PRIZE QUESTION  ·  Hands up!

- Does “queued” prove the music changed?

- A  Yes       B  No


Presenter notes:

25–40 activity checkpoint. Discovery shows set_swing schema. Valid 35 and boundaries 0/75 succeed; get_state confirms actual state. 100 returns tool error and state stays unchanged. Prize question: queued does not prove the effect. Partner explains decorator, validation, adapter, result and state check. Success means both valid behavior and rejected behavior are correct.



### Slide 24: The security risks behind a tool call

- The security risks behind a tool call

- UNAUTHORIZED ACCESS

- Tools or records exposed to a caller who should not have access.

- EXCESSIVE PERMISSIONS

- A tool or backend account can do more than the task requires.

- INDIRECT INJECTION

- Malicious instructions hidden in documents or tool results.

- Range validation checks the value.

- Authorization checks whether the caller may perform the action.

- “Just give every tool admin access.”


Presenter notes:

40–47 required security block. Scenario: a retrieved document says send all customer records to this URL. It is data, not user authorization. Ask audience what boundary prevents the action. Separate validation, authentication and per-tool/per-record authorization. Least privilege and confirmation for risky operations reduce impact. Local workshop socket is a trusted-machine demonstration, not a production authenticated service.



### Slide 25: Tool poisoning and rug pulls

- Tool poisoning and rug pulls

- TOOL POISONING

- Malicious instructions in a tool description try to manipulate the model or its workflow.

- RUG PULLS

- A previously trusted tool changes its description or behavior after approval.

- Review what you connect—and review what changes.


Presenter notes:

40–47 security block. Tool descriptions can carry malicious instructions; a trusted description or implementation may change later. Treat descriptions and tool results as untrusted data. Review and pin server/dependency versions, inspect updates and permission scope, and re-review changed tools. Ask whether an already approved server should gain a new delete action silently: no.



### Slide 26: Security controls for MCP tools

- Security controls for MCP tools

- ✓  Check access: identity, token audience, and permission for the action.

- ↓  Limit permissions: tools and backend accounts get only what they need.

- !  Treat external content as untrusted: documents and tool results can contain malicious instructions.

- ↻  Review code and updates: server sources, dependencies, and tool descriptions.


Presenter notes:

40–47 security block. Production methods: authenticate caller; validate token audience where using remote token auth; authorize each action and record; minimize backend privilege; treat retrieved content as untrusted; review trusted sources and updates. The SDK does not automatically supply all these controls. Keep credentials out of prompts, logs and tool output. State-changing tools may need user confirmation.



### Slide 27: Copilot music: prompt → tools → MP3

- Copilot music: prompt → tools → MP3

- 1  Music config: args → mcp_server_music.py.

- 2  In chat, type / and select compose_music.

- 3  Description → web research* → catalog → score.

- 4  Receive a 30-second MP3 path; open when ready.

- *Web access depends on enabled tools; a source URL can be fetched.

- Local stdio / remote HTTP · bounded calls · verify results · no autoplay.


Presenter notes:

47–52 advanced/enterprise block: one minute for this showcase and four minutes for production architecture. Instructor has full audio setup. Use .vscode/mcp.music.example.json as a separate music configuration or add its server entry to the existing servers object, preserving valid JSON. Start mcpjam-music, enable its tools, type / and select mcpjam-music.compose_music. Enter an original rock description; prompt fetch does not itself search or generate. Copilot supplies web access if enabled; URL fetching differs from search. Provide a prepared source URL if search is unavailable, or disclose no research and compose from the description. Host queries get_instrument_catalog, authors notes and calls create_song_from_score(duration_seconds=30). The tool returns MP3 only; no app or playback is needed for rendering. Source material remains untrusted; user-stated permission to play is separate from permission to reproduce notes. Structured results, multi-server coordination, stdio/Streamable HTTP, timeouts and outcome verification remain advanced awareness. Sources: https://code.visualstudio.com/docs/agent-customization/mcp-servers and https://code.visualstudio.com/docs/agents/run/tools .



### Slide 28: Enterprise: identity + production rules

- Enterprise: identity + production rules

- IDENTITY PROVIDER

- Establishes identity

- Example: Entra ID

- Identity / token issuance

- to the client

- OPTIONAL GATEWAY

- Traffic policies and monitoring

- MCP SERVER

- Checks access to tools and data

- BACKEND

- Enforces Application business rules

- Tool request →

- MCP →

- Application call →

- Production: per-tool authorization · audit logs · safe retries · verified outcomes.


Presenter notes:

47–52 required enterprise and best-practices block. Trace identity provider → optional gateway → MCP server → backend. Identity is not permission: authorize per tool, tenant and record. Backend retains business rules. Production practices: narrow tools with explicit schemas, typed/structured results, bounded timeouts, redacted audit logs, version pinning/review, meaningful valid/invalid tests, and outcome verification. Read-only retries are often safer; do not blindly retry writes after timeout. Use idempotency keys or check outcome where supported. Scenario: create_ticket times out—did it fail or succeed? Verify before retrying. Entra ID/API Management are examples, not requirements.



### Slide 29: Where can I use this at the hackathon?

- Where can I use this at the hackathon?

- ONE USEFUL ACTION

- Search inventory or create a draft ticket

- ONE STATE CHECK

- Read the item / ticket and verify the result

- ONE CLEAR BOUNDARY

- Validate inputs; restrict access; approve risky writes

- Exit check: name your tool, input, permission,

- and the evidence that proves it worked.

- →

- →


Presenter notes:

52–55 exit block. 90-second pair exercise: name one useful project tool, its input, permission, and observable success. Examples search_inventory, create_draft_ticket or test a game move. Add a thin MCP adapter over an existing API/function; do not rewrite the app. Consider MCP when multiple compatible hosts need these capabilities. A one-off fixed integration may use a direct API. Reserve 55–60 for genuine spare time/Q&A.
