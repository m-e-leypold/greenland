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


r""" A Testframework.

     The example below illustrates the use of the test
     framework. Basic entities in the framework are test suites
     (classes that contain tests), tests (methods of those clases) and
     expectations (basically measurements, what others call test
     assertions).

     - Test suites are defined by deriving a class from the class
       'Tests' and registering it with the @suite decorator. Not
       decorating with suite results in a class that is not known as a
       test suite, but can be used as base class of a suite instead of
       'Tests'.

     - Tests are methods in test suite classes. They are registered as
       tests with the @test decorator which is only available in
       classes derived from 'Tests'. Tests can contain arbitrary
       sequences of python statements. Callbacks into the framework
       are passed to tests under the names of 'expect' and 'test'.

       - expect is a callback that can be used to express and check
         expectations about the system/code under test. Examples:

         - expect ( lambda: math.sqrt(-1) ) .raises ( ValueError )
         - expect ( lambda: math.sqrt(4) )  .returns( 2.0 )

         Here 'lambda' is used to suspend statement expression
         evaluation outside of the control of expect, so expect can
         actually diagnose unexpected exception.

       - 'test' is a callback that can be used to control the test
         result directly for cases where 'expect' for some reason is
         not expressive enough:

         - if something ... : test.fail()

         This will effect a non-local exit.

       All exceptions from tests -- raised by 'expect' or outside of
       its control -- are caught be the framework and registered as
       test failures.

     'execute_suites_and_report' runs all registered suites and prints
     reports on sys.stderr. It exits with 0 if all tests in all suites
     passed and with a status >0 if some tests failed.

     There is currently no way to run single suites or tests. This
     might change.  Typically one would place a bunch of test suites
     that somehow belong together in one file and place the following
     python idiom as last statement in the file:

       if __name__== '__main__': execute_suites_and_report()

     To execute the tests one would simply run the file with the
     python interpreter:

       python foo/bar-tests


     Example:
     --------     

       import sys
       from greenland.testing2 import *

       @suite                            # register as test suite
       class  Basic( Tests ):            # test suites need to be derived from Tests

           def prepare(self):            # optional: Do once before running tests (prep test data etc)
               do_something()
    
           def finish(self):             # optional: Do once after running all tests in the suite.
               do_something_else() 

           @test                             # mark method as test
           def basic(self,expect,test,**more):    # 'expect' and 'test' are callbacks passed in by the framework

               do_stuff()
               expect ( lambda : square(5) ) .returns (25)     # what others call test assertion

               do_more()
               expect ( lambda : frobnicate() ) .raises  (FroomError)  # expect a specific exception

               do_even_more()
               test.fail()     # signal test failure  
               
       if __name__== '__main__': execute_suites_and_report()
"""

from greenland.testing2.internals import Tests, suite, execute_suites_and_report


