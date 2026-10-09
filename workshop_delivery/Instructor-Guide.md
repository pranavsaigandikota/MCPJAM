# Intro to MCP Servers: instructor guide

[Edit/present the current Figma deck](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ).
Matching export: MCPJAM-Workshop-29-Slides.pptx and PDF.
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
Use core-only setup for the lab. Gemini and sampled audio are optional instructor
preparation; explicit tool tests need no API key and visual state can be verified
without audio. The check-in QR is an event QR; README/GitHub is the setup reference.

Keep the existing visual diagrams and two-column comparisons. Pair the read/act/observe concept on slide 17 with the maze illustration on slide 18.
Keep them to 20 and 30 seconds; the standalone transition was removed.
Use the concise recipe on slide 20: imports, server and transport already exist;
students add one tool and explain registration, validation, adapter and verification.
Full music generation, a second tool, detailed JSON-RPC plumbing and installing
multiple third-party servers are outside the clock. Security and enterprise stay live.

## Activity navigation

| Slides | Students should understand/do |
|---|---|
| 14 | MCP over stdio reaches the server; local JSON socket reaches the backend |
| 15 | Map the files and next steps |
| 16 | Tool registration, input type and description |
| 20–21 | MCP BUILD: edit mcp_server_sdk.py below Student exercise, above startup |
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

On screen:

- Presented by Pranav
- X

Presenter notes:

55 minutes planned + 5 minutes spare. 00–08 install/check-in. 08–18 foundations, prompts/APIs and MCP options. 18–25 tempo demo, architecture, contract and paired feedback-loop/maze illustration. 25–40 protected build/test: 3 minutes guided + 12 audience testing/adaptation. 40–47 security. 47–52 advanced awareness, enterprise and production practices. 52–55 hackathon transfer and exit check. 55–60 spare. Start setup at minute 1 and pair blocked learners. Transition and duplicate exercise slide were cut. Full music showcase stays outside the hour.

### Slide 2: Install now

On screen:

- SETUP · README.md
- Windows
- setup.ps1 -CoreOnly
- Mac
- bash setup.sh --core-only
- Pair if blocked
- QR: event check-in

Presenter notes:

00–08 min: installation starts now. Windows: powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -CoreOnly. Mac: bash setup.sh --core-only, with Homebrew available. Open README for clone and manual Python/Tk instructions. Core-only supports visual verification. Full audio and Gemini are optional instructor preparation. Ask who is ready, installing, or blocked. Continue setup during theory, check readiness before minute 25, and pair blocked learners. Fresh Python/Homebrew installs may run long. Reserve 55–60 for spare time.

### Slide 3: Today’s workshop

On screen:

- 8 min setup · 10 theory · 7 demo · 15 practice
- 7 security · 5 enterprise · 3 exit · 5 spare
- UNDERSTAND
- Connect an AI Application to useful software capabilities.
- TRACE
- Follow a request from the host to the music Application.
- IMPLEMENT + TEST
- Extend the supplied server with one validated tool.

Presenter notes:

55 minutes planned + 5 minutes spare. 00–08 install/check-in. 08–18 foundations, prompts/APIs and MCP options. 18–25 tempo demo, architecture, contract and paired feedback-loop/maze illustration. 25–40 protected build/test: 3 minutes guided + 12 audience testing/adaptation. 40–47 security. 47–52 advanced awareness, enterprise and production practices. 52–55 hackathon transfer and exit check. 55–60 spare. Start setup at minute 1 and pair blocked learners. Transition and duplicate exercise slide were cut. Full music showcase stays outside the hour. Security and enterprise are required live content.

### Slide 4: What MCP is

On screen:

- Model Context Protocol
- An open standard that connects AI Applications to tools, data, and reusable instructions.
- An MCP server is the program that exposes those capabilities.
- Today: extend an existing server using the Python SDK.

Presenter notes:

Explain the shared interface. The workshop extends an existing server using the Python SDK; it does not build an application or server from scratch.

Meme image source: https://imgflip.com/memetemplate/609042041/Tralalero-Tralala

### Slide 5: Why MCP instead of one prompt?

On screen:

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

On screen:

- HOST · the AI Application you use
- Codex · Claude Code · Antigravity
- Our demo: gemini_host.py uses Gemini
- The host coordinates model + tools + permissions.
- CLIENT · the MCP connection inside it
- Our demo: Python ClientSession
- Discovers tools, sends calls, receives results.
- ↔
- MCP
- SERVER · exposes tools
- Our demo: mcp_server_sdk.py
- Built with FastMCP
- Starter: get_state + set_tempo; you add set_swing
- Model ≠ host: Gemini/Claude/GPT supply model reasoning; the host Application coordinates the work.
- Backend ≠ MCP server: app.py changes the music; our server exposes its controls.

Presenter notes:

08–18 segment. Model reasons; host coordinates tools, permissions and model interaction; MCP client speaks to server; server exposes capabilities. Starter has get_state and set_tempo plus the instrument catalog resource. Students add set_swing. Explicit workshop_client.py tests need no model or API key.

### Slide 7: Where an API fits

On screen:

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

On screen:

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

On screen:

- TOOLS
- Callable operations
- Example: set_tempo or get_state
- RESOURCES
- Read-only context and data
- Our app: GeneralUser GS instrument catalog
- PROMPTS
- Reusable instructions
- Example: a review workflow

Presenter notes:

08–18 segment. Tools are callable operations; resources are readable context; prompts are reusable instructions. get_state is a read-only tool, not a resource merely because it reads state. GeneralUser GS catalog is our real resource. Quick audience classification: set_tempo = tool, instrument catalog = resource, reusable review instructions = prompt.

### Slide 10: Discover → select → invoke

On screen:

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

On screen:

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

### Slide 12: Links and readiness

On screen:

- github.com/pranavsaigandikota/MCPJAM
- aistudio.google.com/api-keys
- 1  Open README.md for setup and launch instructions.
- 2  Start the music Application.
- 3  Open mcp_server_sdk.py.
- 4  Use workshop_client.py for explicit tool tests.
- Gemini key: AI demo only. Explicit tool tests need no key.

Presenter notes:

Finish theory by minute 18. Install was started at minute 1. README has Windows/Mac clone, setup and launch commands. Run the app and open mcp_server_sdk.py. Use workshop_client.py for tests; no Gemini key needed. Core-only supports visual verification even if audio is unavailable. Pair blocked learners before minute 25.

### Slide 13: Demo: an AI controls the music app

On screen:

- “Set the tempo to 120 BPM.”
- 1  Inspect the selected tool and arguments.
- 2  Observe the change in the music Application.
- 3  Call get_state to verify the result.

Presenter notes:

18–25 segment, about 90 seconds. Use set_tempo(120), then get_state. Inspect actual tool arguments and app state. Queued is acknowledgement, not proof of completed mutation. Gemini demo optional; explicit client path works without API key.

### Slide 14: MCP ACTIVITY · trace the call

On screen:

- Host + MCP client
- gemini_host.py or the explicit workshop_client.py
- mcp_server_sdk.py
- Tool definitions and the Python SDK
- call_daw()
- Backend adapter
- app.py
- Music Application · UI and audio
- ↓  Client ↔ server: MCP over stdio
- ↓  Tool function → adapter: Python function call
- ↓  Adapter ↔ app: newline-delimited JSON over the local socket

Presenter notes:

18–25 segment. This is the MCP architecture slide for the activity. Host/client → mcp_server_sdk.py uses MCP over stdio. Python tool calls call_daw; adapter sends newline-delimited JSON over localhost socket to app.py. That socket is the backend protocol, not MCP. Students edit the server, not the music application.

### Slide 15: Activity map: where we edit

On screen:

- File
- Workshop step
- README.md
- SETUP · slide 12: launch and test commands
- mcp_server_sdk.py
- BUILD · slides 20–21: add set_swing here
- workshop_client.py
- TEST · slides 22–23: discover, call, verify
- mcp_server_solution.py
- REFERENCE · compare after your attempt
- MCP slides 14 + 16 explain the path and contract. app.py is the backend.

Presenter notes:

18–25 demo block, 30 seconds. Slide 14 traces MCP/backend boundaries; 16 explains the contract. Slides 17–18 pair the read/act/observe concept with a maze. MCP BUILD slides 20–21 edit mcp_server_sdk.py; MCP TEST slides 22–23 use workshop_client.py and get_state. README is the command reference; compare solution only after attempting.

### Slide 16: MCP ACTIVITY · understand the contract

On screen:

- @mcp.tool()
- def set_tempo(bpm: int) -> str:
-     """Set tempo from 40 to 240 BPM."""
- DECORATOR
- Registers the tool
- TYPE ANNOTATION
- Describes the input
- DOCSTRING
- Describes its purpose

Presenter notes:

18–25 segment. Three lines are enough to understand registration, input type and purpose. AI can generate implementation, but students must judge the contract, validation, permission and outcome. Existing set_tempo has 40–240 range validation in its body.

### Slide 17: A useful tool can act and observe

On screen:

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

On screen:

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

On screen:

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

On screen:

- YOUR EDIT: mcp_server_sdk.py
- Register set_swing(amount: int).
- Describe its purpose and range.
- Validate 0–75 in Python.
- call_daw: cmd=set_swing, / amount=the validated input.
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
- FastMCP handles the order channel. app.py does the work. get_state checks what actually changed.

Presenter notes:

25–40 activity begins: 3 minutes guided build + 12 audience testing/adaptation. Read the six-step recipe; AI may generate code, but students explain registration, input contract, validation, adapter, acknowledgement and outcome verification. Implement set_swing below Student exercise and above startup. Validate 0–75; call_daw cmd=set_swing, amount=validated value; return the actual acknowledgement, then verify get_state. Full implementation remains in README/solution, not on the slide.

### Slide 21: MCP BUILD · edit mcp_server_sdk.py

On screen:

- 1  Explorer → MCPJAM       2  mcp_server_sdk.py       3  Add below “Student exercise”
- Keep it above server startup. Save → reconnect → test → verify with get_state.

Presenter notes:

25–40 hands-on block. Point to Student exercise and add function above if __name__ == __main__. Save. workshop_client.py starts a fresh server per run; persistent hosts require reconnect/restart. Students should be able to say which file is MCP and which is the backend.

### Slide 22: MCP TEST · discover, call, verify

On screen:

- 1  Implement and save your tool.
- 2  Restart or reconnect to load the changes.
- 3  Confirm discovery and test explicit inputs.
- 4  Use get_state to verify the change.
- 15 minutes.
- Test and adapt.
- 25–40 min · build, reconnect, test, then explain to a partner
- 2 / 3 · PRIZE QUESTION  ·  Hands up!
- Should set_swing(100) succeed?
- A  Yes       B  No

Presenter notes:

25–40 protected activity. Build 3 minutes guided, then 12 minutes testing/adapting and partner explanation. Use README commands for Windows/Mac. Discover set_swing, test 35, boundary 0/75, invalid 100, and verify with get_state. Ask audience to predict whether 100 succeeds: no. Pair blocked learners. Do not consume the final 5-minute buffer as planned teaching.

### Slide 23: MCP TEST · evidence of success

On screen:

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

On screen:

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

On screen:

- TOOL POISONING
- Malicious instructions in a tool description try to manipulate the model or its workflow.
- RUG PULLS
- A previously trusted tool changes its description or behavior after approval.
- Review what you connect—and review what changes.

Presenter notes:

40–47 security block. Tool descriptions can carry malicious instructions; a trusted description or implementation may change later. Treat descriptions and tool results as untrusted data. Review and pin server/dependency versions, inspect updates and permission scope, and re-review changed tools. Ask whether an already approved server should gain a new delete action silently: no.

### Slide 26: Security controls for MCP tools

On screen:

- ✓  Check access: identity, token audience, and permission for the action.
- ↓  Limit permissions: tools and backend accounts get only what they need.
- !  Treat external content as untrusted: documents and tool results can contain malicious instructions.
- ↻  Review code and updates: server sources, dependencies, and tool descriptions.

Presenter notes:

40–47 security block. Production methods: authenticate caller; validate token audience where using remote token auth; authorize each action and record; minimize backend privilege; treat retrieved content as untrusted; review trusted sources and updates. The SDK does not automatically supply all these controls. Keep credentials out of prompts, logs and tool output. State-changing tools may need user confirmation.

### Slide 27: Advanced capabilities

On screen:

- Structured results, images, and audio where supported.
- Local stdio or remote Streamable HTTP + authorization.
- Workflows using tools from multiple servers.
- Timeouts, outcome verification, and careful retries.
- The host can retrieve from one server, call another,
- and save a result through a third. The host coordinates.

Presenter notes:

47–52 enterprise/advanced block: spend the first 60 seconds here, then four minutes on production architecture. Structured output/content support depends on host and protocol version. The host coordinates multi-server workflows. Lab uses pinned SDK v1 and stdio; remote services generally use Streamable HTTP with appropriate auth. Current protocol docs have deprecated sampling, so do not teach it as a required new-design feature. Structured results, user elicitation where supported, timeouts and outcome verification are useful awareness topics. Source: https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture .

### Slide 28: Enterprise: identity + production rules

On screen:

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

On screen:

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

