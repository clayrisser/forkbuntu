CWD := $(shell pwd)

.PHONY: all
all: clean

.PHONY: start
start: env
	@cd example && ../env/bin/python3 ../src

env:
	@virtualenv env
	@env/bin/pip3 install -r ./requirements.txt
	@echo ::: ENV :::

.PHONY: freeze
freeze:
	@env/bin/pip3 freeze > ./requirements.txt
	@echo ::: FREEZE :::

.PHONY: clean
clean:
	-@rm -rf */__pycache__ */*/__pycache__ >/dev/null || true
	@echo ::: CLEAN :::
