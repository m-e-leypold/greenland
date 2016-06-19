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

"""Implements _synchronous_ shell procedures with the greenland.processpattern.
"""

import greenland.processpattern as pp
from   abc import abstractmethod, ABCMeta
import greenland.debugging as _dbg

import os


class Driver ( object ):
    def __init__ ( self, parse = None ):
        if parse == None:
            self.parse = lambda x: x
        else:
            self.parse = parse

        
class GetStdoutDriver ( Driver ):
    def __call__( self, script ):
        result     = None
        f =  os.popen( script )    # error handline
        result = f.readlines()
        statuscode = f.close()
        if statuscode == None: statuscode = 0
        return ( self.parse(result), statuscode )

class GetExitcodeDriver ( Driver ):
    def __call__( self, script ):
        statuscode = os.system( script )
        return ( None , statuscode )
    
class RunOnlyDriver ( Driver ):
    def __call__( self, script ):
        result     = None
        statuscode = os.system( script )
        return ( self.parse(result), statuscode )
            
STDOUT    = GetStdoutDriver
EXITCODE  = GetExitcodeDriver

class ExitStatus ( pp.Status ):

    def __init__( self, proc, prg, statuscode ):
        super().__init__(proc,prg)
        self.statuscode = statuscode

    @property
    def killed ( self ):
        return self.statuscode % 256 != 0

    def signal ( self ):
        if not self.killed: return None
        return self.statuscode % 256
    
    def exitcode ( self ):
        if self.killed: return None
        else: return self.statuscode // 256

    def __str__( self ):
        if self.killed:
            return "signal {N}".format( N = self.signal() )
        else:
            return "exitcode {N}".format( N = self.exitcode() )
        
class ShellCall ( pp.Process ):

    def __init__( my, prg, *pargs, **kwargs ):
        super().__init__( prg, *pargs, **kwargs )
        my.script = my.prg.expand_template(*pargs,**kwargs)
        
    def start( self ):
        super().start()
        self.__result__, self.__status__= self.prg.run_process( self )
        return self

    def get_result( self ): return self.__result__
    def wait( self ): self.status = self.__status__; return super().wait()
        

class ShellProgram ( pp.Program ):    

    def __init__( self, returns = None, parse = None, ignore_exits = [0] ):

        super().__init__()

        self.ignore_exits = ignore_exits
        self.driver = None
        
        if returns == None:
            if parse == None:
                self.driver = RunOnlyDriver()
            else:
                self.driver = GetStdoutDriver(parse)
        else:
            self.driver = returns(parse)

            
        
    ProcessType = ShellCall
    
    def has_failed      ( self, st ):
        return (st.signal() or (not st.exitcode() in self.ignore_exits))

    @abstractmethod
    def expand_template ( self, *pargs, **kwargs ): pass

    def run_process     ( self, process ):
        ( result, statuscode ) = self.driver( process.script )
        return ( result, ExitStatus(process,self,statuscode) )
        


