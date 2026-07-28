# Tutorial: from a bug to a proof

A retry loop, end to end. Every console block below is real output — you can reproduce all of it.

```console
$ pip install "minicheck @ git+https://github.com/nickharris808/minicheck.git"
```

## The claim we want to check

*A request is retried at most three times, and always finishes.*

Two claims, and they are different kinds. "At most three times" is **safety** — nothing bad happens.
"Always finishes" is **liveness** — something good eventually happens. The checker treats them
differently and this tutorial shows why that matters.

## 1. Write the machine down

Save as `retry.json`:

```json
{
  "name": "retry",
  "fields": ["tries", "done"],
  "initial": {"tries": 0, "done": 0},
  "transitions": [
    {"label": "attempt", "when": {"done": 0}, "set": {"tries": {"incr": 1}}},
    {"label": "succeed", "when": {"done": 0}, "set": {"done": 1}}
  ],
  "invariants": {"at_most_3": {"forbid": {"tries": 4}}},
  "goal": {"require": {"done": 1}}
}
```

Read it as: two fields starting at zero; while not done you may attempt (incrementing the counter) or
succeed; `tries` must never reach 4; and `done = 1` is the goal.

## 2. Check it

```console
$ minicheck check retry.json
REFUTED

  states explored   129
  exhaustive        NO
  stopped because   IntBoundExceeded: transition 'attempt' drives field 'tries' to 65, outside int_bound 64. The state space is not finite under this bound, so no exhaustive verdict is available. Re-run with int_bound >= 65.

  [REFUTED]      at_most_3 — violated in 4 steps
        0  (initial)        tries=0, done=0
        1  attempt          tries=1, done=0
        2  attempt          tries=2, done=0
        3  attempt          tries=3, done=0
        4  attempt          tries=4, done=0

  [undetermined] liveness — every reachable state can still reach the goal

  To get a definite answer, either raise --int-bound, or add a 'when' guard so
  the growing field stops. An undetermined result is not a pass.
$ echo $?
2
```

Three separate things happened, and separating them is most of the value.

**`at_most_3` is REFUTED.** The exact four steps that break it. Nothing bounds `attempt`, so it
fires forever. Notice this verdict is trustworthy *even though the search never finished* — a
counterexample is a witness that stands alone. Replay it yourself if you like.

**`exhaustive: NO`.** `tries` grows without limit, so the search stopped at the bound rather than
saturating there and reporting a proof it had not performed.

**Liveness is `undetermined`, not refuted.** Proving that *every* state can still reach the goal is
a claim about the whole space, and the whole space was not explored. So it abstains rather than
guessing. This is the difference between the two claims we started with, showing up in the output.

## 3. Fix it

Guard each attempt on the counter, so the loop is genuinely bounded:

```json
{
  "name": "retry",
  "fields": ["tries", "done"],
  "initial": {"tries": 0, "done": 0},
  "transitions": [
    {"label": "attempt1", "when": {"done": 0, "tries": 0}, "set": {"tries": {"incr": 1}}},
    {"label": "attempt2", "when": {"done": 0, "tries": 1}, "set": {"tries": {"incr": 1}}},
    {"label": "attempt3", "when": {"done": 0, "tries": 2}, "set": {"tries": {"incr": 1}}},
    {"label": "succeed",  "when": {"done": 0},             "set": {"done": 1}}
  ],
  "invariants": {"at_most_3": {"forbid": {"tries": 4}}},
  "goal": {"require": {"done": 1}}
}
```

```console
$ minicheck check retry.json
PROVED

  states explored   8
  exhaustive        yes

  [proved]       at_most_3

  [proved]       liveness — every reachable state can still reach the goal
$ echo $?
0
```

Eight states, all of them examined. That is a proof over the model, not a sample of it.

**Check the state count.** Eight is a plausible size for two fields with these guards. If a model you
expect to be complicated proves in four states, that number is telling you a transition is missing.

## 4. Look at it

```console
$ minicheck check retry.json --format mermaid
stateDiagram-v2
    %% verdict: PROVED
    [*] --> S0
    S0 : tries=0, done=0
    S1 : tries=1, done=0
    S2 : tries=0, done=1
    ...
```

Paste that into a GitHub PR or issue and it renders. When there is a counterexample its path is
highlighted and its steps are **numbered**, so the order is unambiguous.

Try it on the *broken* version and you get:

```console
$ minicheck check retry.json --format mermaid
BAD SPEC

  the reachable graph exceeds 60 states, which does not render legibly. Raise max_nodes if you
  really want it, or narrow the model — a diagram is for understanding one counterexample, not
  surveying a space.
```

Refusing rather than emitting an unreadable hairball. That pattern — decline instead of producing
something useless-but-plausible — repeats throughout.

## 5. See what liveness is really asking

Delete the `succeed` transition and re-run. `at_most_3` still holds; the retry bound is fine. But the
goal is now unreachable from everywhere, so liveness is **REFUTED** with a trap state.

The check is not "is the goal reachable from the start". It is "can *every* reachable state still
reach it". The difference shows up in models where the goal is reachable down one branch and
permanently lost down another — a plain reachability check passes those; this does not.

## 6. Put it in CI

```yaml
- uses: nickharris808/minicheck-action@v1
  with:
    specs: "specs/**/*.spec.json"
```

Exit `0` as it stands, `2` if someone removes a guard, `3` if a later edit makes the space unbounded
again. All three are the right answer, and none is a silent pass.

The Action posts a job summary with the diagram, and writes SARIF you can upload to code scanning so
a refuted invariant appears in the **Security** tab.

## 7. Write it in Python instead

The JSON format is for specs that arrive from elsewhere. For your own models:

```python
from minicheck import Model, check_safety, invariant, transition

class Retry(Model):
    tries: int = 0
    done: int = 0

    @transition(when=lambda s: s.done == 0 and s.tries < 3)
    def attempt(s):
        s.tries = s.tries + 1

    @transition(when=lambda s: s.done == 0)
    def succeed(s):
        s.done = 1

    @invariant
    def at_most_3(s):
        return s.tries < 4

check_safety(Retry.protocol())["properties"]["at_most_3"]["holds"]   # True
```

Same machine, same verdict — there is a test asserting both forms produce identical reachable sets.

## 8. Leave when you outgrow it

```console
$ minicheck check retry.json --format promela > model.pml
$ spin -a model.pml && gcc -o pan pan.c && ./pan -a
```

The export is cross-checked against SPIN in CI, so its verdict matches. `--format tla` does the same
for TLC.

## What you now know

- The three verdicts, and why `UNDETERMINED` is not a pass
- Why a counterexample is trustworthy from an unfinished search but a proof is not
- That AG-EF liveness is stronger than reachability
- How to get the verdict into CI, into a diagram, and into another checker

Next: [what "proved" actually means](../concepts/what-it-proves.md), or
[the FAQ](faq.md) if you are still sceptical.
