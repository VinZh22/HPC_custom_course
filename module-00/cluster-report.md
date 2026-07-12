# Cluster Report — TODO(cluster name)

The reference card for every roofline and cost model in this course. Every `TODO` is a value
to fill; the HTML comments give the command or source for each. Fill it **on the cluster**.
Gate: `python3 labs/lab3_cluster_report/check_report.py` (run from `module-00/`).

**Filled on:** TODO(date) · **by:** TODO

## 1. Node inventory

<!-- commands: lscpu · numactl --hardware · free -h · nvidia-smi -->

| Field | Value |
|---|---|
| CPU model | TODO |
| Sockets × cores/socket × threads/core | TODO |
| NUMA nodes | TODO |
| RAM per node | TODO |
| L3 cache (total) | TODO |
| GPU model | TODO |
| GPUs per node | TODO |
| VRAM per GPU | TODO |
| Number of GPU nodes you can actually use | TODO |

## 2. GPU peak numbers (from the datasheet)

<!-- Find the official datasheet for your exact GPU model. Record DENSE numbers -
     headline TFLOP/s often include "with 2:4 sparsity" (a x2 you won't get). -->

| Metric | Value | Source (URL) |
|---|---|---|
| fp32 TFLOP/s | TODO | TODO |
| tf32 tensor TFLOP/s (dense) | TODO | TODO |
| bf16/fp16 tensor TFLOP/s (dense) | TODO | TODO |
| fp8 tensor TFLOP/s (dense, if supported) | TODO | TODO |
| HBM capacity / bandwidth | TODO | TODO |
| NVLink bandwidth per GPU (aggregate) | TODO | TODO |
| PCIe generation × lanes | TODO | TODO |

## 3. Intra-node topology

<!-- command: nvidia-smi topo -m   (legend in module README section 0.6) -->

```
TODO(paste the topology matrix here)
```

Interpretation (2–3 sentences: which GPU pairs are NVLink, which go through PCIe/CPU,
what that implies for placing communication-heavy jobs): TODO

## 4. Inter-node fabric

<!-- commands: ibstat · ibv_devinfo · ip link   — or ask your cluster admin/docs -->

| Field | Value |
|---|---|
| Fabric type (InfiniBand / RoCE / Ethernet) | TODO |
| Nominal bandwidth per port | TODO |
| Ports per node | TODO |
| Evidence (command output or doc link) | TODO |

## 5. Scheduler

<!-- commands: sinfo · squeue · scontrol show partition   (or PBS/LSF equivalents) -->

| Field | Value |
|---|---|
| Scheduler & version | TODO |
| Partitions/queues relevant to you (name, nodes, GPUs, time limit) | TODO |
| Interactive shell with 1 GPU (exact command) | TODO |
| Batch job, 2 nodes × all GPUs (path to a working example script) | TODO |
| Default & max walltime | TODO |

## 6. Storage

<!-- commands: df -h ~ · df -h /scratch (or wherever) · quota — plus cluster docs -->

| Tier | Path | Size/quota | Purged? | Use for |
|---|---|---|---|---|
| Home | TODO | TODO | TODO | TODO |
| Scratch | TODO | TODO | TODO | TODO |
| Shared/project | TODO | TODO | TODO | TODO |

## 7. Measured — STREAM memory bandwidth

<!-- Recipe in module README, Lab 3. Run on a COMPUTE node via the scheduler. -->

| Field | Value |
|---|---|
| Build line used | TODO |
| `OMP_NUM_THREADS` / binding | TODO |
| `STREAM_ARRAY_SIZE` (and your L3, for the ≥4× rule) | TODO |
| Copy | TODO GB/s |
| Scale | TODO GB/s |
| Add | TODO GB/s |
| Triad | TODO GB/s |
| Theoretical (channels × MT/s × 8 B) | TODO GB/s |
| Sustained as % of theoretical | TODO |

## 8. Numbers to know by heart

<!-- The denominators of every prediction you will make for 20 weeks. -->

| # | Number | Value |
|---|---|---|
| 1 | DRAM bandwidth per socket (STREAM Triad) | TODO |
| 2 | GPU HBM bandwidth | TODO |
| 3 | GPU bf16 dense TFLOP/s | TODO |
| 4 | GPU↔GPU link bandwidth (NVLink or PCIe) | TODO |
| 5 | Inter-node bandwidth per node | TODO |
| 6 | GPUs per node / VRAM per GPU | TODO |
