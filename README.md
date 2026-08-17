# verdatia.com

The Verdatia company site. Static HTML, no build step, no JavaScript.

**Live:** https://verdatia.com

**Brand system, copy decisions, and firm plan of record:** private repo `verdatia` (fonts, logos, DESIGN.md, WEBSITE-DECISIONS.md — read DESIGN.md before any visual change here).

## How it deploys

GitHub Pages serves this repository's root directly from `main`. A merge to
`main` is a deploy: there is no build, no bundler, and no staging step. What is
in the repo is what is on the domain, usually within a minute.

`CNAME` is what points verdatia.com at Pages. **Do not delete or edit it.** If
it goes, Pages quietly falls back to the github.io URL, the site still looks
fine, and the domain everyone has been given starts failing. CI checks for this
on every change.

## Working on it

```bash
# Serve locally (any static server works)
python3 -m http.server 8000
# then open http://localhost:8000
```

Because a merge is a deploy, changes go through a pull request rather than a
direct push to `main`. CI runs on the PR and checks:

- `CNAME` still says `verdatia.com`
- every internal link and asset reference resolves to a real file
- HTML is well formed (no unclosed tags)
- no file over 2MB has crept in

Run the link check yourself before pushing:

```bash
python3 scripts/check-links.py
```

## Structure

```
index.html              home
about/                  about + founder
services/               services + fees
construction-finance/   flagship specialism
builddatum/             BuildDatum
contact/                contact
privacy/  terms/        legal
404.html                not-found page
assets/                 css, images, og images
CNAME                   custom domain (do not remove)
```
