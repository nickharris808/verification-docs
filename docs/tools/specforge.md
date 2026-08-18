# specforge

**A benchmark that cannot be memorised**

Generates protocol-shaped verification tasks whose ground truth is computed by an exhaustive checker rather than written down. Change the seed and nothing has seen the task set.

[:material-github: Source](https://github.com/nickharris808/specforge){ .md-button }
[:material-database: Dataset](https://huggingface.co/datasets/nickh007/specforge){ .md-button }
[:material-trophy: Leaderboard](https://huggingface.co/spaces/nickh007/specforge-leaderboard){ .md-button }

77 tests · ~741 lines of source · MIT

## Install

```console
$ pip install "pcar-specforge @ git+https://github.com/nickharris808/specforge.git"
```

!!! warning "Do not run `pip install specforge`"
    The name `specforge` on PyPI belongs to somebody else — it is [SGLang's SpecForge](https://github.com/sgl-project/SpecForge), an unrelated
    project. `pip install specforge` **does not fail**: it succeeds and installs that project instead of
    this one. Always install from GitHub with the quoted URL above, until this package is released
    under a name of its own.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**What a score measures.** How well a solver finds and *demonstrates* safety violations in synthetic
finite state machines, at a given size.

**What it does not measure.**

- Nothing about real-world protocol implementations. The shapes are drawn from how protocols are
  built; the machines are synthetic and deliberately so.
- Nothing about specification reading. The model is given; inferring one from prose is a harder and
  different problem.
- Nothing comparable across seeds or difficulties without saying which you used.

**What it deliberately does not do.** It makes no claim about any named third-party protocol,
product or implementation. Judgements about named systems belong in a corpus a human has reviewed —
not in one a generator emits. If you want ground-truth tasks drawn from published standards, that is
[`protocol-bench`](https://github.com/nickharris808/protocol-bench), which is fixed, small, and
reviewed.

**`bfs` is the ceiling, not a competitor.** It is sound and complete over a model already formalised
for it. The open problem is doing this from a description.

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/specforge#readme).
