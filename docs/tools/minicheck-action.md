# minicheck-action

**Model-check specs in CI**

Checks every spec in a repo, posts the counterexample as a diagram, uploads SARIF. UNDETERMINED fails the job.

[:material-github: Source](https://github.com/nickharris808/minicheck-action){ .md-button }

20 tests · MIT

## Install

```console
$ pip install "minicheck-action @ git+https://github.com/nickharris808/minicheck-action.git"
```

!!! note
    `pip install minicheck-action` does not work yet — nothing here is on PyPI. Install from GitHub.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**What a `PROVED` run establishes.** That every reachable state of the *models you wrote* satisfies
the invariants you declared. A model abstracts; an abstraction can hide a real defect. This checks
your spec, not your implementation.

**What it does not do.** It does not extract specs from your code, it does not check liveness unless
the spec declares a `goal`, and it cannot verify anything outside `int-bound` or `max-states` —
exceeding either yields `UNDETERMINED`, never a quiet pass.

---

Full documentation, quickstart and troubleshooting live in the [repository README](https://github.com/nickharris808/minicheck-action#readme).
