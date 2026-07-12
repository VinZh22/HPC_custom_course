# Module Format — How Every Module of This Course Is Built

This document is the template for generating course modules. Every module follows this
structure (or deviates from it consciously, with a stated reason). The goal of the format:
train *applied* performance engineering — the loop of **predict → implement → measure →
explain the gap** — not academic knowledge recall.

## Core principles

1. **Every lab is a contract.** A lab = spec + correctness tests + an executable performance
   target. It is done when tests are green AND the benchmark prints PASS. No lab is
   "read and understood" — it is measured.
2. **Predict before you measure.** Each lab's report starts with a prediction (roofline,
   cost model, scaling law) written *before* running the code. The learning lives in the
   gap between prediction and measurement.
3. **De-scaffold over time.** First contact with a concept gets a skeleton; second contact
   gets a blank file and a spec. By mid-course, labs are "match the reference within
   tolerance, hit the perf bar" with no starter code.
4. **Diagnosis is a first-class exercise type.** Each module (Module 2 onward) includes at
   least one deliberately slow or subtly broken program to diagnose under a profiler.
   This is the most job-like exercise that exists.
5. **Work compounds.** Later modules import earlier work: the Module 1 benchmark harness is
   used everywhere; Module 3 kernels plug into the Module 5 training loop; the Module 5
   model is served in Module 6. Nothing is throwaway — never generate a standalone
   one-off harness where `common/bench` or an earlier module's artifact fits.
6. **Reports over notes.** The written deliverable is a short engineering report per lab,
   not lecture notes. Knowledge md files stay lean — mental models, vocabulary, reading
   pointers — and textbooks/papers carry the depth.

## Directory template

```
module-XX/
  README.md                  # the "course" file — see anatomy below
  labs/
    labN_<slug>/
      <code>.{c,cu,py}       # tier-1: skeleton with TODOs / tier-2: empty + spec
      test_correctness.py    # validates against a reference implementation
      bench.py               # runs the benchmark; perf target encoded, prints PASS/FAIL
      report.md              # learner-written: prediction, measurement, gap analysis
  diagnose/
    <slug>/                  # "why is this slow/wrong?" exercise: code + symptom description
  lab-notebook.md            # running log: what ran, on what hardware, what surprised

common/                      # shared across modules, built by the learner
  bench/                     # timing, roofline, plotting utilities (built in Module 1)
```

## README.md anatomy (the knowledge file)

Keep it lean — target 300–600 lines. Sections:

1. **Why this module exists** — 2–3 sentences connecting it to the previous and next module.
2. **Mental models** — the handful of ideas everything else hangs on (e.g., "decode is
   memory-bound", "a cache line is 64 bytes and you pay for all of it").
3. **Concepts** — the actual teaching content, concise, with diagrams-as-ASCII where useful.
4. **Vocabulary** — terms the learner must be able to use in a professional conversation.
5. **Reading** — pointed references (chapter/section granularity, not whole books), split
   into *required before labs* and *depth, optional*.
6. **Lab specs** — for each lab: goal, inputs/outputs, correctness criterion, perf target,
   scaffolding tier, estimated hours.
7. **Self-check** — the "you should now be able to…" list from COURSE_PLAN.md, expanded.

## Lab anatomy

- **Spec**: precise enough to implement from alone (function signature, shapes, dtypes,
  tolerance). Lives in the lab's section of README.md and as a docstring in the code file.
- **Scaffolding tier** (stated explicitly in the spec):
  - *Tier 1 — first contact*: boilerplate done (allocation, launch, argument parsing),
    `TODO` markers on the core logic only.
  - *Tier 2 — consolidation*: empty file + spec + tests. Used on second+ encounter with
    a concept, and for everything from Module 5 onward unless the concept is brand new.
- **test_correctness.py**: compares against a trustworthy reference (NumPy, PyTorch,
  cuBLAS, `MPI_Allreduce`, single-GPU baseline) with explicit tolerances. Must be runnable
  with plain `pytest`.
- **bench.py**: uses `common/bench`; encodes the performance target as an assertion
  (e.g., `>= 0.6 * cublas_gflops`, `>= 0.85 scaling efficiency at 4 GPUs`); prints a
  one-line PASS/FAIL plus the measured numbers; saves a plot when relevant.
- **report.md** (learner-written, ~half a page), fixed template:
  1. Prediction and the model behind it (written before first run)
  2. Measured result (hardware, versions, command line)
  3. Gap analysis — why prediction and measurement differ
  4. Profiler evidence (screenshot/trace excerpt) with one paragraph of interpretation

## Diagnosis exercises (`diagnose/`)

Deliberately defective code with a realistic symptom description, e.g. "this scales to
2 threads then stops improving" or "GPU utilization is 95% but it's slower than the naive
version". The learner must find the cause *with profiler evidence* before fixing it.
Defects are drawn from real failure classes: false sharing, uncoalesced access, missing
compute/comm overlap, tiny-message collectives, input-starved GPU, sync-in-hot-loop.

## Solutions policy

Reference solutions live on the `solutions` branch, never on `main`. Each solution includes
its own report.md showing the numbers it achieved, so the learner can compare after — not
before — their own attempt.

## Role of Claude as course author

When generating a module, Claude produces: README.md, lab skeletons/specs, reference
implementations (on `solutions`), correctness tests, bench scripts with targets calibrated
to the learner's hardware (see `module-00/cluster-report.md`), and diagnosis exercises.
When the module is scaffolded, add its lab checklist to PROGRESSION.md.

All interaction with the learner working through the material — hints, debugging,
report review, revealing anything — is governed by TUTOR.md, not this file.
