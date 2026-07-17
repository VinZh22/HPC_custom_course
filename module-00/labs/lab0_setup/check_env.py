#!/usr/bin/env python3
"""
Lab 0 — environment gate for Module 0, plus a preview of what later modules need.

Run it on every machine you intend to work on — your workstation AND the cluster:

    python3 check_env.py

Done when: every REQUIRED line shows [ ok ] (exit code 0). The [cluster] block must
pass on the cluster before Lab 3. "later" lines name the module that will need them —
install those when that module starts, not today.
"""
import importlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def has_bin(*names):
    """True if any of the given executables is on PATH."""
    return any(shutil.which(n) for n in names)


def can_import(mod):
    try:
        importlib.import_module(mod)
        return True
    except Exception:
        return False


def cuda_available():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def c_toolchain_works():
    """Compile and run a hello-world end to end — catches broken headers/linkers,
    not just a missing compiler binary."""
    cc = shutil.which("gcc") or shutil.which("cc") or shutil.which("clang")
    if not cc:
        return False
    src = '#include <stdio.h>\nint main(void){puts("ok");return 0;}\n'
    with tempfile.TemporaryDirectory() as d:
        s = Path(d) / "t.c"
        s.write_text(src)
        exe = Path(d) / "t"
        try:
            c = subprocess.run([cc, str(s), "-o", str(exe)], capture_output=True, timeout=60)
            if c.returncode != 0:
                return False
            r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
            return r.returncode == 0 and r.stdout.strip() == "ok"
        except Exception:
            return False


REQUIRED = [
    ("python >= 3.9",                 sys.version_info >= (3, 9),
     "install a recent python3"),
    ("gcc (or clang)",                has_bin("gcc", "clang"),
     "apt install gcc   (cluster: module load gcc)"),
    ("C toolchain builds & runs",     c_toolchain_works(),
     "compiler present but hello-world failed — headers? (apt install libc6-dev)"),
    ("make",                          has_bin("make"),
     "apt install make"),
    ("gdb",                           has_bin("gdb"),
     "apt install gdb"),
    ("valgrind",                      has_bin("valgrind"),
     "apt install valgrind — the diagnose exercise gates on it"),
    ("git",                           has_bin("git"),
     "apt install git"),
    ("numpy",                         can_import("numpy"),
     "pip install numpy — correctness tests compare against it"),
    ("pytest",                        can_import("pytest"),
     "pip install pytest — every lab's tests run with it"),
]

CLUSTER = [  # needed on the cluster for Lab 3
    ("nvidia-smi",                    has_bin("nvidia-smi"),
     "must work on a GPU node"),
    ("scheduler (srun/sbatch/qsub)",  has_bin("srun", "sbatch", "qsub"),
     "none found is a valid answer (direct-access server) — record it in the "
     "cluster report instead of guessing"),
    ("numactl",                       has_bin("numactl"),
     "apt install numactl — NUMA layout for the report"),
]

LATER = [
    ("matplotlib",             can_import("matplotlib"), "Module 1 (roofline plots)"),
    ("perf",                   has_bin("perf"),          "Modules 1–2 (CPU profiling)"),
    ("torch",                  can_import("torch"),      "Module 3 onward"),
    ("torch sees a GPU",       cuda_available(),         "Module 3 (fine if false on a laptop)"),
    ("triton",                 can_import("triton"),     "Module 3 (lab 5)"),
    ("nsys (Nsight Systems)",  has_bin("nsys"),          "Module 3 onward (timeline profiling)"),
    ("ncu (Nsight Compute)",   has_bin("ncu"),           "Module 3 onward (kernel profiling)"),
    ("py-spy",                 has_bin("py-spy"),        "Module 7 (data-pipeline debugging)"),
    ("cmake",                  has_bin("cmake"),         "occasionally, Module 3 onward"),
]


def show(rows, hint_prefix=""):
    missing = 0
    for name, ok, hint in rows:
        mark = "[ ok ]" if ok else "[MISS]"
        line = f"  {mark} {name}"
        if not ok:
            line += f"   -> {hint_prefix}{hint}"
            missing += 1
        print(line)
    return missing


def main():
    print("Module 0 environment gate\n")
    print("REQUIRED now (labs 1-2 + diagnose):")
    missing = show(REQUIRED)
    print("\n[cluster] Needed on the cluster for Lab 3:")
    cluster_missing = show(CLUSTER)
    print("\nNeeded by later modules (informational today):")
    show(LATER, hint_prefix="needed by ")

    print()
    if missing:
        print(f"FAIL — {missing} required item(s) missing. Fix and re-run.")
        return 1
    if cluster_missing:
        print("PASS (required items) — but re-run this on the cluster: the [cluster]")
        print("block above must be green there before Lab 3.")
    else:
        print("ALL CHECKS PASSED — ready for Module 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
