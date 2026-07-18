# HPC for AI — Custom Course Plan

A self-paced course taking you from "I train models on one GPU" to "I understand and can build
optimized, multi-GPU / multi-node training and inference systems."

**Assumed background:** ML / Deep Learning / LLMs (single-device level), CS fundamentals, applied
mathematics. C/C++ seen academically but rusty — Module 0 includes a refresher.
**Not assumed:** parallel programming, computer architecture beyond basics, distributed systems.
**Hardware:** you have a real multi-GPU machine for sure; whether it's *several nodes* with a
*scheduler* is unconfirmed — Module 0 (Lab 3) establishes it. Labs use real hardware from
Module 3 onward — no simulators. The few multi-node/scheduler-specific labs (Modules 4 and 7)
carry stated single-node fallbacks.

**Format:** 9 modules ≈ 21–22 weeks at 8–10 h/week, balanced between distributed training and
optimized inference. Each module has theory, hands-on labs, and a deliverable committed to this
repo (`module-XX/` folders). Compress or stretch as needed — the module *order* is the important
part: each layer builds on the one below.

```
Hardware → CPU parallelism → GPU programming → Communication → Distributed training
                                                                      ↓
                              Systems & clusters  ←  Optimized inference
```

## Modules at a Glance

| # | Module | Weeks |
|---|---|---|
| 0 | Setup, C Refresher & Know Your Cluster | 0–1 |
| 1 | Hardware Architecture & the Performance Mental Model | 1–2 |
| 2 | CPU Parallelism: Threads, SIMD, OpenMP | 3–4 |
| 3 | GPU Architecture & CUDA Programming | 5–8 |
| 4 | Communication: MPI, Collectives & NCCL | 9–10 |
| 5 | Distributed Training of Deep Networks | 11–14 |
| 6 | Optimized Inference & Serving | 15–18 |
| 7 | Clusters, Systems & Production Concerns | 19–20 |
| 8 | Capstone | 21+ |

---

## Module 0 — Setup, C Refresher & Know Your Cluster (Weeks 0–1)

Get an environment where you can actually measure things. HPC is an empirical discipline:
every claim in this course should be verified with a benchmark you ran yourself.

### Setup
- Linux toolchain: `gcc`/`clang`, `perf`, `htop`, `numactl`, CMake.
- Python stack: PyTorch (recent), Triton, Nsight Systems & Nsight Compute, `py-spy`.

### C refresher (≈3–4 evenings — enough for Modules 1–3, not a full C course)
Your C is rusty, so warm it up on exactly the subset this course uses:
- Pointers, arrays, and pointer arithmetic; `malloc`/`free`; stack vs heap.
- Structs; passing by pointer; 2-D arrays as flat 1-D buffers with index math
  (`A[i*N + j]` — you'll write this a hundred times in matmul labs).
- Compiling and flags that matter here: `-O0` vs `-O2`/`-O3`, `-march=native`,
  a 20-line Makefile; timing code correctly (`clock_gettime`).
- Debug tooling you'll actually use: `gdb` basics, `valgrind` for memory errors.
- **Warm-up exercises:** (1) dynamic 2-D matrix alloc + transpose; (2) dot product with
  timing harness at `-O0` vs `-O3`; (3) intentional out-of-bounds bug found via valgrind.
- Reference while coding: *Modern C* (Gustedt, free PDF) or Beej's Guide to C — as lookup
  material, not cover-to-cover reading.

### Know your cluster
Map what you have now, because every later lab is designed against these numbers:
- **First, establish what it actually is:** one node or several? A scheduler
  (`sinfo` → SLURM, `qstat` → PBS, `bhosts` → LSF; all "command not found" → probably
  direct SSH to one server, which is a valid answer — record it, don't guess)?
- Node inventory: GPU model & count per node, `nvidia-smi topo -m` (NVLink vs PCIe pairs),
  CPU cores & NUMA layout (`lscpu`, `numactl --hardware`).
- Interconnect between nodes (InfiniBand? RoCE? plain Ethernet?) and its nominal bandwidth.
- Scheduler: which one (SLURM?), partitions/queues, how to request GPUs, storage layout
  (home vs scratch vs shared FS).

### Deliverable
`module-00/` — C warm-up exercises + `cluster-report.md`: node specs, GPU topology matrix,
interconnect, memory bandwidth (STREAM), peak FLOPs per GPU (spec sheet). This report is the
reference card for every roofline and cost model in the course.

---

## Module 1 — Hardware Architecture & the Performance Mental Model (Weeks 1–2)

Why code is slow. Everything later in the course is an application of the ideas here.

### Topics
- CPU microarchitecture for performance: pipelining, superscalar execution, instruction-level
  parallelism, branch prediction — just enough to reason about throughput.
- **The memory hierarchy** (the single most important topic): registers → L1/L2/L3 → DRAM;
  latency vs bandwidth; cache lines; spatial & temporal locality; NUMA.
- **Arithmetic intensity and the roofline model**: compute-bound vs memory-bound. You will use
  this model in *every* subsequent module.
- FLOPs accounting for deep learning: why matmul dominates, counting FLOPs of a transformer
  layer, what "Model FLOPs Utilization (MFU)" means.

### Labs
1. Naive triple-loop matmul in C; measure GFLOP/s. Add loop reordering, then cache blocking
   (tiling). Explain each speedup with the memory hierarchy.
2. Run STREAM; compute your machine's roofline; place your matmul variants on it.
3. Count the FLOPs of one forward+backward pass of a small transformer by hand; verify against
   PyTorch's profiler.
4. Turn your timing/plotting code from labs 1–2 into `common/bench` v1 (timer, GFLOP/s
   computation, roofline plot). Every later module reuses this harness — build it to last.

### Deliverable
`module-01/` — matmul variants + a short report: roofline plot of your machine with your kernels
placed on it. Plus `common/bench` v1.

### Resources
- Hennessy & Patterson, *Computer Architecture* (memory hierarchy chapters — skim, don't read cover to cover).
- "What Every Programmer Should Know About Memory" (Drepper) — sections 1–6.
- Roofline model paper (Williams et al.) or any lecture treatment of it.

---

## Module 2 — CPU Parallelism: Threads, SIMD, OpenMP (Weeks 3–4)

Your first parallel programs. CPU-land is where the concepts (races, synchronization, scaling
laws) are easiest to learn and debug — they transfer directly to GPUs and clusters.

### Topics
- Processes vs threads; shared memory; data races, mutexes, atomics, false sharing.
- OpenMP: `parallel for`, scheduling (static/dynamic/guided), reductions, thread affinity.
- SIMD vectorization: what AVX does, auto-vectorization and reading compiler reports, a taste
  of intrinsics.
- **Amdahl's law & Gustafson's law; strong vs weak scaling** — the vocabulary of every scaling
  discussion you'll ever have.
- Why you still shouldn't write your own BLAS: OpenBLAS/MKL as the standard of comparison.

### Labs
1. Parallelize your Module 1 tiled matmul with OpenMP; add vectorization; plot GFLOP/s vs
   thread count (strong scaling curve). Identify where and why scaling breaks.
2. Deliberately create a false-sharing bug; measure its cost; fix it.
3. Benchmark against OpenBLAS. Aim for ≥50% of its single-node performance — then read about
   what the last 2× costs.
4. Parallelize a real DL-adjacent workload: image preprocessing / tokenization pipeline
   (this is what `DataLoader` workers do for a living).

### Deliverable
`module-02/` — parallel matmul + scaling plots + a paragraph applying Amdahl's law to your results.

### Resources
- *Parallel Programming for Science and Engineering* (Victor Eijkhout, free online).
- OpenMP tutorial (Lawrence Livermore / HPC-tutorials).

---

## Module 3 — GPU Architecture & CUDA Programming (Weeks 5–8)

The core skill module. Four weeks because this is where the "no parallel programming background"
gap closes for real.

### Topics
- GPU design philosophy vs CPU: throughput over latency; SMs, warps, SIMT execution,
  latency hiding through massive oversubscription.
- CUDA programming model: grids/blocks/threads, kernel launches; memory spaces — global,
  shared, registers, constant; **memory coalescing** (the GPU analogue of cache lines).
- Occupancy, warp divergence, bank conflicts.
- Asynchrony: streams, events, pinned memory, overlapping copy & compute.
- Tensor cores and mixed precision (fp16/bf16/fp8) at the hardware level.
- Profiling: Nsight Systems (timeline) and Nsight Compute (kernel deep-dive).
- **Triton**: writing fused kernels from Python — your bridge from CUDA concepts back to the
  PyTorch world.

### Labs (a deliberate ladder)
1. Vector add → grasp the launch model.
2. Naive matmul → tiled matmul in shared memory → measure against cuBLAS; roofline analysis
   of each version.
3. Softmax, then LayerNorm kernels (reductions + numerical care — directly relevant to
   transformers).
4. Fuse them: a single kernel doing `bias + activation + norm`; measure memory traffic saved
   vs separate kernels — this *is* the logic behind FlashAttention.
5. Rewrite lab 4 in Triton; compare effort and performance.
6. Profile a real PyTorch training step with Nsight Systems; identify the top-5 kernels and
   whether each is compute- or memory-bound.

### Deliverable
`module-03/` — kernel collection with benchmark table (yours vs cuBLAS/PyTorch) + one profiler
screenshot with written interpretation.

### Resources
- **Programming Massively Parallel Processors** (Kirk & Hwu, 4th ed.) — the course textbook
  for this module; chapters 1–6, 10 minimum.
- GPU MODE lecture series (YouTube) — practitioner-level, LLM-focused.
- Triton official tutorials (fused softmax, matmul).
- Simon Boehm's blog post "How to Optimize a CUDA Matmul Kernel" — read *after* lab 2.

---

## Module 4 — Communication: MPI, Collectives & NCCL (Weeks 9–10)

Distributed training is 20% math and 80% moving bytes. This module is about the moving-bytes part,
studied in isolation so Module 5 isn't magic.

### Topics
- Anatomy of a cluster: nodes, NVLink/NVSwitch (intra-node), InfiniBand / RoCE (inter-node),
  network topologies; where the bandwidth cliffs are.
- MPI fundamentals: ranks, point-to-point send/recv, and the **collectives** — broadcast,
  scatter/gather, all-gather, reduce-scatter, **all-reduce**.
- The **ring all-reduce algorithm** and its cost model: `2·(N−1)/N · size / bandwidth` — derive
  it, believe it, use it forever.
- NCCL: what it is, how it maps collectives onto NVLink/IB topology; `nccl-tests`.
- Launching things: `mpirun`, `torchrun`, and SLURM (`sbatch`, `srun`) basics.
- Communication cost modeling: latency (α) – bandwidth (β) model; when messages are too small.

### Labs
1. MPI hello-world → ping-pong latency/bandwidth measurement between two ranks.
2. **Implement ring all-reduce yourself** with MPI point-to-point ops; validate against
   `MPI_Allreduce`; measure and compare to the cost model.
3. Run `nccl-tests` on your cluster: all-reduce bus bandwidth intra-node (NVLink/PCIe) vs
   inter-node (IB/RoCE); compare against the topology you mapped in Module 0.
4. Write and submit real scheduler jobs on your cluster: single-node multi-GPU, then a
   2-node job; verify NCCL picks the fast interconnect (`NCCL_DEBUG=INFO`).
   *(Single node / no scheduler per your Module 0 report: run the same NCCL checks
   multi-process on one node, and treat the scheduler workflow as survey material.)*

### Deliverable
`module-04/` — your ring all-reduce implementation + measured vs predicted cost plot.

### Resources
- Eijkhout's MPI chapters; MPI tutorial (mpitutorial.com).
- NVIDIA NCCL documentation + the classic "ring all-reduce" Baidu blog post.

---

## Module 5 — Distributed Training of Deep Networks (Weeks 11–14)

The centerpiece. Everything so far was preparation for this.

### Part A — Data parallelism & the memory equation (Weeks 11–12)
- **Training memory anatomy**: parameters, gradients, optimizer states (Adam = 2 extra copies),
  activations. The `16·N bytes` mixed-precision rule of thumb; activation memory vs batch/seq.
- Mixed-precision training (bf16/fp16 + loss scaling), gradient accumulation,
  activation (gradient) checkpointing.
- Data parallelism: how DDP really works — gradient bucketing, all-reduce overlapped with the
  backward pass. Why the naive parameter-server picture is obsolete.
- **ZeRO stages 1/2/3 and FSDP**: sharding optimizer states, gradients, parameters;
  the communication it adds (all-gather/reduce-scatter) and when it's worth it.

### Part B — Model parallelism & 3D strategies (Weeks 13–14)
- **Tensor parallelism** (Megatron-style): splitting matmuls column/row-wise; why it needs
  all-reduces *inside* forward/backward; why it wants NVLink (intra-node only, usually).
- **Pipeline parallelism**: GPipe, 1F1B schedule, the bubble fraction formula, microbatching.
- Sequence/context parallelism; expert parallelism (MoE) — survey level.
- **Putting it together**: 3D parallelism; how real configs are chosen (TP within node,
  PP across nodes, DP over the rest); computing MFU and communication overhead for a config
  *before* running it.

### Labs
1. Write data-parallel training **from scratch**: `torch.distributed` primitives only —
   broadcast params, all-reduce grads. Then switch to `DistributedDataParallel` and measure
   the speedup from its overlapping/bucketing.
2. Fine-tune a ~1B LLM with FSDP on 2–8 GPUs. Produce a memory budget table (predicted vs
   measured via `torch.cuda.memory_summary`) for ZeRO-1 vs ZeRO-3 equivalents.
3. Implement 2-way tensor parallelism *by hand* on an MLP block (two GPUs, explicit collectives);
   verify numerics against the single-GPU version.
4. Profile a distributed run (PyTorch profiler / Nsight): find the communication in the
   timeline; compute the compute/comm overlap fraction; measure strong-scaling efficiency
   from 1→N GPUs.
5. Paper exercise: given a 70B model and 64 H100s, propose a full parallelism config with a
   justified memory & communication budget.

### Deliverable
`module-05/` — from-scratch DDP + hand-rolled TP code, memory-budget report, and the
parallelism-design exercise write-up.

### Resources
- **HuggingFace "Ultra-Scale Playbook"** — the single best modern text for this module; use it
  as the spine.
- Megatron-LM paper (Shoeybi et al.), ZeRO paper (Rajbhandari et al.), GPipe / PipeDream papers.
- Stanford CS336 (Language Modeling from Scratch) — systems lectures & assignments.

---

## Module 6 — Optimized Inference & Serving (Weeks 15–18)

Different game than training: decode is memory-bound, latency matters, and requests arrive
one by one.

### Topics
- The two phases: **prefill (compute-bound) vs decode (memory-bound)**; roofline of a decode
  step; why batch size is the whole story for throughput.
- **KV cache**: exact size math, why it dominates memory at long context.
- Batching strategies: static → dynamic → **continuous batching**; PagedAttention (vLLM) as
  virtual memory for the KV cache.
- Attention kernels: FlashAttention (training/prefill) and flash-decoding — you implement
  FlashAttention yourself in lab 3, closing the loop from your Module 3 fusion lab.
- **Quantization** for inference: int8/fp8 weights & activations, GPTQ/AWQ, KV-cache
  quantization; accuracy/perf tradeoffs.
- Speculative decoding; (survey) distillation, early exit.
- Multi-GPU inference: tensor parallelism for serving, disaggregated prefill/decode.
- Serving metrics & SLOs: TTFT, TPOT/ITL, goodput; the latency–throughput frontier.
- Engines landscape: vLLM, TensorRT-LLM, SGLang — what each optimizes.

### Labs
1. Compute the roofline for single-request decode of a 7–8B model on your GPU; predict
   tokens/sec from memory bandwidth alone; measure and compare.
2. Implement a KV cache from scratch inside a minimal GPT generation loop; measure the
   speedup vs recomputation.
3. **Implement FlashAttention**: a fused Triton (or CUDA) attention kernel — tiled,
   online-softmax, never materializing the full attention matrix. This is the payoff of
   your Module 3 fusion lab. Validate numerics against
   `torch.nn.functional.scaled_dot_product_attention`; benchmark yours vs naive attention
   and PyTorch's flash backend across sequence lengths; show the memory-traffic win.
   *(Stretch: a flash-decoding variant — split over KV length — for the decode phase.)*
4. Benchmark naive HF `generate` vs vLLM on the same model & workload; plot the
   latency-vs-throughput frontier for several batch sizes / request rates.
5. Quantize the model (e.g., AWQ or fp8); measure tokens/sec gain and quality change on a
   small eval set.

### Deliverable
`module-06/` — KV-cache implementation + your FlashAttention kernel with its benchmark table
(naive vs yours vs PyTorch SDPA) + benchmark report with predicted-vs-measured decode
speeds and the vLLM frontier plot.

### Resources
- vLLM / PagedAttention paper (Kwon et al.), FlashAttention papers (Dao et al.).
- vLLM & TensorRT-LLM docs; "LLM inference arithmetic" style posts (e.g., kipply's blog).

---

## Module 7 — Clusters, Systems & Production Concerns (Weeks 19–20)

The unglamorous layer that determines whether the fast code actually runs.

### Topics
- SLURM for real: job arrays, GRES/GPU scheduling, topology-aware placement.
- Containers on clusters: Docker vs Apptainer/enroot; reproducible CUDA environments.
- Storage & data pipelines at scale: parallel filesystems (Lustre), object storage,
  WebDataset/streaming loaders, the "GPUs starving on data" failure mode.
- Fault tolerance: checkpointing strategies (async, sharded), elastic training, the MTBF math
  of large jobs (why a 10k-GPU job *will* see failures).
- Observability: DCGM GPU metrics, NCCL debugging (`NCCL_DEBUG`), straggler detection.
- Cost & energy: $/token, GPU-hour economics, power as a first-class constraint.

### Labs
1. Containerize your Module 5 training job; run it under SLURM with a resume-from-checkpoint
   test (kill the job mid-run, resume, verify loss continuity). *(No scheduler? Substitute a
   shell-script/tmux launcher — the checkpoint/kill/resume test is the point, not SLURM.)*
2. Build a streaming data pipeline and prove (with profiler evidence) the GPU is never
   input-starved.

### Deliverable
`module-07/` — reproducible job: container + SLURM script + checkpoint/resume demonstration.

---

## Module 8 — Capstone (Weeks 21+)

Pick one; each exercises the full stack. Write it up like an engineering report: design,
predicted performance (rooflines, comm models), measured results, and the gap analysis.

1. **Train:** Pretrain a small GPT (~125M–1B params, token budget sized to your cluster time)
   across multiple nodes with a parallelism config you chose and justified. Report MFU
   and scaling efficiency; try to beat your own first attempt by ≥30%.
2. **Serve:** Build an inference service for an 7–8B model hitting explicit SLOs
   (e.g., p99 TTFT < 500 ms at X req/s) on fixed hardware; document every optimization and
   its measured contribution.
3. **Kernel:** Write a fused Triton/CUDA kernel — one you haven't already built in this
   course (attention is done in Module 6) — e.g., a fused dequant→matmul for W4A16
   inference, an RMSNorm+matmul fusion, or a fused SwiGLU MLP block, that beats the stock
   PyTorch implementation in a real model's end-to-end step time, with Nsight evidence.

### Deliverable
`module-08/` — code + engineering report. This is the portfolio piece.

---

## Cross-Cutting Habits (every module)

- **Predict before you measure.** Write down the roofline / cost-model estimate first; the gap
  between prediction and measurement is where all learning happens.
- **Profile before you optimize.** Nsight/`perf`/PyTorch profiler evidence, not vibes.
- Keep a `lab-notebook.md` per module: what you ran, on what hardware, what surprised you.
- Every benchmark in the repo must be reproducible: pin versions, record hardware, commit
  the run script.

## Milestone Self-Checks

| After module | You should be able to… |
|---|---|
| 1 | Explain any slowdown in terms of the memory hierarchy; place a workload on a roofline |
| 2 | Write correct multithreaded code; predict scaling limits with Amdahl's law |
| 3 | Write a tiled CUDA matmul within ~2–5× of cuBLAS; read an Nsight timeline |
| 4 | Derive ring all-reduce cost; explain what NCCL does on your topology |
| 5 | Design and justify a 3D-parallelism config for a given model & cluster; compute its memory budget by hand |
| 6 | Predict decode tokens/sec from bandwidth; explain vLLM's throughput advantage mechanistically; implement a working FlashAttention kernel |
| 7 | Ship a fault-tolerant, containerized, scheduler-managed training job |
| 8 | Do all of the above on a problem nobody scoped for you |

## Primary References (course-wide)

1. Kirk & Hwu, *Programming Massively Parallel Processors* (4th ed.) — GPU bible.
2. HuggingFace, *The Ultra-Scale Playbook* — distributed LLM training.
3. Eijkhout, *Parallel Programming for Science and Engineering* (free) — MPI/OpenMP.
4. Stanford CS336 + GPU MODE lectures — video companions.
5. Papers: Megatron-LM, ZeRO, GPipe, FlashAttention 1–2, vLLM/PagedAttention.
