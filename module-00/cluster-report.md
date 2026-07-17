# Cluster Report — (ml-prd-research)

The reference card for every roofline and cost model in this course. The HTML comments give the command or source for each. Fill it **on the cluster**. Note that we are working in docker inside a vm.
Gate: `python3 labs/lab3_cluster_report/check_report.py` (run from `module-00/`).

**Filled on:** (16/07) · **by:** VZU

## 1. Node inventory

<!-- commands: lscpu · numactl --hardware · free -h · nvidia-smi -->

| Field | Value |
|---|---|
| CPU model | INTEL(R) XEON(R) PLATINUM 8558 |
| Sockets × cores/socket × threads/core | 1 * 128 * 1 |
| NUMA nodes | 1 |
| RAM per node | 503Gi |
| L3 cache (total) | 260 MiB |
| GPU model | H200 |
| GPUs per node | 8 |
| VRAM per GPU | 143771MiB |
| Number of GPU nodes you can actually use | 1 |

## 2. GPU peak numbers (from the datasheet)

<!-- Find the official datasheet for your exact GPU model. Record DENSE numbers -
     headline TFLOP/s often include "with 2:4 sparsity" (a x2 you won't get). -->

| Metric | Value | Source (URL) |
|---|---|---|
| fp32 TFLOP/s | 67 | https://resources.nvidia.com/en-us-gpu-resources/hpc-datasheet-sc23 |
| tf32 tensor TFLOP/s (dense) | 494 | same (datasheet quotes 989 with 2:4 sparsity; ÷2) |
| bf16/fp16 tensor TFLOP/s (dense) | 989 | same (datasheet: 1,979 with sparsity; ÷2) |
| fp8 tensor TFLOP/s (dense, if supported) | 1979 | same (datasheet: 3,958 with sparsity; ÷2) |
| HBM capacity / bandwidth | 141GB / 4.8TB/s | same |
| NVLink bandwidth per GPU (aggregate) | 900 GB/s | same |
| PCIe generation × lanes | Gen5 ×16 (128 GB/s bidirectional) | same |

## 3. Intra-node topology

<!-- command: nvidia-smi topo -m   (legend in module README section 0.6) -->

```
        GPU0    GPU1    GPU2    GPU3    GPU4    GPU5    GPU6    GPU7    CPU Affinity    NUMA Affinity   GPU NUMA ID
GPU0     X      NV18    NV18    NV18    NV18    NV18    NV18    NV18    0-127   0               N/A
GPU1    NV18     X      NV18    NV18    NV18    NV18    NV18    NV18    0-127   0               N/A
GPU2    NV18    NV18     X      NV18    NV18    NV18    NV18    NV18    0-127   0               N/A
GPU3    NV18    NV18    NV18     X      NV18    NV18    NV18    NV18    0-127   0               N/A
GPU4    NV18    NV18    NV18    NV18     X      NV18    NV18    NV18    0-127   0               N/A
GPU5    NV18    NV18    NV18    NV18    NV18     X      NV18    NV18    0-127   0               N/A
GPU6    NV18    NV18    NV18    NV18    NV18    NV18     X      NV18    0-127   0               N/A
GPU7    NV18    NV18    NV18    NV18    NV18    NV18    NV18     X      0-127   0               N/A
```

Interpretation (2–3 sentences: which GPU pairs are NVLink, which go through PCIe/CPU,
what that implies for placing communication-heavy jobs): All the gpu are linked with NV18
*(expanded by Claude, 2026-07-17):* every pair shows `NV18` — 18 4th-gen NVLink links,
i.e. a fully connected all-to-all fabric at 900 GB/s aggregate per GPU, with no
PCIe-only or cross-socket (`SYS`) pairs. Placement is therefore unconstrained on this
node: any subset of GPUs is equivalent for tensor parallelism and collectives (Module 5),
and NCCL should never fall back to PCIe for GPU↔GPU traffic.

## 4. Inter-node fabric

<!-- commands: ibstat · ibv_devinfo · ip link   — or ask your cluster admin/docs.
     Single machine? Fill the first row and write "n/a — single node" in the rest. -->

| Field | Value |
|---|---|
| Multiple nodes available? (how many) | n/a — single node |
| Fabric type (InfiniBand / RoCE / Ethernet) | n/a — single node |
| Nominal bandwidth per port | n/a — single node |
| Ports per node | n/a — single node |
| Evidence (command output or doc link) | n/a — single node |

## 5. Scheduler

<!-- probe: sinfo (SLURM) · qstat (PBS) · bhosts (LSF). None found → direct access:
     write "none — direct SSH" as the scheduler, note how the machine is shared with
     other users, and put "n/a" in the job-command rows. -->

| Field | Value |
|---|---|
| Scheduler & version (or "none — direct SSH") | n/a — single node |
| Partitions/queues relevant to you (name, nodes, GPUs, time limit) | n/a — single node |
| Interactive shell with 1 GPU (exact command) | n/a — single node |
| Batch job, 2 nodes × all GPUs (path to a working example script) | n/a — single node |
| Default & max walltime | n/a — single node |

## 6. Storage

<!-- commands: df -h ~ · df -h /scratch (or wherever) · quota — plus cluster docs -->

| Tier | Path | Size/quota | Purged? | Use for |
|---|---|---|---|---|
| Home | ~ | 3.8T | No | everything |
| Scratch | /tmp | 3.8T | No | cache, dl |
| Shared/project | /workspace | 28T | No | cross project file (mounted to the docker) |

## 7. Measured — STREAM memory bandwidth

<!-- Recipe in module README, Lab 3. Run on a COMPUTE node via the scheduler. -->

| Field | Value |
|---|---|
| Build line used | `gcc -O3 -march=native -fopenmp -DSTREAM_ARRAY_SIZE=134000000 stream.c -o stream` |
| `OMP_NUM_THREADS` / binding | 96 / `OMP_PROC_BIND=spread` |
| `STREAM_ARRAY_SIZE` (and your L3, for the ≥4× rule) | 134000000 (1.07 GB/array vs 260 MiB L3 ≈ 4×) |
| Copy | 64355.0 MB/s |
| Scale | 64122.8 MB/s |
| Add | 72915.2 MB/s |
| Triad | 72647.0 MB/s |
| Theoretical (channels × MT/s × 8 B) | 332 GB/s (host silicon — not directly applicable to this VM slice) |
| Sustained as % of theoretical | 21.7% — low % expected: virtualized topology hides NUMA, memory may interleave across host sockets; 72.6 GB/s is the honest ceiling for this environment |

## 8. Numbers to know by heart

<!-- The denominators of every prediction you will make for 20 weeks. -->

| # | Number | Value |
|---|---|---|
| 1 | DRAM bandwidth per socket (STREAM Triad) | 72647 MB/s |
| 2 | GPU HBM bandwidth | 4.8 TB/s |
| 3 | GPU bf16 dense TFLOP/s | 1980 |
| 4 | GPU↔GPU link bandwidth (NVLink or PCIe) | 900 GB |
| 5 | Inter-node bandwidth per node | n/a |
| 6 | GPUs per node / VRAM per GPU | 8 / 143 GB |
