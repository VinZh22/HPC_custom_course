"""Done-gate for diagnose/flaky_wordcount: exact correct output AND a valgrind-clean run.

Run from the repo root:  pytest module-00/diagnose/flaky_wordcount
(Expected to be red until you've found and fixed the defects.)
"""
import shutil
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent
INP = D / "sample_input.txt"


def build():
    r = subprocess.run(["make", "-C", str(D)], capture_output=True, text=True)
    assert r.returncode == 0, f"build failed:\n{r.stdout}\n{r.stderr}"


def expected_output():
    """Reference semantics, independent of the C code."""
    words = INP.read_text().split()
    counts = {}
    longest = None
    for w in words:
        c0 = w[0].lower()
        if "a" <= c0 <= "z":
            counts[c0] = counts.get(c0, 0) + 1
        if longest is None or len(w) > len(longest):
            longest = w
    lines = [f"words: {len(words)}"]
    lines += [f"{c}: {counts[c]}" for c in sorted(counts)]
    lines.append(f"longest: {longest}")
    return "\n".join(lines) + "\n"


def test_output_correct():
    build()
    with open(INP) as f:
        r = subprocess.run([str(D / "wordfreq")], stdin=f,
                           capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"crashed (exit {r.returncode}):\n{r.stderr}"
    assert r.stdout == expected_output(), \
        f"output differs from reference:\n--- got ---\n{r.stdout}\n--- expected ---\n{expected_output()}"


def test_valgrind_clean():
    build()
    assert shutil.which("valgrind"), \
        "valgrind not installed — it's part of the Module 0 toolchain (lab 0)"
    with open(INP) as f:
        r = subprocess.run(
            ["valgrind", "--error-exitcode=99", "--leak-check=full",
             "--errors-for-leak-kinds=definite,possible", str(D / "wordfreq")],
            stdin=f, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"valgrind is not clean:\n{r.stderr[-4000:]}"
