# Makefile for filebutler

.PHONY: all doc
.INTERMEDIATE: doc/filebutler.1

all: doc

doc: doc/filebutler.1.gz

doc/%.gz: doc/%
	gzip -f $<

doc/filebutler.1: doc/filebutler.md
	pandoc -f markdown_github $< -V section=1 -V header="FILEBUTLER" -s -t man -o $@
