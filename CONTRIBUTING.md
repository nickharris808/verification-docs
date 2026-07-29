# Contributing

A guide that misleads is a defect, so corrections to these docs are as welcome as corrections to the
code.

## The one rule this documentation exists to state

**A verdict you cannot check is not a verdict**, and its corollary: *undetermined is not a pass.* If
a page ever implies that an unfinished search established something, that is a bug — please report
it, and quote the sentence.

## Reporting a problem

Open an issue with the page URL and what it led you to believe that turned out to be false. "This
paragraph is confusing" is useful; "this paragraph made me think `exhaustive: false` was safe to
ignore" is far more useful, because it names the harm.

## Making a change

```console
$ pip install mkdocs mkdocs-material
$ mkdocs serve                    # live preview on localhost:8000
$ mkdocs build --strict           # what CI runs
```

`--strict` turns a broken internal link into a build failure. That is deliberate: a dead link in
documentation about trustworthiness is worse than an absent page.

## What belongs here, and what does not

The per-tool pages pull each repository's own *Honest scope* section rather than restating it, so
the site and the READMEs cannot drift apart. If a tool's scope is wrong, fix it in that tool's
README and it will flow through here — do not patch the copy on this site.

Numbers belong in the repository that can reproduce them. This site should link to a figure, not
restate one it cannot verify.

## Licence

By contributing you agree that your work is licensed under the MIT licence, as in [LICENSE](LICENSE).
