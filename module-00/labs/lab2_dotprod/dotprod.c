/*
 * Lab 2 — dot product + a timing harness you can trust.            Tier 1 skeleton.
 *
 * Implement the three TODOs; main, fill, now_sec and keep are provided.
 * Full spec: module-00/README.md, "Lab 2". Timing checklist: README section 0.3.
 *
 * Usage:   ./dotprod [N [REPS]]         (defaults: N=200000, REPS=100)
 * Output (parsed by tests and bench.py — keep the format):
 *   n=<N> reps=<REPS>
 *   dot=<value>
 *   best=<seconds> median=<seconds>
 *   gflops=<x> gbps=<y>
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/* ------------------------------ provided ------------------------------ */

/* Monotonic wall-clock in seconds — never jumps, unlike CLOCK_REALTIME. */
__attribute__((unused))
static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* Deterministic 32-bit LCG fill — the tests reproduce it bit-exactly in Python. */
static void fill(double *x, size_t n, unsigned seed) {
    unsigned s = seed;
    for (size_t i = 0; i < n; i++) {
        s = s * 1664525u + 1013904223u;
        x[i] = (double)(s >> 8) / 16777216.0; /* in [0, 1) */
    }
}

/* "This value is used" — stops the compiler from deleting the computation that
 * produced v, and (via the memory clobber) from hoisting a repeated identical
 * call out of your timing loop. The DoNotOptimize idiom from google/benchmark.
 * The unused-attribute only silences a warning until your TODO 2 calls it. */
__attribute__((unused))
static void keep(double v) { __asm__ __volatile__("" : : "g"(v) : "memory"); }

/* ------------------------------ your part ----------------------------- */

/* TODO 1: the dot product — one plain loop, nothing clever. */
double dot(const double *x, const double *y, size_t n) {
    (void)x; (void)y; (void)n;
    return 0.0; /* TODO 1 */
}

/* TODO 2: time dot() honestly. Requirements (each has a "why" — you defend
 * them in report.md):
 *   - one untimed warm-up call before any measurement
 *   - reps individually timed calls (now_sec before/after each), stored
 *   - every result passed to keep() INSIDE the timed region
 *   - *best = fastest rep; *median = middle of the sorted times (qsort)
 */
void time_dot(const double *x, const double *y, size_t n, int reps,
              double *best, double *median) {
    (void)x; (void)y; (void)n; (void)reps;
    *best = 0.0;
    *median = 0.0; /* TODO 2 */
}

/* ---------------------------- provided main ---------------------------- */

int main(int argc, char **argv) {
    size_t n  = argc > 1 ? (size_t)strtoul(argv[1], NULL, 10) : 200000;
    int  reps = argc > 2 ? atoi(argv[2]) : 100;
    if (n == 0 || reps <= 0) {
        fprintf(stderr, "usage: %s [N [REPS]]  (both positive)\n", argv[0]);
        return 2;
    }

    double *x = malloc(n * sizeof *x);
    double *y = malloc(n * sizeof *y);
    if (!x || !y) {
        fprintf(stderr, "allocation failed\n");
        free(x);
        free(y);
        return 1;
    }
    fill(x, n, 1);
    fill(y, n, 2);

    printf("n=%zu reps=%d\n", n, reps);
    printf("dot=%.17g\n", dot(x, y, n));

    double best, median;
    time_dot(x, y, n, reps, &best, &median);
    if (median <= 0.0) {
        fprintf(stderr, "median <= 0 — implement TODO 2 (the timing harness)\n");
        free(x);
        free(y);
        return 1;
    }
    printf("best=%.3e median=%.3e\n", best, median);

    /* TODO 3: operation counts for ONE dot() call — your first arithmetic-
     * intensity accounting. flops: count multiplies and adds. bytes: what must
     * be read from memory. (Both depend on n.) */
    double flops = 0.0; /* TODO 3a */
    double bytes = 0.0; /* TODO 3b */
    printf("gflops=%.2f gbps=%.2f\n", flops / median / 1e9, bytes / median / 1e9);

    free(x);
    free(y);
    return 0;
}
