"""Build the EconML @ NeurIPS 2026 submission package.

Two artifacts, both written next to this script:

    main.pdf                    the submission itself, 9 body pages + refs + appendices + checklist
    econml-supplementary.zip    the anonymized code bundle checklist Q5 promises reviewers

Everything in the zip is read from git (``HEAD``) rather than the working tree, so
build leftovers that carry a machine path -- ``__pycache__/*.pyc``, ``paper/main.log`` --
cannot reach reviewers. The script refuses to write a zip if any member still
contains an identifying string.

    python econml/submission/build_package.py
"""
import pathlib
import re
import subprocess
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
PDF = REPO / "econml" / "paper" / "main.pdf"

# Checklist Q5 promises the certificate files and the panel code. The theory
# module and the environment come too: the certificates import them.
MEMBERS = [
    "econml/ml-contributions/certificates/",
    "econml/ml-contributions/experiments/",
    "econml/ml-contributions/theory/econml_theory.py",
    "econml/ml-contributions/environment/hetero_response_env.py",
    "econml/paper/make_figures.py",
    "econml/ml-contributions/CERTIFICATES.md",
    "econml/ml-contributions/EXPERIMENT-SPECS.md",
]

# Anything that would break the blind or name a machine.
FORBIDDEN = [r"nrvig", r"[Cc]:\\\\Users", r"shriraghav", r"Vignesh", r"Nagarajan", r"Ashok"]

SUPP_README = """\
Supplementary material
======================

Code for "Herd Immunity and Adaptive Learning Externalities under Shared
Foundational Models". Anonymized: no author names, no repository URL, no
absolute paths. The repository is linked in the camera-ready version.

Contents
--------

  ml-contributions/certificates/    eight assertion-based certificate files, 542 checks
  ml-contributions/experiments/     the six-panel harness and its committed result JSONs
  ml-contributions/theory/          the closed-form module the certificates check against
  ml-contributions/environment/     the heterogeneous-response reference environment
  paper/make_figures.py             regenerates every figure from the committed JSONs

Reproducing
-----------

Python 3.12, numpy, scipy (scipy is used only by verify_ensemble_intervals.py,
for the exact Clopper-Pearson interval), matplotlib for the figures.

    for f in ml-contributions/certificates/verify_*.py; do python "$f"; done
    python ml-contributions/experiments/run_panels.py
    python paper/make_figures.py

The full suite is CPU-only and runs in about twenty seconds on one commodity
laptop core. Every panel is deterministic from a (config, seed) pair.

Panel 1 is the paper's one measured result. It runs against the external
order-flow simulator of the cited preprint, which is prior work and is not
redistributed here; its measured outputs are committed under
ml-contributions/experiments/results/ and are reproduced by the rest of the
suite bit for bit.
"""


def git_files(prefix):
    out = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", "HEAD", prefix],
                         capture_output=True, check=True).stdout.decode("utf-8")
    return [line for line in out.splitlines() if line.strip()]


def git_blob(path):
    return subprocess.run(["git", "-C", str(REPO), "show", "HEAD:" + path],
                          capture_output=True, check=True).stdout


def main():
    paths = []
    for m in MEMBERS:
        found = git_files(m)
        if not found:
            sys.exit("nothing in git matches %s" % m)
        paths.extend(found)
    paths = sorted(set(p for p in paths if not p.endswith(".pyc") and "__pycache__" not in p))

    leaks = []
    blobs = {}
    for p in paths:
        data = git_blob(p)
        blobs[p] = data
        text = data.decode("utf-8", "replace")
        for pat in FORBIDDEN:
            if re.search(pat, text):
                leaks.append((p, pat))
    if leaks:
        for p, pat in leaks:
            print("LEAK  %s matches %s" % (p, pat))
        sys.exit("refusing to build: %d leak(s)" % len(leaks))

    if not PDF.exists():
        sys.exit("missing %s -- build the paper first" % PDF)

    HERE.mkdir(exist_ok=True)
    (HERE / "main.pdf").write_bytes(PDF.read_bytes())

    zpath = HERE / "econml-supplementary.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", SUPP_README)
        for p in paths:
            # strip the leading econml/ so the zip roots at the paper's own tree
            z.writestr(p[len("econml/"):], blobs[p])

    print("main.pdf                 %8.1f KB" % (len(PDF.read_bytes()) / 1024))
    print("econml-supplementary.zip %8.1f KB, %d files, no leaks"
          % (zpath.stat().st_size / 1024, len(paths) + 1))
    for p in paths:
        print("    %s" % p[len("econml/"):])


if __name__ == "__main__":
    main()
