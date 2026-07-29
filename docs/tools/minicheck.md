# minicheck

**An explicit-state model checker you can read in an afternoon**

Describe a finite state machine, assert an invariant, get back the shortest concrete trace that breaks it. No required dependencies.

[:material-github: Source](https://github.com/nickharris808/minicheck){ .md-button }

270 tests · ~2888 lines of source · MIT

## Install

```console
$ pip install "minicheck @ git+https://github.com/nickharris808/minicheck.git"
```

!!! note
    `pip install minicheck` does not work yet — nothing here is on PyPI. Install from GitHub.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**Verdicts are three-valued, and the third value is the important one.**

| verdict | means | what it took to earn |
|---|---|---|
| `holds: true` | proved | the *entire* reachable space was enumerated and nothing violated the invariant |
| `holds: false` | refuted | one violating state was reached; the attached trace replays |
| `holds: None` | **undetermined** | the search stopped early. Not a pass. |

The asymmetry is deliberate. Refuting a safety property needs one witness, so `false` is sound even
from a partial search. Proving one is a claim about every reachable state, so `true` is only issued
when `exhaustive` is also true. **Never treat `None` as success** — check `exhaustive` and
`incomplete_reason`, which say exactly what stopped the sweep.

**What it proves.** That a finite, explicitly-enumerated model does or does not satisfy an invariant,
over every interleaving. Counterexamples are shortest by construction, because the search is
breadth-first.

**What it does not prove.**

- Nothing about your *implementation*. It checks the model you wrote, and a model abstracts. An
  abstraction can hide a real defect.
- Nothing beyond the bound. The sweep caps at 200,000 states by default and integer fields at
  `int_bound`. Exceeding either downgrades unrefuted invariants to `None` rather than truncating
  silently — but it still means those states were not examined.
- Nothing about liveness under fairness assumptions beyond the AG-EF check, and nothing in LTL.
  There is no partial-order reduction, no symmetry reduction, and no CTL\* fragment beyond AG-EF.
- Nothing when an invariant is trivially satisfied. `spec_warnings` reports a condition that names a
  value the bounded space cannot represent; such a condition genuinely holds, but it verifies nothing.

**Measured performance — run `python bench.py` to reproduce all of it on your own machine.**
Declarative specs (`protocol_from_spec`, the CLI, the MCP server) run at roughly **2.5×10⁵ to 7.5×10⁵
states/second** in CPython 3.11 on an M-series laptop — the spread is across workload shapes, and it
moves by ±15% between runs on the same machine, so treat it as an order of magnitude rather than a
figure.

The spec's guards and assignments are compiled to index tuples once at build time rather than
re-interpreted on every visited state. `bench.py` measures that against the *pre-optimisation*
transition function, which it re-implements inline — so the comparison needs nothing but this
repository, and the baseline is the same oracle `tests/test_adversarial_soundness.py` uses to prove
the two agree on every successor of every reachable state. The optimisation therefore cannot change
a verdict. On the reference machine the mean is **4.7×** (range 2.7×–6.6×); the guarantee the test
suite enforces is the floor, **never below 2× on any benchmarked workload**.

Models built from a Python `transitions` callable are bounded by *your* function, not by the engine —
profiling puts ~80% of the time inside it. `bench.py`'s deliberately trivial callable reaches
~2×10⁶ states/second, which is the ceiling you approach as the callable gets cheaper, not a figure to
expect from a real one. That is the honest ceiling overall: this is a readable reference
implementation, not a competitor to SPIN, TLC or NuSMV on industrial models.

**A soundness bug shipped in 0.1.0 and is fixed here.** `int_bound` was applied as a *clamp*, so a
counter that genuinely reached 100 saturated at 64 and a `never reach 100` invariant was reported as
holding. See [SECURITY-ADVISORY.md](https://github.com/nickharris808/minicheck/blob/main/SECURITY-ADVISORY.md).

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/minicheck#readme).
