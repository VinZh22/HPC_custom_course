# Lab 1 build.  make → ./transpose   make memcheck → valgrind run   make clean
CC      = gcc
CFLAGS  = -O2 -g -Wall -Wextra   # -g: gdb/valgrind show file:line. Fix every warning.

transpose: transpose.c
	$(CC) $(CFLAGS) $< -o $@

memcheck: transpose
	valgrind --leak-check=full ./transpose 8 8

clean:
	rm -f transpose

.PHONY: memcheck clean
