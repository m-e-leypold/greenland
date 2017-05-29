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


class Result(object):
    def __init__(self,Class,value):
        self.Type  = Class
        self.value = value

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.value)+")"

        
class Value(Result):

    def __init__(self,value):
        super(Value,self).__init__(Value,value)

    def resurrect(self):
        return self.value        
        
class Excn(Result):        
    def __init__(self,ex):
        super(Excn,self).__init__(Excn,ex)

    def resurrect(self):
        raise self.value

def apply(callee,*pargs,**kwargs):
    try: 
        value = callee(*pargs,**kwargs)
        return Value(value)
    except Exception as ex:
        return Excn(ex)
