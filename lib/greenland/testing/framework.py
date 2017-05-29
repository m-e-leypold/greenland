#
#   Greenland -- a Python based scripting environment.
#   Copyright (C) 2015-2017  M E Leypold.
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

"""\

A simple testing framework with an emphasis on readable test
assertions.

This module provides methods to write tests mostly by re-exporting
features from :py:mod:`greenland.testing.expectations` and
:py:mod:`greenland.testing.infix_syntax`. Additionally it provides a
function :py:func:`expect` which constructs objects of class
:py:class:`greenland.testing.expectations.Expectee` with a default
recorder that (a) prints to stderr and (b) stops on the first test
deviation encountered.

The assumptions upon which this framework is founded are:

- Tests are programs that are executed. Their exit status provides
  information if the test has passed, detailed information is printed
  on stderr.

- Testprograms alternate the following steps repeatedly: (a) Construct
  program objects (values, functions, classes, instances), (b) Check
  expectations on these objects (check for specific properties of the
  objects).

*Example*:

.. code-block:: python

   from greenland.testing.framework import *

   def double(x):
       return(2*x)

   expect( lambda: double(5) )  |returns| (10)  # passes
   expect( lambda: double(17) ) |returns| (18)  # raises UnexpectedResult

   def quadruple(x): 
       return double(double(x)):

   expect( lambda: quadruple(5) )  |returns| (20)

See the module documentation in the manual for more details, the
documentation of :py:mod:`greenland.testing.infix_syntax` for the
available vocabulary to phrase expectations and the documentation of
:py:mod:`greenland.testing.expectations` for details on 
:py:class:`~greenland.testing.expectations.Expectee` objects and
:py:class:`~greenland.testing.expectations.Recorder` objects.
"""

import greenland.testing.expectations as expectations

from   greenland.testing.expectations import                               \
    UnexpectedResult, MissingException,                                    \
    UnexpectedException, WrongException, ExceptionConstraintViolation

from greenland.testing.infix_syntax import returns, returning, raises, raising

def expect( expectee, recorder=expectations.Recorder()):

    """Construct an :py:class:`~greenland.testing.expectations.Expectee`
       with the given
       :py:class:`~greenland.testing.expectations.Recorder`. The
       default recorder will (a) print on stdout and (b) stop on the
       first test deviation.

    """
    
    return expectations.Expectee ( expectee ,recorder )
