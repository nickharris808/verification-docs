# How this compares

Where `minicheck` wins, where it loses, and how to leave when you outgrow it. Being straightforward
about the losses is the most useful thing a small tool can do.

## At a glance

| | minicheck | TLA+ / TLC | SPIN | Alloy |
|---|---|---|---|---|
| Language | Python object or JSON | TLA+ | Promela | Alloy |
| Install | `pip install` | JVM + toolbox | `spin` + a C compiler | JVM + IDE |
| Runs in your test suite | **yes** | no | no | no |
| Realistic state ceiling | ~10⁵–10⁶ | 10⁸+ | 10⁹+ with bitstate | bounded scope |
| Partial-order reduction | no | no | **yes** | n/a |
| Symmetry reduction | no | **yes** | no | n/a |
| Temporal logic | AG-EF only | **full TLA+** | **LTL** | first-order relational |
| Refinement / theorem proving | limited | **TLAPS** | no | no |
| Reads the whole engine in an afternoon | **yes** | no | no | no |
| Says *undetermined* | **yes** | no | no | no |

## When to use minicheck

- The invariant you would otherwise not check at all, because adopting a toolchain is not worth it
  for this one.
- Inside CI, as a test, with a real exit code.
- When you want a counterexample in a PR comment as a diagram rather than in a separate tool.
- When an agent needs a decision procedure it can call.
- When you want to read the checker before trusting it.

## When to use something else

- **Over ~10⁶ states.** Use SPIN. Partial-order reduction and bitstate hashing are not features
  minicheck can plausibly add.
- **You need real temporal logic.** AG-EF is one CTL fragment. If you need LTL, use SPIN; if you
  need the full TLA+ apparatus, use TLC.
- **You need refinement proofs or theorem proving.** TLAPS.
- **Your problem is relational structure rather than reachability.** Alloy.
- **Unbounded parameterised verification** — "for all N processes". minicheck checks a fixed N.

## Leaving is supported

```console
$ minicheck check spec.json --format promela > model.pml
$ spin -a model.pml && gcc -o pan pan.c && ./pan -a
```

```console
$ minicheck check spec.json --format tla > Model.tla
```

The exports are **cross-checked, not merely generated**: the test suite runs SPIN on the exported
model and requires its verdict to match minicheck's, on models where the answer is known both ways.
CI installs SPIN so this runs rather than skipping.

Non-integer fields are **refused** rather than mapped onto integers, because a silent encoding would
give you counterexamples that do not correspond to yours.

## The one thing minicheck does that the others do not

It distinguishes "I proved this" from "I did not finish looking".

TLC, SPIN and Alloy all report a completed run or an error. None of them has a first-class verdict
for *the search was truncated and therefore nothing was established* that propagates all the way
through to an exit code, a SARIF `kind`, and a CI job result.

That is not a criticism of them — they are used by people who read the state-count output and know
what it means. It matters here because these tools are also meant to be called by CI and by agents,
which do not read output, and for which a missing third value becomes a silent pass.
