# verification-docs

The front door for a portfolio of verification tools built around one idea:
**a verdict you cannot check is not a verdict.**

**→ [nickharris808.github.io/verification-docs](https://nickharris808.github.io/verification-docs/)**

## What is here

- **Concepts** — the three-valued verdict, and what "proved" actually means
- **Guides** — a tutorial from a bug to a proof, an honest comparison against TLA+/SPIN/Alloy, an
  FAQ written from real objections, architecture notes, and how to contribute
- **Tools** — one page per package, with the *Honest scope* section pulled from each repository's
  own README so the two cannot drift apart

## Building locally

```console
$ pip install mkdocs mkdocs-material
$ mkdocs serve
```

`mkdocs build --strict` is what CI runs: a broken internal link fails the build rather than shipping
a dead end.

## The tools

| | |
|---|---|
| [minicheck](https://github.com/nickharris808/minicheck) | an explicit-state model checker, no required dependencies |
| [specforge](https://github.com/nickharris808/specforge) | a benchmark that cannot be memorised |
| [protocol-bench](https://github.com/nickharris808/protocol-bench) | fixed, reviewed ground truth where a detection must replay |
| [minicheck-mcp](https://github.com/nickharris808/minicheck-mcp) | the checker as an MCP server |
| [minicheck-action](https://github.com/nickharris808/minicheck-action) | model-check specs in CI |
| [failclosed](https://github.com/nickharris808/failclosed) | default-deny ASGI middleware |
| [polyfrac](https://github.com/nickharris808/polyfrac) | exact rational arithmetic with Sturm root counting |

## Licence

MIT.
