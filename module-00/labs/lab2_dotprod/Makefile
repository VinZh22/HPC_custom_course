# Lab 2: the SAME source built at two optimization levels — that's the experiment.
CC    = gcc
BASE  = -Wall -Wextra -g

all: dotprod_O0 dotprod_O3

dotprod_O0: dotprod.c
	$(CC) $(BASE) -O0 $< -o $@

dotprod_O3: dotprod.c
	$(CC) $(BASE) -O3 -march=native $< -o $@

clean:
	rm -f dotprod_O0 dotprod_O3

.PHONY: all clean
