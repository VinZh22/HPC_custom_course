#!/usr/bin/env python3
"""Lab 3 gate: PASSes when ../../cluster-report.md has no TODO left, every section is
present, and a numeric STREAM Triad result is recorded.

It cannot check that your numbers are RIGHT — the next twenty weeks will.
"""
import re
import sys
from pathlib import Path

REPORT = Path(__file__).resolve().parents[2] / "cluster-report.md"

SECTIONS = [
    "## 1. Node inventory",
    "## 2. GPU peak numbers (from the datasheet)",
    "## 3. Intra-node topology",
    "## 4. Inter-node fabric",
    "## 5. Scheduler",
    "## 6. Storage",
    "## 7. Measured — STREAM memory bandwidth",
    "## 8. Numbers to know by heart",
]


def main():
    if not REPORT.exists():
        print(f"FAIL — {REPORT} not found")
        return 1

    text = REPORT.read_text()
    lines = text.splitlines()
    ok = True

    for s in SECTIONS:
        if s not in text:
            print(f"missing section: {s}")
            ok = False

    todos = [(i, l.strip()) for i, l in enumerate(lines, 1) if "TODO" in l]
    if todos:
        print(f"{len(todos)} TODO(s) remain:")
        for i, l in todos[:20]:
            print(f"  line {i}: {l[:90]}")
        if len(todos) > 20:
            print(f"  ... and {len(todos) - 20} more")
        ok = False

    # a digit after the word "Triad" on some line = a recorded measurement
    if not any(re.search(r"\d", l.split("Triad", 1)[1]) for l in lines if "Triad" in l):
        print("no numeric STREAM Triad result found")
        ok = False

    print("PASS — cluster-report.md complete" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
