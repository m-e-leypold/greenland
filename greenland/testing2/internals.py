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

"""  Standalone test framework implementation

     Test suites are classes deriving from 'Tests', decorated by the
     'suite' decorator whose tests are methods decorated by the 'test'
     decorator. Like

       @suite
       class MyTests (Tests):
         
         @test
         def basics(self,expect,**more):
             do_stuff()
             expect( lambda: froom() ) .returns (17)

         @test
         def complex(self,expect,**more):
             do__more_stuff()
             expect( lambda: froom(137) ) .returns ("fine structure")
             do_even_more_stuff()
             expect( lambda: froom(-1) ) .raises (FroomError)

     Where to find more information (parameters):

     - @suite   => class Suite
     - @test    => test_decorator
     - Tests    => see class Test for optional flags
     
     For test execution and reporting => (...)

"""

# TODO: abort_on_failure
#       error_is_failure (per suite!)


import sys, os, copy
import traceback

class TestsuiteMeta ( type ):

    r""" The meta class of 'Tests', provides the @test decorator within
    classes derived from 'Tests'.
    """
    
    def __prepare__(mcl,parent_classes):
        d = (type.__prepare__(parent_classes)).copy()        
        d['__tests__'] = []
        
        def test_decorator(f):
            r""" The decorator for methods that are to be excuted as tests. 

            This decorator only exists at definition time (as @test)
            in classes that have TestSuiteMeta as metaclass.

            '@test' will only record the method in the class member
            __tests__. It is up to the __init__ method of Tests (or
            any other class of the same metaclass) to actually rewrite
            __tests__ to something more useful.  
            """
            
            d['__tests__'].append(f)
            return f

        d['test']=test_decorator
        
        return d

    
class TestFailed( Exception ):

    r""" will be raised when a test fails.

    Tests created by the test decorator will be executed until they
    return or raise an exception. The test vocabulary (see
    TestRunControl and Expectations, usually mapped to parameters
    'test' and 'expect') will raise an exception derived from
    TestFailed to achieve a non local exit. Every exception raised
    from a test counts as failure. Every normal as success (pass).

    TestFailed and instances of more specific exception classes
    already contain more detailed information why the test failed
    (which expectation was not met), whereas other exceptions are
    mapped to UnexpectedException.   
    """

    # Note/TODO: The exceptions need to be reworked when
    # infrastructure for better exception messages has arrived in
    # greenland.
    
    def __init__( self, test, frame_index = -1 ):
        self.test = test

        sf = traceback.extract_stack()[frame_index-2]
        
        self.line       = sf.line
        self.lineno     = sf.lineno
        self.filename   = sf.filename
        
    def __repr__(self):
        return "<{CLASS} at {FILENAME}:{LINENO}: {SOURCE}>".format(
            CLASS    = self.__class__.__name__,
            FILENAME = self.filename,
            LINENO   = self.lineno,
            SOURCE   = self.line
        )

    def message(self):
        return self.__class__.__name__
    
    def __str__(self):
        return "{MSG} in: {SOURCE}".format(
            MSG      = self.message(),
            SOURCE   = self.line
        )

    def error(self):
        return "{FILENAME}:{LINENO}: {MSG} in: {SOURCE}".format(
            MSG      = self.message(),
            FILENAME = self.filename,
            LINENO   = self.lineno,
            SOURCE   = self.line
        )

    
class UnexpectedException ( TestFailed ):

    r""" Will be raised when an exception escapes the test (that is, an
    exception occurs, but was not expected via expect(...).raises(...)
    or when an exeception is raised that has a different type than
    expected or does not satify the 'satisfies' predicate.
    """
    
    def __init__( self, test, exception, expected = None, frame_index = -1 ):
        super().__init__(test, frame_index - 1)
        self.exception = exception
        self.expected  = expected

    def message(self):
        return "got {RESULT} but expecting {EXPECTED}".format(
            EXPECTED = repr(self.expected),
            RESULT   = repr(self.exception)
        )
        

class UnexpectedResult ( TestFailed ):

    r""" Will be raised when the result returned in a
    expect(...).returns(...) clause is not identical to the expected
    result.    
    """
    
    def __init__( self, test, result, expected, frame_index = -1 ):
        super().__init__(test, frame_index - 1)
        self.expected = expected
        self.result   = result

    def message(self):
        return "got {RESULT} but expecting {EXPECTED}".format(
            EXPECTED = repr(self.expected),
            RESULT   = repr(self.result)
        )

    
class ResultStatus ( object ):
    "Tokens that indicate the status of a test result: PASSED, FAILED, SKIPPED, IN_PROGRESS"
    
    def __init__(self,name):
        self.name = name

    def __str__(self): return self.name

    
class TestResult( object ):

    r""" Result returned from running a single test (a method of class
    derived from Tests and marked with @test).
    """

    PASSED      = ResultStatus("PASSED")
    FAILED      = ResultStatus("FAILED")
    SKIPPED     = ResultStatus("SKIPPED")
    ERROR       = ResultStatus("ERROR")
    IN_PROGRESS = ResultStatus("IN_PROGRESS")
    
    def __init__(self,test):
        self.tics = 0
        self.test   = test
        self.status = self.IN_PROGRESS
        self.event  = None
        
    def record_success(self):
        self.status = self.PASSED

    def record_error(self, event = None ):
        self.status = self.ERROR
        self.event  = event
        
    def record_failure( self, event = None ):
        self.status = self.FAILED
        self.event  = event
        
    def tic(self):
        assert self.status == self.IN_PROGRESS
        self.tics += 1

    def __repr__(self):
        return "<test result '{NAME}': {STATUS}, {N} tics>".format(STATUS=str(self.status),N=self.tics,NAME=self.test.name)

    def __str__(self):
        if self.status == self.FAILED:
            return "{STATUS} (at {N} tics): {CAUSE}".format(STATUS=str(self.status),N=self.tics, CAUSE=str(self.event))            
        elif self.status == self.ERROR:
            return "{STATUS} (at {N} tics): {CAUSE}".format(STATUS=str(self.status),N=self.tics, CAUSE=str(self.event))
        else:
            return "{STATUS} ({N} tics)".format(STATUS=str(self.status),N=self.tics)            
    
    def error(self):
        assert self.event != None
        return self.event.error()
        
class TestRunControl( object ):

       
    def __init__( self, result ):
        self.result       = result
        
    def done(self):
        self.result.record_success()

    def fail(self, exc = None ):
        if exc == None:            
            exc = TestFailed(self.result.test, frame_index = -2 )
        self.result.record_failure(exc)
        raise exc

        
    def tic(self):
        self.result.tic()

    def expect(self,expr):
        return Expectations(self,expr)
    
class Expectations ( object ):

    """Callback to express expectations in tests"""

    
    def __init__( self, test, expr ):
        super().__init__()
        self.test    = test  # actually a TestRunControl interface
        self.expr    = expr

    def raises(self,cls, satisfying = lambda ex : True ): 
        self.test.tic()
        try:
            r = self.expr()            
            failure = MissingException( self.test, cls )
            self.test.fail(failure)
            assert False            
        except cls as ex:
            if satisfying(ex): return
            failure = UnexpectedException( self.test, ex )
            # TODO: use extra exception type for that case.            
            self.test.fail(failure)
            assert False
        except Exception as ex:
            failure = UnexpectedException( self.test, ex, cls )
            self.test.fail(failure)
            assert False
            
    def returns(self,value):

        self.test.tic()
        
        try:
            r = self.expr()            
        except Exception as ex:
            failure = UnexpectedException( self.test, ex, frame_index = -1 )
            self.test.fail(failure)
            assert False
            
        if r != value:
            failure = UnexpectedResult( self.test, r, value, frame_index = -1 )
            self.test.fail(failure)
            assert False
        
class Test (object):

    def __init__(self,suite,test):
        self.suite      = suite
        self.test       = test


    @property
    def basename(self):
        return self.test.__name__

    @property
    def name(self):
        return "{SUITE}.{BASENAME}".format(SUITE=self.suite.name(),BASENAME=self.basename)
    
    def __repr__(self):
        return "<test {name}>".format(name=self.basename)

    def new_control(self):
        return TestRunControl(TestResult(self))
                

    def run(self):
        print("\n=> running test: {name} ... ".format(name=self.basename), file=sys.stderr, end=" ")

        control = self.new_control()
        try:            
            self.test(self=suite,expect=control.expect,test=control)
            control.done()
        except TestFailed as ex:
            control.result.record_failure(ex)
        except Exception  as ex:
            # TODO: Log exception here ...
            failure = UnexpectedException( self.test, ex, frame_index = -1 )
            #
            # TODO: This must go into extra exception class. Must show backtrace of the exception caught and raise location.
            #            
            control.result.record_error(failure)

        assert (   control.result.status == TestResult.PASSED
                or control.result.status == TestResult.FAILED
                or control.result.status == TestResult.ERROR )

        print ( str(control.result), file=sys.stderr )
        if not control.result.status == TestResult.PASSED:        
            print ( control.result.error(), file=sys.stderr )
        return control.result

        # should be more ...

    def tic(self):
        self.__result__.tic()
        
        
class Tests ( object, metaclass = TestsuiteMeta ):    
    
    def __init__(self):

        print(file=sys.stderr)
        print("=> Preparing suite {name}, {N} test(s) ...".format(N=len(self.__tests__),name=self.name()), file=sys.stderr, end=" ")
        self.__tests__ = [ Test(self,test) for test in self.__tests__ ]
        
        # still need to work on the expectation interface, though.
        # process stuff in __tests__ (actually: Just bind the test methods
        pass # setup run, but don't run yet.


    @property
    def tests(self):
        return self.__tests__

    def prepare(self):
        pass
    
    def finish(self):
        pass    
    
    @classmethod
    def execute(cls):
        process = cls()
        result  = None
        try:
            try:
                process.prepare()
                result = process.run_tests()
            except:
                print(" *** preparations failed ***",file=sys.stderr, end="\n\n")
                traceback.print_exc(file=sys.stderr)
                result = None # must be handled properly by caller
        finally:
            process.finish()
        return result

    def run_tests(self):
        results = {}
        for t in self.tests:
            r = t.run()            
            results[t.basename]=r
            # TODO: maybe bail out if "abort_on_failure"
        return results
    
    @classmethod
    def group(cls):
        group = os.path.normpath(sys.modules[cls.__module__].__file__)
        return group
    
    @classmethod
    def name(cls):
        group = cls.group()        
        return "{group}.{name}".format(group=group,name=cls.__name__)


__suites__ = []

class SuiteSummary( object ):
    def __init__(self,suite,results):
        self.suite        = suite
        self.results      = results
        self.test_count   = 0
        self.tics         = 0
        self.suite_count  = 1
        self.passed       = 0
        self.failed       = 0
        self.skipped      = 0        
        self.errors       = 0
        self.preparations_failed = 0
        
        if results != None:
            for name in results:
                r=results[name]
                self.test_count += 1
                self.tics       += r.tics        
                if   r.status == TestResult.PASSED:  self.passed  += 1
                elif r.status == TestResult.FAILED:  self.failed  += 1
                elif r.status == TestResult.SKIPPED: self.skipped += 1
                elif r.status == TestResult.ERROR:   self.errors  += 1
        else:
            self.preparations_failed = 1
            
    def add(self, test_summary ):
        return


    def __repr__(self):
        
        return ("<results(suite={SUITE}) {PASSED} passed, {FAILED} failed, {ERRORS} errors in {N} test(s); {TICS} tics; skipped {SKIPPED}>"
                .format( SUITE=self.suite.name,
                         N=self.test_count,
                         TICS=self.tics,
                         PASSED=self.passed,
                         FAILED=self.failed,
                         ERRORS=self.errors,
                         SKIPPED=self.skipped
                ))

    def __str__(self):
        if self.results == None:
            return "{SUITE} => *** PREPARATIONS FAILED *** ".format(
                SUITE=self.suite.name
            )
        if self.skipped ==0:
            skipped = ""
        else:
            slipped = ", skipped {SKIPPED}".format(SKIPPED=self.skipped)
        if self.failed == 0:
            return "{SUITE} => all tests passed (of {N}){SKIPPED}".format(
                SUITE=self.suite.name,
                N = self.test_count,
                SKIPPED = skipped
            )
        elif (self.errors+self.failed) != 0:
            return "{SUITE} => *** {FAILED} FAILED, {ERRORS} ERRORS, {PASSED} PASSED *** (of {N}){SKIPPED}".format(
                SUITE=self.suite.name,
                N = self.test_count,
                FAILED=self.failed,
                ERRORS=self.errors,
                PASSED=self.passed,
                SKIPPED = skipped
            )
        else:
            
            return repr(self)


class TotalSummary( object ):
    def __init__(self, summaries):
        self.summaries   = summaries
        self.suite_count = 0
        self.test_count  = 1
        self.failed      = 0
        self.passed      = 0
        self.errors      = 0
        self.skipped     = 0        
        self.preparations_failed = 0
        self.tics = 0
        for s in summaries:
            self.suite_count += 1
            self.test_count  += s.test_count
            self.failed      += s.failed
            self.passed      += s.passed
            self.errors      += s.errors
            self.skipped     += s.skipped            
            self.preparations_failed += s.preparations_failed
            self.tics += s.tics
            
    def summary_line(self):
        return "{N} suites: {PASSED} passed tests, {FAILED} failed, {ERRORS} errors, {SKIPPED} skipped; {FAILED_PREPS} failed suite preparation(s); {TICS} assertions (tics).".format(
            N      = self.suite_count,
            PASSED = self.passed,
            FAILED = self.failed,
            ERRORS = self.errors,
            SKIPPED = self.skipped,
            TICS    = self.tics,
            FAILED_PREPS = self.preparations_failed 
        )
    
    def print(self,file):
        for s in self.summaries:
            print(s,file=file)
        print("---",file=file)
        print(self.summary_line())
        
class Suite():
    def __init__(self,Definitions):
        self.Definitions = Definitions
        __suites__.append(self)

        
    @property
    def name(self):
        return self.Definitions.name()

    def execute(self):
        results = self.Definitions.execute()
        return SuiteSummary(self,results)
        
    def __str__(self): return self.name
    def __repr__(self): return "<tests {name}>".format(name=self.name)

    def __call__(self):
        return self.execute()
    
def suite( Defs = None ,**kwargs):
    if Defs != None:
        suite = Suite(Defs, **kwargs)
        return suite
    else:    
        return lambda defs : Suite(defs,**kwargs)

    # TODO: Consider to return a wrapper that can run a suite instead. 

    
def suites(): return __suites__

def execute_suites(): 
    return TotalSummary([ suite.execute() for suite in suites() ])
    # TODO: option: parameters to determine which suites to run?
    
def execute_suites_and_report():
    s = execute_suites()
    print("\n---", file=sys.stderr)
    s.print(file=sys.stderr)
    if s.failed == 0 and s.errors == 0 and self.failed_preparations == 0:
        exit(0)        
    else:
        print("\n*** TESTS FAILED OR CRASHED ***", file=sys.stderr)
        exit(1)

    
