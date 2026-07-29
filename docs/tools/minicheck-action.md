# minicheck-action

**Model-check every spec in a repository, in CI**

Counterexamples render as diagrams in the pull request and as SARIF in the Security tab. UNDETERMINED fails the job by default.

[:material-github: Source](https://github.com/nickharris808/minicheck-action){ .md-button }

20 tests · MIT

## Use it

```yaml
- uses: nickharris808/minicheck-action@v1
```

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**What a `PROVED` run establishes.** That every reachable state of the *models you wrote* satisfies
the invariants you declared. A model abstracts; an abstraction can hide a real defect. This checks
your spec, not your implementation.

**What it does not do.** It does not extract specs from your code, it does not check liveness unless
the spec declares a `goal`, and it cannot verify anything outside `int-bound` or `max-states` —
exceeding either yields `UNDETERMINED`, never a quiet pass.

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/minicheck-action#readme).
