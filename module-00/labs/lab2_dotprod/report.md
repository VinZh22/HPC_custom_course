# Lab 2 Report — dot product & honest timing

<!-- Learner-written (TUTOR.md rule 5). Template per MODULE_FORMAT.md. -->

## 1. Prediction — write BEFORE the first timed run

- Expected `-O3` vs `-O0` speedup: **___×** — reasoning:
- At `-O3`, the loop's limit will be (arithmetic | loading data): **___** — reasoning:

*(Gut answers are fine — Module 1 gives you the roofline to answer this rigorously.
The point is to have a number on record before the machine gives you one.)*

## 2. Measured

- CPU: · gcc version: · exact commands:

| Binary | best (s) | median (s) | GFLOP/s | GB/s |
|---|---|---|---|---|
| `dotprod_O0` | | | | |
| `dotprod_O3` | | | | |

- `bench.py` verdict:

## 3. Gap analysis

Why did prediction and measurement differ? What did `-O3` actually do?
(`gcc -O3 -march=native -fopt-info-vec dotprod.c` tells you whether it vectorized.)

## 4. Evidence & harness defense

One sentence each — you implemented these, now defend them:
- Why the warm-up call?
- Why median rather than mean?
- What exactly breaks without `keep()`?

Optional: `perf stat -e instructions,cycles ./dotprod_O3 200000 100` — compare
instructions-per-cycle between the two binaries and interpret.
