# minicheck-mcp

**The checker as an MCP server**

Gives an agent a decision procedure instead of prose reasoning. Specs are data, never code.

[:material-github: Source](https://github.com/nickharris808/minicheck-mcp){ .md-button }

96 tests · ~437 lines of source · MIT

## Install

```console
$ pip install "minicheck-mcp @ git+https://github.com/nickharris808/minicheck-mcp.git"
```

!!! note
    `pip install minicheck-mcp` does not work yet — nothing here is on PyPI. Install from GitHub.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**Read the verdict as three-valued.** This is the part that matters most for an agent, because an
agent reads a field and acts on it rather than bringing judgement to a paragraph.

| `all_hold` | `verdict` | meaning |
|---|---|---|
| `true` | `PROVED` | every reachable state was enumerated; nothing violated the invariant |
| `false` | `REFUTED` | a counterexample is attached and it replays against your spec |
| `null` | `UNDETERMINED` | the search did not finish. **Not a pass.** |
| `null` | `ERROR` | with `ok: false` — no verdict was produced at all |

Every response also carries `verdict_means`, a one-line explanation an agent can quote to a user
verbatim rather than paraphrasing (and possibly softening) it.

Every response carries `all_hold` and `holds` explicitly, including errors. An earlier version
omitted them on failure, so `result.get("all_hold")` returned `None` for a crash and for a genuine
undetermined result alike — and both are falsy, exactly like a refutation.

When `exhaustive` is `false`, the response also carries `incomplete_reason` and `advice` naming what
to change. A `warnings` array appears when an invariant is trivially satisfied — it genuinely holds,
but verifies nothing.

**What it proves.** That a finite declarative state machine does or does not satisfy an invariant
over every interleaving, within the declared bounds.

**What it does not prove.**

- Nothing about your implementation — only about the spec you sent. A spec abstracts.
- Nothing outside `int_bound` (default 64) or the 200,000-state cap. Exceeding either yields
  `UNDETERMINED`, never a silent pass.
- Nothing about liveness beyond AG-EF, and nothing in LTL.

**Nothing in a spec is ever executed.** A spec is data: field names, literals, and comparisons. There
is no `eval`, no `exec`, and no code path that turns a string in a spec into a callable. That is why
the declarative loader exists rather than accepting Python.

---

Full documentation, quickstart and troubleshooting live in the [repository README](https://github.com/nickharris808/minicheck-mcp#readme).
