"""Regenerate herd-immunity/ieee-abcss/submission/ from paper/.

This is the only thing that writes the PDF, source.zip and form-fields.txt
in submission/. Never hand-edit those; change paper/ and run this again.
UPLOAD.md in the same folder is hand-written and left alone.

    python herd-immunity/ieee-abcss/build_submission.py

It rebuilds the PDF, refuses to continue if the build has errors, overfull
boxes, undefined references, more than 10 pages or a font that is not
embedded, then writes the upload PDF, the source archive for camera-ready,
and the plain-text abstract and keywords for the web form.
"""
import hashlib
import os
import re
import shutil
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(ROOT, 'paper')
OUT = os.path.join(ROOT, 'submission')

PDF_NAME = 'abcss2026-herd-immunity.pdf'
MAX_PAGES = 10
SOURCES = ['main.tex', 'references.bib', 'main.bbl',
           'figures/fig_herd.pdf', 'figures/fig_phase.pdf',
           'figures/fig_substitution.pdf']


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    return subprocess.run(cmd, cwd=PAPER, capture_output=True, text=True,
                          errors='replace')


def build():
    run(['latexmk', '-C', 'main.tex'])
    run(['latexmk', '-pdf', '-interaction=nonstopmode', 'main.tex'])
    with open(os.path.join(PAPER, 'main.log'), errors='replace') as fh:
        log = fh.read()
    problems = [l for l in log.splitlines()
                if l.startswith('!') or 'Overfull' in l or 'undefined' in l]
    assert not problems, 'build problems:\n' + '\n'.join(problems)


def check_pdf(pdf):
    info = run(['pdfinfo', pdf]).stdout
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    assert pages <= MAX_PAGES, f'{pages} pages, limit is {MAX_PAGES}'
    fonts = run(['pdffonts', pdf]).stdout.splitlines()[2:]
    for line in fonts:
        assert 'Type 3' not in line, 'Type 3 font: ' + line
        # Columns: name type encoding emb sub uni id. Type names can hold a
        # space ("CID TrueType"), so read emb from the right.
        assert line.split()[-5] == 'yes', 'font not embedded: ' + line
    return pages


def plain(tex):
    """Turn the abstract's LaTeX into text a web form will take."""
    tex = re.sub(r'\\emph\{([^}]*)\}', r'\1', tex)
    tex = tex.replace('~', ' ').replace('$', '')
    return ' '.join(tex.split())


def main():
    build()
    src_pdf = os.path.join(PAPER, 'main.pdf')
    pages = check_pdf(src_pdf)

    # Replace only what this script writes. UPLOAD.md lives here too and is
    # hand-written.
    os.makedirs(OUT, exist_ok=True)
    for name in (PDF_NAME, 'source.zip', 'form-fields.txt'):
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            os.remove(path)

    dst_pdf = os.path.join(OUT, PDF_NAME)
    shutil.copy2(src_pdf, dst_pdf)
    assert sha256(src_pdf) == sha256(dst_pdf)
    print(f'{PDF_NAME:32s} {pages} pages  {sha256(dst_pdf)[:16]}')

    zip_path = os.path.join(OUT, 'source.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel in SOURCES:
            zf.write(os.path.join(PAPER, rel), rel)
    print(f'{"source.zip":32s} {len(SOURCES)} files')

    with open(os.path.join(PAPER, 'main.tex'), encoding='utf-8') as fh:
        tex = fh.read()
    title = re.search(r'\\title\{(.*?)\}\n', tex).group(1).replace('\\\\', '')
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',
                         tex, re.S).group(1)
    keywords = re.search(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}',
                         tex, re.S).group(1)
    with open(os.path.join(OUT, 'form-fields.txt'), 'w',
              encoding='utf-8') as fh:
        fh.write('TITLE\n' + ' '.join(title.split()) + '\n\n')
        fh.write('ABSTRACT\n' + plain(abstract) + '\n\n')
        fh.write('KEYWORDS\n' + plain(keywords) + '\n')
    print(f'{"form-fields.txt":32s} title, abstract, keywords')


if __name__ == '__main__':
    main()
