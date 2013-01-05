MODULES_REPO="git://git.sugarlabs.org/sugar-build/sugar-build.git"
MODULES_SOURCE_PATH="config"
MODULES_DEST_PATH=$(CURDIR)/modules

MODULES=modules/sugar.json \
        modules/activities.json

SOURCES=master.cfg \
        builders.py \
        repos.py \
        slaves.py \
        changesources.py \
        schedulers.py \
        statustargets.py \

TEMPLATES=templates/root.html \
          templates/layout.html

SYNC_PATH=$(shell cat sync.path)

.PHONY: all sync pull-modules

all:
	@echo -e "Targets:\n"
	@echo -e  "sync\\t\\tSync to the master directory."

sync.path:
	@echo "Please create a sync.path file pointing to the master directory."
	@exit 1

sync: sync.path pull-modules
	@DEST_PATH=$(SYNC_PATH) && \
	cp $(SOURCES) $$DEST_PATH && \
	cp -n config.py $$DEST_PATH && \
        mkdir -p $$DEST_PATH/modules && \
        cp $(MODULES) $$DEST_PATH/modules && \
	echo "Sync done".

pull-modules:
	@TMP_DIR=`mktemp -td sugar-build-XXXX` && \
	git clone $(MODULES_REPO) $$TMP_DIR && \
        mkdir -p $(MODULES_DEST_PATH) && \
        cd $$TMP_DIR/$(MODULES_SOURCE_PATH) && \
        cp $(MODULES) $(MODULES_DEST_PATH) && \
	rm -rf $$TMP_DIR && \
	echo "Modules updated."

restart: sync
	@buildbot restart $(SYNC_PATH)

check:
	pep8 $(CURDIR)
	pylint --reports=n --disable=C,W,R,E,F --enable=W0611 $(CURDIR)/*.py 
