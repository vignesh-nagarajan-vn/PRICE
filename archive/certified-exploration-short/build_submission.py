"""Regenerate math-ai/submission/ from paper/ and supporting/.

This is the only thing that writes into submission/. Never hand-edit a file
in there; change paper/ or supporting/ and run this again.

    python math-ai/build_submission.py
"""
import hashlib
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(ROOT, 'paper')
SUPPORT = os.path.join(ROOT, 'supporting')
OUT = os.path.join(ROOT, 'submission')

EXCLUDE_DIRS = {'__pycache__', '.pytest_cache', '.git', '.ipynb_checkpoints',
                '.mypy_cache', '.ruff_cache'}
# LaTeX build droppings. '.log' is deliberately absent: supporting/ holds no
# LaTeX build, and the two .log files it does hold are run records that
# Appendix D names by path (posk-pipeline/results/full_run.log and
# mlxor-derivations/verify/last_run.log). Excluding the suffix wholesale
# shipped an appendix that pointed at a file not in the archive.
EXCLUDE_SUFFIX = ('.pyc', '.pyo', '.aux', '.out', '.fls',
                  '.fdb_latexmk', '.blg', '.synctex.gz')

# Anything matching these would be a LaTeX log rather than a run record, and
# would mean supporting/ had picked up a build tree.
LATEX_LOG_NAMES = {'main.log', 'appendix.log', 'paper.log'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)

    src_pdf = os.path.join(PAPER, 'main.pdf')
    dst_pdf = os.path.join(OUT, 'main.pdf')
    shutil.copy2(src_pdf, dst_pdf)
    print('main.pdf         ', sha256(dst_pdf))
    assert sha256(src_pdf) == sha256(dst_pdf)

    zip_path = os.path.join(OUT, 'supplementary.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(SUPPORT):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for name in sorted(files):
                if name.endswith(EXCLUDE_SUFFIX) or name in LATEX_LOG_NAMES:
                    continue
                full = os.path.join(base, name)
                arc = os.path.relpath(full, SUPPORT).replace(os.sep, '/')
                zf.write(full, arc)
                count += 1
    print('supplementary.zip', sha256(zip_path), '(%d files)' % count)


if __name__ == '__main__':
    main()
