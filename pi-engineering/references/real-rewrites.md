# Verified rewrite evidence

These cases show how the method behaves. They are evidence for decisions, not recipes to copy blindly.

| Case | Initial direction | Final decision | Transferable rule |
|---|---|---|---|
| Theme selector migration | Rebuilt the component to resemble adjacent selectors, changing structure, layout, keys, and marker | Reverted; final diff changed theme plumbing and removed a duplicate border while preserving the component contract | Infrastructure migration preserves target-specific behavior |
| Tool diff rendering | UI maintained a second ~98-line diff algorithm | Deleted; rendered the structured diff already produced upstream | Presentation does not recompute domain results |
| Invalid themes | try/catch and console output scattered across UI and loader | Loader returned structured status; UI chose presentation; a valid fallback remained | Error owner and display owner are different |
| Retry | Provider-specific OpenAI/Azure retry | Moved to session/orchestration and shared across providers | Cross-provider policy belongs above adapters |
| Clear session | Cleared arrays and added abort guards | Unsubscribe → abort → await idle → reset → resubscribe | Lifecycle order beats scattered conditionals |
| Fuzzy search | External fd/find implementation, then pure standard-library rewrite | Real 55k-file measurement showed ~900 ms vs ~10 ms; returned to fd | Measurements may reverse stdlib/dependency preference |
| Editor word movement | Separate movement logic in Editor and Input | Unified visual-line and word-boundary model in Editor | Related operations share one semantic boundary model |
| Poller | 1,921 lines of DB adapters, configuration, polling, and TUI | Rejected; external wrapper called existing JSON/RPC mode | Deployment-specific orchestration stays outside a general core |
| Preview lines | CLI/env/settings value propagated through layers | One transient Ctrl+O expanded state | Transient interaction is not permanent configuration |
| Context filename typo | Proposed preserving an accidental third filename for compatibility | Removed typo; retained actual conventions | Compatibility protects real contracts, not newly found accidents |
| Truncated text | Width logic treated multiline content as one line | Defined component as single-line and stopped at newline | Define semantic contract before satisfying an assertion |
| Compaction | Saved and replayed user input to resume after compaction | Added a small `continue()` primitive for the missing semantic | Add a precise primitive instead of reconstructing old input |

## How to use these cases

When reviewing a proposal, ask:

1. Is it recomputing an upstream result?
2. Is it moving policy into a protocol adapter or core?
3. Is it turning transient UI state into permanent configuration?
4. Is it preserving an accidental behavior as a contract?
5. Is it compensating for a missing semantic by replaying data?
6. Is a small benchmark being generalized beyond realistic scale?
7. Is a reference implementation erasing target-specific behavior?

The expected answer is not always “delete code.” The clear-session fix became larger because it reduced invalid state combinations. Correct ownership takes priority over diff size.
