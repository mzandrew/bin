cflags = -std=c99
makeflags = -j2
libraries = -lm
cc = gcc

cfiles = $(wildcard src/*.c)
objfiles = $(patsubst src/%.c,work/%.o,$(cfiles))
binfiles = $(patsubst src/%.c,work/%,$(cfiles))

default:
	if [ ! -e work ]; then mkdir work; fi
	if [ ! -e src  ]; then mkdir  src; fi
	$(MAKE) $(makeflags) $(binfiles)

work/%.o : src/%.c
	$(cc) $(cflags) -c $< -o $@

work/% : work/%.o
	$(cc) $(libraries) $< -o $@

.PRECIOUS: work/%.o

