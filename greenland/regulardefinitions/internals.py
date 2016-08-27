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

from greenland.stringsystems import *
import re
import string

class MissingFieldClose(Exception): pass

class RegexFormatter ( string.Formatter ):

    __rx_open_delim__ = re.compile("([{]{2,3})|([}]{3})")
    __rx_field_spec__ = re.compile("(?P<fieldname>[0-9_A-Za-z.-]+)[}]{2}")

    def parse(self,template):
        fields = tuple(self.__parse__(template))
        return fields
    
    def __parse__(self,template):

        if template == None:
            yield((None,None,None,None))
            return
        
        while len(template)>0:
            m = self.__rx_open_delim__.search(template)
            if not m:
                yield(template,None,None,None)
                return
            else:
                i = m.start()
                j = m.end()
                if (j-i) == 2:
                    text = template[:i]
                    template = template[j:]
                    m = self.__rx_field_spec__.match(template)
                    if m:
                        i = m.start()
                        j = m.end()                    
                        yield(text,m.group(1),None,None)
                        template = template[j:]
                    else:
                        raise MissingFieldClose(template)
                else:
                    yield(template[:j-1],None,None,None)
                    template = template[j:]

                    
class RegularDefinitionsBase ( StringSystem ):

    formatter = RegexFormatter()

    def __init__(self):
        super().__init__()
        self.__convert__ = {}
    
    def compile(self,symbol,text):
        return RegexProxy(self,symbol,re.compile(text))

    def __define_group__( self, symbol, text ):

        text = "(?P<"+symbol+">"+text+")"        
        StringSystem.__define__(self,symbol,text)

    def __define__( self, symbol, text, conversion = None ):
        if type(text) == tuple:
            assert len(text) == 2
            self.__define__(symbol, text[0], text[1] )
        else:
            self.__define_group__( symbol, text )
            if conversion:
                self.__convert__[symbol] = conversion
    
    def __define_expr__( self, symbol, text ):
        text = "(?:"+text+")"
        super().__define__(symbol,text)

    def __convert_field__( self, symbol, text ):
        if symbol in self.__convert__:
            return self.__convert__[symbol](text)
        else:
            return text

    @property
    def expr(self): return ExprProxy(self)
        
class ExprProxy( object ):

    def __init__(self, defs):
        self.__defs__ = defs

    def __setattr__(self,symbol,val):

        if symbol[0]=='_':
            self.__dict__[symbol]  = val
            return
        
        self.__defs__.__define_expr__(symbol,val)
        
class RegexProxy ( object ):

    def __init__(self,defs,name,rx):
        self.__defs__ = defs
        self.rx   = rx
        self.name = name
        
    def match(self,text):
        m = self.rx.match(text)
        if m: return MatchProxy(self.__defs__,self.name,m)
        else: return m
        
    def __repr__(self): return "<{CLASS} {NAME} {RX_REPR}>".format(CLASS = __name__+"."+self.__class__.__qualname__, NAME=self.name, RX_REPR = repr(self.rx))

    @property
    def regex(self): return self.rx
    
class MatchProxy (object):

    def __init__(self, defs, name, match):
        self.__defs__ = defs
        self.raw=match
        # self.groups = match.groupdict()
        self.name = name
        self.__groups__ = None
        
    @property
    def groups(self):
        if self.__groups__ == None:
            self.__groups__ = {}
            matched = self.raw.groupdict()
            convert = self.__defs__.__convert_field__
            for symbol in self.raw.groupdict():
                self.__groups__[symbol] = convert(symbol,matched[symbol])
        return self.__groups__
    
    def __getattr__(self,name):
        return self.groups[name]
    
    def __repr__(self):
        return "<{CLASS} {NAME} {FIELDS}>".format(CLASS = __name__+"."+self.__class__.__qualname__, NAME=self.name, FIELDS=self.groups)

    @property
    def fields (self): return self.groups
    

def regular_definitions():
    rx   = RegularDefinitionsBase()
    expr = rx.expr
    return (rx,expr)
