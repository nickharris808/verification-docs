# The three-valued verdict

Most verification tools answer a yes/no question with a yes/no answer. That is the mistake this
whole portfolio is organised around avoiding.

## Why two values is not enough

A checker can end a run in three genuinely different situations:

1. It examined every reachable state and found no violation.
2. It found a violating state, and can show you how to reach it.
3. It ran out of room — memory, time, an integer bound — before doing either.

The third is not a rare edge case. It is what happens on any model large enough to be interesting.
And if you only have two output values, the third case has to be squeezed into one of them.

Squeezing it into "fails" makes the tool useless: every real model would fail. So in practice tools
squeeze it into "passes" — and now the tool reports success for a search that established nothing.

That is not a hypothetical. **It is the defect that shipped in version 0.1.0 of `minicheck`**, and
it is documented in the [security advisory](https://github.com/nickharris808/minicheck/blob/main/SECURITY-ADVISORY.md).
An integer field was clamped at its bound instead of raising, so a counter that genuinely reaches
100 stopped at 64, the forbidden state was never generated, and `never reach 100` was reported as
**holding**. Every part of that behaved reasonably in isolation.

## The three values

```python
from minicheck.verdict import Verdict

Verdict.PROVED        # every reachable state was enumerated; the property held in all of them
Verdict.REFUTED       # a counterexample exists; it is attached and it replays
Verdict.UNDETERMINED  # the analysis did not finish, so nothing was established
Verdict.ERROR         # no analysis ran at all
```

`ERROR` is separate from `UNDETERMINED` on purpose. "I looked and could not tell" and "I never got
as far as looking" are different situations, and collapsing them hides which one you are in.

## The asymmetry that makes it work

Here is the part worth internalising, because everything else follows from it.

**Refuting needs one witness. Proving needs the whole space.**

A counterexample is a finite object you can hand to a sceptic. They replay it against the model —
does it start at the initial state, is every step a real transition, does the last state actually
violate the property — and they either agree or they do not. **Whether the search that produced it
ran to completion is irrelevant.** The witness stands alone.

A proof of safety is a claim about *every* reachable state. There is no finite object to hand over;
the evidence is the exhaustiveness of the search itself. So if the search stopped early, there is no
proof, no matter how many states it did examine.

In code:

```python
from minicheck.verdict import from_holds

from_holds(False, exhaustive=False)  # REFUTED — a witness stands without exhaustiveness
from_holds(True,  exhaustive=False)  # UNDETERMINED — downgraded, not trusted
```

That second line is load-bearing. A caller claiming "it holds" while also reporting "I did not look
everywhere" is contradicting itself, and the contract resolves it against the optimistic reading.

The practical payoff: `check_safety` still returns **real counterexamples from searches that never
finished**. The fix for the clamp bug did not cost you the ability to find bugs in models too big to
enumerate — because finding a bug never needed exhaustiveness in the first place.

## Aggregation never rounds up

Combining verdicts follows one precedence:

```
ERROR  >  REFUTED  >  UNDETERMINED  >  PROVED
```

```python
from minicheck.verdict import Verdict, combine

combine([Verdict.PROVED, Verdict.UNDETERMINED])   # UNDETERMINED
combine([Verdict.UNDETERMINED, Verdict.REFUTED])  # REFUTED
combine([])                                       # UNDETERMINED, not PROVED
```

One undetermined spec among ninety-nine proved ones makes the run undetermined. And combining
*nothing* is `UNDETERMINED`, not `PROVED` — a run that checked nothing has proved nothing, and that
is the purest form of the failure this exists to prevent.

## How it survives contact with two-valued systems

The awkward part is that the systems you report into mostly have two values. Each mapping is chosen
so that `UNDETERMINED` cannot be mistaken for success:

| Destination | PROVED | REFUTED | UNDETERMINED |
|---|---|---|---|
| CLI exit code | `0` | `2` | **`3`** |
| SARIF | `kind: pass` | `level: error, kind: fail` | `kind: informational` — never `pass` |
| JUnit | passing case | `<failure>` | **`<error>`** |
| GitHub Action | job passes | job fails | **job fails** by default |
| Python API | `holds: True` | `holds: False` | `holds: None` |

The JUnit choice is the one that took thought. `<skipped>` looks like the natural home for "we did
not determine this" — and it is exactly wrong, because **every CI dashboard renders a skipped test
green**. Using it would have quietly reintroduced the original defect through a reporting format.
`UNDETERMINED` is `<error>`, and the emitted XML carries `skipped="0"`.

## Opting out, deliberately

Sometimes you genuinely want to accept an unestablished result — a model you know is too big, in a
pipeline where you want the refutations but not the strictness.

```console
$ minicheck check big.json --allow-undetermined
```

Two properties of that flag matter:

- It **widens only the undetermined case**. A refutation still fails. A flag meaning "I accept not
  knowing" must not also mean "I accept known-broken", and there is a test named for exactly that.
- It is **explicit**. The default is strict, so accepting an unproven result is a decision you made
  rather than one made quietly for you.

## Defined once

This contract lives in [`minicheck/verdict.py`](https://github.com/nickharris808/minicheck/blob/main/src/minicheck/verdict.py)
and nowhere else. It was previously re-implemented in five places, and every new output format was
another chance for those copies to drift apart — so the CLI, the MCP server, the GitHub Action, the
SARIF and JUnit emitters, and `specforge` all call the same functions.

Its test suite asserts the properties rather than the implementation: that `combine` never rounds
up, that an incomplete proof is downgraded, that `allow_undetermined` widens only one case, and that
combining nothing is not a pass.
