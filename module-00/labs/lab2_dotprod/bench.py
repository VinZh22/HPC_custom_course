#!/usr/bin/env python3
"""Lab 2 bench gate: is -O3 really faster — and is your harness telling the truth?

PASS requires ALL of:
  - median(-O0) / median(-O3) >= 3          (the actual perf target)
  - speedup <= 100                          (higher almost always means -O3 deleted
                                             your loop: is keep() inside the timed region?)
  - 0 < GB/s(-O3) <= 500                    (0 means TODO 3 not done; >500 from a
                                             single core means the timer measured nothing)

Self-contained on purpose: you build the real harness (common/bench) in Module 1 Lab 4;
Module 0 predates it (stated deviation, module README).
"""
import re
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
N, REPS, TARGET = 200_000, 200, 3.0


def die(msg):
    print(msg)
    print("FAIL")
    sys.exit(1)


def run(binary):
    p = subprocess.run([str(LAB / binary), str(N), str(REPS)],
                       capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        die(f"{binary} exited {p.returncode}:\n{p.stderr}")
    return {k: float(v) for k, v in re.findall(r"(\w+)=([-+0-9.eE]+)", p.stdout)}


def main():
    b = subprocess.run(["make", "-C", str(LAB)], capture_output=True, text=True)
    if b.returncode != 0:
        die(f"build failed:\n{b.stderr}")

    o0, o3 = run("dotprod_O0"), run("dotprod_O3")
    speedup = o0["median"] / o3["median"]

    print(f"n={N} reps={REPS}")
    print(f"-O0:              median {o0['median']:.3e} s   {o0['gbps']:6.2f} GB/s")
    print(f"-O3 -march=native: median {o3['median']:.3e} s   {o3['gbps']:6.2f} GB/s")
    print(f"speedup: {speedup:.1f}x   (target: >= {TARGET}x)")

    if o3["gbps"] <= 0:
        die("GB/s is 0 — TODO 3 (flops/bytes accounting) isn't done")
    if speedup > 100:
        die("speedup > 100x is not plausible for this loop — the compiler almost "
            "certainly deleted the timed work. Is keep() called inside the timed region?")
    if o3["gbps"] > 500:
        die(f"{o3['gbps']:.0f} GB/s from one core is beyond DRAM and cache reality — "
            "the harness is measuring an empty loop.")
    if speedup < TARGET:
        die(f"speedup {speedup:.1f}x < {TARGET}x — if both binaries built fine, "
            "suspect the harness (warm-up? per-rep timing?) before suspecting gcc.")

    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
