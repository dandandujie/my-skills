# Review checklist

Use the relevant sections; do not produce a ceremonial checklist dump in the final response.

## Need and scope

- Is every changed behavior requested or required by the root cause?
- Did the change touch unrelated names, formatting, UI, text, generated files, or public contracts?
- Does the target have behavior that an adjacent reference does not?

## Ownership

- Which layer owns the policy, state, calculation, display, and error?
- Is the same result computed in two layers?
- Would moving the fix to a shared owner remove sibling patches?
- Is deployment-specific orchestration entering a general core?

## Code shape

- Does a class have one implementation?
- Is an interface a real boundary or decorative indirection?
- Is a registry static and small enough for exhaustive dispatch?
- Is a helper called once and hiding the main data flow?
- Is a long function cohesive despite its length?
- Could two clear passes replace one clever reducer?

## State and lifecycle

- Is there one owner per mutable runtime state?
- Can concurrent calls overwrite a controller, promise, or status?
- Does state update before event publication?
- Are starts and ends paired on setup error, stream error, and cancellation?
- Can EOF leave a result promise unresolved?
- Can observers break producers?
- Can cancellation still start another side effect?
- Can queue work arrive during the final-empty check?

## Boundaries and safety

- Are network, model, plugin, config, and persisted values runtime-validated?
- Does validation fail closed before side effects?
- Are destructive writes atomic where needed?
- Are downloaded executables pinned and verified?
- Is untrusted text separated from terminal/HTML/control syntax?
- Are Unicode storage and display coordinate systems explicit?

## Configuration and dependencies

- Is this setting actually transient interaction state?
- Does the repository already have a helper or dependency?
- Does a standard/platform primitive solve the real semantics?
- Is the dependency benefit measured on realistic data?
- Is every direct import declared by the importing package?

## Tests and claims

- Is non-trivial logic covered by one deterministic check at minimum?
- Are protocol events tested without external keys?
- Was the real hot path tested at realistic scale?
- Were full root checks run without truncated output?
- Does the completion report separate verified and unverified claims?

## Review output

Rank findings by correctness and ownership impact. For each finding provide:

```text
location → violated invariant/duplicate mechanism → smallest correct owner/fix
```

Do not demand abstractions merely to make code “cleaner.”
