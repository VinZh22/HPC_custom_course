/*
 * Lab 1 — dynamic matrices, pointer arithmetic, index math.        Tier 1 skeleton.
 *
 * A matrix is stored ROW-MAJOR in one flat heap buffer:
 *   element (i, j) of an n x m matrix lives at   buf[i*m + j]
 *
 * Implement the three TODO functions; everything else is provided.
 * Full spec: module-00/README.md, "Lab 1".
 *
 * Usage:   ./transpose N M
 * Output (parsed by the tests — don't change the format):
 *   matrix A (N x M), then B = A^T (M x N); if N == M, also C = a copy of A
 *   transposed in place.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------ provided ------------------------------ */

/* Deterministic fill so the Python tests can reproduce A exactly. */
static void fill(double *A, size_t n, size_t m) {
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < m; j++)
            A[i * m + j] = (double)(i * 100000 + j);
}

static void print_matrix(const char *name, const double *A, size_t n, size_t m) {
    printf("# %s %zu %zu\n", name, n, m);
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < m; j++)
            printf("%.1f%c", A[i * m + j], j + 1 == m ? '\n' : ' ');
}

/* ------------------------------ your part ----------------------------- */

/* TODO 1: return a heap buffer able to hold an n x m matrix of doubles
 * (NULL if allocation fails). While writing it, answer in the lab notebook:
 * why is the byte count computed in size_t and not int? Why can't a
 * 4096 x 4096 matrix be a local variable instead?
 */
double *alloc_matrix(size_t n, size_t m) {
    double *res = malloc(n * m * sizeof *res);
    return res;
}

/* TODO 2: out-of-place transpose. A is n x m, B is m x n, and
 * B[j][i] = A[i][j] for all i, j — written as flat index math.
 * You will type this pattern in every module of this course.
 */
void transpose(const double *A, double *B, size_t n, size_t m) {
    for (size_t i=0; i<n; i++){
        for (size_t j=0; j<m; j++){
            B[j*n + i] = A[i*m+j];
        }
    }
}

/* TODO 3: transpose a square n x n matrix in place — no second buffer.
 * Think first: which (i, j) pairs must you visit — all of them, or half?
 */
void transpose_inplace(double *A, size_t n) {
    for (size_t i=0; i<n; i++){
        for (size_t j=i+1; j<n; j++){
            double tmp = A[i*n+j];
            A[i*n+j] = A[j*n+i];
            A[j*n+i] = tmp;
        }
    }
}

/* ---------------------------- provided main ---------------------------- */

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s N M\n", argv[0]);
        return 2;
    }
    size_t n = (size_t)strtoul(argv[1], NULL, 10);
    size_t m = (size_t)strtoul(argv[2], NULL, 10);
    if (n == 0 || m == 0 || n > 100000 || m > 100000) {
        fprintf(stderr, "N and M must be in 1..100000\n");
        return 2;
    }

    double *A = alloc_matrix(n, m);
    double *B = alloc_matrix(m, n);
    if (!A || !B) {
        fprintf(stderr, "alloc_matrix returned NULL — implement TODO 1 first\n");
        free(A);
        free(B);
        return 1;
    }

    fill(A, n, m);
    transpose(A, B, n, m);
    print_matrix("A", A, n, m);
    print_matrix("B", B, m, n);

    if (n == m) {
        double *C = alloc_matrix(n, n);
        if (!C) {
            free(A);
            free(B);
            return 1;
        }
        memcpy(C, A, n * n * sizeof(double));
        transpose_inplace(C, n);
        print_matrix("C", C, n, n);
        free(C);
    }

    free(A);
    free(B);
    return 0;
}
