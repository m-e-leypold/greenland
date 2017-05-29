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

This module provides basic utilities to write test expectations and
record test failures.

The class :py:class:`Expectee` is a wrapper around objects about which
one wants to write tests expectations. Its methods provide the
vocabulary for expectations: :py:meth:`~Expectee.returns` and
:py:meth:`~Expectee.raises`.


The class :py:class:`Recorder` provides hooks to record test
progress and failures as well as to implement policies when to abort
a test sequence.

*Example*: 

.. code-block:: python

   expect ( lambda: double(5) ) .returns (10)

Note, that `expect` is not a part of this module and needs to be
provided by a framework implementation as, in example,
:py:mod:`greenland.testing.framework`.

"""

import greenland.introspection.caller as caller
import greenland.introspection.safe   as safe
from   greenland.introspection.safe   import Excn, Value
from   greenland.errors               import Error, next_stackframe

at_statement = " at statement: {source}"

class TestFailure(Error):

    """XXX TBD"""

    
    def __init__(self,expected,actual,__stackframe__=0,location=None,**kwargs):

        """XXX TBD"""
        
        mro = ", ".join(( cls.__module__+"."+cls.__name__ for cls in type(actual).__mro__ ))
        super(TestFailure,self).__init__(
            expected = expected, actual = actual,mro=mro,__stackframe__= next_stackframe(__stackframe__),location=location,**kwargs
        )

    info = """
           at: {source}

           actual            : {actual!r}
           actual.__class__  : {actual.__class__!r}
           expected:         : {expected!r}
           """

    
class UnexpectedResult(TestFailure):

    """XXX TBD"""
    
    message = "Unexpected result: expected = {expected!r}, actual = {actual!r}" + at_statement

class MissingException(TestFailure):

    """XXX TBD"""
    
    message = "Missing exception (got value return instead): expected = {expected!r}, actual = {actual!r}" + at_statement

class UnexpectedException(TestFailure):

    """XXX TBD"""
    
    message = "Unexpected exception (instead of value return): expected = {expected!r}, actual = {actual!r}" + at_statement

class WrongException(TestFailure):

    """XXX TBD"""
    
    message = "Wrong exception: expected = {expected!r}, actual = {actual!r}" + at_statement    

class ExceptionConstraintViolation(TestFailure):

    """XXX TBD"""
    
    message = "Exception constraint violated: actual = {actual!r}, constraint = {constraint!r}" + at_statement
    
class ErrorsOccurred(Error):

    """XXX TBD"""
    
    message = "Error occcured during test: {recorder}, stop_on_error = {stop_on_error}"
    
#  Recorders (also: Stop-Policy)      

import sys

class Recorder (object):

    """XXX TBD"""


    errors        = 0           #: Conter for errors (test deviations).
    stop_on_error = True        #: If to stop on first error.
    logfile       = sys.stderr  #: File where to log test events.
    
    def __init__( self, stop_on_error = True, logfile = sys.stderr ):

        """XXX TBD"""
        
        self.errors = 0
        self.stop_on_error = stop_on_error
        self.logfile = logfile
        
    def report(self,e,__stackframe__=0):

        """XXX TBD"""
        
        if self.stop_on_error:            
            raise e
        else:
            self.errors += 1
            print(e,file=self.logfile)
            print(file=self.logfile)
                       
    def unexpected_return_value(self,expected,actual,__stackframe__=-1,location=None):

        """XXX TBD"""
            
        self.report( UnexpectedResult(expected,actual,__stackframe__=next_stackframe(__stackframe__),location=location))
        
    def missing_exception(self,expected,actual,__stackframe__=-1,location=None):

        """XXX TBD"""
        
        self.report( MissingException(expected,actual,__stackframe__=next_stackframe(__stackframe__),location=location))
        
    def unexpected_exception(self,expected,actual,__stackframe__=-1,location=None):

        """XXX TBD"""
        
        self.report( UnexpectedException(expected,actual,__stackframe__=next_stackframe(__stackframe__),location=location))
        # better to pass None here and ignore that in raise_here

    def wrong_exception(self,expected,actual,__stackframe__=-1,location=None):

        """XXX TBD"""
            
        self.report( WrongException(expected,actual,__stackframe__=next_stackframe(__stackframe__),location=location))

    def exception_constraint_violation(self,expected,actual,constraint,__stackframe__=-1,location=None):

        """XXX TBD"""
        
        self.report( ExceptionConstraintViolation(expected,actual,constraint=constraint,__stackframe__=next_stackframe(__stackframe__),location=location))        


    def tick(self):   # XXX also __stackframe__

        """XXX TBD"""

        return
        
    def done(self):   # XXX also __stackframe__

        """XXX TBD"""
        
        if self.errors>0:
            raise ErrorsOccurred(recorder=self,stop_on_error=self.stop_on_error,__stackframe__=-1)
        

class Expectee (object):

    """XXX TBD"""
    
    def __init__(self,expectee,recorder,__stackframe__=0):

        """XXX TBD"""
        
        self.expectee = expectee
        self.recorder = recorder
        self.location = caller.capture(next_stackframe(__stackframe__-1))
        

    def check_returns(self,thunk,expected,__stackframe__=-2,location=None):

        """XXX TBD"""
        
        result = safe.apply(thunk)
        if result.Type == Excn:
            self.recorder.unexpected_exception(expected,result.value,__stackframe__,location)
        else:
            actual = result.value
            if actual != expected:
                self.recorder.unexpected_return_value(expected,actual,__stackframe__,location)
                
    def returns(self,expected,__stackframe__=0):

        """XXX TBD"""
        
        self.check_returns(self.expectee,expected)
        
    def returning(self,table,stackframe_depth=0):

        """XXX TBD"""
        
        for value in table:
            self.check_returns(lambda: self.expectee(value),table[value],location=self.location)
        return self

    def check_raises(self,thunk,Expected, satisfying = lambda ex : True ,__stackframe__=-2,location=None):
        try:
            actual = thunk()
        except Exception as ex:
            if isinstance(ex,Expected):
                if not satisfying(ex):
                    self.recorder.exception_constraint_violation(Expected,ex,satisfying,__stackframe__,location) # XXX this branch is broken.
                else:
                    return
            else:
                self.recorder.wrong_exception(Expected,ex,__stackframe__,location)
        self.recorder.missing_exception(Expected,actual,__stackframe__,location)
        
    def raises(self,Expected, satisfying = lambda ex : True ,__stackframe__=0):

        """XXX TBD"""
        
        self.check_raises(self.expectee,Expected,satisfying = satisfying, location=self.location)
        
    def raising(self,table,stackframe_depth=0):

        """XXX TBD"""
        
        for value in table:
            self.check_raises(lambda: self.expectee(value),table[value],location=self.location)
        return self    


# TODO: source lines: replace multiple white spaces by one simple space
