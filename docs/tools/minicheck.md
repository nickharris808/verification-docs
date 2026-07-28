# minicheck

**An explicit-state model checker with no required dependencies**

Describe a finite state machine, assert an invariant, get a shortest counterexample. Or a proof. Or an honest *undetermined*.

[:material-github: Source](https://github.com/nickharris808/minicheck){ .md-button }

229 tests · ~2826 lines of source · MIT

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

**Measured performance.** Declarative specs (`protocol_from_spec`, the CLI, the MCP server) run at
roughly **3.2×10⁵ to 1.0×10⁶ states/second** in CPython on an M-series laptop. The spec's guards and
assignments are compiled to index tuples once at build time rather than re-interpreted on every
visited state, which is a **measured 2.8× mean speedup** (2.06×–3.15×) over 0.2.0 across four
workloads. Verified by a differential test that requires the compiled and interpreted paths to agree
on every successor of every reachable state, so the optimisation cannot change a verdict.
Models built from a Python `transitions` callable run at roughly 1.4×10⁵–3.2×10⁵ states/second — for
those, profiling shows ~80% of the time is inside *your* callable, so the engine is not the limit. That is the honest ceiling: this is a readable reference implementation,
not a competitor to SPIN, TLC or NuSMV on industrial models.

**A soundness bug shipped in 0.1.0 and is fixed here.** `int_bound` was applied as a *clamp*, so a
counter that genuinely reached 100 saturated at 64 and a `never reach 100` invariant was reported as
holding. See [SECURITY-ADVISORY.md](https://github.com/nickharris808/minicheck/blob/main/SECURITY-ADVISORY.md).

---

Full documentation, quickstart and troubleshooting live in the [repository README](https://github.com/nickharris808/minicheck#readme).
