# Course Progression

Single source of truth for where the learner is. Claude reads this at the start of every
session instead of asking for context, and updates it whenever a lab or module changes state.

**Legend:** `⬜ not started` · `🔶 in progress` · `✅ done` (tests green + bench PASS) ·
`✅🅰 done with override: solve`

## Current Status

- **Current module:** 1 — not yet scaffolded (Module 0 ✅ closed 2026-07-17)
- **Current lab:** —
- **Next action:** compare Module 0 work against the `solutions` branch (now allowed);
  scaffold Module 1 under the new format (results-only + MCQ + questions.md — see
  MODULE_FORMAT.md format decision 2026-07-17)
- **Last updated:** 2026-07-17

## Modules

| # | Module | Status |
|---|---|---|
| 0 | Setup, C Refresher & Know Your Cluster | ✅ |
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

- [x] Lab 0 — environment gate ✅ (all REQUIRED ok 2026-07-16; single direct-access GPU
  server, scheduler MISS recorded as valid in cluster report)
- [x] Lab 1 — ✅ tests green incl. valgrind (4/4, re-verified 2026-07-17), `size_t`
  indices fixed after review; notebook-prediction requirement dropped with the
  lab-notebook deliverable (format decision 2026-07-17)
- [x] Lab 2 — ✅ code all learner-written, review-clean (warm-up, keep() in timed
  region, correct median, no leak); tests 4/4 + bench PASS, stable 4.0× over 5 runs
  (2026-07-17; bench gate switched to best-vs-best scoring for shared-machine noise);
  report.md gap analysis completed by Claude (learner-authorized, format change)
- [x] Diagnose — ✅ all three defects found and fixed by learner, tests 2/2 incl.
  valgrind clean (2026-07-17); findings.md Defect 1 evidence + after-fix summary
  backfilled by Claude (learner-authorized — the applied fix matched the diagnosis)
- [x] Lab 3 — ✅ check_report PASS (2026-07-17); STREAM valid (array ≈4× L3, Triad
  72.6 GB/s, VM caveat recorded), §2 dense GPU peaks with datasheet URL, topology
  interpretation expanded by Claude

Notes: scaffolded 2026-07-12; closed ✅ 2026-07-17. All code learner-written, all gates
verified green same day. Interpretation/commentary sections completed by Claude per the
2026-07-17 format decision (see MODULE_FORMAT.md): future modules use results-only
deliverables + MCQ self-checks + questions.md; lab-notebook.md dropped as a deliverable.
Reference solutions on the `solutions` branch — comparison now unlocked.
