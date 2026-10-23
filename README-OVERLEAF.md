# Open in Overleaf: fork additions

This is a fork of [openai/math](https://github.com/openai/math). It adds one thing: for every manuscript listed in `CONTENTS.md`, a link that opens the paper's LaTeX source as a new project in the visitor's Overleaf account.

The upstream `README.md` and all upstream content are unchanged. This file is separate so that syncing with upstream does not cause merge conflicts.

## Where to find the result

- Published page: https://dmackinnon1.github.io/OpenAIMathViaOverleaf/
- Markdown version: https://dmackinnon1.github.io/OpenAIMathViaOverleaf/CONTENTS-overleaf.md
- Build report: https://dmackinnon1.github.io/OpenAIMathViaOverleaf/report.txt

`CONTENTS-overleaf.md` mirrors upstream `CONTENTS.md`. Relative links are made absolute and point at the upstream repository. Each paper line gains an **Open paper source in Overleaf** link.

## How it works

Overleaf's [Open in Overleaf API](https://www.overleaf.com/devs) creates a project from a URL passed as `snip_uri`. Two forms exist:

1. Several files via `snip_uri[]` and `snip_name[]`. This **does not preserve folders**: `sections/intro.tex` is flattened, so `\input{sections/intro}` fails to compile.
2. A single **zip file** via `snip_uri`. Folders are preserved.

So each paper's `preprints/<slug>/build/` folder is zipped and published, and the link points at that zip:

```
https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fdmackinnon1.github.io%2FOpenAIMathViaOverleaf%2Fzips%2F<slug>.zip
```

Overleaf downloads the zip from GitHub Pages and creates the project, using its usual main-file detection (the file containing `\documentclass`).

## What was added

| Path | Purpose |
| --- | --- |
| `scripts/build_overleaf.py` | Zips each `preprints/*/build/` folder, rewrites `CONTENTS.md` into `CONTENTS-overleaf.md`, writes `index.html` and `report.txt`. Python 3 standard library only. |
| `.github/workflows/overleaf-zips.yml` | Runs the script and deploys the output to GitHub Pages. |
| `README-OVERLEAF.md` | This file. |

## Details

- **Triggers:** manual run (Actions tab)
- **Skipped files:** LaTeX build artefacts (`.aux`, `.log`, `.bbl`, and similar) and hidden or OS folders, mirroring Overleaf's own ignore pattern.
- **Ambiguous main file:** if a build folder has several files containing `\documentclass`, the link adds `main_document=main.tex` when a root `main.tex` exists. Otherwise the build report shows a `WARN` line. A few papers fall into this group; check `report.txt` (`NOTE` and `WARN` lines).
- **Papers without a build folder:** `report.txt` lists them (`MISS`). They get no Overleaf link.
- **Size:** about 750 zips, roughly 54 MB in total.

## Setup (if you fork this fork)

1. Settings, then Pages: set the source to **GitHub Actions**.
2. Update the Pages base URL in the workflow if your account or repository name differs. It is derived from `github.repository_owner` and the repository name.
3. Run the workflow, or push to `main`.

## Run locally

```sh
python3 scripts/build_overleaf.py . _site https://<user>.github.io/<repo> \
  https://github.com/openai/math/blob/main
```

Output goes to `_site/`. The last argument is the upstream base URL used for the absolute PDF links.

## Staying in sync with upstream

Use GitHub's **Sync fork** button, or `git pull upstream main`. Because the Action runs on push, a sync triggers a rebuild.

## Known limitations

- Only the `build/` folder is included. Lean formalizations, verification material and reasoning traces are not.
- The link is generated per folder, so older dated versions of a paper that appear under `preprints/` but not in `CONTENTS.md` are zipped but not linked.
- Overleaf's handling of `main_document` together with a zip file has not been confirmed for every case.
- Links depend on this fork's GitHub Pages site being available.

## Credit

All mathematical content and LaTeX sources belong to the upstream project and its authors; see the upstream repository for its license.
