#!/usr/bin/env python3
"""Regenerate `docs/tools/*.md` from the sibling repositories.

    python build_tool_pages.py --repos /path/to/checkouts

Every per-tool page restates two things a page cannot verify for itself: the *Honest scope* section,
and the test and line counts. Both drift. They drifted here — the `specforge` page claimed 38 tests
and ~736 lines when the package had 77 and 741 — which is exactly the kind of small confident wrong
number this portfolio exists to argue against.

So the pages are generated instead of written. Each one is built from that repository's own README,
which is the source of truth, and from counting its files. If a repository is missing this script
**fails** rather than emitting a page with a guessed number in it.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

GITHUB = "https://github.com/nickharris808"

# name -> (tagline, one-paragraph description, pip-installable?)
TOOLS = {
    "minicheck": (
        "An explicit-state model checker you can read in an afternoon",
        "Describe a finite state machine, assert an invariant, get back the shortest concrete trace "
        "that breaks it. No required dependencies.",
        True,
    ),
    "protocol-bench": (
        "Ground truth from published standards, where a detection must replay",
        "Fifteen IEEE 802.11 and 3GPP procedures with named safety properties and reviewed labels. A "
        "claimed counterexample is replayed against the model before it earns credit.",
        True,
    ),
    "specforge": (
        "A benchmark that cannot be memorised",
        "Generates protocol-shaped verification tasks whose ground truth is computed by an exhaustive "
        "checker rather than written down. Change the seed and nothing has seen the task set.",
        True,
    ),
    "minicheck-mcp": (
        "The checker as an MCP server",
        "Lets an agent verify a state machine instead of reasoning about it in prose. Specs are data, "
        "never code, so nothing the agent submits is executed.",
        True,
    ),
    "minicheck-action": (
        "Model-check every spec in a repository, in CI",
        "Counterexamples render as diagrams in the pull request and as SARIF in the Security tab. "
        "UNDETERMINED fails the job by default.",
        False,
    ),
    "protocol-bench-action": (
        "Enforce a benchmark claim in CI, by replay",
        "Scores a submission on every push and fails the build if a claimed detection cannot be "
        "demonstrated. The gate cannot be passed by guessing.",
        False,
    ),
    "failclosed": (
        "Default-deny middleware for a verification-gated endpoint",
        "A gated path succeeds only on an affirmative machine-checked verdict. There is no code path "
        "from 'we could not determine safety' to a success status.",
        True,
    ),
    "polyfrac": (
        "Exact real-root counting over the rationals",
        "Sturm's theorem over exact rational arithmetic: the number of distinct real roots in an "
        "interval, as an integer, with no floating point anywhere.",
        True,
    ),
}

PAGE = """# {name}

**{tagline}**

{description}

[:material-github: Source]({github}/{name}){{ .md-button }}{extra_button}

{facts}

{install}## Honest scope

*Reproduced from the package README, which is the source of truth.*

{scope}

---

Full documentation, quickstart and troubleshooting live in the
[repository README]({github}/{name}#readme).
"""

#: Names on PyPI that belong to SOMEBODY ELSE. For these, "does not work yet" is FALSE and
#: dangerous: the command succeeds and installs an unrelated project. The generic template flattened
#: that distinction and shipped the wrong warning to a live page for `specforge`.
#:
#: Each value is the owning project, stated factually. This is a fact about a name in a public index,
#: not a claim about the other project's software — nothing here evaluates or criticises it.
NAME_TAKEN_ON_PYPI = {
    "specforge": ("SGLang's SpecForge", "https://github.com/sgl-project/SpecForge"),
}

#: Published by us, and therefore `pip install <name>` WORKS. Declared rather than probed so the
#: build stays offline and deterministic; `tests/test_install_lines.py` probes PyPI for real and
#: fails if reality and this table disagree, in either direction.
#:
#: This table exists because publishing four packages on 2026-07-30 instantly made the opposite
#: caveat false on every page. "Not on PyPI yet" is a claim with a shelf life, and the moment it
#: expired it became the same defect class as the specforge warning above — a documented statement
#: about a command that does not match what the command does.
ON_PYPI = {
    "minicheck": "0.4.0",
    "protocol-bench": "1.1.0",
    "polyfrac": "0.2.0",
    "failclosed": "0.2.0",
}

INSTALL_PUBLISHED = """## Install

```console
$ pip install {name}
```

"""

INSTALL = """## Install

```console
$ pip install "{name} @ git+{github}/{name}.git"
```

!!! note
    `pip install {name}` does not work yet — nothing here is on PyPI. Install from GitHub.

"""

#: The name resolves, but to someone else's project. A user who reads "does not work" and tries it
#: anyway gets a SUCCESSFUL install of the wrong software — which is why this wording differs.
INSTALL_NAME_TAKEN = """## Install

```console
$ pip install "{name} @ git+{github}/{name}.git"
```

!!! warning "Do not run `pip install {name}`"
    The name `{name}` on PyPI belongs to somebody else — it is [{owner}]({owner_url}), an unrelated
    project. `pip install {name}` **does not fail**: it succeeds and installs that project instead of
    this one. Always install from GitHub with the quoted URL above, until this package is released
    under a name of its own.

"""

USES = """## Use it

```yaml
- uses: nickharris808/{name}@v1
```

"""


def count_tests(root: pathlib.Path) -> int | None:
    """Collect-only, so the number is the repository's own rather than this script's guess.

    REFUSES on a failed collection. This function used to read pytest's trailing integer without
    looking at the exit status, and on 2026-07-30 that published four wrong counts to live pages in
    one command: minicheck 270 -> 10, protocol-bench 125 -> 13, minicheck-mcp 97 -> 7, specforge
    77 -> 2. The cause was mundane — the packages were not installed, so collection aborted with
    `ModuleNotFoundError` and pytest printed "10 tests collected, 9 errors". The regex took the 10.

    A count derived from a collection that FAILED is not a smaller count; it is not a count at all.
    Publishing it is the vacuous-pass class wearing a documentation-generator costume, so this now
    raises rather than degrading quietly.
    """
    if not (root / "tests").is_dir():
        return None
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=root,
    )
    blob = out.stdout + out.stderr
    if out.returncode == 5:
        return 0  # "no tests ran" is a real, honest zero
    if out.returncode != 0 or re.search(r"\berrors?\b", blob):
        raise SystemExit(
            f"REFUSING to count tests for {root.name}: collection did not succeed "
            f"(exit {out.returncode}). Publishing pytest's partial number would understate the "
            f"suite — this is exactly how 270 became 10. Install the packages first:\n"
            f"    python3 -m venv .venv && .venv/bin/pip install -e '{root}[test]'\n"
            f"then re-run. Tail of collection output:\n"
            + "\n".join(blob.strip().splitlines()[-3:]))
    lines = [ln for ln in out.stdout.strip().splitlines() if ln.strip()]
    if not lines:
        return None
    last = lines[-1]
    # pytest -q --collect-only prints "N tests collected" for multi-file runs but "path: N" when a
    # single file matches. The regex only handled the first shape, so `minicheck-action`'s real 20
    # silently became "no count at all" — a number dropping out of a published page with no signal.
    m = re.match(r"(\d+)", last) or re.search(r":\s*(\d+)\s*$", last)
    if not m:
        raise SystemExit(
            f"REFUSING to count tests for {root.name}: collection SUCCEEDED but its output could not "
            f"be parsed, so the page would silently omit a count that exists. Last line was:\n"
            f"    {last!r}")
    return int(m.group(1))


def count_lines(root: pathlib.Path) -> int | None:
    src = root / "src"
    if not src.is_dir():
        return None
    return sum(len(p.read_text(encoding="utf-8").splitlines()) for p in sorted(src.rglob("*.py")))


def honest_scope(root: pathlib.Path) -> str:
    md = (root / "README.md").read_text(encoding="utf-8")
    m = re.search(r"##+ Honest scope\n(.*?)(?=\n##+ )", md, re.S)
    if not m:
        raise SystemExit(f"{root.name}: no 'Honest scope' section in README — refusing to invent one")
    body = m.group(1).strip()
    # A README's relative links point at files in its own repository. Reproduced on this site they
    # would 404, so they are rewritten to absolute URLs rather than shipped broken.
    return re.sub(
        r"\]\((?!https?://|#)([^)]+)\)",
        lambda mm: f"]({GITHUB}/{root.name}/blob/main/{mm.group(1)})",
        body,
    )


#: Published repo name -> the directory it lives in HERE. `protocol-bench-action` is published as one
#: repository but is assembled locally from `action/` (the `action.yml`) and `action-repo/` (the
#: README). Without this alias the build aborted at that name and NEVER REACHED `failclosed` or
#: `polyfrac`, so those two tool pages silently stopped being regenerated — a coverage hole created by
#: a fail-fast on an unrelated entry.
LOCAL_DIR_ALIAS = {"protocol-bench-action": "action-repo"}


def build(repos: pathlib.Path, out: pathlib.Path) -> None:
    missing = []
    for name, (tagline, description, pip_installable) in TOOLS.items():
        root = repos / LOCAL_DIR_ALIAS.get(name, name)
        if not root.is_dir():
            # Collect and report at the END. Aborting here means one unresolvable entry starves
            # every entry after it, which is exactly how failclosed and polyfrac went stale.
            missing.append(name)
            print(f"  {name:24s} MISSING under {repos} — no page emitted")
            continue

        facts = []
        n = count_tests(root)
        if n:
            facts.append(f"{n} tests")
        lines = count_lines(root)
        if lines:
            facts.append(f"~{lines} lines of source")
        facts.append("MIT")

        extra = ""
        if name == "protocol-bench":
            extra = (
                "\n[:material-database: Dataset](https://huggingface.co/datasets/nickh007/protocol-bench){ .md-button }"
                "\n[:material-play: Live demo](https://huggingface.co/spaces/nickh007/protocol-bench-demo){ .md-button }"
            )
        elif name == "specforge":
            extra = (
                "\n[:material-database: Dataset](https://huggingface.co/datasets/nickh007/specforge){ .md-button }"
                "\n[:material-trophy: Leaderboard](https://huggingface.co/spaces/nickh007/specforge-leaderboard){ .md-button }"
            )

        # A name cannot be both ours-on-PyPI and owned-by-someone-else. If it ever is, the tables
        # disagree and neither can be trusted — so refuse rather than pick one.
        if name in ON_PYPI and name in NAME_TAKEN_ON_PYPI:
            raise SystemExit(
                f"REFUSING: {name} appears in BOTH ON_PYPI and NAME_TAKEN_ON_PYPI. One says we "
                f"published it; the other says the name belongs to somebody else. Resolve the "
                f"contradiction before generating a page that asserts either.")

        if not pip_installable:
            install = USES.format(name=name, github=GITHUB)
        elif name in ON_PYPI:
            install = INSTALL_PUBLISHED.format(name=name)
        elif name in NAME_TAKEN_ON_PYPI:
            owner, owner_url = NAME_TAKEN_ON_PYPI[name]
            install = INSTALL_NAME_TAKEN.format(name=name, github=GITHUB,
                                                owner=owner, owner_url=owner_url)
        else:
            install = INSTALL.format(name=name, github=GITHUB)

        # REFUSAL. "does not work yet" asserts the command FAILS. For a name owned by another
        # project the command succeeds and installs their software, so that sentence would send a
        # reader to a confident wrong outcome. This is the priority-1 defect class — a documented
        # command whose stated behaviour is not its real behaviour — so it is fatal, not a lint.
        if name in NAME_TAKEN_ON_PYPI and "does not work yet" in install:
            raise SystemExit(
                f"REFUSING to generate {name}.md: the page would say `pip install {name}` 'does not "
                f"work yet', but that name on PyPI belongs to {NAME_TAKEN_ON_PYPI[name][0]} and the "
                f"command SUCCEEDS with their package. Use INSTALL_NAME_TAKEN.")

        page = PAGE.format(
            name=name, tagline=tagline, description=description, github=GITHUB,
            extra_button=extra, facts=" · ".join(facts),
            install=install,
            scope=honest_scope(root),
        )
        (out / f"{name}.md").write_text(page, encoding="utf-8")
        print(f"  {name:24s} {' · '.join(facts)}")

    # COVERAGE, printed every run. "8/8 pages" is the denominator that tells a reader whether a
    # clean result was clean or merely empty.
    print(f"tool-pages: {len(TOOLS) - len(missing)}/{len(TOOLS)} pages emitted")
    if missing:
        raise SystemExit(
            f"REFUSING: {len(missing)} declared tool(s) produced no page: {missing}. Every other "
            f"page was still written, so the run is diagnosable — but a docs site missing a tool it "
            f"declares is not a complete site.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default="..", type=pathlib.Path)
    ap.add_argument("--out", default="docs/tools", type=pathlib.Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    build(a.repos.resolve(), a.out)
