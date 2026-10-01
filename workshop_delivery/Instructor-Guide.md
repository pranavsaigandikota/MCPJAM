# MCPJAM workshop: Windows and macOS

21 core slides, 60 minutes; 12 appendix slides are reference only.

See ../MAC_SETUP.md and ../WORKSHOP_PRESENTATION.md for platform setup and the teaching route.

## 1. Make an AI control a music studio

00–03 min  /  Live demo

Demo the preconfigured host calling set_tempo, then call get_state. Point to the actual tool name and bpm argument. If audio fails, visual state is enough. Ask students to predict which program changes the tempo. Goal: add and test a new server capability, not merely chat with a model.

## 2. The route through our hour

03–05 min  /  Goal + prerequisites

Prerequisites: basic Python functions and dictionaries, Python 3.10+, dependencies installed, and one host configured before class. A one-hour beginner-to-MCP session is realistic with setup preflight; it is not a promise to teach Python, install accounts, and deploy production systems too. Core task is set_swing. Mute is guided/stretch. Advanced implementation remains follow-up.

## 3. MCP standardizes the connection

05–07 min  /  What is an MCP server?

Expand MCP as Model Context Protocol. Contrast standard discovery and invocation with custom integrations per AI application. The model may propose a call; the host/client sends it under host policy. A server need not contain an LLM. Ask: can this server wrap a non-AI application? Yes. The DAW is the example.

## 4. Find the MCP boundary

07–10 min  /  Architecture

Open the repo and locate mcp_server_sdk.py, app.py, requirements.txt, README.md. Draw the first boundary: host/client to server is MCP over stdio. Second boundary: call_daw sends newline-delimited JSON to a local socket; this is not MCP. app.py queues commands and updates the UI. mcp_server.py is an older educational protocol sketch; do not run it in the workshop.

## 5. Three ways a server can help

10–12 min  /  Capabilities

Tools are model-controlled, resources application-controlled, and prompts user-controlled in the conceptual model; actual host UI can differ. Tools may also read: get_state is a read-only tool in our starter. Ask students to classify “list instruments”, “set swing”, “start a composition template”. Only tools are implemented today; the other two are extension examples, not existing starter features.

## 6. Connect first, then explain the plumbing

12–15 min  /  Run + connect

Setup is prepared before class on each platform. Mac instructions in MAC_SETUP.md use standard Python 3.13 from python.org, which includes Tk, and matching pygame wheels. Run workshop_preflight.py and -m tkinter beforehand. Use the interpreter inside the project venv; create it locally on each computer. __main__.py imports app.main and calls main(). Run from the package parent. The host launches the stdio subprocess; no second manually launched server is needed. Use workshop_preflight.py --host-config to print actual paths, adapted to the selected host. Windows and Mac setup/config examples are in separate appendix slides.

## 7. Observe → act → verify

15–17 min  /  First successful call

Important backend behavior: write commands are acknowledged when queued, before the UI applies them. A successful queued acknowledgement is not proof the state changed. Read get_state after the UI has had time to process it. The revised tool says queued, not updated. Students should distinguish tool response, backend acknowledgement and application state.

## 8. One call, four protocol moments

17–20 min  /  SDK lifecycle

Trace the successful call just observed. The SDK handles JSON-RPC requests/responses, serialization, IDs, initialization and dispatch. Capability negotiation matters: optional features depend on both sides. Tool discovery may succeed even if the DAW is offline because discovery does not invoke call_daw. Avoid teaching an old hard-coded protocol version as current.

## 9. Read the tool you just used

20–23 min  /  Function anatomy

This function is extracted directly from mcp_server_sdk.py, including its docstring, range check, error text and return message. Long lines wrap visually; copy code from the source file. Explain typed parameter, description, validation, backend mapping and result. A plain int does not encode the BPM range; the explicit check enforces it. Use stderr for debugging in a stdio server. The real startup is from mcp.server.fastmcp import FastMCP, mcp = FastMCP("mcpjam-workshop"), and mcp.run() under the main guard.

## 10. Validate before crossing the boundary

23–26 min  /  Safe tool design

Ask what happens for 500 BPM, 40 BPM and 240 BPM. Demonstrate invalid input with an explicit client/Inspector call because the model may refuse or choose not to invoke an invalid request. Schema/type validation and domain validation are distinct. Narrow tools reduce authority; never expose an arbitrary shell command or arbitrary backend command passthrough to an LLM for convenience.

## 11. Build a new capability: set_swing

26–28 min  /  Core exercise

Explain swing as timing groove, not a music theory lesson. Students edit mcp_server_sdk.py above the if __name__ block. Show app.py set_swing handler to confirm the command spelling and range. Require validation before call_daw; the backend clamps values, so checking only the visual result would hide incorrect tool behavior. Core outcome is student-owned implementation of one new registered capability.

## 12. Good tool design helps the model choose

28–30 min  /  Before you code

Take a quick student suggestion for a docstring. Explain why name, units and side effects matter for discovery. Read-only vs destructive tool annotations can inform a host, but are hints, not permission enforcement. Return actual backend acknowledgements and verify state; do not invent success. Keep arbitrary user text out of trusted instruction positions.

## 13. Your turn: write, connect, test

30–40 min  /  Protected coding block

Protect all ten minutes; do not lecture over the lab. Minute 2: check decorators and signatures. Minute 5: confirm valid range logic and command mapping. Minute 8: reconnect/restart host process so edited code loads. Fast finishers use SDK client --tool set_swing --arguments with 100. Provide solution only after an attempt or for recovery. If students lag, skip live mute coding and keep security discussion intact.

## 14. Prove the server enforces its contract

40–43 min  /  Deterministic verification

Use workshop_client.py with --arguments-file to avoid native shell JSON quoting differences. The exact PowerShell calls are in the setup appendix. The client defaults to mcp_server_sdk.py, starts the server with its own Python interpreter, initializes, lists tools, then optionally calls one. It prints the SDK result and exits 1 when isError is true. Follow with a new get_state call after the UI processes its queue. get_state returns a dict, not an object with attribute .swing: inspect the returned swing key. Backend-off test must produce error, not claim success.

## 15. Debug the correct layer

43–45 min  /  Recovery buffer

Reserve these two minutes for recovery instead of adding extra content. stdout belongs to protocol messages: debug output should go to stderr. The host starts the stdio server; a separate manual process is not its connection. If host UI fails, students can demonstrate the server with workshop_client.py. If dependencies are unavailable, instructor can use the same client on the prepared environment.

## 16. Two inputs, one validated action

45–47 min  /  mute_track

Instructor demonstrates or students use as stretch exercise. Allowlist from constants.py: kick, snare, hihat, clap, bass, keys, lead, pad. Validation is security at the function boundary, not authentication. Reading state shows muted.kick. Fast students may implement; the one-hour promise remains at least one student-written tool. Exact completed implementation in mcp_server_solution.py.

## 17. Treat content as data, not authority

47–50 min  /  Injection, poisoning, rug pulls

Tie the risks to the tools students just built. A song_ref or returned resource can contain adversarial instructions. Tool metadata itself can be poisoned. A rug pull is a change after approval, so review initial installation and updates. Ask which control actually stops exporting files: backend/service permissions and narrow exposed capabilities; prompting alone is insufficient. Keep secrets out of results and logs. Host policy can request user approval for sensitive actions.

## 18. Local demo → remote production

50–53 min  /  Transports + identity

Compare process pipes with a network endpoint. OAuth authorization is for HTTP-based MCP, not automatically added to stdio. Verify identity, issuer/audience/expiry and required scopes through a proper implementation. Do not forward a received MCP bearer token to unrelated backend services. Use correctly authorized downstream credentials; enforce per-user data access. The demo localhost socket has no authentication and is not production-ready. Bind remote local HTTP appropriately and validate Origin to defend DNS rebinding where applicable.

## 19. Advanced features are negotiated

53–55 min  /  Beyond today’s tools

These are recognition-level concepts in this hour, not implementation objectives. Sampling does not mean the server secretly owns the model; the client controls model access and permissions. Elicitation lets supported clients ask users for information; follow spec restrictions for sensitive information. Support varies by SDK/host and protocol revision. Retry read operations carefully; retries of mutating tools can duplicate side effects. Multiple servers are coordinated by the host, not magically orchestrated by MCP.

## 20. Enterprise: enforce policy at each hop

55–57 min  /  Production stack

Retain the original enterprise topic: example deployment could use Entra ID, API Management, an MCP server and internal APIs. These are example components, not mandatory dependencies. A gateway does not replace object-level authorization in server/backend. Log caller, tool, outcome and correlation identifiers without secrets or sensitive raw results. Apply request-size/rate limits, isolation and timeouts. SDK handles protocol, not all production controls.

## 21. Explain what you built

57–60 min  /  Demonstrate + close

Have pairs explain to each other while two students show their tool. Expected: mcp_server_sdk.py, registered function + schema/description, protocol and transport/dispatch, backend uses its own local JSON socket, enforce policy at host/server/backend. Close with transfer: name an existing API or Python function they could wrap next. Students should leave with one implemented tool and a map of advanced/security topics, not a claim of production deployment expertise.

## 22. Reference: Windows setup and test

Reference only  /  Outside the 60-minute route

These are exact single-line commands matching README.md and workshop_client.py. Run the swing call only after adding the tool to the starter. The package directory must be named MCPJAM. Python 3.10+. requirements pins mcp[cli]==1.19.0 for FastMCP. Unix: python3 -m venv .venv; ./.venv/bin/python -m pip install -r requirements.txt; from parent ./MCPJAM/.venv/bin/python -m MCPJAM. Explicit client from package: ./.venv/bin/python workshop_client.py --tool set_swing --arguments-file swing-input.json. Set-Content creates a JSON file rather than embedding quoted JSON in native program arguments.

## 23. Reference: Mac setup before class

Reference only  /  Terminal: zsh or bash

Use the standard Python 3.13 macOS installer from python.org for a new installation. It provides universal2 binaries for Intel/Apple Silicon and native Tk. Run the matching Install Certificates.command after installation. Python 3.13 pygame wheels are available for both architectures. Existing compatible Python 3.10–3.13 with working Tk can be used instead. Do not use the Apple system interpreter or copy a Windows venv. Activation is unnecessary because commands select the interpreter explicitly. See MAC_SETUP.md for detailed troubleshooting and sources. Native Mac rehearsal is required; Windows validation does not test GUI/audio on a Mac.

## 24. Reference: explicit calls on a Mac

Reference only  /  Inside MCPJAM with the DAW running

Single quotes preserve literal JSON in zsh/bash. These calls start a fresh MCP subprocess using the client interpreter each time; no AI host is required for this explicit SDK test. Keep the DAW running in its original terminal. Client prints discovery and the result. Invalid 100 must return isError true and exit 1. Follow valid changes with get_state after the UI processes its queue. To use the completed solution add --server mcp_server_solution.py. The optional --arguments-file works on both platforms.

## 25. Reference: host configuration

Reference only  /  Host-specific example

This mcpServers layout is an example used by some desktop hosts, not a universal MCP configuration standard. Rehearse the exact host chosen for the event in advance. It launches the server; no manually launched second server is needed. Do not put secrets into slides/config committed to the repo.

## 26. Reference: Mac host configuration

Reference only  /  Host-specific JSON example

Print example JSON containing actual paths from inside the project with ./.venv/bin/python workshop_preflight.py --host-config. It uses sys.executable without resolving the Unix venv symlink and the absolute server path, so it preserves the environment and handles spaces. Adapt the mcpServers structure to the selected host. Do not use tilde expansion in host configuration. The host launches the server; it need not have a shell PATH or activated venv. The Windows equivalent uses .venv/Scripts/python.exe. The script prints only and does not edit host settings.

## 27. Reference: set_swing solution

Reference only  /  Reveal after the lab

Matches the completed solution file. Include actual tests for typical and boundary values, invalid values and backend failures. Discovery of the tool alone is not sufficient.

## 28. Reference: mute_track solution

Reference only  /  Optional extension

Tests: kick true, kick false, violin true. Read state.muted.kick after UI update. This is a guided extension, not a second required beginner implementation within the timed hour.

## 29. Reference: JSON ≠ JSON-RPC ≠ MCP

Reference only  /  Protocol envelope

This illustrates the envelope, not a payload students must manually write. The SDK handles it. Notifications have no request ID and no response. Tool execution errors can be represented as isError tool results; malformed/unsupported protocol operations use JSON-RPC error responses. mcp_server.py is an intentionally incomplete older inspection example, not the main implementation.

## 30. Reference: production security review

Reference only  /  Beyond the local demo

These are production engineering controls, not implemented by the demo. Loopback reduces network exposure but provides no caller identity. For remote servers use the authorization and transport requirements of the supported protocol revision. Treat tool annotations as untrusted hints. Preserve separate authorization to downstream services and avoid confused-deputy behavior. Gateway controls supplement, not replace, per-user backend checks.

## 31. Reference: the adapter and server startup

Reference only  /  mcp_server_sdk.py

Startup and get_state are exact source excerpts. call_daw uses socket.create_connection with timeout=5, sends JSON plus newline, reads at most 1_048_577 bytes and rejects responses above 1_048_576 or without the terminating newline. Empty replies, malformed JSON and a missing/false ok produce errors. Those are adapter checks, not authentication, rate limits or complete server-side protection. app.py accepts many commands but the SDK starter exposes only get_state and set_tempo. The DAW mutation handlers already implement set_swing and mute_track; students expose them as MCP tools. get_state returns a dictionary containing bpm, swing, muted and other keys. Full adapter source:

def call_daw(command: dict[str, Any]) -> dict[str, Any]:
    with socket.create_connection((HOST, PORT), timeout=5) as connection:
        connection.sendall(json.dumps(command).encode("utf-8") + b"\n")
        with connection.makefile("rb") as stream:
            reply = stream.readline(1_048_577)
    if not reply:
        raise RuntimeError("The DAW did not return a response")
    if len(reply) > 1_048_576 or not reply.endswith(b"\n"):
        raise RuntimeError("The DAW response exceeded the limit or was incomplete")
    result = json.loads(reply.decode("utf-8"))
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise RuntimeError(f"DAW rejected the command: {result}")
    return result

## 32. Instructor: rehearse the success path

Instructor reference  /  Preparation

Distribute platform-specific setup before class. Rehearse on native Mac hardware used by participants: Windows protocol tests do not establish Mac GUI/audio results. Run preflight and a Tk window test, then actual DAW and host calls. No MIDI hardware or soundfont is needed. The same MCP Python files serve both platforms. The supplied protocol tests use a mock DAW, not the real GUI. Protect coding time and keep advanced concepts at recognition level. Instructor uses solution, students use starter.

## 33. Sources + version scope

Reference only  /  Updated October 1, 2026

Official Python SDK — workshop v1.x API
https://github.com/modelcontextprotocol/python-sdk/tree/v1.19.0
MCP architecture and concepts
https://modelcontextprotocol.io/docs/learn/architecture
Tools, resources and prompts — versioned spec
https://modelcontextprotocol.io/specification/2025-11-25/server/tools
Security best practices
https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices
HTTP authorization
https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
Sampling + elicitation
https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
Mac Python/Tk: https://docs.python.org/3/using/mac.html
Mac installer: https://www.python.org/downloads/macos/
Pygame architecture/version wheels: https://pypi.org/project/pygame/#files
Additional: https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation . The workshop pins the v1 SDK API. Original deck: MCPJAM-Workshop-Full-Edition (1).pptx. All original major subjects retained, retimed or moved into the appendices. Mac setup instructions are documented; native GUI/audio/host rehearsal remains an instructor prerequisite.