CC    := gcc
RM    := rm

ifeq ($(DEBUG), true)
	DEBUG_FLAGS := -g
else
	OPTIMISATION_LEVEL := -O2
endif

CFLAGS := -Wall -Wextra -pedantic -std=c99 $(DEBUG_FLAGS) $(OPTIMISATION_LEVEL)

LIBS := -lrt

.PHONY: all clean

all: markov

clean:
	$(RM) markov

markov: markov.c Makefile
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)
