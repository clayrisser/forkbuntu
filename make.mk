MAKEFLAGS += --no-print-directory

# Local Make state (markers, generated env.mk, etc.) lives under MAKEDIR.
# Defined early so -include below can reference it. NOT exported — these
# are Make-side only; sub-makes redefine via their own include of make.mk.
MAKEDIR := $(ROOTDIR)/.venv/.make
MARKERS := $(MAKEDIR)/markers

-include $(MAKEDIR)/env.mk

# Recipes spawn fresh non-interactive shells that don't source ~/.zshrc, so
# the asdf shim dir isn't on PATH unless we add it here.
export PATH := $(or $(ASDF_DATA_DIR),$(HOME)/.asdf)/shims:$(PATH)

GIT ?= git
CLOC ?= cloc
SHFMT ?= shfmt
UV ?= uv
BLACK ?= $(UV) run black
BASEDPYRIGHT ?= $(UV) run basedpyright
PYTEST ?= $(UV) run pytest

SUDO ?= $(eval SUDO := $(shell command -v sudo >/dev/null && echo sudo))$(SUDO)
PKG_INSTALL ?= $(eval PKG_INSTALL := $(or \
	$(shell command -v brew >/dev/null && echo 'brew install'), \
	$(shell command -v apt-get >/dev/null && echo '$(SUDO) apt-get update && $(SUDO) apt-get install -y'), \
	$(shell command -v dnf >/dev/null && echo '$(SUDO) dnf install -y'), \
	echo "no supported package manager" >&2;false))$(PKG_INSTALL)

.PHONY: FORCE
FORCE:

.PHONY: sudo
sudo:
	@$(SUDO) true

# .env → $(MAKEDIR)/env.mk: any change to .env triggers regeneration before
# targets run (Make's -include auto-rebuilds the included file if it has a
# rule). .env itself bootstraps from .env.example on first use.
$(ROOTDIR)/.env: $(ROOTDIR)/.env.example
	@[ -f $@ ] && cp $@ $@.bak; cp $< $@
$(MAKEDIR)/env.mk: $(ROOTDIR)/.env
	@mkdir -p $(@D)
	@awk '/^[[:space:]]*(#|$$)/&&!m{next}'\
	'm{if(/"$$/){sub(/"$$/,"");print;print"endef";print"export "k;m=0}else print;next}'\
	'/^[A-Za-z_][A-Za-z0-9_]*=/{k=substr($$0,1,index($$0,"=")-1);v=substr($$0,index($$0,"=")+1);'\
	'if(v~/^"/&&v!~/"$$/){printf"define %s ?=\n",k;sub(/^"/,"",v);print v;m=1}else{gsub(/^"|"$$/,"",v);'\
	'if(v)printf"define %s ?=\n%s\nendef\nexport %s\n",k,v,k;else printf"%s ?=\nexport %s\n",k,k}}' $< > $@
