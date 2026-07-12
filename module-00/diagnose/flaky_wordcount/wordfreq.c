/*
 * diagnose/flaky_wordcount — start with symptom.md, then TUTOR.md rule 4.
 *
 * wordfreq: reads whitespace-separated words from stdin and prints
 *   - the total word count
 *   - how many words start with each letter (a-z, case-insensitive)
 *   - the longest word seen
 *
 * Build: make        Run: ./wordfreq < sample_input.txt
 * Done-gate: pytest .   (exact expected output + a valgrind-clean run)
 */
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char buf[256];
    int *counts = malloc(26 * sizeof(int));
    char *longest = NULL;
    long nwords = 0;

    if (!counts)
        return 1;

    while (scanf("%255s", buf) == 1) {
        size_t len = strlen(buf);
        char *word = malloc(len);
        if (!word)
            return 1;
        strcpy(word, buf);

        unsigned char c0 = (unsigned char)tolower((unsigned char)word[0]);
        if (c0 >= 'a' && c0 <= 'z')
            counts[c0 - 'a']++;

        if (!longest || len > strlen(longest)) {
            free(longest);
            longest = word;
        }
        nwords++;
    }

    printf("words: %ld\n", nwords);
    for (int i = 0; i < 26; i++)
        if (counts[i] > 0)
            printf("%c: %d\n", 'a' + i, counts[i]);
    printf("longest: %s\n", longest ? longest : "(none)");

    free(counts);
    free(longest);
    return 0;
}
