# protocol-bench

**Ground truth from published standards, where a detection must replay**

Fifteen IEEE 802.11 and 3GPP procedures with named safety properties and reviewed labels. A claimed counterexample is replayed against the model before it earns credit.

[:material-github: Source](https://github.com/nickharris808/protocol-bench){ .md-button }
[:material-database: Dataset](https://huggingface.co/datasets/nickh007/protocol-bench){ .md-button }
[:material-play: Live demo](https://huggingface.co/spaces/nickh007/protocol-bench-demo){ .md-button }

125 tests · ~1290 lines of source · MIT

## Install

```console
$ pip install protocol-bench
```

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**Scoring credits a detection only when its trace replays.** For a task that really is violated:

| submission | scored as |
|---|---|
| `violated` + a trace that replays | true positive |
| `violated` + a trace that does not replay | false negative |
| `violated` + no trace | false negative |
| not `violated` | false negative |

For a safe task, *any* violation claim is a false positive. `accuracy_ignoring_replay` is reported
alongside so the gap between what a submission asserted and what it demonstrated stays visible, and
`unreplayed_claims` counts the difference.

This matters because guessing is easy here. "The WPA2 four-way handshake" sits next to "vulnerable"
in every training corpus, so a model can be right about it having done no reasoning at all. Under
verdict-only scoring, a submission that answers every task correctly and fabricates every trace
scores **1.0**. Under replay-gated scoring it scores **0.5** — exactly the trivial always-safe
guesser, which is what it is.

**What a result proves.** That a submission produced a counterexample which replays against the
published model: it starts at the initial state, every step is a real transition, and the final state
violates the named property.

**What it does not prove.**

- Nothing about shipping products. These are **models of published procedures**, not the standards
  themselves and not implementations. `PROVEN_SAFE` means the property holds over the modelled state
  space; a model abstracts, and an abstraction can hide a real defect.
- Nothing statistically robust. 15 tasks, 2 of them violated. The set is deliberately imbalanced
  because the published-procedure population is. **Treat per-task outcomes as the primary result and
  any aggregate as a summary** — a single task flipping moves balanced accuracy by 0.25.
- Nothing about generalisation. A model that has memorised these 15 will score well.

**A scoring bug shipped in 1.0.0 and is fixed here (1.1.0).** Replay validation was computed and then
ignored by the headline metric. See [SECURITY-ADVISORY.md](https://github.com/nickharris808/protocol-bench/blob/main/SECURITY-ADVISORY.md).

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/protocol-bench#readme).
