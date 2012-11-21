SOURCES=master.cfg \
        builders.py \
        repos.py \
        slaves.py \
        changesources.py \
        schedulers.py \
        statustargets.py \

all:
	@echo -e "Targets:\n"
	@echo -e  "sync\\t\\tSync to the master directory."

sync.path:
	@echo "Please create a sync.path file pointing to the master directory."
	@exit 1

sync: sync.path
	@cp $(SOURCES) `cat sync.path`
	@cp -n config.py `cat sync.path`
	@echo "Sync done".
