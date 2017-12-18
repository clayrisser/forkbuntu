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

.PHONY: build
build:
	@sudo python ./src/forkbuntu.py
	@echo ::: BUILD :::

.PHONY: freeze
freeze:
	@env/bin/pip freeze > ./requirements.txt
	@echo ::: FREEZE :::

.PHONY: clean
clean:
	-@rm -rf ./env ./tmp ./**/*.pyc ./**/**/*.pyc &>/dev/null || true
	@echo ::: CLEAN :::
