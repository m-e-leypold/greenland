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

import string

class NameAlreadyExists (Exception): pass



class StringSystem ( object ):

    formatter = string.Formatter()
    
    def __init__(self):
        self.__templates__ = {}
        self.__texts__     = {}
        self.__cache__     = {}
        
    def compile( self, symbol, text ):
        return text

    def __define__( self, symbol, template ):
        assert not symbol in self.__templates__
        self.__templates__[symbol] = template
        self.__texts__[symbol]     = self.formatter.format(template,**self.__texts__)

    def __getattr__(self,symbol):
        
        if symbol in self.__cache__: val = self.__cache__[symbol]
        else                   :
            if symbol in self.__texts__:
                val = self.compile( symbol, self.__texts__[symbol] )
                self.__cache__[symbol]=val
            else:
                raise AttributeError(symbol)
            
        return val
        

    def __setattr__(self,symbol,val):

        # recursion: need to except __*-symbols
        
        if symbol[0]=='_':
            self.__dict__[symbol]  = val
            return
        
        if symbol in self.__texts__: raise NameAlreadyExists(symbol)
        self.__define__(symbol,val)
