# Findings — flaky_wordcount

<!-- Learner-written, BEFORE fixing (TUTOR.md rule 4: hypothesis + evidence first).
     Note: one root cause can produce several different valgrind messages. -->

## Defect 1

*(Evidence backfilled by Claude 2026-07-17 after the fix was already correctly applied
by the learner — the leak-per-word diagnosis below matches the applied fix.)*

- Symptom(s) it explains: memory growth over time ("error malloc" on long runs)
- Hypothesis: `word` is malloc'd every loop iteration but only freed when it replaces
  `longest` — every non-longest word leaks
- Valgrind evidence (original binary, sample_input.txt):
  ```
  1,052 bytes in 187 blocks are definitely lost in loss record 1 of 1
     at 0x4846828: malloc (vgpreload_memcheck-amd64-linux.so)
     by 0x1092AA: main (wordfreq.c:28)
  ```
- Root cause (`file:line`): wordfreq.c:28 — allocation per word, no `free` on the
  non-longest path (the `if (len > strlen(longest))` branch at :38 is the only free path)
- Fix: `else free(word);` after the longest-word check — applied by learner ✅

## Defect 2

- Symptom(s) it explains: Sometime the count is very wrong
- Hypothesis: bad initialization
- Valgrind evidence: 
at 0x48CBD89: __printf_buffer (vfprintf-process-arg.c:186)
==287799==    by 0x48CD73A: __vfprintf_internal (vfprintf-internal.c:1544)
==287799==    by 0x48C21B2: printf (printf.c:33)
==287799==    by 0x10952B: main (wordfreq.c:50)
==287799==  Uninitialised value was created by a heap allocation
==287799==    at 0x4846828: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==287799==    by 0x109271: main (wordfreq.c:19)
- Root cause (`file:line`): l19, no initilization
- Fix: memset

## Defect 3

- Symptom(s) it explains: longest have no sense
- Hypothesis: the buf is always same size, even for varried word size, which means bad copy from buf to word
- Valgrind evidence:
==287358==    at 0x484F39E: strcpy (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==287358==    by 0x1092DE: main (wordfreq.c:31)
==287358==  Address 0x4a78133 is 0 bytes after a block of size 3 alloc'd
==287358==    at 0x4846828: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==287358==    by 0x1092AA: main (wordfreq.c:28)
- Root cause (`file:line`): l28
- Fix: add another buffer that is the length of the word

## After the fix

- Valgrind summary line (should be 0 errors, no leaks):
  `ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)` — all heap blocks
  freed *(verified by Claude 2026-07-17, `valgrind --leak-check=full ./wordfreq <
  sample_input.txt`)*
- In one paragraph: what would this class of bug look like in a service that has
  been running in production for two weeks?

it would create a huge memory leak as well as create a tons of errors

*(Expanded by Claude, per format change:)* Defect 1 is RSS creeping up ~linearly with
requests served until the OOM killer takes the process down at an hour that guarantees
paging someone — the classic "restart it nightly" workaround. Defects 2 and 3 are worse
because they're *silent*: uninitialized counts and a one-byte heap overrun usually
produce plausible-looking wrong output (or corrupt an adjacent allocation), so two weeks
of served results are quietly untrustworthy, and the crash — when it finally comes — is
in an unrelated malloc call, nowhere near the bug.
