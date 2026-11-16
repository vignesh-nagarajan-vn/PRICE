"""Build the zip archive to upload to arXiv.

arXiv rejects a package carrying both TeX source and a compiled PDF, so main.pdf
is deliberately excluded, as is this directory's README and this script, which
are repository documentation rather than part of the paper. Everything else here
is needed: arXiv's TeX Live has every \\usepackage the build calls for, but
neurips_2026.sty is a local style file and must ship with the source.

    python econml/paper/arxiv/package.py

Then upload arxiv-submission.zip. Paths are stored at the archive root, which is
what arXiv expects. It runs pdfLaTeX, forced by the \\pdfoutput=1 on line 2 of
main.tex, and needs no BibTeX pass, since the bibliography is a thebibliography
environment inside main.tex.
"""
import pathlib
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "arxiv-submission.zip"

MEMBERS = [
    "main.tex",
    "appendix.tex",
    "checklist.tex",
    "neurips_2026.sty",
    "figures/fig_cadence.pdf",
    "figures/fig_herd.pdf",
    "figures/fig_phase.pdf",
    "figures/fig_substitution.pdf",
    "figures/fig_wedge.pdf",
]

missing = [m for m in MEMBERS if not (HERE / m).is_file()]
if missing:
    raise SystemExit("missing source files: " + ", ".join(missing))

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for m in MEMBERS:
        z.write(HERE / m, arcname=m)

print("wrote {} ({:,} bytes)".format(OUT.name, OUT.stat().st_size))
for info in zipfile.ZipFile(OUT).infolist():
    print("  {:<32} {:>9,}".format(info.filename, info.file_size))
