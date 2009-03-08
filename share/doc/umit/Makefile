SRCDIR = src
SPHINXBUILD = sphinx-build
SPHINXOPTIONS =


ALLSPHINXOPTIONS = -b $(BUILDER) -d doctrees $(SPHINXOPTIONS) \
				   $(SRCDIR) $(BUILDER)

.PHONY: html build clean

html: BUILDER = html
html: build
	@echo "Build finished. The HTML pages are in html/."

build:
	mkdir -p $(BUILDER) doctrees
	$(SPHINXBUILD) $(ALLSPHINXOPTIONS)

clean:
	rm -rf html/*
	rm -rf doctrees/*
