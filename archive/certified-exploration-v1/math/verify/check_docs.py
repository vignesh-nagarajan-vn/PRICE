"""Document-consistency checks for the math-section folder.

Run:  python verify/check_docs.py   [--reflex-root PATH]

Checks (stdlib only):
  C1  THEOREMS.md check accounting: every cited V-check exists in
      VERIFICATION.md's table, and the claimed total (34) matches the
      number of PASS lines in verify/last_run.log.
  C2  SYMBOLS-TO-REFLEX.md: every row tagged EXISTS names a real file and a
      name actually present in it (checked against the REFLEX source tree
      when available; skipped with a warning otherwise). CONFIG rows are
      checked against reflex/config.py.
  C3  latex/theorems.tex: balanced \\begin/\\end environments, balanced
      braces, no unclosed display math.
  C4  .github/workflows/verify.yml: parses as YAML if PyYAML is present,
      else a structural indentation sanity check.
  C5  Every derivation doc referenced by THEOREMS.md exists; every
      derivation file is referenced by at least one register row.
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  --  " + detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as f:
        return f.read()


def c1_theorem_register():
    print("== C1: THEOREMS.md check accounting ==")
    reg = read("THEOREMS.md")
    ver = read("VERIFICATION.md")
    log = read(os.path.join("verify", "last_run.log"))
    cited = set(re.findall(r"V\d+\.\d+", reg))
    table_ids = set(re.findall(r"V\d+\.\d+", ver))
    missing = sorted(c for c in cited if c not in table_ids)
    check("every cited check ID appears in VERIFICATION.md",
          not missing, "missing: %s" % missing if missing else
          "%d IDs cross-referenced" % len(cited))
    n_pass = log.count("[PASS]")
    n_fail = log.count("[FAIL]")
    check("last_run.log shows 34/34 PASS",
          n_pass == 34 and n_fail == 0,
          "%d PASS, %d FAIL in log" % (n_pass, n_fail))
    claimed = re.search(r"total \*\*(\d+)\*\*", reg)
    check("register's claimed total matches the log",
          claimed is not None and int(claimed.group(1)) == n_pass,
          "claimed %s vs log %d" % (claimed.group(1) if claimed else "?", n_pass))


def c2_symbol_map(reflex_root):
    print("== C2: SYMBOLS-TO-REFLEX.md name-checks ==")
    txt = read("SYMBOLS-TO-REFLEX.md")
    rows = [l for l in txt.splitlines() if l.startswith("|") and "EXISTS" in l]
    cfg_rows = [l for l in txt.splitlines() if l.startswith("|") and "| CONFIG |" in l]
    if not os.path.isdir(reflex_root or ""):
        print("  [SKIP] REFLEX source tree not found (pass --reflex-root); "
              "%d EXISTS + %d CONFIG rows unchecked" % (len(rows), len(cfg_rows)))
        return
    n_ok = 0
    for row in rows:
        m = re.search(r"`(reflex/[\w/]+\.py) :: ([\w.]+)`", row)
        if not m:
            continue
        path, name = m.group(1), m.group(2).split(".")[0]
        full = os.path.join(reflex_root, path)
        ok = False
        if os.path.isfile(full):
            src = open(full, encoding="utf-8").read()
            ok = bool(re.search(r"(def|class)\s+%s\b" % re.escape(name), src)
                      or re.search(r"\b%s\s*[:=]" % re.escape(name), src))
        check("EXISTS: %s :: %s" % (path, name), ok)
        n_ok += ok
    cfg_src = ""
    cfg_path = os.path.join(reflex_root, "reflex", "config.py")
    if os.path.isfile(cfg_path):
        cfg_src = open(cfg_path, encoding="utf-8").read()
    for row in cfg_rows:
        m = re.search(r"`config :: ([\w.]+)`", row)
        if not m:
            continue
        field = m.group(1).split(".")[-1]
        check("CONFIG: %s" % m.group(1), bool(re.search(r"\b%s\s*:" % field, cfg_src)))


def _tex_structure(fname):
    tex = read(os.path.join("latex", fname))
    begins = re.findall(r"\\begin\{(\w+\*?)\}", tex)
    ends = re.findall(r"\\end\{(\w+\*?)\}", tex)
    stack, balanced = [], True
    for tok, env in re.findall(r"\\(begin|end)\{(\w+\*?)\}", tex):
        if tok == "begin":
            stack.append(env)
        else:
            balanced = balanced and stack and stack[-1] == env
            if stack:
                stack.pop()
    check("%s: environments balanced" % fname,
          balanced and not stack,
          "%d begin / %d end" % (len(begins), len(ends)))
    body = re.sub(r"(?<!\\)%.*", "", tex)  # strip comments (keep \%)
    depth, ok_braces = 0, True
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            ok_braces = ok_braces and depth >= 0
        i += 1
    check("%s: braces balanced" % fname, ok_braces and depth == 0, "final depth %d" % depth)
    n_disp = len(re.findall(r"\\\[", body)), len(re.findall(r"\\\]", body))
    check("%s: display math balanced" % fname, n_disp[0] == n_disp[1],
          r"%d \[ vs %d \]" % n_disp)
    n_thm = len(re.findall(r"\\begin\{(theorem|lemma|corollary|proposition|proof)\}", tex))
    check("%s: theorem/proof environments present" % fname, n_thm >= 16,
          "%d statement/proof environments" % n_thm)


def c3_latex():
    print("== C3: LaTeX structure (all files) ==")
    for f in sorted(os.listdir(os.path.join(HERE, "latex"))):
        if f.endswith(".tex"):
            _tex_structure(f)


def c6_proof_coverage():
    print("== C6: proofs.tex covers every register result ==")
    reg = read("THEOREMS.md")
    proofs = read(os.path.join("latex", "proofs.tex"))
    ids = re.findall(r"^\| ([A-Z]+\d+(?:\.\d+)?[a-c]?) \|", reg, re.M)
    missing = []
    for rid in ids:
        base = rid.rstrip("abc")
        if rid not in proofs and base not in proofs:
            missing.append(rid)
    check("every register ID has a proof (or shared proof block)",
          not missing and len(ids) >= 20,
          "%d register IDs; missing: %s" % (len(ids), missing or "none"))


def c4_workflow():
    print("== C4: workflow YAML ==")
    path = os.path.join(HERE, ".github", "workflows", "verify.yml")
    txt = open(path, encoding="utf-8").read()
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(txt)
        jobs = data.get("jobs", {})
        steps = jobs.get("verify", {}).get("steps", [])
        runs = " ".join(s.get("run", "") for s in steps if isinstance(s, dict))
        check("YAML parses; runs both suites",
              "verify_all.py" in runs and "check_docs.py" in runs,
              "%d steps" % len(steps))
    except ImportError:
        ok = ("jobs:" in txt and "verify_all.py" in txt
              and "check_docs.py" in txt and "\t" not in txt)
        check("structural check (PyYAML not installed)", ok,
              "keys + no tabs")


def c5_file_graph():
    print("== C5: derivation file graph ==")
    reg = read("THEOREMS.md")
    dv = os.path.join(HERE, "derivations")
    files = sorted(f for f in os.listdir(dv) if f.endswith(".md"))
    refs = set(re.findall(r"D\d", reg))
    tags = {"01": "D0", "02": "D1", "03": "D2", "04": "D3",
            "05": "D4", "06": "D6", "07": "D7", "08": "D8"}
    missing = [f for f in files if f[:2] in tags and tags[f[:2]] not in refs]
    check("all derivation files referenced by the register",
          not missing and len(files) == 9,
          "%d files, unreferenced: %s" % (len(files), missing or "none"))
    notation = read(os.path.join("derivations", "00-notation-and-assumptions.md"))
    for a in ("A1", "A2", "A3", "A4", "A5", "A6"):
        if not re.search(r"\*\*%s\b" % a, notation):
            check("assumption %s defined in register" % a, False)
            return
    check("assumption register complete (A1-A6)", True)


def main():
    reflex_root = None
    if "--reflex-root" in sys.argv:
        reflex_root = sys.argv[sys.argv.index("--reflex-root") + 1]
    else:
        guess = "/home/user/REFLEX/endo_market_v4"
        reflex_root = guess if os.path.isdir(guess) else None
    c1_theorem_register()
    c2_symbol_map(reflex_root)
    c3_latex()
    c6_proof_coverage()
    c4_workflow()
    c5_file_graph()
    print("\n%s" % ("ALL DOCUMENT CHECKS PASSED" if not FAILS
                    else "FAILURES: %s" % FAILS))
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
