CWD := $(shell pwd)

.PHONY: all
all: clean

.PHONY: start
start: env
	@sudo PYTHONPATH="." env/bin/python app build --debug

env:
	@virtualenv env
	@env/bin/pip install -r ./requirements.txt
	@echo ::: ENV :::

.PHONY: freeze
freeze:
	@env/bin/pip freeze > ./requirements.txt
	@echo ::: FREEZE :::

.PHONY: clean
clean:
	-@sudo rm -rf ./tmp ./**/*.pyc ./**/**/*.pyc *.iso &>/dev/null || true
	@echo ::: CLEAN :::

.PHONY: purge
purge: clean
	-@rm -rf ./env ./extras &>/dev/null || true
	@echo ::: PURGE :::
