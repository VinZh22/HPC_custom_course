# Course Progression

Single source of truth for where the learner is. Claude reads this at the start of every
session instead of asking for context, and updates it whenever a lab or module changes state.

**Legend:** `⬜ not started` · `🔶 in progress` · `✅ done` (tests green + bench PASS) ·
`✅🅰 done with override: solve`

## Current Status

- **Current module:** 0 — scaffolded, ready to start
- **Current lab:** —
- **Next action:** run `python3 module-00/labs/lab0_setup/check_env.py` (Lab 0)
- **Last updated:** 2026-07-12

## Modules

| # | Module | Status |
|---|---|---|
| 0 | Setup, C Refresher & Know Your Cluster | ⬜ |
| 1 | Hardware Architecture & the Performance Mental Model | ⬜ |
| 2 | CPU Parallelism: Threads, SIMD, OpenMP | ⬜ |
| 3 | GPU Architecture & CUDA Programming | ⬜ |
| 4 | Communication: MPI, Collectives & NCCL | ⬜ |
| 5 | Distributed Training of Deep Networks | ⬜ |
| 6 | Optimized Inference & Serving | ⬜ |
| 7 | Clusters, Systems & Production Concerns | ⬜ |
| 8 | Capstone | ⬜ |

<!-- When a module is scaffolded, add a "## Module XX" section here with one checkbox per
lab (from its README.md) and a one-line Notes field. No narrative — details live in the
module's lab-notebook.md and report.md files. Labs are checked ✅ only with evidence. -->

## Module 00 — Setup, C Refresher & Know Your Cluster

- [ ] Lab 0 — environment gate (`check_env.py` all-green, workstation + cluster)
- [ ] Lab 1 — transpose (pytest green, incl. valgrind test; notebook predictions logged)
- [ ] Lab 2 — dot product & timing harness (pytest green + `bench.py` PASS + report.md)
- [ ] Diagnose — flaky_wordcount (pytest green + findings.md filled before the fix)
- [ ] Lab 3 — cluster report (`check_report.py` PASS)

Notes: scaffolded 2026-07-12; reference solutions pending — `solutions` branch needs a first commit on `main`.
