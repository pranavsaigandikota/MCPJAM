# Instructor guide — current Figma workshop

[Open the 27-slide presentation](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ)

60 minutes: 35 teaching, 20 practice, 5 setup/help buffer. Six image memes and three additional brainrot moments.

## 1. Intro to MCP Servers

Presented by Pranav

X

01 / 27

Presenter notes:

Exact 60-minute allocation:
- Before the clock: check-in and installation readiness.
- 0–15 minutes: introduction, MCP theory, APIs, real-world examples, discovery, and SDK.
- 15–25 minutes: links, demo, architecture, code walkthrough, and exercise briefing.
- 25–30 minutes: flexible setup/help buffer; ready students begin early.
- 30–50 minutes: protected student implementation and testing.
- 50–55 minutes: security risks and defenses.
- 55–58 minutes: advanced capabilities, multiple servers, and enterprise overview.
- 58–60 minutes: apply the pattern elsewhere, check understanding, and close.
35 minutes guided teaching/demo + 20 minutes practical work + 5 minutes buffer.

## 2. Check-In

02 / 27

Presenter notes:

Before the clock: check-in and installation readiness. Follow README.md. Confirm that Python, the app, and workshop_client.py work. Gemini is optional for the explicit student tests.

## 3. Today’s workshop

Understand MCP, trace a tool call, and implement and test a tool in a starter MCP server.

UNDERSTAND

Connect an AI application to useful software capabilities.

TRACE

Follow a request from the host to the music application.

IMPLEMENT + TEST

Extend the supplied server with one validated tool.

03 / 27

Presenter notes:

0–15 minutes: introduction and theory. Outcome: extend an existing Python SDK server; students implement and test one tool.

## 4. What MCP is

Model Context Protocol

An open standard that connects AI applications to tools, data, and reusable instructions.

An MCP server is the program that exposes those capabilities.

Today: extend an existing server using the Python SDK.

04 / 27

Presenter notes:

Explain the shared interface. The workshop extends an existing server using the Python SDK; it does not build an application or server from scratch.

## 5. Why developers use MCP

Benefit

In your project

Interoperability

Connect compatible hosts to one server.

Consistency

Use common discovery and calling.

Reusability

Reuse tools across AI applications.

Faster development

Let the SDK handle protocol messages.

Me when the next
compatible AI host
uses the same server.

05 / 27

Presenter notes:

Brief theory segment within 0–15 minutes. Common discovery and invocation help compatible hosts reuse capabilities. Chill Guy is a quick visual joke about reuse, not a claim that all hosts support every capability. Source: https://imgflip.com/memetemplate/562547797/Chill-Guy. Original character by Phillip Banks.

## 6. The roles in an MCP connection

HOST · AI application

Manages the model, interface, permissions, and tool workflow.

CLIENT · inside the host

Communicates with an MCP server.

↔

MCP

SERVER

Program that exposes tools, resources, and prompts.

The model proposes a tool and its arguments.
The host coordinates the call through its MCP client.

06 / 27

Presenter notes:

The model proposes a tool and its arguments. The host coordinates the call through its MCP client. The client is a component inside the host.

## 7. Where an API fits

AI HOST

Contains the MCP client

MCP SERVER

Exposes a useful tool

EXISTING API

Applies application rules

DATA / ACTION

Reads or changes the app

MCP request →

API call →

Read / write →

An MCP tool can call an existing API, Python function, or supported application command.

Existing permissions and business rules still apply.

07 / 27

+1000 AURA

Reusing an API you already have.

Presenter notes:

An MCP tool can wrap an existing HTTP API, Python function, or supported application command. Existing permissions and business rules still apply.
Quick brainrot aside: +1000 AURA — Reusing an API you already have. Tie the joke back to the technical point; keep the existing timing.

## 8. MCP servers you can use in real projects

MCP server

Practical use

Connection to this workshop

Figma

Read design context for a UI

Retrieve useful application data

GitHub

Inspect repos, issues, and PRs

Expose specific project operations

Playwright

Interact with and test a web app

Act, then verify the result

Filesystem

Read and edit permitted files

Validate inputs and restrict access

★ MCPJAM

Read music state; change tempo or swing

Implement and test your own tool

Connect an existing server for familiar software.
Build your own to expose your application’s capabilities.

Available actions depend on the server implementation and granted permissions.

08 / 27

Presenter notes:

Keep this explanation to approximately one minute. Figma already provides a server for design capabilities. Today, we are learning how to expose a capability from our own application using the same underlying pattern. Do not add another setup exercise.

## 9. Tools, resources, and prompts

TOOLS

Callable operations

Example: set_tempo or get_state

RESOURCES

Application context and data

Example: a reference document

PROMPTS

Reusable instructions

Example: a review workflow

The server exposes capabilities. The host decides how to use them.

09 / 27

Presenter notes:

Tools can read or change state. get_state is a read tool. This starter exposes tools; resources and prompts are other MCP capabilities.

## 10. Discover → select → invoke

1 · DISCOVER

The client lists tools with their names, descriptions, and input schemas.

2 · SELECT

The model proposes a tool and arguments; the host coordinates the call.

3 · INVOKE

The client calls the tool. The server validates, executes, and returns a result.

set_tempo accepts bpm, an integer.
Python validation enforces the allowed range.

10 / 27

TOOL DISCOVERY RIZZ

The host reads the schema before making a move.

Presenter notes:

For the pinned workshop SDK: initialize the connection, list tools, and call a tool. Discovery provides the tool name, description, and input schema. The model proposes; the host coordinates. Explicit clients can call a tool without any model.
Quick brainrot aside: TOOL DISCOVERY RIZZ — The host reads the schema before making a move. Tie the joke back to the technical point; keep the existing timing.

## 11. JSON, JSON-RPC, MCP, and the SDK

Layer

Responsibility

JSON

A format for representing data

JSON-RPC

An envelope for requests, responses, and errors

MCP

Defines capability messages and their meaning

Python SDK

Handles protocol messages and dispatches tool calls

You implement behavior, validation, permissions,
and backend integration.

11 / 27

Presenter notes:

The SDK handles protocol messages and dispatches tool calls. You implement useful behavior, validation, and backend integration. The SDK does not automatically implement business authorization or make every tool safe.

## 12. Links and readiness

github.com/pranavsaigandikota/MCPJAM

aistudio.google.com/api-keys

1  Open README.md for setup and launch instructions.

2  Start the music application.

3  Open mcp_server_sdk.py.

4  Use workshop_client.py for explicit tool tests.

Gemini key: AI demo only. Explicit tool tests need no key.

12 / 27

Presenter notes:

15–25 minutes: links, demo, architecture, code walkthrough, and exercise briefing. Follow README.md launch commands. Gemini API key is only for the AI host demonstration; workshop_client.py needs no model or key.

## 13. Watch This

13 / 27

WORDS  →  TOOL CALL  →  MUSIC

Let the host cook.

Presenter notes:

A transition lasting only a few seconds. Move directly into the approximately three-minute live demo.
Let Him Cook visual: https://imgflip.com/memetemplate/430535625/Let-Him-Cook. A few-second transition only; the model proposes the call, and the host coordinates it.

## 14. Demo: an AI controls the music app

“Set the tempo to 120 BPM.”

1  Inspect the selected tool and arguments.

2  Observe the change in the music application.

3  Call get_state to verify the result.

14 / 27

Presenter notes:

Approximately three minutes. Start at a tempo other than 120. Show set_tempo with bpm: 120. The model proposes the call; the host coordinates execution. Observe the app, then call get_state. If the AI host fails, use the rehearsed workshop_client.py command from README.md. Save set_swing for the student exercise.
Optional preparation before the clock: configure GeneralUser GS using README.md. The optional mcp_server_music.py supports instrumental pop arrangements and edits; keep the workshop demo focused on tempo and save swing for students.
Optional sound demo outside the timed tempo walkthrough: Windows run_music_chat.ps1 starts a background GeneralUser GS player with no visual window. Ask for a 30-second original R&B instrumental with legato and held notes. Type pause, play, stop to control transport locally without API requests. MIDI and WAV export support exact durations. Keep the 60-minute schedule unchanged.

## 15. Architecture: follow the call

Host + MCP client

gemini_host.py or the explicit workshop_client.py

mcp_server_sdk.py

Tool definitions and the Python SDK

call_daw()

Backend adapter

app.py

Music application · UI and audio

↓  Client ↔ server: MCP over stdio

↓  Tool function → adapter: Python function call

↓  Adapter ↔ app: newline-delimited JSON over the local socket

15 / 27

Presenter notes:

mcp_server_sdk.py is the MCP server. app.py is the music application. The backend socket is separate from MCP. The optional Gemini host calls Google over its API, while the local client-server connection remains MCP over stdio.

## 16. The files you will use

File

Purpose

README.md

Setup, launch commands, and exercises

mcp_server_sdk.py

Starter MCP server and backend adapter

workshop_client.py

Discover tools and test explicit arguments

mcp_server_solution.py

Completed reference implementation

MCPJAM · edit the starter, test through the client.

16 / 27

Presenter notes:

Open these files in the local clone. The completed solution is a reference after attempting the exercise. gemini_host.py is the optional model-driven demo host.

## 17. A tool is a clear function contract

@mcp.tool()
def set_tempo(bpm: int) -> str:
    """Set tempo from 40 to 240 BPM."""

DECORATOR

Registers the tool

TYPE ANNOTATION

Describes the input

DOCSTRING

Describes its purpose

Validation and backend execution live in the function body.

17 / 27

Presenter notes:

Open set_tempo in mcp_server_sdk.py. Point to validation, call_daw(), and the return value. Briefly identify FastMCP server creation and mcp.run(). Keep full code in the repository.

## 18. A useful tool can act and observe

1 · READ STATE

Observe the starting value.

2 · PERFORM AN ACTION

Call a specific tool.

3 · READ STATE AGAIN

Verify the expected result.

Trust “queued”
or verify the actual state?

A queued or accepted request does not prove
the action finished. Verify application state.

Choose the state check.

18 / 27

Presenter notes:

Read state, perform an action, read state again. An acknowledgement can mean queued rather than finished. The two-buttons visual is a quick joke: choose verification. Template: https://imgflip.com/memetemplate/Two-Buttons. Keep within the 15–25 minute walkthrough.

## 19. Your task: add a swing tool

Implement set_swing(amount: int) in mcp_server_sdk.py.

Register it with @mcp.tool() and a clear description.

Accept integers from 0 to 75; reject values outside that range.

Use call_daw(): command set_swing, field amount.

Return a useful result.

Use set_tempo as your example.
Place your tool definition before server startup.

19 / 27

Presenter notes:

Finish the briefing by minute 25. Students extend the supplied server, not build it from scratch. Do not reveal the reference solution before the attempt. Define the tool before server startup.

## 20. Build, reconnect, and test

1  Implement and save your tool.

2  Restart or reconnect to load the changes.

3  Confirm discovery and test explicit inputs.

4  Use get_state to verify the change.

LOCKED IN

20 minutes.
One useful tool.

Edit mcp_server_sdk.py · Test with workshop_client.py

5-minute setup/help buffer  →  20 minutes of protected practice

20 / 27

NO SCHEMA? NO RIZZ.

Validate inputs. Keep your aura.

Presenter notes:

25–30 minutes: separate five-minute flexible setup/help buffer; ready students begin early.
30–50 minutes: protect all 20 minutes for student implementation and testing.
- 3 minutes: locate and understand the existing tool.
- 8 minutes: implement set_swing.
- 3 minutes: restart/reconnect and confirm discovery.
- 4 minutes: test valid, boundary, and invalid inputs.
- 2 minutes: show a partner the result and explain the implementation.
Early finishers: natural-language request or optional mute_track. A second tool is not required.
Locked In Cat visual: https://imgflip.com/memetemplate/579964988/LOCKED-IN-CAT. Keep this slide up during practice; the meme adds no teaching segment.
Quick brainrot aside: NO SCHEMA? NO RIZZ. — Validate inputs. Keep your aura. Tie the joke back to the technical point; keep the existing timing.

## 21. What a successful test shows

Test

Expected evidence

Discovery

set_swing appears in available tools

Amount 35

Accepted and verified through get_state

Amount 0 and 75

Boundary values accepted

Amount 100

Tool error; application state unchanged

When the valid call
AND the rejected call
both behave correctly.

Absolute verification.

Test validation with explicit client arguments.
The model may refuse or modify an invalid request before calling.

21 / 27

Presenter notes:

Success: demonstrate one valid call, one rejected call, and explain the decorator, validation, and backend connection. Explicit arguments test validation; a model may refuse or change invalid natural-language requests. Absolute Cinema visual: https://imgflip.com/memetemplate/602369493/Absolute-cinema. This reaction rewards valid AND invalid tests.

## 22. The security risks behind a tool call

UNAUTHORIZED ACCESS

Tools or records exposed to a caller who should not have access.

EXCESSIVE PERMISSIONS

A tool or backend account can do more than the task requires.

INDIRECT INJECTION

Malicious instructions hidden in documents or tool results.

Range validation checks the value.
Authorization checks whether the caller may perform the action.

22 / 27

“Just give every tool admin access.”

Presenter notes:

50–55 minutes: security risks and defenses. Range validation checks a value. Authorization checks whether this caller may perform the action. The local workshop socket is a trusted-machine demo, not a production authenticated service.
Quick visual joke: unchecked permissions are a fire, not a shortcut. This Is Fine template via https://imgflip.com/memetemplate/This-Is-Fine; original comic by KC Green. Keep within the five-minute security segment.

## 23. Tool poisoning and rug pulls

TOOL POISONING

Malicious instructions in a tool description try to manipulate the model or its workflow.

RUG PULLS

A previously trusted tool changes its description or behavior after approval.

Review what you connect—and review what changes.

23 / 27

Presenter notes:

These are related risks, not synonyms. A malicious description can influence a model before execution. A rug pull changes a previously trusted tool. Review tool metadata and updates, and keep access controls outside model instructions.

## 24. Security controls for MCP tools

✓  Check access: identity, token audience, and permission for the action.

↓  Limit permissions: tools and backend accounts get only what they need.

!  Treat external content as untrusted: documents and tool results can contain malicious instructions.

↻  Review code and updates: server sources, dependencies, and tool descriptions.

24 / 27

Presenter notes:

For protected remote services, validate tokens intended for that service. Do not blindly forward incoming tokens to downstream APIs. Prompt-injection filters can help, but do not replace access controls. Keep secrets out of source code and projected demonstrations.

## 25. Advanced capabilities

Structured results, images, and audio where supported.

Host-mediated model requests or user input where supported.

Workflows using tools from multiple servers.

Timeouts, outcome verification, and careful retries.

The host can retrieve from one server, call another,
and save a result through a third. The host coordinates.

25 / 27

Presenter notes:

55–58 minutes: advanced capabilities, multiple servers, and enterprise overview. Support depends on the host, server, SDK, and protocol version. Servers do not automatically cooperate merely because they use MCP.

## 26. MCP in an enterprise application

IDENTITY PROVIDER

Establishes identity
Example: Entra ID

Identity / token issuance
to the client

OPTIONAL GATEWAY

Traffic policies and monitoring

MCP SERVER

Checks access to tools and data

BACKEND

Enforces application business rules

Tool request →

MCP →

Application call →

Entra ID and API Management are examples—not MCP requirements.

26 / 27

Presenter notes:

55–58 minutes: brief overview, not a complete OAuth tutorial. Entra ID and API Management are examples, not requirements. Identity provider establishes identity; it is not a proxy that every tool request passes through.

## 27. The same pattern in your own project

EXISTING API

Call a focused API endpoint

PYTHON OR COMMAND

Use a Python function or a constrained command

APPLICATION

Use a supported application interface

Expose a useful capability, validate the request,
enforce permissions, and verify the result.

27 / 27

→

→

Presenter notes:

58–60 minutes: apply the pattern elsewhere, check understanding, and close.
Ask students:
- Where is the MCP server?
- What registers your tool?
- How did you verify that it worked?

