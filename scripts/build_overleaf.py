#!/usr/bin/env python3
"""Zip every preprints/*/build/ folder and rewrite CONTENTS.md with
"Open paper source in Overleaf" links.

Usage: build_overleaf.py <repo_root> <site_dir> <pages_base_url> [upstream_blob_base]
Outputs: <site_dir>/zips/<slug>.zip, <site_dir>/CONTENTS-overleaf.md, <site_dir>/report.txt
"""
import re, sys, zipfile
from pathlib import Path
from urllib.parse import quote

root, site, base = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].rstrip("/")
blob = (sys.argv[4] if len(sys.argv) > 4 else "https://github.com/openai/math/blob/main").rstrip("/")
(site / "zips").mkdir(parents=True, exist_ok=True)

# Mirrors Overleaf's fileIgnorePattern so we don't ship junk.
SKIP_DIRS = {"__MACOSX", ".git", ".texpadtmp", ".R", ".venv", "venv"}
SKIP_EXT = {"dvi","aux","log","toc","out","pdfsync","synctex","fdb_latexmk","fls","nlo",
            "ind","glo","gls","glg","bbl","blg","doc","docx","gz","swp"}

def zip_build(build: Path, dest: Path) -> int:
    n = 0
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(build.rglob("*")):
            rel = p.relative_to(build)
            if p.is_dir() or SKIP_DIRS & set(rel.parts):
                continue
            if p.suffix.lstrip(".") in SKIP_EXT or (p.name.startswith(".") and p.name != ".latexmkrc"):
                continue
            z.write(p, rel.as_posix()); n += 1
    return n

report, built, mains = [], {}, {}
for build in sorted((root / "preprints").glob("*/build")):
    slug = build.parent.name
    n = zip_build(build, site / "zips" / f"{slug}.zip")
    built[slug] = n
    report.append(f"OK   {slug}: {n} files")
    # Detect ambiguous main file (several files with \documentclass).
    docs = [p.relative_to(build).as_posix() for p in build.rglob("*.tex")
            if re.search(r"^\s*\\documentclass", p.read_text(errors="ignore"), re.M)]
    if len(docs) > 1:
        if "main.tex" in docs:
            mains[slug] = "main.tex"
            report.append(f"NOTE {slug}: {len(docs)} documentclass files {docs}; using main.tex")
        else:
            report.append(f"WARN {slug}: ambiguous main file {docs}")

text = (root / "CONTENTS.md").read_text(encoding="utf-8")
# absolutize relative links (PDFs, lean docs, overview)
text = re.sub(r"\]\((?!https?://|#)([^)\s]+)\)", lambda m: f"]({blob}/{m.group(1)})", text)

link_re = re.compile(r"^(&emsp;\[[^\n]*\]\(" + re.escape(blob) + r"/preprints/([^/]+)/[^)]+\.pdf\))", re.M)
def add(m):
    slug = m.group(2)
    if slug not in built:
        report.append(f"MISS {slug}: no build/ folder")
        return m.group(1)
    url = "https://www.overleaf.com/docs?snip_uri=" + quote(f"{base}/zips/{quote(slug)}.zip", safe="")
    if slug in mains:
        url += "&main_document=" + quote(mains[slug], safe="")
    return f"{m.group(1)} — [Open paper source in Overleaf]({url})"
text = link_re.sub(add, text)

(site / "CONTENTS-overleaf.md").write_text(text, encoding="utf-8")
(site / "index.html").write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mathematics manuscripts: Open in Overleaf</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:60rem;margin:0 auto;padding:1rem 16px}
td{padding:.6rem 0;border-bottom:1px solid #ddd}table{border-collapse:collapse;width:100%}</style>
</head><body><p><a href="CONTENTS-overleaf.md">Raw markdown</a> &middot; <a href="report.txt">Build report</a></p>
<div id="c">Loading&hellip;</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>fetch("CONTENTS-overleaf.md").then(r=>r.text()).then(t=>{document.getElementById("c").innerHTML=marked.parse(t)})</script>
</body></html>
""", encoding="utf-8")
(site / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
