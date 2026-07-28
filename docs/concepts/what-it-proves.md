# What "proved" actually means

A `PROVED` verdict is a precise statement, and it is narrower than it sounds. This page says exactly
what it covers, so you can tell what you are entitled to conclude.

## The statement

> For the finite state machine **as written in your spec**, every state reachable from the initial
> state by the declared transitions satisfies every declared invariant. The search enumerated all of
> them.

Four qualifications are doing real work in that sentence.

### "as written in your spec"

The checker verifies your model. It has never seen your implementation and cannot know whether the
two agree.

This is not a technicality — it is where most of the risk lives. If your model says a lock is
acquired atomically and your code does a check-then-set, the model is safe and the code is not, and
nothing in the tool can notice. **The model is a claim you are making about your system, and it is
your claim to justify.**

What you get in exchange: the model is small enough to read, so a reviewer can check it against the
code by eye. That is a much easier review than checking the code against a property directly.

### "reachable from the initial state"

Only reachable states are examined. A state that violates the invariant but that no execution can
arrive at is correctly ignored — it is not a bug, because it cannot happen.

The consequence: **your initial state is part of the specification.** Start the machine somewhere
else and you may get a different answer, legitimately.

### "by the declared transitions"

The checker explores the interleavings your transitions permit — all of them, which is the point.
Humans miss interleavings; breadth-first search does not.

But it cannot explore a transition you did not declare. A missing transition is a modelling error
that presents as a *proof*: the space is smaller than reality, everything in it is fine, and the
verdict is `PROVED`. This is the most common way to get a true verdict about the wrong machine.

The defence is the one the tool already gives you: `reachable_states` is reported with every
verdict. If a model you expect to be complicated proves in four states, that number is telling you
something.

### "enumerated all of them"

This is what separates `PROVED` from `UNDETERMINED`, and it is checked rather than assumed. See
[the three-valued verdict](verdicts.md).

## What a counterexample means

Stronger, and much easier to check.

> There is an execution, starting from the initial state and following only declared transitions,
> that reaches a state violating the named invariant. Here it is.

A counterexample is **falsifiable evidence**. You do not have to trust the tool: replay it. Each
step either is a declared transition or is not; the final state either violates the invariant or
does not. `protocol-bench` and `specforge` both make this the basis of scoring, precisely because it
is checkable by a third party.

And because the trace stands alone, it remains valid even when the search that found it never
finished.

Two honest caveats:

- **Shortest, not unique.** Breadth-first search returns a minimum-length trace. Other, longer
  counterexamples usually exist.
- **A modelling artefact is possible.** The trace is real *for the model*. If the model permits
  something the real system does not, the counterexample is real and irrelevant. `protocol-bench`
  ships "repaired twin" models for exactly this reason — if adding one guard removes the
  counterexample, it was about the guard rather than about the modelling.

## What safety and liveness cover

**Safety** — "nothing bad happens" — is what `check_safety` establishes. Every invariant is checked
at every reachable state.

**Liveness** — "something good eventually happens" — is `check_liveness`, and it asks a stronger
question than most people expect. Not "is the goal reachable from the start", but:

> Can **every** reachable state still reach a goal state?

This is AG-EF in temporal-logic terms, and the difference matters. A model where the goal is
reachable down one branch and permanently lost down another passes a reachability check and fails
this one. That branch is a trap, and traps are precisely the liveness bugs worth finding.

What is **not** covered: fairness assumptions beyond that, LTL formulas generally, and anything
about *how long* something takes. If you need those, that is a real model checker's job — and
[minicheck exports to one](https://github.com/nickharris808/minicheck#export-to-spin-and-tla).

## The bounds, concretely

| Bound | Default | What happens at the edge |
|---|---|---|
| `max_states` | 200,000 | `UNDETERMINED` — never a truncated pass |
| `int_bound` | 64 | `IntBoundExceeded`; the run reports `exhaustive: false` |
| render `max_nodes` | 60 | the diagram is **refused**; a hairball is not a diagram |

Measured throughput is 3.2×10⁵–1.0×10⁶ states/second for declarative specs on an M-series laptop,
and memory runs at roughly **342 bytes per state** — so 200,000 states is about 66 MB, a million is
around 340 MB, and ten million is where the representation stops being viable.

Those numbers are reproducible from the published code; they are not estimates.

## The failure mode to watch for

Not a crash. Not a wrong counterexample — those are self-checking. The one to watch for is:

> **A true verdict about a machine that is not the one you meant.**

A dropped transition, an invariant naming a value the space cannot represent, a field whose initial
value is wrong. Every one of these produces a genuinely correct `PROVED` about a genuinely wrong
model.

The tool helps where it can — `spec_warnings` flags an invariant that cannot be violated by
construction, `reachable_states` gives you a sanity check, and the CLI prints both — but this one is
ultimately on the modeller. It is the reason the models are meant to stay small enough to read.
