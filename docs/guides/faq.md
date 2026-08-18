# Questions and objections

Written from the objections a sceptical reader actually raises, and answered directly. Where the
honest answer is "you are right", it says that.

---

## "Why would I use this instead of TLA+ or SPIN?"

For most serious work, you should not. They are better model checkers with more capability, more
users, and decades of engineering behind them.

Use `minicheck` for the invariant you would otherwise **not check at all** — because adopting TLC or
SPIN means adopting a toolchain: a separate language, a separate binary, a build step, and a
translation layer between your code and the thing being verified. That friction is why the retry
logic and the session lifecycle get reasoned about in a code review instead, and why the missed
interleaving ships.

This is a Python object that runs in your existing test suite with no dependencies, and the whole
engine is short enough to read before you trust it.

And when a model outgrows it, `--format promela` or `--format tla` exports to the real thing. That
is deliberate: a tool that strands you at its own ceiling is one to be wary of adopting in the first
place. See [the full comparison](comparison.md).

---

## "How do I know the checker itself is correct?"

You do not have to take it on faith, and there are three independent reasons not to:

1. **A differential test against a naive reimplementation.** 500 random protocols are checked
   against a deliberately dumb reachability implementation sharing no code with the engine. Verdicts
   and state counts must match exactly.
2. **A differential test against SPIN.** Models are exported to Promela and checked by SPIN — a
   completely independent industrial model checker — and its verdict must match. CI installs SPIN so
   this runs rather than skips.
3. **Counterexamples are self-checking.** You never have to trust a `REFUTED`: replay the trace.

For `PROVED` the trust question is real, which is why (1) and (2) exist and why the engine is kept
small enough to audit.

---

## "This found a bug that isn't real."

Then the model permits something the real system does not — and that is worth knowing, because it
means your model and your system disagree.

Replay the trace step by step. One of the transitions it uses is one your system cannot actually
take. Add the guard that makes that true in the model, and re-check.

`protocol-bench` ships "repaired twin" models for exactly this: if adding one guard removes the
counterexample, the finding was about the guard rather than about the modelling.

---

## "It says UNDETERMINED. Is that a pass or a fail?"

Neither, and treating it as either loses information.

It means the search did not cover the whole state space, so nothing was established. Read
`incomplete_reason`. Usually one of:

- **A field grows without bound** — a counter with no guard stopping it. Bound it in the model, or
  raise `--int-bound` if the real range is genuinely larger.
- **The space exceeded `max_states`** — raise `--max-states`, or reduce the model.

Do not reach for `--allow-undetermined` to make it go away. That converts a non-answer into a pass,
which is the failure this tool exists to prevent. Use it only when you consciously accept an
unestablished result.

---

## "`--allow-undetermined` means I can ignore the strictness, so what's the point?"

The point is that it is a **decision you made**, visible in your config, rather than a default that
quietly decided for you.

It also does less than you might assume: it widens only the undetermined case. A refutation still
fails the build. A flag meaning "I accept not knowing" must not also mean "I accept known-broken",
and there is a test named for that.

---

## "Isn't the three-valued verdict just over-engineering?"

It came from a real defect, not from theory.

Version 0.1.0 clamped integer fields at `int_bound` instead of raising. A counter that genuinely
reaches 100 saturated at 64, the forbidden state was never generated, and `never reach 100` was
reported as **holding**. That was a false proof, and it was live on the public demo and reachable
from an agent-facing MCP server.

Every individual piece behaved sensibly. The bug was structural: there was nowhere to put "I did not
finish looking", so it became "nothing was found". The third value is that missing place.

Full detail in the [security advisory](https://github.com/nickharris808/minicheck/blob/main/SECURITY-ADVISORY.md).

---

## "Why does a benchmark need traces? Isn't the verdict the answer?"

Because the verdict is guessable and the trace is not.

"The WPA2 four-way handshake" sits next to "vulnerable" in every training corpus. A model can be
right about it having done no reasoning at all, and verdict-only scoring cannot tell that apart from
understanding.

Measured, on `protocol-bench`: a submission that answers **every task correctly** and fabricates
every trace scored **1.0** under the original verdict-only scoring. Under replay-gated scoring it
scores **0.5** — exactly what guessing scores, which is what it is.

Both benchmarks report `accuracy_ignoring_replay` next to `accuracy`. The gap between those two
numbers is the measurement.

---

## "A generated benchmark can't be as good as a curated one."

Correct, and they are for different things.

`protocol-bench` is fixed, small, drawn from published standards, and human-reviewed. It is what you
cite. Its weakness is stated in its own README: 15 tasks with 2 violated means **one task flipping
moves balanced accuracy by 0.25**, and its answers age into training corpora.

`specforge` generates unlimited tasks whose ground truth is computed by an exhaustive checker rather
than written down. It cannot be memorised — change the seed and the answer key changes. Its weakness
is that the machines are synthetic; they resemble how protocols are built, but they are not real
protocols.

Use `protocol-bench` for a citable number and `specforge` for a number you can trust has not leaked.

---

## "How do I know the generated answer key is right?"

Three rules, each enforced at generation time and each covered by a test:

1. A task is emitted **only on a definite verdict**. A candidate the checker could not settle is
   discarded, never labelled.
2. Every violated task's counterexample is **replayed against its own model** before the task is
   emitted.
3. Generation is **deterministic from the seed**, so the set is reproducible by anyone.

The test that matters most re-runs the checker on every generated task and requires the stored label
to match. If a label and its model ever disagree, every score computed against that set is
meaningless.

---

## "Doesn't running a spec from a language model let it execute code?"

No, and this is why the declarative format exists.

A spec is data: field names, literals, and equality comparisons. There is no `eval`, no `exec`, and
no code path that turns a string in a spec into a callable. A field value that looks like
`__import__('os').system(...)` stays a string and is compared as one. There is a test that asserts
exactly that, and the MCP server's adversarial suite fires code-shaped payloads at every tool.

The Python `Model` API is different — that *is* code, and you should treat a model from an untrusted
source the way you would treat any other untrusted Python.

---

## "Why isn't this on PyPI?"

Mostly nothing is blocking it technically. The distributions build and pass `twine check`.

**Three** of the packages — `protocol-bench`, `minicheck-mcp` and `specforge` — declare their
`minicheck` dependency as a PEP 508 direct reference so they install today with no package index at
all. PyPI rejects direct references on upload, so each ships a `build_pypi.py` that swaps in an
ordinary version constraint and builds an uploadable artifact, to be used once `minicheck` itself is
published.

One thing *is* blocking, for one package. **The name `specforge` on PyPI already belongs to somebody
else** — [SGLang's SpecForge](https://github.com/sgl-project/SpecForge), an unrelated
speculative-decoding training framework, also at version `0.1.0`. So `pip install specforge` does not
fail; it succeeds and installs a different project. That package needs a rename before any index
release, and its README says so at the top of its install section.

Of the other five, four are on the index and install with a plain `pip install <name>`:
`minicheck`, `protocol-bench`, `failclosed` and `polyfrac`. Only `minicheck-mcp` is still
GitHub-only, and its README says so plainly rather than implying otherwise. Each package's
`tests/test_install_line.py` checks its own README against the live index, so none of these
sentences can go stale quietly again — which is why this one is written down rather than hedged.

---

## "Are these production-ready?"

Depends which, and the honest answers differ:

- **`polyfrac`** — yes. Small, exact, no dependencies, and it refuses inexact input rather than
  silently approximating.
- **`minicheck`** — yes for models that fit its bounds, which it tells you about rather than
  guessing. It is not SPIN and does not claim to be.
- **`failclosed`** — yes as an enforcement point. It does not decide verdicts and cannot audit your
  prover; it enforces the consequence.
- **`minicheck-mcp`, `minicheck-action`** — yes, both fully tested, but the surrounding ecosystems
  move quickly.
- **`protocol-bench`, `specforge`** — usable now; treat per-task outcomes as the primary result and
  aggregates as summaries, especially on the 15-task fixed set.

Every package has an **Honest scope** section stating what it does not establish. Those are the
first thing to read.

---

## "Something here gave me a confident answer that was wrong."

That is the most serious class of bug in this portfolio, and it is worth an issue rather than a
workaround. Please include the input.

Ten defects of exactly that kind were found and fixed in an earlier audit; three of them carry
public security advisories. The response to this category is disclosure and a regression test, not a
quiet patch.
