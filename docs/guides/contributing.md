# Contributing

Contributions are welcome. This page is short because most of it is one rule.

## The rule

**No change may let a tool give a confident answer it has not earned.**

Everything else is negotiable. That is not.

Concretely, a change is unlikely to be accepted if it:

- lets `holds: True` or `PROVED` be returned from a search that did not complete;
- maps `UNDETERMINED` onto anything a downstream system renders as success;
- makes an error path return a value a caller reads as a pass;
- adds an output format that changes a verdict in translation;
- silently coerces input rather than refusing it.

If you are unsure whether a change crosses that line, open an issue first — it is a much easier
conversation before the code exists.

## Reporting a false verdict

This is the most valuable bug report you can send, and it gets priority over everything else.

Include the input that produced it. If a tool told you something was proved and it was not, that is
a security-grade defect: earlier ones got public advisories in `minicheck`, `failclosed` and
`protocol-bench`, and the response is disclosure plus a regression test, not a quiet patch.

## Getting set up

```console
$ git clone https://github.com/nickharris808/minicheck.git
$ cd minicheck
$ python -m venv .venv && source .venv/bin/activate
$ pip install -e ".[test,smt]"
$ pytest -q
```

Some suites want extra tools. They **skip** without them, so a green local run may be less green
than it looks:

- `minicheck` — `spin` and a C compiler, for the export differential. CI installs SPIN, so it runs
  there whether or not it ran for you.
- `polyfrac` — `numpy`, for the differential against an independent root finder.

If you are changing either of those areas, install the tool.

## What a good test looks like

Three kinds, in increasing order of how much they are worth:

1. **Unit tests.** They ask whether the code agrees with itself. Necessary, least informative.
2. **Adversarial tests.** Malformed, empty, enormous, out-of-distribution input, with one oracle:
   *no input may produce a confident-looking answer that is wrong.*
3. **Differential tests.** The best. Check the thing against an independent implementation of the
   same question — a naive reimplementation, SPIN, numpy, an interpreted path versus a compiled one.

Every defect found in the original audit came from a suite that only ever asked the first question.

**Mutation-test your regression test.** Reintroduce the bug and confirm the test goes red. A test
that passes on both the broken and the fixed code is worth nothing, and this has already caught one
test passing for the wrong reason.

## Numbers in documentation

Every numeric claim in a README is re-derived by `tests/test_readme_claims.py` in that repo. If you
change the test count or add source, that test will fail until the README matches. That is working
as intended.

Do not write a number into documentation that the published code cannot reproduce.

## Style

- `ruff check .` and `ruff format --check .` must pass; line length is 120.
- Comments explain **why**, not what. The code says what.
- Error messages name the fix, not just the fault. `'initial' must assign exactly the declared
  fields ['a', 'b'], but it is missing ['b']` beats `invalid initial state`.

## Responsible disclosure

Do not add findings or verdicts about **named** third-party products, vendors or protocols. Ship the
checker and the methodology.

`protocol-bench` contains a small, human-reviewed corpus drawn from published standards; additions
to it are a human decision, not an automated one. `specforge` exists partly so that growing the
benchmark does not require making new claims about named systems.

## Licence

MIT, across every package. By contributing you agree your contribution is licensed the same way.
