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


"""This module contains a small test framework which currently is only
used within the greenland development effort to bootstrap the "official"
testframework (`greenland.testing.framework`).

Do not use this module.
"""

class TestError(Exception):
    def __init__(self,message):
        super(Exception,self).__init__(message)

class TestErrorPredicate(Exception):
    def __init__(self):
        super(Exception,self).__init__("assertion failed.")

class TestErrorRaises(Exception):
    def __init__(self,ex):
        super(Exception,self).__init__("exception raised: "+repr(ex))        

class TestErrorRaisedNot(Exception):
    def __init__(self,actual,expected):
        super(Exception,self).__init__(
            "did not raise: expected: "+repr(expected)  + "; actual = " + repr(actual) +"."
        )

class TestErrorRaisedWrong(Exception):
    def __init__(self,actual,expected,satisfying):
        super(Exception,self).__init__(
            "raised unexpected exception: expected: "+repr(expected)  + "; actual = " + repr(actual) + "; satisfying = " + repr(satisfying) + "."
        )
        
        
class TestErrorComparing(Exception):

    def __init__(self,actual,op,expected):
        super(Exception,self).__init__(
            "not (expected " + op + " actual): expected = " + repr(expected) + "; actual = " + repr(actual) +"."
        )

class TestErrorShouldNotBeReached(Exception):
    def __init__(self):
        super(Exception,self).__init__("This source location should not be reached (missing exception?)")
        

import operator as op

operator = {
    "==" : op.eq
}


def test_check(a,op,b):
    compare = operator[op]
    if not compare(a,b):
        raise TestErrorComparing(a,op,b)

def test_assert(p):
    if not p:
        raise TestErrorPredicate()    

def test_assert_not_reached(p):
    raise TestErrorShouldNotBeReached()


def test_assert_raises_not(p):
    try:
        _ = p()
    except Exception as ex:
        raise TestErrorRaises(ex)

def test_assert_raises( p, raises, satisfying = None ):
    Ex = raises
    try:
        actual = p()
        raise TestErrorRaisedNot(actual,Ex)
    except Exception as ex:
        if  not issubclass(ex.__class__,Ex) or ( satisfying != None and not (satisfying(ex))):
            raise TestErrorRaisedWrong(ex,Ex,satisfying)            
        

class test(object):

    """This class serves as namespace for test assertion vocabulary. Never
       import * from `greenland.testing`, but only this class. Then write your assertions as (e.g.)
       `test.check.raises(...)`.

       *Usage*: `from greenland.testing.simple import test`

       `test` then provides the following methods as test vocabulary:

       - `check( cond )` -- check condition *cond*.

       - `check.raises( thunk, What, satisfying = lambda ex: true
         )` -- check that *thunk* raises exception of type *What*,
         satisfying the condition `satisfying`.

       - `check.raises_not( thunk )` -- check that *thunk* does
         not raise.
       
       - `check.not_reached()` -- check that this statement is
         not reached.
     
       - `check( x, operator, y )` -- check that `(x operator
         y)`. The `operator` should be given as a string like in
         `check( 15, "<", 16 )`.
    
    
       For details see methods of the `__check__` class below.
       (...)

    """

    assert_raises       = test_assert_raises
    assert_not_reached  = test_assert_not_reached

    class __check__(object):

        """Check operations. Don't use this class directely, but rather the instance `check` below.           
        """
        
        def __call__(self,*pargs):
            if len(pargs) == 3: test_check(*pargs)
            else: test_assert(*pargs)

        def raises      (self,*pargs,**kwargs):  test_assert_raises(*pargs,**kwargs)
        def raises_not  (self,*pargs,**kwargs):  test_assert_raises_not(*pargs,**kwargs)        
        def not_reached (self,*pargs,**kwargs):  test_assert_not_reached(*pargs,**kwargs)

    check = __check__() #: The `check` namespace, see class `__check__` for contents.
