"""Correctness tests for Lab 2 (dot product), reference = NumPy on bit-identical inputs.

Run from the repo root:  pytest module-00/labs/lab2_dotprod
"""
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

LAB = Path(__file__).resolve().parent
N = 10_000


def build():
    r = subprocess.run(["make", "-C", str(LAB)], capture_output=True, text=True)
    assert r.returncode == 0, f"build failed:\n{r.stdout}\n{r.stderr}"


def run(binary, n=N, reps=5):
    build()
    return subprocess.run([str(LAB / binary), str(n), str(reps)],
                          capture_output=True, text=True, timeout=120)


def fields(out):
    return {k: float(v) for k, v in re.findall(r"(\w+)=([-+0-9.eE]+)", out)}


def lcg_fill(n, seed):
    """Bit-exact replica of fill() in dotprod.c."""
    s = seed
    out = np.empty(n)
    for i in range(n):
        s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
        out[i] = (s >> 8) / 16777216.0
    return out


EXPECTED = float(np.dot(lcg_fill(N, 1), lcg_fill(N, 2)))


@pytest.mark.parametrize("binary", ["dotprod_O0", "dotprod_O3"])
def test_dot_value(binary):
    # Checked even while the timing harness (TODO 2) is unfinished.
    r = run(binary)
    f = fields(r.stdout)
    assert "dot" in f, f"no dot=... line in output:\n{r.stdout}\n{r.stderr}"
    assert f["dot"] == pytest.approx(EXPECTED, rel=1e-9), \
        "dot product disagrees with numpy on identical inputs"


@pytest.mark.parametrize("binary", ["dotprod_O0", "dotprod_O3"])
def test_harness(binary):
    r = run(binary)
    assert r.returncode == 0, f"exit {r.returncode}:\n{r.stderr}"
    f = fields(r.stdout)
    assert f["best"] > 0 and f["median"] > 0, "non-positive times"
    assert f["best"] <= f["median"] * (1 + 1e-9), \
        "the best rep cannot be slower than the median — check your sort/selection"
