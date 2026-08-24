# State machines and trust boundaries

Load this reference for asynchronous agents, queues, streams, transports, sessions, terminals, plugins, tools, or destructive I/O.

## One owner

If an object has one controller, idle promise, stream flag, or mutable state record, it supports one active run unless it explicitly queues or isolates runs.

Choose one and encode it:

```text
reject concurrent run
queue concurrent run
return existing run
allocate independent per-run state
```

Never silently overwrite shared runtime fields.

Separate:

- configuration state;
- persistent/domain state;
- transient run state.

Do not allow initial configuration or public mutable getters to forge transient run state.

## Event order

Use:

```text
validate event → reduce state → publish event
```

A listener receiving an event should observe the corresponding new state. Isolate listener exceptions so observers cannot terminate the producer. Define whether asynchronous listeners are awaited, serialized, or deliberately detached.

## Terminal states

Every started lifecycle has one explicit terminal state:

```text
success(result)
error(error)
cancelled(partial result, when useful)
```

Iterator completion and final-result promises must agree. EOF, malformed frames, missing newline, cancellation, callback errors, and setup errors must settle all waiters.

Detached producers require an outer `try/catch/finally` that emits a terminal error and closes the stream.

## Cancellation

Passing a cancellation signal is not enough.

Before every new irreversible side effect:

```text
if cancelled → stop
else start side effect
```

After cancellation, do not start another tool, write, network request, subprocess, or queue acknowledgement. Clean up resources owned by that run only; an old run must not clear a newer run's controller.

## Queue termination

Define enqueue/dequeue/wakeup atomically. If messages can arrive while a consumer is running, enqueue must wake it or the API must declare that late messages belong to the next run.

Do not end based on a final non-atomic “queue empty” observation.

## Trust boundaries

Compile-time types do not validate runtime data. Validate values arriving from:

- HTTP/SSE/WebSocket;
- model tool calls;
- plugins/extensions;
- persisted sessions/configuration;
- downloaded/generated metadata.

Incremental data may be permissive for display; final data must parse and validate strictly. Validation infrastructure failure should fail closed for side effects.

## Files and terminals

For destructive files:

```text
read/check expected version → write temporary file → fsync if required → atomic rename
```

For terminals, restore raw mode, cursor, paste mode, encoding, and handlers on success, error, signal, and cancellation.

Treat external text as data, not trusted ANSI/control sequences.

## Deterministic checks

At minimum cover:

- normal terminal event;
- setup error;
- stream error and EOF without framing convenience;
- cancellation before and during a side effect;
- concurrent run;
- queue final-check race;
- listener exception;
- malformed runtime payload;
- shortened/cleared terminal output;
- Unicode grapheme and display width where relevant.

Live service tests supplement these checks; they do not replace them.
