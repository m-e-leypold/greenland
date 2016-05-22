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

from abc import abstractmethod, ABCMeta

class ProcessError(Exception):
    pass

class ProcessFailed( ProcessError ):
    pass

class ProcessGotKilled( ProcessError ):
    pass

class Status (object, metaclass=ABCMeta):

    def __init__( self, proc, prg ):
        self.proc = proc
        self.prg  = prg
        
    @property
    def failed    ( st ): return st.killed or st.prg.has_failed(st)
    @property
    def succeeded ( st ): return not self.failed
    
    @property
    @abstractmethod
    def killed ( st ): pass

class Program ( object, metaclass=ABCMeta ):

    ProcessFailedType     = ProcessFailed
    ProcessGotKilledType  = ProcessGotKilled

    def ProcessGotKilled( self, proc ): return ProcessGotKilled(proc)
    def ProcessFailed( self, proc ): return ProcessFailed(proc)
    
    StatusType = Status    

    def Status( self, proc, *pargs, **kwargs ):
        return self.StatusType( proc, self, *pargs, **kwargs )       
    
    @abstractmethod
    def __init__( self, *pargs, **kwargs ):
        super().__init__( *pargs, **kwargs )
    
    @property
    @abstractmethod
    def ProcessType( my ): pass
    
    def start ( my, *pargs, **kwargs ):
        proc = my.ProcessType( my, *pargs, **kwargs )
        proc.start()
        return proc

    def run   ( my, *pargs, **kwargs ):
        proc   = my.start( *pargs, *kwargs )
        result = proc.run()
        return result

    @abstractmethod
    def has_failed    ( self, st ): pass

class Process (object, metaclass=ABCMeta):

    def Status( self, *pargs, **kwargs ): return self.prg.Status( self, *pargs, **kwargs )

    def __init__( my, prg, *pargs, **kwargs ):
        
        super().__init__( *pargs, **kwargs )
        my.prg    =  prg        
        my.status    = None
        my.finished  = None
        my.executing = False
        my.result    = None
        
    def run(my):   my.start(); return my.wait()
    
    @abstractmethod
    def start(my):
        my.finished   = False
        my.executing  = True

    def wait( my ) :
        my.executing  = False
        my.finished   = True
        if my.killed:
            raise my.prg.ProcessGotKilled(my)
        if my.failed:
            raise my.prg.ProcessFailed(my)
        my.result = my.get_result()
        return my.result
        
    @property
    def failed (self): return self.status.failed

    @property
    def killed (self): return self.status.killed
    
    @property
    def succeeded (self): return not self.failed

    def get_result(self):
        return None
