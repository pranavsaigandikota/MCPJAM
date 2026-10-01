# MCP interview preparation: explain the design

Use this alongside the introductory workshop. Practise answers aloud, using
MCPJAM as evidence and a second application to show transfer. You should be
able to reason about the interface without reciting Python syntax. These are
foundational and system-design topics; interview depth depends on the role.

## Version scope comes first

The exercise pins the official Python SDK to **1.19.0** and uses its older
`initialize`/`initialized` lifecycle. Do not describe that as universal current
MCP behavior. The **2026-07-28** revision removes that exchange and the protocol
session header; requests carry metadata and discovery of server capabilities
can use optional `server/discover`. Application state can still exist using
explicit handles. Interaction mechanics for sampling, elicitation and roots
also changed to multi-round-trip flows. State which revision your host and SDK
support before giving wire-level details. [Official release notes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

## Twenty questions to practise

### 1. What is MCP, and what is an MCP server?

MCP standardizes how an AI application accesses server-provided capabilities.
A server is a program exposing a focused interface to software/data; it need
not contain an LLM. Separate the capability interface, message envelope,
transport, and actual business operation. Example: our server exposes a tempo
tool and adapts it to the music app. [Architecture](https://modelcontextprotocol.io/specification/2025-11-25/architecture)

**Follow-up:** Could the same server wrap a database or ordinary REST API?
Yes; the adapter changes, and access controls must still be enforced.

### 2. Distinguish host, client, server, and backend.

The host owns AI interaction, context and connection/consent policy. A client
handles the protocol relationship with a server. A server exposes capabilities
and maps requests to a backend. A remote server may serve many callers; the
logical client/server relationship does not mean a server supports one user.
The host coordinates multiple connections. [Architecture](https://modelcontextprotocol.io/specification/2025-11-25/architecture)

**Evidence:** AI host → client → `mcp_server_sdk.py` → `app.py`.

### 3. Tools, resources, prompts: how do you choose?

A tool is a callable operation, including reads. A resource exposes context
that the application can select/read. A prompt exposes reusable messages for
a user-selected task. Choose by interaction semantics: order lookup as a
bounded read tool; policy documents as resources; a support workflow template
as a prompt. Host interfaces vary. [Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools),
[Resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources),
[Prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)

**Trap:** A read-only function is not automatically a resource.

### 4. Is MCP the same as model function calling?

No. Function calling is the model-facing mechanism for proposing an operation
and arguments. MCP standardizes the integration interface through which a host
discovers and invokes capabilities. The host can combine them: discover tools,
make relevant definitions available to a model, then route an approved call.
This is an architectural comparison, not a claim that every host works alike.

### 5. Does MCP replace an API or RAG?

An existing API still supplies business behavior; an MCP adapter can wrap it.
RAG is a retrieval pattern supplying relevant context to a model. MCP can expose
retrieval, but does not itself create a vector store or guarantee good answers.
Explain the layer and how the approaches compose.

### 6. When is MCP useful, and when would you avoid it?

Use it when a discoverable capability interface can be reused by compatible AI
hosts: internal knowledge, approved business operations, or developer tools.
For one fixed application calling one known API, a direct integration may be
simpler. Discuss host support, permissions, maintenance, latency and ownership.
Do not claim that every application needs MCP.

### 7. JSON, JSON-RPC, and MCP: what does each contribute?

JSON encodes data. JSON-RPC supplies request/response/error/notification
envelopes and correlation IDs. MCP defines capability methods and behavior for
a revision. A notification is not an ordinary request expecting an ID-matched
response. The SDK handles these mechanics in the workshop.
[Base protocol](https://modelcontextprotocol.io/specification/2025-11-25/basic)

### 8. What happens when a host discovers and calls a tool?

Specify the revision first. In our older SDK: initialize, signal readiness,
list tools, then call the selected name with arguments and receive a result.
In 2026-07-28, requests carry capabilities/version metadata, optional discovery
can precede use, and the old handshake is retired. Tool discovery describes
the callable interface; it does not prove the backend is reachable.
[2026 changes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

### 9. Why stdio versus Streamable HTTP?

Stdio is a subprocess connection using input/output pipes; reserve stdout for
protocol messages and log to stderr. Streamable HTTP supports a separately
managed network service; assess authentication, access, limits and deployment.
SSE can be a streaming mechanism, so distinguish it from the deprecated legacy
HTTP+SSE transport. A local process is not automatically a sandbox.
[Versioned transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)

**Evidence:** MCP uses stdio here; port 8765 is the separate DAW backend socket.

### 10. What makes a good tool contract?

Give a clear name, purpose, input types/units, domain constraints, known side
effects and truthful results. Prefer structured outputs for machine consumers
when appropriate. Keep the adapter narrow and reuse backend rules. Types and
descriptions help calling; they do not replace domain checks or authorization.
Annotations such as read-only/destructive hints are not permission controls.
[Tool interfaces and results](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

### 11. How would you distinguish validation, authorization, and approval?

Validation checks argument shape/domain rules. Authentication establishes a
caller identity. Authorization checks the action and particular object/data
scope. Host approval asks whether to proceed under user policy. A confirmed
action must still be authorized. Token scope alone may not establish access
to a particular order or tenant. [Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)

### 12. How would you secure an MCP server wrapping another API?

Validate the MCP caller's token for the intended audience and supported auth
profile. Apply per-user/tool/object scope. Use correctly authorized downstream
credentials, rather than forwarding an MCP token to an unrelated service.
Avoid confused-deputy behavior: your server's broad access must not become the
caller's unrestricted access. Apply per-client consent in the relevant proxy
flows. [Security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)

### 13. Explain prompt injection, tool poisoning, and a rug pull.

Untrusted retrieved content can try to redirect model behavior. Tool metadata
can itself carry hostile instructions. A reviewed server may later change its
metadata/code. Defend with narrow trusted permissions, provenance/update review,
isolation, appropriate consent and data boundaries. A helpful system prompt or
an SDK does not provide all those controls. [Security context](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)

**Follow-up:** A document says to export all files. Which trusted layer blocks it?

### 14. What changes if a tool accepts an arbitrary URL or file path?

The input may access an unintended internal service or escape an allowed path.
Constrain destinations/schemes, redirects and network egress; validate file
paths and use OS/service permissions. Roots communicate relevant locations;
they do not by themselves create an OS sandbox. Enforce the boundary in code
and infrastructure. [SSRF guidance](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices),
[Roots](https://modelcontextprotocol.io/specification/2025-11-25/client/roots)

### 15. How do protocol errors differ from execution errors?

A malformed or unsupported protocol operation is a protocol-layer error. A
valid tool call can return an execution failure, such as invalid business
input or backend outage. HTTP auth/transport failures add another layer. The
client should report the actual failure, not a made-up successful effect.
[Tool errors](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

**Evidence:** Our client checks `isError`; missing backend and rejected swing
produce failures even though the tools can be discovered.

### 16. Can a timeout be retried safely?

Not automatically. A timeout may leave the result unknown after a write already
occurred. Assess the backend operation: bounded read retries may be appropriate;
writes may need an idempotency key, status check or reconciliation. Backoff,
limits and monitoring are distributed-system design choices applied to MCP,
not a blanket protocol guarantee. Cancellation does not imply rollback.

**Scenario:** A refund timed out after being applied. How do you avoid a second refund?

### 17. How do you report queued or long-running work?

Distinguish accepted from completed. Return a truthful acknowledgement; where
needed, an explicit operation handle plus a status/read action allows later
verification. Task/progress features depend on supported protocol/SDK features.
In the 2026 stateless protocol, application state can remain in explicit
handles without a protocol session. [Current state model](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

**Evidence:** Our backend queues writes; `get_state` verifies the eventual effect.

### 18. What are sampling, elicitation, and roots for?

Sampling enables model work requested through the host/client. Elicitation
requests user input through supported flows. Roots describe relevant locations.
Use host policy, consent and capability checks. Older revisions use
server-to-client requests; 2026-07-28 uses multi-round-trip interaction mechanics.
Do not confuse the feature's purpose with one version's wire method.
[Sampling](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling),
[Elicitation](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation),
[2026 interaction changes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

### 19. How would you operate and scale this in production?

Describe TLS and appropriate identity for remote access, per-user/object checks,
bounded work, scoped backend credentials, safe retries, isolation and audit
without secrets. A gateway can add network controls, not replace backend
authorization. Keep application state and idempotency explicit where necessary.
The chosen revision changes protocol state/caching/routing considerations.
These are design choices to evaluate, not a requirement that every server use
the same cloud products. [Current revision](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

### 20. Design a customer-support MCP integration.

Map host → client → server → backend. Expose policy context as a resource;
scoped order lookup as a read tool; refund as a separate narrow write tool.
Authorize the specific order/customer and enforce eligibility in the backend.
Use appropriate consent, downstream access, injection-resistant authority
boundaries, idempotency/reconciliation and truthful outcomes. State what you
would log, test and limit. Explain why MCP is useful compared with direct APIs.

**Follow-ups:** What if order text is hostile? The customer ID is changed?
Refund times out? A tool update adds new side effects? A new host lacks a feature?

## Six production patterns to remember

These are engineering patterns; distinguish them from normative MCP requirements.

| Pattern | Remember | What MCPJAM implements | What production still needs |
| --- | --- | --- | --- |
| 1. Thin adapter, narrow contract | Describe and constrain one capability. | Typed tools, domain checks, backend mapping. | Per-caller/object authorization; structured contracts where appropriate. |
| 2. Truthful outcomes | Accepted is not completed. | Queued messages; state readback. | Durable operation/status model if required. |
| 3. Least privilege | Authorize caller, action and object. | Limited exposed tool set; loopback binding. | Caller identity, scoped accounts, tenant checks and sensitive approvals. |
| 4. Trust boundaries | Untrusted data must not gain authority. | No generic shell/export tool. | Review updates/provenance; isolate code; enforce permitted actions. |
| 5. Reliable operations | Bound work; retry by side effect. | 5-second socket timeout, 1 MiB response limit, acknowledgement checks. | Rate/concurrency bounds, idempotency, safe retry policy and audit. |
| 6. Defense at every hop | Gateway controls supplement server/backend rules. | Separate server and backend processes. | Identity/network/service controls appropriate to deployment. |

## What code must you know?

Recognize the decorator, typed signature and description. Explain validation,
backend mapping and a truthful result. Full implementations, host JSON,
platform commands and manual protocol examples are reference material. AI may
generate the exercise function; you still review its contract, permission
scope, side effects and tests. Writing every line from memory is not the goal.

## A 90-second answer structure

1. Define the standard and server's responsibility.
2. Map host, client, server and backend.
3. Choose primitives and transport for a concrete use case.
4. State revision/feature assumptions and define the tool contract.
5. Explain trusted permissions, failure behavior and verification.

For self-assessment, answer without notes, handle two follow-ups, and justify a
trade-off. If you can only repeat a definition, practise the scenario again.
