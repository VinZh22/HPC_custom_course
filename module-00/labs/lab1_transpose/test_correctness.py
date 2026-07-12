"""Correctness tests for Lab 1 (transpose), reference = NumPy.

Run from the repo root:  pytest module-00/labs/lab1_transpose
"""
import shutil
import subprocess
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent
BIN = LAB / "transpose"


def build():
    r = subprocess.run(["make", "-C", str(LAB)], capture_output=True, text=True)
    assert r.returncode == 0, f"build failed:\n{r.stdout}\n{r.stderr}"


def run(n, m):
    build()
    r = subprocess.run([str(BIN), str(n), str(m)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"run failed (exit {r.returncode}):\n{r.stderr}"
    return parse(r.stdout)


def parse(out):
    """Output format: '# <name> <rows> <cols>' headers, then one row per line."""
    mats, name, rows = {}, None, []
    for line in out.splitlines():
        if line.startswith("# "):
            if name is not None:
                mats[name] = np.array(rows)
            name = line.split()[1]
            rows = []
        elif line.strip():
            rows.append([float(x) for x in line.split()])
    if name is not None:
        mats[name] = np.array(rows)
    return mats


def expected_A(n, m):
    i, j = np.mgrid[0:n, 0:m]
    return (i * 100000 + j).astype(float)


def test_rectangular():
    mats = run(7, 5)
    np.testing.assert_allclose(mats["A"], expected_A(7, 5),
                               err_msg="A doesn't match the fill pattern")
    assert mats["B"].shape == (5, 7), "B must be M x N"
    np.testing.assert_allclose(mats["B"], mats["A"].T,
                               err_msg="B must equal A transposed")


def test_rectangular_awkward_sizes():
    mats = run(31, 17)  # non-square, non-power-of-two: catches swapped i/j
    np.testing.assert_allclose(mats["B"], mats["A"].T)


def test_square_inplace():
    mats = run(6, 6)
    assert "C" in mats, "square input must also print C (in-place transpose)"
    np.testing.assert_allclose(mats["C"], mats["A"].T,
                               err_msg="in-place transpose is wrong")


def test_valgrind_clean():
    build()
    assert shutil.which("valgrind"), \
        "valgrind not installed — it's part of the Module 0 toolchain (lab 0)"
    r = subprocess.run(
        ["valgrind", "--error-exitcode=99", "--leak-check=full",
         "--errors-for-leak-kinds=definite,possible", str(BIN), "8", "8"],
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, \
        f"valgrind found problems (leaks are part of the spec):\n{r.stderr[-3000:]}"
