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


"""Poor mans tracing decorators.

Getting these to print nice backtraces still requires some amount of
work.Currently only used for greenland upstream development. Not
thought to be used by the end user;-).

"""



from types import *
import sys

def trace_fun_call(p,*pargs,**kwargs):
    sys.stderr.write("=> {proc}(*{pargs},**{kwargs})\n".format(proc=p.__qualname__,pargs=pargs,kwargs=kwargs))

def trace_fun_result(p,r,*pargs,**kwargs):
    sys.stderr.write("<= {result} <= {proc}(*{pargs},**{kwargs})\n\n".format(result=r,proc=p.__qualname__,pargs=pargs,kwargs=kwargs))
    
def traced_function(p):
    def traced(*pargs,**kwargs):
        trace_fun_call(p,*pargs,**kwargs)
        r = p(*pargs,**kwargs)
        trace_fun_result(p,r,*pargs,**kwargs)
        return r
    return traced

def traced(p,*pargs,**kwargs):
    if type(p) == FunctionType:
        assert len(pargs)  == 0
        assert len(kwargs) == 0
        return traced_function(p)
    else:
        assert false # not yet implemented
