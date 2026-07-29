# failclosed

**Default-deny middleware for a verification-gated endpoint**

A gated path succeeds only on an affirmative machine-checked verdict. There is no code path from 'we could not determine safety' to a success status.

[:material-github: Source](https://github.com/nickharris808/failclosed){ .md-button }

62 tests · ~301 lines of source · MIT

## Install

```console
$ pip install "failclosed @ git+https://github.com/nickharris808/failclosed.git"
```

!!! note
    `pip install failclosed` does not work yet — nothing here is on PyPI. Install from GitHub.

## Honest scope

*Reproduced from the package README, which is the source of truth.*

**What it guarantees.** On a gated path, a status below 400 is returned only when the handler stamped
an affirmative `SAFE` verdict *and* the response body arrived intact within the deadline. There is no
code path from "could not determine" to success.

The deadline covers the **whole exchange** — handler dispatch and reading the response body. Wrapping
only the handler left streaming outside the budget, so a handler that returned headers instantly and
then stalled blew through a 500 ms deadline and still returned 200.

**Completeness is required, not assumed.** A `SAFE` response must be one whose body can be confirmed
whole: it declares a `Content-Length` that matches, or it declares a JSON media type and parses. If
neither holds, the gate refuses and says so. This is because Starlette's `BaseHTTPMiddleware` records
a mid-stream handler exception but only re-raises it *after* the response has been sent — so
truncation is the only evidence available at gate time. Pass `require_verifiable_body=False` to
accept that risk deliberately for a genuinely unbounded stream.

**What it does not do.**

- It does not decide the verdict. Mapping your solver's output — or your endpoint's response shape —
  to SAFE/UNSAFE/REFUSED is your handler's job, because that mapping is specific to what you are
  proving. `failclosed` enforces the *consequence*, which is the part everyone gets wrong.
- It does not verify that a `SAFE` stamp was *earned*. A handler that stamps `SAFE` unconditionally
  will pass. The gate enforces that an unstamped or negatively-stamped response cannot succeed; it
  cannot audit your prover for you.
- It does not protect ungated paths, and gating is prefix-matched literally — `/g` also gates
  `/ghost`. Choose prefixes that cannot collide.
- It buffers gated response bodies up to `max_body_bytes` (8 MiB default), so gated endpoints are not
  suitable for large downloads.

**A bypass shipped in 0.1.0 and is fixed here.** The deadline did not cover body streaming. See
[SECURITY-ADVISORY.md](https://github.com/nickharris808/failclosed/blob/main/SECURITY-ADVISORY.md).

If you want the other half — a verification engine that produces those verdicts — see
[`minicheck`](https://github.com/nickharris808/minicheck), an explicit-state model checker with no required dependencies.

`failclosed` is the enforcement point extracted from a production verification gate. The gate itself
— the solver fleet behind it, the response classifiers that map each endpoint's shape to a verdict,
and the evidence trail that makes a verdict auditable after the fact — is the commercial offering.
This middleware is MIT and always will be.

---

Full documentation, quickstart and troubleshooting live in the
[repository README](https://github.com/nickharris808/failclosed#readme).
