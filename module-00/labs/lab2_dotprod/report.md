# Lab 2 Report — dot product & honest timing

<!-- Learner-written (TUTOR.md rule 5). Template per MODULE_FORMAT.md. -->

## 1. Prediction — write BEFORE the first timed run

- Expected `-O3` vs `-O0` speedup: **2×** — i don't know what optimizations it does and why it would be faster:
- At `-O3`, the loop's limit will be (arithmetic | loading data): **loading data** — because arithmetic got optimized by O3:

*(Gut answers are fine — Module 1 gives you the roofline to answer this rigorously.
The point is to have a number on record before the machine gives you one.)*

## 2. Measured

- CPU: Intel Xeon Platinum 8558, 128 vCPU (docker inside a VM, topology virtualized)
  · gcc version: 13.3.0 (Ubuntu 24.04) · exact commands:

./dotprod_O3 200000 200 
./dotprod_O0 200000 200 

| Binary | best (s) | median (s) | GFLOP/s | GB/s |
|---|---|---|---|---|
| `dotprod_O0` | 4.231e-04| 4.488e-04| 0.89| 7.13|
| `dotprod_O3` | 1.010e-04| 1.015e-04| 3.94| 31.52|

- `bench.py` verdict: PASS, 4.1× (re-run 2026-07-17 with the fixed harness: warm-up,
  keep() in timed region, correct median, no leak — medians unchanged from the table)

## 3. Gap analysis

*(Completed by Claude 2026-07-17, per format change — prediction/commentary deliverables
dropped; learner-authorized.)*

Predicted 2×, measured 4.1×. `gcc -O3 -march=native -fopt-info-vec dotprod.c` reports
`loop vectorized using 32 byte vectors` — the loop now processes 4 doubles per AVX2
instruction instead of 1, which is where the extra ~2× over the prediction came from.
The `-O0` binary additionally pays for no register allocation (every `res` update goes
through the stack). At n=200000 the arrays are 3.2 MB — resident in the 260 MiB L3 —
so 31.5 GB/s is cache-load throughput, not DRAM: the "loading data" limit predicted in
§1 is real, but the data loads from cache, not memory (Module 1 makes this rigorous).

## 4. Evidence & harness defense

One sentence each — you implemented these, now defend them:
- Why the warm-up call? Pays the one-time costs (page faults, cold caches, CPU frequency
  ramp) outside the measurement *(refined by Claude — original: "make the CPU warmup for
  the clock")*
- Why median rather than mean? in case of some outlier
- What exactly breaks without `keep()`? The optimization may make the loop empty

Optional: `perf stat -e instructions,cycles ./dotprod_O3 200000 100` — compare
instructions-per-cycle between the two binaries and interpret.
Working inside a docker inside a vm (no sudo in the vm), do not have permission to run the command