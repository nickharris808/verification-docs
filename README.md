# verification-docs

[![deploy](https://github.com/nickharris808/verification-docs/actions/workflows/deploy.yml/badge.svg)](https://github.com/nickharris808/verification-docs/actions/workflows/deploy.yml)
[![site](https://img.shields.io/badge/site-live-brightgreen)](https://nickharris808.github.io/verification-docs/)
[![built with](https://img.shields.io/badge/built%20with-MkDocs%20Material-blue)](https://squidfunk.github.io/mkdocs-material/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The front door for a portfolio of verification tools built around one idea:
**a verdict you cannot check is not a verdict.**

**→ [nickharris808.github.io/verification-docs](https://nickharris808.github.io/verification-docs/)**

## Why this exists

Eight small repositories look like eight unrelated weekend projects. They are not: they are one
argument, made in code, that a tool should refuse rather than guess. This site is the front door
that says so once, properly — what an explicit-state check actually proves, why refuting a property
takes one witness while proving it takes the whole space, and what `exhaustive: false` really means.

Without it a visitor has to reconstruct that from eight README files. With it, the collection reads
as the single body of work it is.

## What is here

- **Concepts** — the three-valued verdict, and what "proved" actually means
- **Guides** — a tutorial from a bug to a proof, an honest comparison against TLA+/SPIN/Alloy, an
  FAQ written from real objections, architecture notes, and how to contribute
- **Tools** — one page per package, with the *Honest scope* section pulled from each repository's
  own README so the two cannot drift apart

## Quickstart — build and serve it locally

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
| [protocol-bench](https://github.com/nickharris808/protocol-bench) | fixed, reviewed ground truth where a detection must replay |
| [specforge](https://github.com/nickharris808/specforge) | a benchmark that cannot be memorised |
| [minicheck-mcp](https://github.com/nickharris808/minicheck-mcp) | the checker as an MCP server |
| [minicheck-action](https://github.com/nickharris808/minicheck-action) | model-check specs in CI |
| [protocol-bench-action](https://github.com/nickharris808/protocol-bench-action) | score a submission in CI |
| [failclosed](https://github.com/nickharris808/failclosed) | default-deny ASGI middleware |
| [polyfrac](https://github.com/nickharris808/polyfrac) | exact rational arithmetic with Sturm root counting |

**Try it in the browser** · [model-check a state machine](https://huggingface.co/spaces/nickh007/protocol-bench-demo) · [the specforge leaderboard](https://huggingface.co/spaces/nickh007/specforge-leaderboard)

**Ground-truth data** · [protocol-bench](https://huggingface.co/datasets/nickh007/protocol-bench) · [specforge](https://huggingface.co/datasets/nickh007/specforge)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Corrections to the docs are as welcome as corrections to the
code — a guide that misleads is a defect.

## Citing

Citation metadata is in [CITATION.cff](CITATION.cff).

## Licence

MIT. See [LICENSE](LICENSE).
