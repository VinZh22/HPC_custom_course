# Symptom — flaky_wordcount

The ticket, as ops filed it:

> `wordfreq` (build: `make`, run: `./wordfreq < sample_input.txt`) misbehaves in prod:
>
> - On the production corpus it sometimes aborts — `malloc(): corrupted top size`
>   or a plain segfault. **We could not reproduce the crash on the small sample
>   input — it "works" there.** Classic.
> - One run printed a count of `1731040` for a letter that barely appears in the
>   corpus; the next run of the *same command* was fine.
> - The `longest:` line occasionally ends in garbage characters.
> - The total word count is always right.
>
> Since the crash won't reproduce locally, "it runs and the output looks right"
> proves nothing. Convict it with valgrind instead.

## Your job

1. Reproduce under valgrind (the module README section 0.5 tells you how to read it).
2. For each distinct root cause: write hypothesis + valgrind evidence in
   [findings.md](findings.md) **before** touching the code (TUTOR.md rule 4).
3. Fix. Done when `pytest module-00/diagnose/flaky_wordcount` is green — that runs
   the exact-output check *and* a valgrind-clean gate.

Claude will not name the defects (that would delete the exercise). Bring a hypothesis
and evidence, and it will confirm, refute, or nudge.
