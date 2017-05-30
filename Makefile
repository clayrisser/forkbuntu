SHELL := /bin/bash
CWD := $(shell pwd)

.PHONY: all
all: clean

env:
	@virtualenv env
	@env/bin/pip install -r ./requirements.txt
	@echo created virtualenv

.PHONY: build
build:
	@sudo python ./src/forkbuntu.py
	@echo built

.PHONY: freeze
freeze:
	@env/bin/pip freeze > ./requirements.txt
	@echo froze requirements

.PHONY: clean
clean:
	-@sudo rm -rf ./env ./MyBuildInstall
	@echo cleaned
