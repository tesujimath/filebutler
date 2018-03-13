# Makefile for filebutler

.PHONY: all doc install
.INTERMEDIATE: doc/filebutler.1

all: doc

doc: doc/filebutler.1.gz

doc/%.gz: doc/%
	gzip -f $<

doc/filebutler.1: doc/filebutler.rst
	pandoc $< -V section=1 -V header="FILEBUTLER" -s -t man -o $@

install: doc
	install -m 644 -D doc/filebutler.1.gz $(DESTDIR)/usr/share/man/man1/filebutler.1.gz
