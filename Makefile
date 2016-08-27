BUILDOUT_FILENAME ?= buildout.cfg

BUILDOUT_BIN ?= $(shell command -v buildout || echo 'bin/buildout')
BUILDOUT_ARGS ?= -c $(BUILDOUT_FILENAME)

all: build check

show: $(BUILDOUT_BIN)
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) annotate

build: $(BUILDOUT_BIN)
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS)

test: bin/pocompile bin/test
	bin/pocompile src
	bin/test --all

test-plone-4:
	make -f Makefile.docker BUILDOUT_FILENAME=buildout-plone-4.x.cfg

test-plone-5:
	make -f Makefile.docker BUILDOUT_FILENAME=buildout-plone-5.x.cfg

test-all:
	make -j test-plone-4 test-plone-5

check: test

dist:
	bin/fullrelease

watch: bin/instance
	RELOAD_PATH=src bin/instance fg

robot-server: bin/robot-server
	RELOAD_PATH=src bin/robot-server collective.pfg.dexterity.testing.ROBOT_TESTING -v

robot: bin/robot
	bin/robot -d parts/test src/collective/pfg/dexterity/tests

clean:
	rm -rf .installed bin develop-eggs parts

###

.PHONY: all show build test check dist watch clean

bootstrap-buildout.py:
	curl -k -O https://bootstrap.pypa.io/bootstrap-buildout.py

bin/buildout: bootstrap-buildout.py $(BUILDOUT_FILENAME)
	python bootstrap-buildout.py -c $(BUILDOUT_FILENAME)

bin/test: $(BUILDOUT_BIN) $(BUILDOUT_FILENAME) setup.py
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) install test

bin/robot-server: $(BUILDOUT_BIN) $(BUILDOUT_FILENAME) setup.py
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) install robot

bin/robot: $(BUILDOUT_BIN) $(BUILDOUT_FILENAME) setup.py
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) install robot

bin/instance: $(BUILDOUT_BIN) $(BUILDOUT_FILENAME) setup.py
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) install instance

bin/pocompile: $(BUILDOUT_BIN) $(BUILDOUT_FILENAME)
	$(BUILDOUT_BIN) $(BUILDOUT_ARGS) install i18ndude
