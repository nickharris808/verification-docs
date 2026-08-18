# verification-docs

[![deploy](https://github.com/nickharris808/verification-docs/actions/workflows/deploy.yml/badge.svg)](https://github.com/nickharris808/verification-docs/actions/workflows/deploy.yml)
[![site](https://img.shields.io/website?url=https%3A%2F%2Fnickharris808.github.io%2Fverification-docs%2F&label=site)](https://nickharris808.github.io/verification-docs/)
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

## Install

```console
$ pip install mkdocs mkdocs-material
```

Those two are the only dependencies, and they are needed only to build the site — reading it needs
nothing. There is no Python package here to install; this repository *is* the site.

## 30-second quickstart

```console
$ mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: site
INFO    -  Documentation built in 0.38 seconds
$ echo $?
0
$ mkdocs serve      # then open http://127.0.0.1:8000/
```

`--strict` is the part that matters, and it is what CI runs. Add one bad internal link and the build
refuses rather than shipping a dead end:

```console
$ echo '[dead](does-not-exist.md)' >> docs/index.md
$ mkdocs build --strict
WARNING -  Doc file 'index.md' contains a link 'does-not-exist.md', but the target is not found among documentation files.

Aborted with 1 warnings in strict mode!
$ echo $?
1
```

## Worked example — the tool pages cannot drift

Each page under `docs/tools/` carries the **Honest scope** section lifted from that package's own
README rather than a paraphrase of it. `build_tool_pages.py` regenerates them from local checkouts
of the sibling repositories:

```console
$ python build_tool_pages.py --repos /path/to/checkouts
```

If a repository is missing, it **fails** rather than emitting a page with a guessed number in it. If
a README has no *Honest scope* section it refuses too, with `refusing to invent one`.

The reason is the failure it prevents. A hand-written summary of what a tool does *not* prove is
exactly the text that goes stale first — the package tightens a caveat, the marketing page keeps the
old one, and the docs site becomes the most optimistic description of the work in existence. Pulling
the section from source means the site cannot be more confident than the package it describes.

The same script counts each repository's tests with `pytest --collect-only` and its source lines by
reading `src/`, so neither number quoted here is this script's guess. Both had already drifted once:
the `specforge` page claimed 38 tests and ~736 lines when the package had 77 and 741.

## Building and deploying

| Command | What it does |
|---|---|
| `mkdocs serve` | live-reloading local preview on `127.0.0.1:8000` |
| `mkdocs build --strict` | build to `site/`; **any** warning is a failure |
| `python build_tool_pages.py` | regenerate `docs/tools/*.md` from the source READMEs |

Deployment is a GitHub Actions workflow to GitHub Pages on every push to `main`. There is nothing to
run by hand.

## Honest scope

**What this repository is.** A documentation site. It builds, it link-checks under `--strict`, and it
deploys. That is the whole of what it does.

**What it is not.** It is not a verification tool and it establishes nothing about any protocol,
program or model. Every claim on the site is a claim *about* one of the eight packages, and the
authority for any of them is that package's own README and test suite — not this site. Where the two
disagree, the package is right and this is a bug.

**What `--strict` catches, and what it does not.** It catches a link to a page that is not in the
documentation tree. It does **not** check external links, so a URL to a repository or a Hugging Face
Space can rot without turning the build red. It also cannot tell you a sentence has become false; a
prose claim that drifts away from the code stays green. The generated tool pages exist to shrink that
surface, not to eliminate it.

**On the comparison against TLA+, SPIN, Alloy and CBMC.** It is written from public documentation and
from experience with those tools, not from a benchmark run under controlled conditions. Read it as an
argued position that says where `minicheck` loses, not as a measurement.

## Troubleshooting

**`mkdocs: command not found`.** `pip install mkdocs mkdocs-material`. Note that `mkdocs-material` is
the theme; the config will not load without it.

**The build aborts with `Aborted with N warnings in strict mode!`.** That is `--strict` working. The
`WARNING` lines above it name each file and the link or reference that failed. Fix them; do not drop
`--strict`, which is the only reason a dead link is visible at all.

**A theme option is rejected after an upgrade.** `mkdocs-material` moves quickly and Material for
MkDocs has warned that MkDocs 2.0 will break all plugins and theme overrides with no migration path.
Pin both versions if you need a reproducible build.

**Edits to a tool page vanish.** `docs/tools/*.md` are **generated** by `build_tool_pages.py` from the
package READMEs. Edit the package README and regenerate; an edit made here is overwritten by design.

**A link to a sibling repository 404s.** External links are not checked by `--strict`. Report it —
that is a real defect on this site, just an invisible one.

**The published site is behind `main`.** Deployment is a workflow run; check the
[deploy workflow](https://github.com/nickharris808/verification-docs/actions/workflows/deploy.yml)
before assuming the content is wrong.

## FAQ

**"Why does a set of small tools need a documentation site?"**
Because eight small repositories look like eight unrelated weekend projects, and they are not — they
are one argument, made in code, that a tool should refuse rather than guess. Without a front door a
visitor has to reconstruct that from eight README files.

**"Isn't this just the READMEs again?"**
The tool pages are, deliberately, and the *Honest scope* sections are pulled from source rather than
rewritten so the two cannot drift. What is only here is the connective material: what an
explicit-state check actually proves, why refuting a property takes one witness while proving it
takes the whole space, and the comparison against TLA+/SPIN/Alloy/CBMC.

**"Which page should I read first?"**
[The three-valued verdict](https://nickharris808.github.io/verification-docs/concepts/verdicts/) if
you want the idea, [the tutorial](https://nickharris808.github.io/verification-docs/guides/tutorial/)
if you want to use something, and
[the FAQ](https://nickharris808.github.io/verification-docs/guides/faq/) if you are sceptical — it is
written from real objections and says "you are right" where that is the honest answer.

**"Are these packages on PyPI?"**
Four of six: `minicheck`, `protocol-bench`, `failclosed` and `polyfrac` install with a plain
`pip install <name>`. `minicheck-mcp` is not on the index yet and its README gives a `git+` URL.
`specforge` is the complication worth knowing: that name on PyPI belongs to an unrelated project
(SGLang's SpecForge), so `pip install specforge` does not fail — it succeeds and installs the wrong
thing. Use the `git+` URL its README gives, and which its test suite re-checks against PyPI on every
run.

**"Can I contribute a correction?"**
Yes, and a correction to the docs is as welcome as a correction to the code — a guide that misleads
is a defect. See [CONTRIBUTING.md](CONTRIBUTING.md).

**"Is any of this peer-reviewed?"**
No. It is a working portfolio with tests and public advisories for the defects found in it, which is
a different and lesser thing than review. The comparison page and the FAQ are argued positions;
treat them as such.

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
