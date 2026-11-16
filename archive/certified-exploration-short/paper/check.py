import re, subprocess, sys, hashlib, os

log = open('main.log', encoding='utf-8', errors='replace').read()
print('Overfull boxes      :', len(re.findall(r'Overfull', log)))
print('Underfull hbox      :', len(re.findall(r'Underfull \\hbox', log)))
print('Underfull vbox      :', len(re.findall(r'Underfull \\vbox', log)))
print('LaTeX Warning lines :')
for line in log.splitlines():
    if 'LaTeX Warning' in line or 'Citation' in line and 'undefined' in line:
        print('   ', line.strip())

txt = subprocess.run(['pdftotext', 'main.pdf', '-'], capture_output=True, text=True,
                     encoding='utf-8', errors='replace').stdout
pages = txt.split('\f')
print('\nTotal pages         :', len([p for p in pages if p.strip()]))
for i, p in enumerate(pages, 1):
    if not p.strip():
        continue
    head = ' '.join(p.split())[:90]
    print('  p%-2d %s' % (i, head))

print('\nEm dashes in PDF text:', txt.count('—'), '| "---" occurrences:', txt.count('---'))
for name in ['Vignesh', 'Nagarajan', 'nrvignesh', 'gmail', 'github.com', 'REFLEX-Branch']:
    hits = [l.strip() for l in txt.splitlines() if name.lower() in l.lower()]
    print('  %-14s %d %s' % (name, len(hits), hits[:2]))
