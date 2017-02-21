# Optimization for the brave of heart ;)
# OMITFP=-fomit-frame-pointer

# ---------------------------------------------------------------------------
# Manual configuration for systems without pkgconfig.

OUTFILE=test

CFLAGS=-O2 -Wall -fPIC #$(OMITFP)
CFLAGS+=-I/usr/include/lua5.2 `sdl2-config --cflags`
LFLAGS=`sdl2-config --libs` -llua5.2 -lSDL2_ttf -lSDL2_image

all: $(OUTFILE)

$(OUTFILE): test.c cg/cg-*.c
	$(CC) $(CFLAGS) $(LFLAGS) -o $@ test.c cg/cg-*.c

clean:
	rm -Rfv $(OUTFILE) 

.PHONY: all clean dist

