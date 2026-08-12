.POSIX:
export ROOTDIR ?= $(eval ROOTDIR := $(shell git rev-parse --show-toplevel))$(ROOTDIR)
include $(ROOTDIR)/make.mk

.DEFAULT_GOAL := lint

ASDF_VERSION ?= v0.18.0
.PHONY: prepare prepare/asdf prepare/cloc
prepare: sudo
	@command -v asdf >/dev/null 2>&1 || $(MAKE) prepare/asdf
	@command -v cloc >/dev/null 2>&1 || $(MAKE) prepare/cloc
	@awk '!/^#/ && NF {print $$1}' .tool-versions | \
		while read t; do asdf plugin add "$$t" 2>/dev/null || true; done
	@rcfile=$$(mktemp); \
		{ asdf install 2>&1; echo $$? >$$rcfile; } | grep --line-buffered -v 'is already installed' || true; \
		rc=$$(cat $$rcfile); rm -f $$rcfile; exit $$rc
	@$(UV) sync
prepare/asdf:
	@command -v brew >/dev/null 2>&1 && brew install asdf || { \
		o=$$(uname | tr A-Z a-z); a=$$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/'); \
		curl -fsSL "https://github.com/asdf-vm/asdf/releases/download/$(ASDF_VERSION)/asdf-$(ASDF_VERSION)-$$o-$$a.tar.gz" \
			| $(SUDO) tar -xz -C /usr/local/bin asdf; \
	}
prepare/cloc:
	@$(PKG_INSTALL) cloc

.PHONY: configure
configure:
	@for cmd in asdf $(UV) $(SHFMT) $(CLOC); do \
		command -v $$cmd >/dev/null 2>&1 || { echo "$$cmd is missing, run \`make prepare\`"; exit 1; }; \
	done

# Shared (used by both format and lint)
_SHFILES = find forkbuntu example tests -type f -name '*.sh' -print0

.PHONY: format
format: configure
	@$(BLACK) forkbuntu tests
	@$(_SHFILES) | xargs -0 $(SHFMT) -w

.PHONY: lint
lint: configure
	@$(BLACK) --check forkbuntu tests
	@$(BASEDPYRIGHT)
	@$(_SHFILES) | xargs -0 $(SHFMT) -d

.PHONY: test
test: test/unit

.PHONY: test/unit
test/unit: configure
	@$(PYTEST) --cov=forkbuntu --cov-report=term --cov-report=xml:coverage.xml

DOCKER ?= docker
.PHONY: test/e2e
test/e2e: configure
	@$(DOCKER) run --rm -v "$(ROOTDIR):/opt/forkbuntu" -w /opt/forkbuntu \
		ubuntu:24.04 sh tests/e2e/inside.sh

.PHONY: count
count: configure
	@$(CLOC) --vcs=git

.PHONY: clean
clean:
	@rm -rf dist coverage.xml .pytest_cache example/.tmp example/*.iso
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@rm -rf $(MAKEDIR)

.PHONY: purge
purge: clean
	@$(GIT) clean -fxd
