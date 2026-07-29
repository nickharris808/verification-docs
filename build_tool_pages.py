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

INSTALL = """## Install

```console
$ pip install "{name} @ git+{github}/{name}.git"
```

!!! note
    `pip install {name}` does not work yet — nothing here is on PyPI. Install from GitHub.

"""

USES = """## Use it

```yaml
- uses: nickharris808/{name}@v1
```

"""


def count_tests(root: pathlib.Path) -> int | None:
    """Collect-only, so the number is the repository's own rather than this script's guess."""
    if not (root / "tests").is_dir():
        return None
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=root,
    )
    lines = [ln for ln in out.stdout.strip().splitlines() if ln.strip()]
    if not lines:
        return None
    m = re.match(r"(\d+)", lines[-1])
    return int(m.group(1)) if m else None


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


def build(repos: pathlib.Path, out: pathlib.Path) -> None:
    for name, (tagline, description, pip_installable) in TOOLS.items():
        root = repos / name
        if not root.is_dir():
            raise SystemExit(f"{name}: not found under {repos} — refusing to emit a page for it")

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

        page = PAGE.format(
            name=name, tagline=tagline, description=description, github=GITHUB,
            extra_button=extra, facts=" · ".join(facts),
            install=(INSTALL if pip_installable else USES).format(name=name, github=GITHUB),
            scope=honest_scope(root),
        )
        (out / f"{name}.md").write_text(page, encoding="utf-8")
        print(f"  {name:24s} {' · '.join(facts)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default="..", type=pathlib.Path)
    ap.add_argument("--out", default="docs/tools", type=pathlib.Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    build(a.repos.resolve(), a.out)
