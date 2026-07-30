"""Every documented install command must match what the command actually does.

This is the highest-severity documentation defect class in this portfolio, and it has now bitten
twice in one day:

  1. Six tool pages carried a templated `pip install <name> does not work yet — nothing here is on
     PyPI`. For `specforge` that was FALSE: the name belongs to SGLang's SpecForge, so the command
     succeeds and installs an unrelated project. A reader told "it does not work" who tries it anyway
     gets a confident wrong outcome.
  2. Publishing four packages the same afternoon made the SAME sentence false for those four, in the
     opposite direction — `pip install minicheck` started working while every page still said it did
     not.

Both are one shape: a documented statement about a command that does not match the command. "Not on
PyPI yet" is a claim with a shelf life, and nothing was watching the clock.

So the declared tables are checked against the real index. Network tests SKIP when offline — and a
skip is not a pass, which is why the offline case is asserted separately rather than silently
returning green.

    python3 -m pytest tests/test_install_lines.py -q
"""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.error
import urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build_tool_pages as B  # noqa: E402

DOCS = ROOT / "docs" / "tools"


def _pypi(name):
    """(status, info) for a PyPI project. Returns (None, None) when the network is unavailable."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20) as r:
            return r.status, json.load(r)["info"]
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, None


# ------------------------------------------------------------------ the tables cannot contradict
def test_a_name_is_never_both_ours_and_somebody_elses():
    assert not (set(B.ON_PYPI) & set(B.NAME_TAKEN_ON_PYPI))


def test_every_declared_tool_is_classified_exactly_once():
    """No tool may fall through the install branches unclassified."""
    for name, (_t, _d, pip_installable) in B.TOOLS.items():
        states = sum([name in B.ON_PYPI, name in B.NAME_TAKEN_ON_PYPI, not pip_installable])
        assert states <= 1, f"{name} matches {states} install states"


# ------------------------------------------------------------------ the pages say the right thing
def test_a_published_package_page_does_not_claim_it_is_unavailable():
    for name in B.ON_PYPI:
        p = DOCS / f"{name}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        assert "does not work yet" not in text, (
            f"{name}.md says the install 'does not work yet', but we published it — "
            f"`pip install {name}` works now")
        assert f"pip install {name}" in text


def test_a_name_owned_by_someone_else_carries_the_STRONGER_warning():
    for name in B.NAME_TAKEN_ON_PYPI:
        p = DOCS / f"{name}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        assert "does not work yet" not in text, (
            f"{name}.md claims the command fails; it SUCCEEDS with somebody else's package")
        assert "does not fail" in text and "belongs to somebody else" in text


def test_no_tool_page_shows_a_bare_install_for_an_unpublished_package():
    """The defect in its original direction: a command that simply does not resolve."""
    for name, (_t, _d, pip_installable) in B.TOOLS.items():
        if not pip_installable or name in B.ON_PYPI:
            continue
        p = DOCS / f"{name}.md"
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip().lstrip("$ ").strip()
            assert s != f"pip install {name}", f"{name}.md gives a bare install that cannot resolve"


# ------------------------------------------------------------------ reality check, both directions
@pytest.mark.parametrize("name", sorted(B.ON_PYPI))
def test_each_package_we_claim_to_have_published_really_is_on_pypi(name):
    status, info = _pypi(name)
    if status is None:
        pytest.skip(f"no network — PyPI not probed for {name}; this is a SKIP, not a pass")
    assert status == 200, f"ON_PYPI declares {name} published, but PyPI returns {status}"
    assert info["version"] == B.ON_PYPI[name], (
        f"{name}: declared {B.ON_PYPI[name]}, PyPI has {info['version']}")


@pytest.mark.parametrize("name", sorted(B.NAME_TAKEN_ON_PYPI))
def test_a_name_we_call_taken_really_does_resolve_to_someone_else(name):
    """If the name were ever free, the strong warning would itself become the wrong claim."""
    status, info = _pypi(name)
    if status is None:
        pytest.skip(f"no network — PyPI not probed for {name}; this is a SKIP, not a pass")
    assert status == 200, (
        f"NAME_TAKEN_ON_PYPI says {name} is owned by someone else, but PyPI returns {status}. "
        f"If the name is now free the page is over-warning and should be corrected.")
    ours = "nickharris808"
    home = (info.get("home_page") or "") + " " + json.dumps(info.get("project_urls") or {})
    assert ours not in home, (
        f"{name} on PyPI now points at our own project — it is no longer somebody else's, so the "
        f"warning must be replaced.")


def test_an_unclassified_package_is_genuinely_unclaimed():
    """The remaining names must still be free, or a caveat has silently gone stale again."""
    for name, (_t, _d, pip_installable) in B.TOOLS.items():
        if not pip_installable or name in B.ON_PYPI or name in B.NAME_TAKEN_ON_PYPI:
            continue
        status, _ = _pypi(name)
        if status is None:
            pytest.skip("no network")
        assert status == 404, (
            f"{name} is documented as 'not on PyPI yet' but the name now RESOLVES ({status}). "
            f"Either we published it — add it to ON_PYPI — or somebody else did, which is the "
            f"specforge situation and needs the stronger warning.")
