#
#   Greenland -- a Python based scripting environment.
#   Copyright (C) 2015,2016  M E Leypold.
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation; either version 2 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
#   02110-1301 USA.


HELP-TEXT-IN = Makefile

# -- HELP
#
#  This Makefile is only a shallow wrapper around pip and
#  virtualenv. You can use pip directly to build and install
#  greenland.
#
#  - Type 'make dev-install' to create a virtual environment ./.virtualenv
#    and install greenland there. You can then use '. ./env.sh' to add
#    the virtualenv to your shell environment. This is useful for test
#    driving and development.
#
#  - Type 'make check' to perform all checks implemented so far. Both
#    targets should run the same checks but with a different method.
#    
#  For details see the file INSTALL in the project toplevel directory.
#
# -- END HELP

# TODO: clean + package gaols. help dito.

_default: help

# -- find sources (XXX move to .assets)

.build = .build

clean::
	rm -rf $(.build)

ifndef TIMESTAMP
export TIMESTAMP := $(shell date -Is | sed 's|[+].*||;s|[:-]||g;s|T|_|')
endif

MAKE-LOG  := $(.build)/log/$(TIMESTAMP)_make.log
$(shell mkdir -p $(dir $(MAKE-LOG)))

LOGVAR = $(shell echo '$1 => $($1)' >> $(MAKE-LOG))
$(call LOGVAR,TIMESTAMP)
$(call LOGVAR,MAKELEVEL)



BUILD-DIRS          = $(.build)
VCS-DIRS            = .git CVS 
IGNORED-DIRS        = __pycache__ '*.egg-info' $(VCS-DIRS) $(MORE-IGNORED-DIRS) $(BUILD-DIRS)
IGNORED-FILES       = '*~' '*~BAK' '*.orig' '?' '.git*' $(MORE-IGNORED-FILES)

-dont-traverse-into-submodules     = \( -not \( \( -not -path . \) -a -exec test -e '{}/.git' \; -a -prune -printf "" \) \) -a
-dont-traverse-into-ignored-dirs   =    -not \( -type d -a \( -false $(IGNORED-DIRS:%= -o -name %) \) -a -prune -printf "" \) \
                                     -a \( -not \( -false $(IGNORED-DIRS:%= -o -name %) \) \) \
                                     -a
-ignore-some-files                 = -not \( -false $(IGNORED-FILES:%= -o -name %) \) -a

FIND-IN-GIT-TREE = @find . 					\
		 	 $(-dont-traverse-into-ignored-dirs)	\
			 $(-dont-traverse-into-submodules)	\
			 $(-ignore-some-files)                  \

SOURCE-DIRECTORIES = 

$(.build)/src/Directories: $(SOURCE-DIRECTORIES)
	@mkdir -p $(@D)
	$(FIND-IN-GIT-TREE) -type d -print | sed 's|^[.]/||' >$@

$(.build)/src/Files: $(SOURCE-DIRECTORIES)
	@mkdir -p $(@D)
	$(FIND-IN-GIT-TREE) -type f -print | sed 's|^[.]/||' >$@

$(.build)/src/Files.mk:       VARNAME=SOURCE-FILES
$(.build)/src/Directories.mk: VARNAME=SOURCE-DIRECTORIES

LIST-TO-VAR = @ set -o pipefail ; set -eu ; { echo "$(VARNAME) += \\"; cat $^ | sed 's|^|  |;s|$$|\t\\|'; echo; }

$(.build)/src/Directories.mk $(.build)/src/Files.mk: %.mk: %
	@mkdir -p $(@D)
	$(LIST-TO-VAR) >$@

include $(.build)/src/Directories.mk $(.build)/src/Files.mk

$(call LOGVAR,SOURCE-DIRECTORIES)
$(call LOGVAR,SOURCE-FILES)



# XXX complete source find, the exec executes always in invocation dir, instead of matched?
#
#

# -- Other stuff

PIP = pip3

help:
	@awk  '/-- HELP/{s=1}(s){s++}/-- END HELP/{s=0}(s>=3){print}' "$(HELP-TEXT-IN)" | sed 's|^#||;s|^  ||'

# PYTHON-MODULES = \
#	greenland.errors greenland.argparsing greenland.shellscripting greenland.externalprocedures

PY-SCRIPTED-TESTS = $(filter-out %.py,$(filter tests/%,$(SOURCE-FILES)))
PYTHON-MODULES    = $(filter lib/%.py,$(SOURCE-FILES))

$(call LOGVAR,PY-SCRIPTED-TESTS)
$(call LOGVAR,PYTHON-MODULES)

# -- tests

run-scripted-tests: $(PY-SCRIPTED-TESTS:%=$(.build)/%.log)


$(PY-SCRIPTED-TESTS:%=$(.build)/%.log): $(.build)/%.log: % $(PYTHON-MODULES)
	@mkdir -p $(@D)
	@rm -f $@~FAILED
	{ $< >$@~RUNNING 2>&1 &&  mv $@~RUNNING $@; } || { mv $@~RUNNING $@~FAILED; ln $@~FAILED $@~FAILED~$(TIMESTAMP); }

check:: run-scripted-tests

check::
	@find $(.build)/tests -name '*~FAILED' | sed 's|^[.]/||' > $(.build)/tests/FAILED.logs
	@sed <$(.build)/tests/FAILED.logs 's|[.]log~FAILED$$||;s|^$(.build)/tests/||' > $(.build)/tests/FAILED
	@wc -l $(.build)/tests/FAILED | awk '($$1==0){next}{exit(1)}' || { echo; echo 'Tests failed:'; sed 's|^|  |' <$(.build)/tests/FAILED; echo; }
	@echo; echo '=> All tests OK.'; echo

# --------------

stats:
	@echo "PYUNIT-EXTERNAL-TESTS => $(PYUNIT-EXTERNAL-TESTS)"

prep: virtualenv dev-install
	touch ".$@.DONE"

VIRTUALENV.DEACTIVATE = : # { if declare -f deactivate >/dev/null; then deactivate; fi; }
VIRTUALENV            = : # $(VIRTUALENV.DEACTIVATE); . .virtualenv/bin/activate

dev-install: # .virtualenv
	$(VIRTUALENV); $(PIP) install --force-reinstall --upgrade -e .

.virtualenv:
	$(VIRTUALENV.DEACTIVATE);  virtualenv .virtualenv;
	$(VIRTUALENV); 				\
	{ set -e ; set -u;			\
	  $(PIP) install --upgrade $(PIP); 		\
	  $(PIP) install --upgrade wheel; 		\
	}

.virtualenv.UPDATED: .virtualenv
	$(VIRTUALENV); $(PIP) install --upgrade $(PIP) ; $(PIP) install twine
	$(VIRTUALENV); $(PIP) list
	@touch $@

virtualenv: .virtualenv.UPDATED


distclean:: clean
	rm -rf .virtualenv*

lsd-project: prep Project/.git

Project/.git:
	git submodule update --init Project


clean::
	find . -name '*~' | xargs rm -f 

cleaner: distclean



rcheck:  check check-todos # release check


$(PYTHON-MODULES:%=check[%]): check[%]: 
	@$(VIRTUALENV); XXX python -c 'import $*; import greenland.selftest; greenland.selftest.run($*)'

$(PYUNIT-EXTERNAL-TESTS:%.test=test[%]): test[%]:
	@$(VIRTUALENV); python $(subst .,/,$*).test 

check2: $(PYTHON-MODULES:%=check2[%])

check2[%]:$(subst .,/,$*).py

check-todos:
	! grep -n XXX $(PYTHON-MODULES) $(PYUNIT-EXTERNAL-TESTS) 

wheel:
	$(PIP) wheel .


setup::
	git update --init Project


doc-html::
	cd doc && make html
doc-pdf::
	cd doc && make latexpdf

doc:: doc-html doc-pdf


clean::
	rm -rf doc/_build


-include Project/Project.mk

