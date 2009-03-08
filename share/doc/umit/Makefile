SRCDIR = src
SPHINXBUILD = sphinx-build
SPHINXOPTIONS =


ALLSPHINXOPTIONS = -b $(BUILDER) -d build/doctrees $(SPHINXOPTIONS) \
				   $(SRCDIR) build/$(BUILDER)

.PHONY: html build clean

html: BUILDER = html
html: build
	@echo "Build finished. The HTML pages are in build/html/."

build:
	mkdir -p build/$(BUILDER) build/doctrees
	$(SPHINXBUILD) $(ALLSPHINXOPTIONS)

clean:
	rm -rf build/*
