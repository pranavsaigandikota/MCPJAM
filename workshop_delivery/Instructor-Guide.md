# MCPJAM workshop: Windows and macOS

21 core slides, 60 minutes; 13 appendix slides are reference only.

See ../MAC_SETUP.md and ../WORKSHOP_PRESENTATION.md for setup and timing. Interview practice: ../INTERVIEW_PREP.md. Full code and commands are appendix references; main slides emphasize theory, use cases and six production patterns.

## 1. Introduction to MCP servers

00–02 min / One live example

The workshop is an introduction to MCP servers. Demo the preconfigured tempo tool and read state. Explain that the AI proposes an action, the host/client routes it, and the server calls the backend. Code is evidence of the boundary, not material to memorize. AI assistance is allowed in the lab, but students must explain and verify the implementation. Set expectations: foundational interview preparation and a small practical tool; not a production deployment or a guarantee of any interview result.

## 2. What an MCP server actually is

02–04 min / A precise definition

Interview answer: MCP is a protocol for applications to discover and use server-provided tools, resources and prompts. A server is a program exposing those capabilities. JSON-RPC supplies message envelopes; transports carry them. A tool can read or mutate, so do not define all tools as writes. The LLM does not acquire arbitrary Python execution. Host and server are separate responsibilities even if the application embeds both. A server may wrap an HTTP API, a library, a database, or an application socket.

## 3. Host, client, server: who owns what?

04–07 min / Explain the boundaries

Ask who should decide which servers a user installs and whether to request confirmation: the host manages its connection and consent policy. A server still enforces access to the backend. Multiple servers are integrated by multiple client connections under host control. A shared remote server can serve many callers; one-client-to-one-server relationship does not mean only one user can use a server. Context should be limited to what the task needs. The class server/backend separation is real: MCP stdio is different from the DAW localhost JSON socket.

## 4. Tools, resources, prompts: choose the primitive

07–10 min / Which one fits?

Conceptual control: tools are model-controlled, resources application-controlled and prompts user-controlled; host UX varies. get_state is a read tool, so resource versus tool is about how the context is exposed, not a claim that tools always mutate. Example challenge: expose a reference document as a resource, a database search as a bounded read tool, and a recurring analysis workflow as a prompt. Our starter registers tools only; the resource and prompt examples are hypothetical extensions. Resources can have URI templates and support notifications/subscriptions where supported.

## 5. MCP, function calling, APIs, and RAG

10–13 min / Different jobs

These distinctions are architectural reasoning, not competing-product claims. Model function calling supplies proposed arguments; MCP supplies an interoperable capability interface and wire methods. An API remains responsible for domain behavior and access. RAG is a retrieval pattern, not the same category as a capability protocol; a server can expose retrieval. MCP alone does not select a model, guarantee agent reasoning, create a vector store, or make arbitrary software compatible without an adapter. If one fixed application needs one known API, a direct integration may be simpler.

## 6. Where would you apply MCP?

13–16 min / Choose by the integration need

Decision question: is the objective to reuse capabilities across MCP-compatible AI hosts, or just add a fixed button/API call to one application? MCP is useful for a reusable integration surface. A direct API/function can be the smaller design for a single fixed workflow. Evaluate host support, tool clarity, ownership of data, permission scope, latency and operational cost. MCPJAM demonstrates wrapping a running application; interview answers should transfer the same adapter concept to docs, services and developer tooling. Avoid broad execute-anything tools.

## 7. The call flow depends on the protocol revision

16–19 min / Do not memorize one universal handshake

Version distinction verified against the official July 2026 release notes: initialize/initialized and the Mcp-Session-Id header are retired in 2026-07-28. Metadata on requests carries version/client capabilities; server/discover is optional. Older hosts/SDKs still need their corresponding lifecycle. The class code deliberately remains on the validated v1 SDK, not a migration exercise. JSON is the data format; JSON-RPC is the request/response envelope; MCP defines capability methods and semantics for a given revision. Supported features must be checked against both host and SDK. See https://blog.modelcontextprotocol.io/posts/2026-07-28/ .

## 8. Local stdio or remote Streamable HTTP?

19–22 min / Same purpose, different deployment

Stdout must carry protocol messages only in the class stdio server. Stdio is not itself a sandbox: a launched local server executes code with its OS privileges. Streamable HTTP carries MCP over HTTP and may use SSE for streaming where the revision permits; legacy HTTP+SSE is not synonymous with the modern transport. HTTP is useful for remotely managed/shared services, but network deployment requires proper auth, per-user access, timeouts and limits. In older local HTTP profiles validate Origin against DNS rebinding and bind to loopback as appropriate. The DAW socket at 8765 is a third, application-specific connection, not either MCP transport.

## 9. Design a tool as an API contract

22–25 min / Reason about the interface

Production pattern #1: thin adapter and a narrow contract. This is a common API engineering approach, not a mandatory MCP deployment topology. Name, docstring and types describe how to call; validation and authorization enforce what is allowed. Prefer typed/structured outcomes for machine consumers; our simple write tools return strings and get_state returns a dict. Tool annotations can communicate read-only/destructive hints but are not trusted authorization rules. The class has typed input and range/allowlist checks; it does not implement caller identity or production object-level permissions. Do not move all business rules into a prompt.

## 10. An acknowledgement is not the completed effect

25–28 min / Explain asynchronous behavior

Production pattern #2: distinguish accepted, queued, completed and failed. app.py enqueues writes and immediately acknowledges them; mcp_server_sdk.py honestly says queued. get_state provides observed state after UI processing. In a production asynchronous backend, use an explicit job/operation handle and a status/read operation when needed. This is a design practice, not a built-in universal MCP job guarantee. A timeout does not prove an operation failed or was rolled back. Ask students to explain this without reading code.

## 11. The only Python excerpt to read together

28–31 min / Three lines, five responsibilities

Read the exact first three lines of set_tempo from the starter: decorator, typed signature and description. Do not require syntax memorization or hand-written JSON-RPC. Open the file once to point to the explicit validation, call_daw and queued return. All full functions and Windows/Mac commands are appendix/reference material. AI may draft code; the student must review the tool contract, scope and tests. A function decorator does not create a permission system.

## 12. Seven-minute practice: design, generate, verify

31–38 min / Apply the theory

Setup must be complete before the hour on Windows/Mac. Protect seven minutes. Student first states the name, units, valid range, side effect and proof of success. They may ask AI to generate the short function or use the provided completed solution as a guide; they are responsible for reviewing it and adding it above the main guard. Run explicit calls rather than relying on a model refusing bad input. The DAW already implements set_swing and clamps values, so only backend observation cannot prove the tool range check. If setup fails, use a prepared pair/instructor client and have the student explain the boundary. Mute is optional follow-up, not another required main-deck exercise.

## 13. Explain the failure, not just the happy path

38–40 min / Classify the layer

Interview distinction: a JSON-RPC/protocol error is different from a tools/call result indicating execution failure; HTTP transport authorization failures are another layer. In our SDK, exceptions from range/backend checks produce tool errors. The explicit SDK client prints results and exits 1 on isError. Discovery succeeds without a live backend because it does not call call_daw. Ask which layer to inspect if the tool exists but connection is refused, or if a server fails to start because stdout contains debugging. Test boundaries, invalid types, permissions in real systems, backend outage and retries of mutations.

## 14. Authentication, authorization, approval

40–43 min / Three different decisions

Production pattern #3: least privilege at every boundary. For HTTP use the authorization profile of the supported revision; validate token issuer/audience/expiry and relevant scopes through a correct implementation. Enforce per-user/per-object access in trusted server/backend code. The host may ask for confirmation for sensitive changes, but that is not an authorization bypass. Local stdio generally uses controlled process execution/environment credentials rather than adding OAuth to stdin. Our unauthenticated demo socket is explicitly not a production access-control design.

## 15. Untrusted content can redirect a model

43–46 min / Injection, poisoning and changed tools

Production pattern #4: treat returned context and metadata as untrusted and constrain the authority available even when model reasoning is manipulated. Review provenance and changes, isolate execution, require appropriate confirmations and enforce narrow backend credentials. Tool annotations are hints, not permission checks. Prompt wording alone is not a complete defense. Example is hypothetical: export_all_files is not exposed by our server. Explain the attack and the trusted enforcement point rather than promising the SDK prevents injection.

## 16. Remote tools introduce extra boundaries

46–48 min / Tokens and network destinations

Explain token passthrough: forwarding an MCP access token to an unrelated backend confuses audiences and weakens downstream accountability. Obtain/use correctly scoped downstream authorization. A proxy can become a confused deputy if it uses its broad identity on behalf of an unauthorized caller; apply per-client/user consent where the auth profile requires it and enforce tenant/object access. SSRF is relevant to tools accepting arbitrary URLs: restrict schemes/hosts, redirects and network egress, including internal/metadata endpoints. Do not expose secrets in results/logs. These network/OAuth controls are production extensions, not implemented by the music demo.

## 17. Timeouts and retries can duplicate effects

48–51 min / Think beyond a successful call

Production pattern #5 is common distributed-system engineering applied to MCP. The class adapter implements a 5-second socket timeout, a 1 MiB response bound and ok checks; it does not implement rate limiting, idempotency, durable jobs, production audit trails or tenant isolation. A timeout means the caller does not know the result, not necessarily that the backend stopped. Use backoff/bounded retries for transient safe reads; for writes use backend-supported idempotency or reconciliation/status checks. Cancellation/progress/task features are revision/capability-dependent and cancellation is not transactional rollback. In the 2026 stateless protocol, explicit application state handles allow domain state without a protocol session.

## 18. Advanced capabilities: what do they enable?

51–53 min / Know the intent and the support limits

Optional features depend on supported revision/client/server capabilities. Roots do not enforce OS permissions by themselves. Sampling lets a server request generation through the client/host; elicitation requests information through supported user flows, not an arbitrary secrets channel. Older revisions use server-to-client requests. The July 2026 revision uses multi-round-trip input-required flows for interactions such as sampling, elicitation and roots; do not assert one wire method applies everywhere. Students need the conceptual purpose in the hour; precise modern request shapes are follow-up. Resource subscriptions/list-changed caching are also revision-dependent. Structured MCP results are server data, not the same feature as a model producing schema-constrained text.

## 19. How the same design appears in production

53–55 min / Deployment map

Production pattern #6: enforce the policy at each hop rather than trusting a gateway to solve all access control. Example stack from the original material is Entra ID plus API Management, an MCP service and internal APIs; those products are examples, not mandatory components. Separate transport/session state from business state. Stateless 2026 request handling can simplify load balancing, but does not supply application idempotency, state storage or authorization. Avoid logging secrets; bound requests, isolate services and preserve tenant identity. Our local DAW retains the thin-adapter idea while omitting this production infrastructure.

## 20. Interview scenario: support copilot

55–58 min / Design before choosing libraries

Let pairs answer for one minute; ask one student for a 60-second design. Expected: identify host/client/server/backend, distinguish policy context from operational queries, expose narrow reads and a separate refund write tool, use backend-owned eligibility and limits, authenticate caller and authorize the specific order/customer, require appropriate host confirmation, validate input/output, scoped downstream credentials, prevent prompt-injected policy bypass, idempotency/reconciliation for refund retries and audit without secrets. Follow-ups: what if order text contains instructions? what if timeout occurs after refund? what if caller changes customer ID? These test reasoning, not a decorator recall exercise.

## 21. Give a clear 90-second MCP answer

58–60 min / Explain, apply, defend

Use the companion INTERVIEW_PREP.md for 20 questions, answer outlines, follow-ups and a production gap checklist. Have students give this answer to a partner and identify one validated result from their tool exercise. Interview readiness means transferable explanation and trade-offs, not memorized SDK syntax. The core deck contains one three-line Python excerpt; all full implementations/OS commands are reference-only appendix material. Do not promise passing any particular interview or production expertise in one hour.

## 22. Reference: complete set_tempo implementation

Reference only / Not required to memorize

Exact starter source. Full code is reference material; the main workshop reads only the decorator, signature and description. Point to validation, backend mapping and truthful queued acknowledgement. Interview preparation is based on reasoning about these responsibilities, not Python syntax memorization.

## 23. Reference: Windows setup and test

Reference only  /  Outside the 60-minute route

These are exact single-line commands matching README.md and workshop_client.py. Run the swing call only after adding the tool to the starter. The package directory must be named MCPJAM. Python 3.10+. requirements pins mcp[cli]==1.19.0 for FastMCP. Unix: python3 -m venv .venv; ./.venv/bin/python -m pip install -r requirements.txt; from parent ./MCPJAM/.venv/bin/python -m MCPJAM. Explicit client from package: ./.venv/bin/python workshop_client.py --tool set_swing --arguments-file swing-input.json. Set-Content creates a JSON file rather than embedding quoted JSON in native program arguments.

## 24. Reference: Mac setup before class

Reference only  /  Terminal: zsh or bash

Use the standard Python 3.13 macOS installer from python.org for a new installation. It provides universal2 binaries for Intel/Apple Silicon and native Tk. Run the matching Install Certificates.command after installation. Python 3.13 pygame wheels are available for both architectures. Existing compatible Python 3.10–3.13 with working Tk can be used instead. Do not use the Apple system interpreter or copy a Windows venv. Activation is unnecessary because commands select the interpreter explicitly. See MAC_SETUP.md for detailed troubleshooting and sources. Native Mac rehearsal is required; Windows validation does not test GUI/audio on a Mac.

## 25. Reference: explicit calls on a Mac

Reference only  /  Inside MCPJAM with the DAW running

Single quotes preserve literal JSON in zsh/bash. These calls start a fresh MCP subprocess using the client interpreter each time; no AI host is required for this explicit SDK test. Keep the DAW running in its original terminal. Client prints discovery and the result. Invalid 100 must return isError true and exit 1. Follow valid changes with get_state after the UI processes its queue. To use the completed solution add --server mcp_server_solution.py. The optional --arguments-file works on both platforms.

## 26. Reference: host configuration

Reference only  /  Host-specific example

This mcpServers layout is an example used by some desktop hosts, not a universal MCP configuration standard. Rehearse the exact host chosen for the event in advance. It launches the server; no manually launched second server is needed. Do not put secrets into slides/config committed to the repo.

## 27. Reference: Mac host configuration

Reference only  /  Host-specific JSON example

Print example JSON containing actual paths from inside the project with ./.venv/bin/python workshop_preflight.py --host-config. It uses sys.executable without resolving the Unix venv symlink and the absolute server path, so it preserves the environment and handles spaces. Adapt the mcpServers structure to the selected host. Do not use tilde expansion in host configuration. The host launches the server; it need not have a shell PATH or activated venv. The Windows equivalent uses .venv/Scripts/python.exe. The script prints only and does not edit host settings.

## 28. Reference: set_swing solution

Reference only  /  Reveal after the lab

Matches the completed solution file. Include actual tests for typical and boundary values, invalid values and backend failures. Discovery of the tool alone is not sufficient.

## 29. Reference: mute_track solution

Reference only  /  Optional extension

Tests: kick true, kick false, violin true. Read state.muted.kick after UI update. This is a guided extension, not a second required beginner implementation within the timed hour.

## 30. Reference: JSON ≠ JSON-RPC ≠ MCP

Reference only  /  Protocol envelope

This illustrates the envelope, not a payload students must manually write. The SDK handles it. Notifications have no request ID and no response. Tool execution errors can be represented as isError tool results; malformed/unsupported protocol operations use JSON-RPC error responses. mcp_server.py is an intentionally incomplete older inspection example, not the main implementation.

## 31. Reference: production security review

Reference only  /  Beyond the local demo

These are production engineering controls, not implemented by the demo. Loopback reduces network exposure but provides no caller identity. For remote servers use the authorization and transport requirements of the supported protocol revision. Treat tool annotations as untrusted hints. Preserve separate authorization to downstream services and avoid confused-deputy behavior. Gateway controls supplement, not replace, per-user backend checks.

## 32. Reference: the adapter and server startup

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

## 33. Instructor: rehearse the success path

Instructor reference  /  Preparation

Distribute platform-specific setup before class. Rehearse on native Mac hardware used by participants: Windows protocol tests do not establish Mac GUI/audio results. Run preflight and a Tk window test, then actual DAW and host calls. No MIDI hardware or soundfont is needed. The same MCP Python files serve both platforms. The supplied protocol tests use a mock DAW, not the real GUI. Protect coding time and keep advanced concepts at recognition level. Instructor uses solution, students use starter.

## 34. Sources + version scope

Reference only  /  Updated October 1, 2026

July 2026 revision — stateless request lifecycle
https://blog.modelcontextprotocol.io/posts/2026-07-28/
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