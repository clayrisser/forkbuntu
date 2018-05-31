CWD := $(shell pwd)

.PHONY: all
all: clean

.PHONY: start
start: env
	@cd example && ../env/bin/python3 ../forkbuntu

.PHONY: debug
debug: env
	@cd example && ../env/bin/python3 ../forkbuntu --debug

.PHONY: install
install: env

.PHONY: uninstall
uninstall:
	-@rm -rf env >/dev/null || true

.PHONY: reinstall
reinstall: uninstall install

env:
	@virtualenv env
	@env/bin/pip3 install -r ./requirements.txt
	@echo ::: ENV :::

.PHONY: freeze
freeze:
	@env/bin/pip3 freeze > ./requirements.txt
	@echo ::: FREEZE :::

.PHONY: build
build: dist

dist: clean env
	@python setup.py sdist
	@python setup.py bdist_wheel
	@echo ran dist

.PHONY: publish
publish: dist
	@twine upload dist/*
	@echo published

.PHONY: clean
clean:
	-@rm -rf */__pycache__ */*/__pycache__ README.rst dist \
		example/.tmp *.egg-info >/dev/null || true
	@echo ::: CLEAN :::
