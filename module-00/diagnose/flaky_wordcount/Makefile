# diagnose/flaky_wordcount.  make → ./wordfreq   make memcheck → valgrind run
# Debug build (-O0) while this ticket is open — you want gdb/valgrind to see
# the program exactly as written, not what the optimizer made of it.
CC      = gcc
CFLAGS  = -O0 -g -Wall -Wextra

wordfreq: wordfreq.c
	$(CC) $(CFLAGS) $< -o $@

memcheck: wordfreq
	valgrind --leak-check=full ./wordfreq < sample_input.txt

clean:
	rm -f wordfreq

.PHONY: memcheck clean
