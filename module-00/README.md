# Module 0 — Setup, C Refresher & Know Your Cluster

**Weeks 0–1 · ≈ 8–11 h total · [Course plan: Module 0](../COURSE_PLAN.md)**
**Deliverables:** green `check_env.py` · lab 1–2 code passing tests · fixed `diagnose/` exercise
with findings · completed [`cluster-report.md`](cluster-report.md) · running [`lab-notebook.md`](lab-notebook.md)

## Why this module exists

HPC is an empirical discipline: every claim in this course gets verified by a benchmark you
ran yourself. Module 0 builds the three prerequisites for that: a toolchain that works, enough
C to write and time small numerical kernels (Modules 1–3 live in C and CUDA), and a map of the
machine you will be measuring for the next twenty weeks. Module 1 uses all three immediately —
it takes the timing skills from Lab 2 to matmul and builds the mental model of *why* code is slow.

## Format deviations in this module

[MODULE_FORMAT.md](../MODULE_FORMAT.md) requires deviations to be conscious and stated:

| Deviation | Reason |
|---|---|
| No absolute performance targets | Targets are calibrated against `cluster-report.md`, which this module *produces*. Lab 2's target is relative instead: `-O3` ≥ 3× `-O0`. |
| `bench.py` is self-contained | `common/bench` is built by *you* in Module 1 (Lab 4). Module 0 predates the harness. |
| Lab 0 and Lab 3 have no `report.md`/`bench.py` | They are gates, not predict–measure experiments: their artifacts are a working environment and the cluster report itself. |
| A `diagnose/` exercise appears early (format says Module 2+) | valgrind is Module 0 content; a planted-defect hunt is the most realistic way to learn it. |
| Lab 1 is correctness-only | Transpose *performance* is a Module 1 lab — the cache story shouldn't be spoiled here. Two prediction questions go in the notebook instead of a full report. |

## Mental models

1. **Measure, don't believe.** Specs, blog posts, and intuition are all routinely wrong about
   performance. From this module on, the unit of knowledge is a number you measured, with the
   hardware and flags written next to it.
2. **C is "portable assembly."** There is almost nothing between your line of C and the
   machine's loads, stores, and arithmetic. That's why performance work happens there: what
   you write is what runs.
3. **Memory is 1-D.** A "matrix" is a fiction layered over one flat run of bytes. Row-major
   means element `(i, j)` of an `n × m` matrix lives at `buf[i*m + j]`, and `j` is the axis
   that moves through memory contiguously. You will write this index math a hundred times.
4. **The compiler is your ally and your benchmark's adversary.** `-O3` makes code fast partly
   by *deleting* work whose result is never used. A timing loop whose result goes nowhere
   measures nothing — and reports a spectacular time.
5. **Five numbers rule your cluster.** DRAM GB/s, GPU HBM GB/s, GPU TFLOP/s, GPU↔GPU link GB/s,
   inter-node GB/s. Every prediction in this course is built from them; Lab 3 collects them.

## Concepts

### 0.1 The C you need (and only that)

**Pointers and arrays.** A pointer is an address plus a type; the type sets the stride of its
arithmetic (`p + 1` moves `sizeof(*p)` bytes). An array name decays to a pointer to its first
element in most expressions — which is why `a[i]`, `*(a + i)`, and pointer walks are the same
thing.

**Heap allocation, the idiom:**

```c
double *a = malloc(n * sizeof *a);   /* sizeof *a: right size even if the type changes */
if (!a) { perror("malloc"); exit(1); }
/* ... use a[0..n-1] ... */
free(a);                             /* every malloc has exactly one free */
```

**Stack vs heap:**

| | Stack | Heap |
|---|---|---|
| Size | small (default ~8 MB total) | as big as RAM |
| Lifetime | ends with the function | until `free` |
| Cost | ~free (pointer bump) | allocator call |
| Use for | scalars, small fixed arrays | matrices, anything sized at runtime |

A `double A[4096][4096]` local variable is 128 MB of stack — instant crash. Big data lives
on the heap, always.

**`size_t`, not `int`, for sizes and indices.** Byte counts and flattened indices overflow
32-bit `int` fast: for `i, m` as `int`, `i * m + j` with `i = m = 100000` overflows before the
addition. Write `(size_t)i * m + j` and the multiply happens in 64 bits.

**Structs and pass-by-pointer.** C passes arguments by value; passing a struct copies it.
Pass `T *` (or `const T *` when read-only) — that is the C calling convention for anything
bigger than a scalar, and the reason `f(&x)` is everywhere.

**Row-major layout** (burn this in):

```
A is 3 x 4:            memory (one row after another):
  a b c d
  e f g h      [ a b c d e f g h i j k l ]
  i j k l
A[i][j]  ==  buf[i*4 + j]      j is the fast (contiguous) axis
```

### 0.2 Compiling: the flags that matter here

| Flag | What it does | When |
|---|---|---|
| `-O0` | no optimization; code matches source line-by-line | debugging in gdb |
| `-O2` | standard optimization | default for real builds |
| `-O3` | `-O2` + aggressive inlining, loop transforms, auto-vectorization | benchmarks, kernels |
| `-march=native` | use every instruction this CPU has (AVX2/AVX-512, FMA) | benchmarks — **caveat:** binary may crash with "illegal instruction" on a different (older) node; on heterogeneous clusters, build per node type |
| `-g` | debug symbols; gdb/valgrind show file:line | always — costs ~nothing at runtime |
| `-Wall -Wextra` | warnings | always, non-negotiable; fix every warning |
| `-fopenmp` | OpenMP | Module 2 |

**Anatomy of a ~15-line Makefile** (each lab ships one — read it, don't cargo-cult it):

```make
CC      = gcc                  # variable; `make CC=clang` overrides it
CFLAGS  = -O2 -g -Wall -Wextra

transpose: transpose.c         # target: prerequisites
	$(CC) $(CFLAGS) $< -o $@   # recipe (TAB-indented!)  $< = first prereq, $@ = target

clean:
	rm -f transpose

.PHONY: clean                  # "clean" is a command, not a file to build
```

`make` rebuilds a target only when a prerequisite is newer — that's the entire idea.

### 0.3 Timing code without lying to yourself

The checklist. Lab 2 makes you implement it; later, `common/bench` (Module 1) encodes it.

1. **Use the monotonic clock** — `clock_gettime(CLOCK_MONOTONIC, ...)`. Wall-clock
   (`CLOCK_REALTIME`) can jump when NTP adjusts the time.
2. **Warm up before measuring.** The first run pays for page faults, cold caches, and CPU
   frequency ramp-up. Run once untimed, then measure.
3. **Repeat, and report the median** (and the best). One measurement is a coin flip; the
   *mean* is polluted by outliers (an OS interrupt lands in one rep); the median is robust.
4. **Make the result unavoidable.** If the computed value is never used, `-O3` deletes the
   computation and you time an empty loop. Feed every result to a sink the compiler can't
   see through (Lab 2 provides `keep()` — the `DoNotOptimize` idiom from google/benchmark).
5. **Know your clock frequency is moving.** Turbo and the OS governor change CPU speed
   run-to-run. For now: just be aware (`watch "grep MHz /proc/cpuinfo"` while benchmarking).
6. **Record the context.** A number without hardware, compiler version, and flags next to it
   is noise. This is why every `report.md` has a "Measured" section header for exactly that.

### 0.4 gdb — the 20% you'll use

Compile with `-g` (and usually `-O0` while hunting logic bugs). Then:

| Command | Effect |
|---|---|
| `gdb ./prog` then `run args...` | start |
| `break file.c:42` / `break func` | breakpoint |
| `next` / `step` | next line / step *into* calls |
| `print expr` | inspect (`print A[i*m+j]`, `print *p@10` shows 10 elements) |
| `backtrace` (`bt`) | where am I — **first command after any segfault** |
| `frame 2` | jump to frame 2 of the backtrace |
| `watch var` | break when `var` changes |
| `continue` / `quit` | resume / leave |

Segfault workflow: `gdb ./prog` → `run` → crash → `bt` → you're at the guilty line.

### 0.5 valgrind — reading what it tells you

`valgrind --leak-check=full ./prog` runs your program on a synthetic CPU and checks every
memory access. It's ~20× slower and worth it. The four messages that matter:

| Message | Meaning | Classic cause |
|---|---|---|
| `Invalid write/read of size N` | access outside any allocation | off-by-one bounds, buffer too small |
| `Conditional jump ... depends on uninitialised value(s)` | you used memory you never set | missing initialization (`malloc` doesn't zero; `calloc` does) |
| `N bytes ... definitely lost` | leaked block, pointer gone | missing `free` on some path |
| `Invalid free()` | freeing something twice / not a malloc'd pointer | double free, freeing middle of a block |

Each message comes with two stack traces: where the bad access happened, and where the block
was allocated. Read both — the fix is usually at the allocation.

### 0.6 What "knowing your cluster" means

**A node** = CPUs + RAM + GPUs on one motherboard, sharing an OS. **The cluster** = nodes
joined by a network fabric, fronted by a scheduler.

**Intra-node GPU topology.** GPUs talk to each other over NVLink (fast, hundreds of GB/s) or
over PCIe (slower, tens of GB/s). `nvidia-smi topo -m` prints the matrix; the legend:

| Code | Meaning |
|---|---|
| `NV#` | direct NVLink, # links — the fast path |
| `PIX` / `PXB` | same PCIe switch / via multiple PCIe bridges |
| `PHB` | through the CPU's PCIe host bridge |
| `SYS` | across the inter-socket link — the slow path |

Which pairs share NVLink decides how tensor parallelism is placed in Module 5.

**NUMA.** A two-socket node has two memory controllers: each core reaches its own socket's
RAM faster than the other's. `numactl --hardware` shows the layout. It matters as early as
Module 2 (thread affinity).

**Inter-node fabric.** InfiniBand (HDR ≈ 200 Gb/s ≈ 25 GB/s, NDR ≈ 400 Gb/s ≈ 50 GB/s per
port), RoCE (Ethernet carrying RDMA), or plain Ethernet. This number is the ceiling for
multi-node training (Module 4–5). `ibstat` / `ibv_devinfo` reveal InfiniBand adapters.

**Scheduler.** You never run on cluster nodes directly; you ask the scheduler for resources.
SLURM vocabulary: *partition* (a queue of nodes), `sinfo` (what exists), `squeue` (what's
running), `srun --gres=gpu:1 --pty bash` (interactive shell with one GPU),
`sbatch job.sh` (batch submission). If your cluster runs something else (PBS, LSF), map the
equivalents in the report.

**Storage tiers.** Home (small, backed up, slow) vs scratch (big, fast, purged) vs shared
project space. Datasets and checkpoints belong on scratch/parallel FS — Module 7 shows what
happens when they don't ("GPUs starving on data").

### 0.7 STREAM and peak numbers

**STREAM** measures *sustainable* DRAM bandwidth with four simple kernels; **Triad**
(`a[i] = b[i] + s*c[i]`) is the headline number. Sustained is normally 70–85% of the
theoretical `channels × MT/s × 8 bytes` — that gap is real life, not an error. Rules:
compile with `-O3 -march=native -fopenmp`, set `STREAM_ARRAY_SIZE` so each array is ≥ 4× your
L3 cache (`lscpu | grep L3`), pin threads. Full recipe in the Lab 3 spec.

**GPU peaks come from the datasheet, not folklore.** Find the official spec sheet for your
exact GPU model. Trap: NVIDIA headline TFLOP/s often quote "with 2:4 sparsity" — a ×2 you
will not get on dense matmuls. Record the **dense** numbers, and the source URL.

**CPU peak FLOP/s** (you'll want it for Module 1's roofline):
`cores × clock (GHz) × SIMD lanes × 2 (FMA) × FMA units/core`.

## Vocabulary

You should be able to use these in a professional conversation after this module:

| Term | One-liner |
|---|---|
| pointer arithmetic | address math in units of the pointed-to type |
| array decay | array name becoming a pointer to its first element |
| stack / heap | automatic small+fast vs manual big+flexible memory |
| `size_t` | unsigned type for sizes/indices; 64-bit on your machines |
| undefined behavior (UB) | C's "anything may happen" — out-of-bounds, uninit reads, overflow |
| segfault | hardware-trapped invalid memory access |
| memory leak | allocated block with no remaining pointer to free it |
| row-major | rows contiguous in memory; `buf[i*m + j]` |
| stride | bytes between consecutively accessed elements |
| monotonic clock | timer that never jumps backwards |
| warm-up run | untimed first run paying one-time costs |
| dead-code elimination | compiler deleting computation with unused results |
| auto-vectorization | compiler emitting SIMD from scalar loops |
| NUMA node | CPU socket + its locally attached RAM |
| NVLink / PCIe | fast direct GPU link vs the general-purpose bus |
| InfiniBand / RoCE | RDMA network fabrics between nodes |
| partition (SLURM) | a named queue of nodes |
| GRES | SLURM's "generic resources" — how GPUs are requested |
| interactive vs batch job | `srun --pty bash` now vs `sbatch` queued script |
| scratch filesystem | fast, big, *purged* storage for data and checkpoints |
| STREAM Triad | the standard sustained-DRAM-bandwidth number |
| MT/s × channels × 8 B | theoretical DRAM bandwidth formula |

## Reading

**Required (as lookup while doing the labs — not cover-to-cover):**

- *Modern C*, Jens Gustedt (free PDF) — the pointers, memory-model, and storage/allocation
  chapters (Ch. 11–13 in the 1st-edition numbering). Open it when a lab's syntax fights you.
  Friendlier alternative: *Beej's Guide to C* — pointers, arrays, and manual memory chapters.
- [Valgrind quick start](https://valgrind.org/docs/manual/quick-start.html) — 10 minutes,
  read before the diagnose exercise.
- [STREAM homepage](https://www.cs.virginia.edu/stream/) — before Lab 3.

**Depth (optional):**

- *Beej's Quick Guide to GDB* — if §0.4 isn't enough.
- [makefiletutorial.com](https://makefiletutorial.com) — if Makefiles still feel like magic.

## How to work through this module

1. Lab 0 first (it gates everything). Then labs 1 → 2 → diagnose, with the C reading open as
   lookup. Lab 3 (cluster report) is independent — interleave it whenever you have cluster
   access.
2. Keep [`lab-notebook.md`](lab-notebook.md) as you go: date, machine, what ran, what
   surprised you. Predictions are written **before** first runs — that's the course's core
   habit starting now.
3. Working with Claude: [TUTOR.md](../TUTOR.md) governs. Syntax, API, tooling questions —
   ask freely, that's trivia. The TODO logic in labs and the diagnose defect — hint ladder.

## Labs

### Lab 0 — Environment gate (`labs/lab0_setup/`) — 0.5–1 h

- **Goal:** a toolchain you can trust, on every machine you'll use.
- **Run:** `python3 module-00/labs/lab0_setup/check_env.py` — on your workstation **and** on
  the cluster (login node at minimum).
- **Done when:** every REQUIRED line is `[ ok ]` (exit code 0), and the `[cluster]` items pass
  on the cluster. Items marked "later" name the module that will need them — install them when
  that module starts.
- No report — this lab is a gate (deviation table above).

### Lab 1 — Matrices by hand (`labs/lab1_transpose/`) — 1.5–2 h — Tier 1

- **Goal:** heap-allocated matrices, row-major index math, and leak-free `malloc`/`free` —
  fluent, not just remembered.
- **Spec** — implement three functions in `transpose.c` (skeleton provides `main`, fill,
  printing):

  | Function | Contract |
  |---|---|
  | `double *alloc_matrix(size_t n, size_t m)` | heap buffer for an `n × m` matrix of `double`, or `NULL` |
  | `void transpose(const double *A, double *B, size_t n, size_t m)` | `A` is `n × m`, `B` is `m × n`, `B[j][i] = A[i][j]` — out-of-place |
  | `void transpose_inplace(double *A, size_t n)` | square `n × n` transpose, no second buffer |

- **Predict first** (two answers in the notebook before running anything):
  1. How many bytes is a `4096 × 4096` matrix of `double`? Would it fit on the stack?
  2. Gut answer, rigor comes in Module 1: does your `transpose` read `A` in a
     memory-friendly order, write `B` in one, or both — and can any transpose do both?
- **Correctness:** `pytest module-00/labs/lab1_transpose` — compares against NumPy and
  includes a valgrind gate (leak-free is part of the spec).
- **No bench** (deviation table above): transpose performance is Module 1 material.
- **Done when:** all tests green. Log the notebook entry.

### Lab 2 — Dot product & an honest timer (`labs/lab2_dotprod/`) — 2–3 h — Tier 1

- **Goal:** your first real measurement — and a timing harness that survives `-O3`. This
  harness's logic becomes `common/bench` in Module 1.
- **Spec** — three TODOs in `dotprod.c` (skeleton provides `main`, deterministic fill,
  `now_sec()`, `keep()`):
  1. `dot(x, y, n)` — one plain loop.
  2. `time_dot(...)` — the §0.3 checklist made real: one warm-up, `REPS` individually-timed
     calls, every result through `keep()` *inside* the timed region, then best and median
     (`qsort`). Each requirement has a "why" — you defend them in the report.
  3. The FLOP and byte counts of one `dot` call (for the `gflops=`/`gbps=` output lines) —
     your first arithmetic-intensity accounting, the heart of Module 1.
- **Build:** the Makefile builds the same source twice: `dotprod_O0` and `dotprod_O3`
  (`-O3 -march=native`). Default size `n = 200000` (~3.2 MB — cache-resident on purpose;
  Module 1 explains why that matters).
- **Correctness:** `pytest module-00/labs/lab2_dotprod` — dot value vs NumPy on bit-identical
  inputs, harness sanity.
- **Bench target:** `python3 module-00/labs/lab2_dotprod/bench.py` —
  **PASS = `-O3` ≥ 3× faster than `-O0`**, with sanity rails: a speedup over 100× or absurd
  GB/s means your harness is measuring a deleted loop, and fails.
- **Report:** `report.md` **required**, template in the lab dir. The prediction (how much
  faster will `-O3` be? what's the limit — arithmetic or memory?) is written *before* the
  first timed run.
- **Done when:** tests green + bench PASS + report filled.

### Diagnose — `diagnose/flaky_wordcount/` — 1–1.5 h

- **Goal:** first planted-defect hunt: reproduce, get valgrind evidence, then fix.
- **Start with** `symptom.md` — the "ticket" as ops filed it. The program builds with `make`
  and runs on `sample_input.txt`.
- **Rules** ([TUTOR.md](../TUTOR.md) rule 4): hypothesis + evidence go into `findings.md`
  **before** you change the code. Claude will not name the defects; bring valgrind output.
- **Done when:** `pytest module-00/diagnose/flaky_wordcount` green (exact correct output
  **and** a valgrind-clean gate) + `findings.md` filled.

### Lab 3 — Cluster report (`labs/lab3_cluster_report/`) — 2–3 h

- **Goal:** the reference card for the whole course. Every later module's perf targets are
  calibrated against this file (MODULE_FORMAT.md points here).
- **Do:** fill [`cluster-report.md`](cluster-report.md) — the template embeds the command
  for every field. Sections: node inventory, GPU datasheet peaks (dense, with source URLs),
  `nvidia-smi topo -m` + interpretation, inter-node fabric, scheduler, storage, measured
  STREAM, and the "numbers to know by heart" table.
- **STREAM recipe:**

  ```bash
  wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c
  gcc -O3 -march=native -fopenmp -DSTREAM_ARRAY_SIZE=80000000 stream.c -o stream
  export OMP_NUM_THREADS=$(nproc)  OMP_PROC_BIND=spread
  ./stream        # record all four kernels; Triad is the headline
  ```

  `80000000` (640 MB/array) is enough for L3 ≤ 160 MB — scale up if yours is bigger. Run it
  on a *compute* node (via the scheduler!), not the login node.
- **Done when:** `python3 module-00/labs/lab3_cluster_report/check_report.py` prints PASS
  (no TODOs left, all sections present, Triad number recorded).

## Self-check — you should now be able to…

- Explain stack vs heap and say instantly why a big matrix must be `malloc`'d.
- Write `buf[(size_t)i*m + j]` without thinking, and say why the cast is there.
- Say what `-O3` does that `-O0` doesn't, and when `-march=native` bites back.
- Time a loop and defend the methodology: monotonic clock, warm-up, median, `keep()`.
- Drive gdb through a segfault (`run` → `bt` → inspect) and read all four valgrind messages.
- Recite your cluster's numbers from memory: GPUs/node, NVLink or PCIe, fabric + GB/s,
  STREAM Triad, GPU dense TFLOP/s and HBM GB/s.
- Explain why sustained bandwidth ≠ spec bandwidth, and where each number comes from.
- Get an interactive shell with one GPU on your cluster, and submit a batch job.

## Done when

- [ ] Lab 0 — `check_env.py` all-green (workstation + cluster)
- [ ] Lab 1 — tests green (incl. valgrind), notebook predictions logged
- [ ] Lab 2 — tests green + `bench.py` PASS + `report.md` filled
- [ ] Diagnose — tests green + `findings.md` filled before the fix
- [ ] Lab 3 — `check_report.py` PASS

Then update [PROGRESSION.md](../PROGRESSION.md) and start
[Module 1](../COURSE_PLAN.md#module-1--hardware-architecture--the-performance-mental-model-weeks-12).
