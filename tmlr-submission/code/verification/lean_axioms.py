"""Build the Lean development and check which axioms every public theorem depends on.

Lists every `theorem` declared in lean/CreditCert/*.lean (private helpers are skipped; they are covered through
the public theorems that use them), asks Lean for `#print axioms` of each, and checks that only Lean's three
standard axioms appear: propext, Classical.choice and Quot.sound.  Writes results/lean_axioms.log.

Usage: python verification/lean_axioms.py        (needs `lake` on PATH or in ~/.elan/bin)
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAN = os.path.join(ROOT, "lean")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}


def main():
    env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ.get("PATH", ""))
    build = subprocess.run(["lake", "build", "CreditCert"], cwd=LEAN, env=env, capture_output=True, text=True)
    last = [l for l in (build.stdout + build.stderr).splitlines() if l.strip()][-1]
    names, per_file = [], {}
    for path in sorted(glob.glob(os.path.join(LEAN, "CreditCert", "*.lean"))):
        src = open(path).read()
        assert "sorry" not in re.sub(r"/-.*?-/", "", src, flags=re.S), f"sorry in {path}"
        assert not re.search(r"^\s*axiom\s", src, flags=re.M), f"axiom declared in {path}"
        found = re.findall(r"^theorem\s+([^\s({:\[]+)", src, flags=re.M)
        per_file[os.path.basename(path)] = len(found)
        names += found
    assert len(names) == len(set(names)), "duplicate theorem names"
    check = os.path.join(LEAN, "AxiomCheck.lean")
    with open(check, "w") as f:
        f.write("import CreditCert\n" + "".join(f"#print axioms CreditCert.{n}\n" for n in names))
    try:
        res = subprocess.run(["lake", "env", "lean", "AxiomCheck.lean"], cwd=LEAN, env=env, capture_output=True, text=True)
    finally:
        os.remove(check)
    text = " ".join((res.stdout + res.stderr).split())
    seen, bad = {}, []
    for m in re.finditer(r"'CreditCert\.([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", text):
        axioms = {a.strip() for a in (m.group(3) or "").split(",") if a.strip()}
        seen[m.group(1)] = axioms
        if not axioms <= STANDARD:
            bad.append(f"{m.group(1)}: {sorted(axioms - STANDARD)}")
    missing = [n for n in names if n not in seen]
    out = [last, "non-standard lines:" + "".join("\n  " + b for b in bad),
           "not reported:" + "".join("\n  " + n for n in missing),
           f"theorems checked: {len(seen)}", f"declared: {len(names)}",
           "by file: " + ", ".join(f"{k} {v}" for k, v in per_file.items())]
    open(os.path.join(ROOT, "results", "lean_axioms.log"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    ok = build.returncode == 0 and not bad and not missing and len(seen) == len(names)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
