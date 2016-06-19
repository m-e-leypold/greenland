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

default:
	@awk  '/-- HELP/{s=1}(s){s++}/-- END HELP/{s=0}(s>=3){print}' "$(HELP-TEXT-IN)" | sed 's|^#||;s|^  ||'

# PYTHON-MODULES = \
#	greenland.errors greenland.argparsing greenland.shellscripting greenland.externalprocedures

PYUNIT-EXTERNAL-TESTS = $(wildcard */*.test)
PYTHON-MODULES        = $(wildcard */*.py)

stats:
	@echo "PYUNIT-EXTERNAL-TESTS => $(PYUNIT-EXTERNAL-TESTS)"

prep: virtualenv dev-install
	touch ".$@.DONE"

VIRTUALENV.DEACTIVATE = { if declare -f deactivate >/dev/null; then deactivate; fi; }
VIRTUALENV            = $(VIRTUALENV.DEACTIVATE); . .virtualenv/bin/activate

dev-install: .virtualenv
	$(VIRTUALENV); pip install --force-reinstall --upgrade -e .

.virtualenv:
	$(VIRTUALENV.DEACTIVATE);  virtualenv .virtualenv;
	$(VIRTUALENV); 				\
	{ set -e ; set -u;			\
	  pip install --upgrade pip; 		\
	  pip install --upgrade wheel; 		\
	}

.virtualenv.UPDATED: .virtualenv
	$(VIRTUALENV); pip install --upgrade pip ; pip install twine
	$(VIRTUALENV); pip list
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


check:   $(PYUNIT-EXTERNAL-TESTS:%.test=test[%]) # $(PYTHON-MODULES:%=check[%])
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
	pip wheel .


setup::
	git update --init Project


-include Project/Project.mk

