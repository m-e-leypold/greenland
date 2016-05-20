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

#   TODO: output to stderr (Requires using DocTestRunner)


import sys
import unittest

class TestCase (unittest.TestCase): pass

class ModuleUnderTestNotUnique(Exception): pass
class ModuleUnderTestNotFound(Exception):  pass

__suite__ = sys.modules['__main__']


def __find_mut__(m):
    objs = m.__dict__
    
    if 'MUT' in objs: return m.MUT
    if 'M'   in objs: return m.M

    M = None
    
    for name in objs:
        obj = objs[name]
        if (type(obj) == type(__suite__)) and (obj.__name__ != 'builtins'):
            if M != None:
                raise ModuleUnderTestNotUnique("module under test not unique in {suite}: {module1} vs. {module2}."
                                               .format( suite=__suite__.__file__, module1=M.__name__, module2=obj.__name__ ))
            M = obj
    if M == None: raise ModuleUnderTestNotFound("module under test not found in {suite}.".format(suite=__suite__.__file__))
    return M

__mut__   = __find_mut__(__suite__)

def execute_tests():
    __run_unittest__(__suite__)
    __run_doctests__(__mut__)

def __run_doctests__(module):        
    import sys
    import doctest
    m = module

    filename = m.__name__.replace(".","/")+".py"
    
    sys.stdout.write("=> doctests " + filename  + "   ... ")
    
    (failed, tested) = doctest.testmod(m,report=True)
    if (failed==0):
        sys.stdout.write("OK  (tested: {count:>2}).\n".format(count=tested))
    else:
        sys.stdout.write("\n=> selftests for " + m.__file__ + " failed: ")
        sys.stdout.write("tested = "+ str(tested)  +", failed = " + str(failed) + ".\n")        

def __run_unittest__(suite):

    import sys
    import tempfile
    
    sys.stderr.write("=> unittest {name} ... ".format(name=suite.__file__))
    suite  = unittest.TestLoader().loadTestsFromModule(suite)
    report = tempfile.TemporaryFile(mode="w+")
    result = unittest.TextTestRunner(verbosity=0,stream=report).run(suite)

    if result.failures or result.errors:
        sys.stderr.write("***FAILED*** => tested = {tested}, failed = {errors}.\n\n".format(tested=result.testsRun,errors=len(result.failures)+len(result.errors)))
        report.seek(0)
        for line in report.readlines():
            sys.stderr.write(" "*3)
            sys.stderr.write(line)
        sys.stderr.write("\n")
    else:
        sys.stderr.write("OK  (tested: {count:>2}).\n".format(count=result.testsRun))        

# helper functions

def raise_and_print(ex):
    try:
        raise ex
    except Exception as e:
        print(e)

