# protocol-bench-action

**Enforce a benchmark claim in CI, by replay**

Scores a submission on every push and fails the build if a claimed detection cannot be demonstrated. The gate cannot be passed by guessing.

[:material-github: Source](https://github.com/nickharris808/protocol-bench-action){ .md-button }

MIT

## Use it

```yaml
- uses: nickharris808/protocol-bench-action@v1
```

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**What a passing run establishes.** That the submission you gave it scored at or above your declared
thresholds on the fifteen tasks in `protocol-bench`, and that every counterexample it claimed was
replayed against the model it claims to break — starting at the initial state, moving only along real
transitions, ending in a genuinely violating state.

**What it does not establish.**

- Nothing about protocols beyond the fifteen in the task set. Fifteen tasks with two violated is a
  small sample: a single task flipping moves balanced accuracy by 0.25, which is why the score should
  always be reported with the task set version rather than on its own.
- Nothing about any implementation. The tasks are models of published *procedures*; a model
  abstracts, and an abstraction can hide a real defect.
- Nothing about a submission's reasoning. A replaying trace shows the counterexample is real, not
  that it was derived rather than recalled — that is what the `spec` mode and
  [`specforge`](https://github.com/nickharris808/specforge) exist to probe.
- Nothing when a threshold is loosened. `min-balanced-accuracy: "0"` makes the gate vacuous; the
  defaults are strict on purpose.

**A failed replay is scored as no detection, never as an error.** A claim that cannot be
demonstrated earns nothing, which is the same rule the rest of the portfolio applies.

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/protocol-bench-action#readme).
