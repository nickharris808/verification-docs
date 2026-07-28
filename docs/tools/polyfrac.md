# polyfrac

**Exact rational arithmetic with Sturm root counting**

Exact counts of distinct real roots in an interval. Refuses float input rather than silently approximating.

[:material-github: Source](https://github.com/nickharris808/polyfrac){ .md-button }

66 tests · ~390 lines of source · MIT

## Install

```console
$ pip install "polyfrac @ git+https://github.com/nickharris808/polyfrac.git"
```

!!! note
    `pip install polyfrac` does not work yet — nothing here is on PyPI. Install from GitHub.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**Exactness is enforced at the boundary, not merely intended.** Passing a `float` raises
`InexactInput` rather than being converted, because `0.1` is not one tenth — it is
`3602879701896397/36028797018963968`, and exact arithmetic on it produces an exact answer to a
question you did not ask. Use `Fraction(1, 10)`, the string `"0.1"`, or the explicit
`Poly.from_floats()` when a float really is the value you mean.

```python
>>> Poly([0.1])
InexactInput: refusing the float 0.1: it is a binary approximation ...
>>> Poly(["0.1"]).c[0]
Fraction(1, 10)
```

**What it proves.** An exact count of *distinct* real roots in the half-open interval `(a, b]`, and
an exact sign certificate over an interval. No sampling, no tolerance, no numerical root finding —
the count comes from sign changes in a Sturm chain over exact rationals.

**What it does not prove.**

- Univariate only, over ℚ. For multivariate sign conditions you want cylindrical algebraic
  decomposition, which this package does not implement.
- Multiplicities are not reported. `Poly.from_roots([2, 2, 2])` has *one* distinct root.
- Irrational and complex roots are outside the interval arithmetic entirely; only real roots at
  rational-bounded intervals are counted.
- The interval convention is half-open `(a, b]` — the left endpoint is excluded and the right is
  included. Off-by-one here is silent, so it is asserted in the test suite.
- `gauss_solve` requires a non-singular system; a singular one raises rather than returning a value.
- The zero polynomial raises. It is zero at every point, so no finite root count exists, and
  returning `0` would be a confident wrong answer.

---

Full documentation, quickstart and troubleshooting live in the [repository README](https://github.com/nickharris808/polyfrac#readme).
