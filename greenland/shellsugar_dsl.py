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

r""" Defines a simple shell script template language
"""

# TODO: Recognize opened but not closed brackets as error.

import string
import re
import sys

from abc import ABCMeta, abstractmethod

class __SimpleSubst__ ( string.Template ):
    def where(self,*pargs,**kwargs):
        return self.substitute(*pargs,**kwargs)
    def __call__( self, **kwargs ):
        return self.where(**kwargs)
        
_ = __SimpleSubst__

# TODO distinguish labels and identifiers!
    
identifier = r'[_a-z][_a-z0-9]*'
flag       =  _( r'(?:${PREFIX}${ID}(?:[:]${ID}){0,1})'                  )
option     =  _( r'(?:${PREFIX}${ID}(?:[${SEPS}](?:${ID}|[.]{3})){0,1})' )

item       =  _( r'(?:${ID})'     ) .where( ID=identifier )
list       =  _( r'(?:${ID} ...)' ) .where( ID=identifier )

gnu        = { 'ID' : identifier, 'PREFIX' : "--", 'SEPS' : '=' }
classic    = { 'ID' : identifier, 'PREFIX' : "-",  'SEPS' : ' ' }

options = {
    'GNUFLAG'     : flag    .where( **gnu ),
    'CLASSICFLAG' : flag    .where( **classic ),
    'GNUOPT'      : option  .where( **gnu ),
    'CLASSICOPT'  : option  .where( **classic ),
    'ITEM'        : item,
    'LIST'        : list
}

argtypes = {
    'OPTARG' : _( r'(?P<optarg>\[(?:${GNUFLAG}|${GNUOPT}|${CLASSICFLAG}|${CLASSICOPT}|${ITEM}|${LIST})])' ) .where( **options ),
    'NONOPT' : _( r'(?P<nonopt>[<](?:${ITEM}|${LIST})[>])' ) .where( **options )    
}

pattern     = _( r'(?:(?P<braced>(?P<named>${OPTARG}|${NONOPT})))' ) .where ( **argtypes )
sourcespec  = _( r'(?P<labelprefix>[+-]{1,2}){0,1}(?P<label>${ID})(?:(?P<separator>[ :=])(?:(?P<key>${ID})|(?:[.]{3}))){0,1}$$' ) \
              .where ( ID = identifier )

def quote(s):
    return "'"+s.replace("'","'\"'\"'")+"'"

def format_item (value ):
    if type(value) == str:
        return quote(value)
    else:
        return quote(str(value))

def format_list ( values ):
    return ' '.join( [ format_item( value ) for value in values ] )
    
def format ( value ):
    if type(value) == str:
        return format_item(value)
    elif hasattr(value,'__iter__'):
        return format_list(value)
    else:
        return format_item(value)


# much of the stuff below should go to a different module

class MissingArgument( Exception ): pass
    
class Translator( object, metaclass = ABCMeta):
    def __init__(self,label,key=None):
        self.label = label
        self.key = key if key else label

    @abstractmethod
    def get( self, **kwargs ): pass
    
class FieldArgument ( Translator ):

    def __init__(self,label,optional):
        super().__init__(label,label)     # key is label then
        self.optional = optional
        
    def get( self, **kwargs ):
        
        if not self.key in kwargs:
            if not self.optional: raise MissingArgument(self.key)
            return ""

        return format_item(kwargs[self.key])
        
class ListArgument ( FieldArgument ):

    def get( self, **kwargs ):
        
        if not self.key in kwargs:
            if not self.optional: raise MissingArgument(self.key)
            return ""

        value = format(kwargs[self.key])
        
        if len(value) == 0 and not self.optional:
            raise MissingArgument(self.key)
        else:
            return value
        
class LabelledArgument ( Translator ):
    def __init__(self,prefix,label,key=None):

        super().__init__(label,key)
        self.prefix = prefix
 
    def get( self, **kwargs ): assert False; return None

class FlagArgument ( LabelledArgument ):    

    def get( self, **kwargs ):
        if not self.key in kwargs:
            return ""
        v = kwargs[self.key]
        if  v in [False,None]:
            return ""
        assert v==True
        return self.prefix + self.label


class OptionArgument ( LabelledArgument ):
    def __init__(self,prefix,label,sep=None,key=None):
        super().__init__(prefix,label,key)
        self.sep = sep

    def get( self, **kwargs ):
        if not self.key in kwargs:
            return ""
        return self.prefix+self.label+self.sep+format_item(kwargs[self.key])

class Template ( string.Template ):
    __p__ = pattern
    pattern = __p__
    field_pattern = sourcespec
    
    
    def __init__(self,template):
        super().__init__(template)
        self.field_pattern = re.compile(self.field_pattern)
        self.translator = { }
        fields = self.fields =  self.search_fields()
        for f in fields:
            key  = template[f.start():f.end()]
            if not key in self.translator:
                spec = key[1:-1]
                self.translator[key] = self.get_translator(spec,f)
        
    def get_translator(self,spec,match):
        d        = match.groupdict()
        optional = ('optarg' in d)
        if not optional: assert 'nonopt' in d

        m = self.field_pattern.match(spec)
        assert(m)
        
        d = m.groupdict()

        translator = None

        label = d['label']
        
        if (not 'labelprefix' in d) or not d['labelprefix']:
            if ('key' in d) and d['key']:
                assert d['key'] == '...'            
                translator = ListArgument  (label,optional)
            else:
                translator = FieldArgument (label,optional)
        else:
            prefix = d['labelprefix']
            if 'key' in d and d['key'] and (not d['key'] == "..." ):
                key = d['key']
            else:
                key = label        
            if (not 'separator' in d or not d['separator']) or d['separator']==':':
                sep = None
            else:
                sep = d['separator']
                
            if not sep:
                translator = FlagArgument(prefix,label,key)
                pass
            else:
                translator = OptionArgument(prefix,label,sep,key)
                pass
            
        return translator
            
    def search_fields( self ):
        fields = []
        i = 0
        m = self.pattern.search( self.template, i )
        while m:
            fields.append(m)
            i = m.end()
            m = self.pattern.search( self.template, i )
        return fields

    def translate_args( self, **kwargs ):
        values = { }
        for k in self.translator:
            values[k] = self.translator[k].get(**kwargs)
        return values
    
    def expand ( self, **kwargs ):
        return self.substitute( self.translate_args(**kwargs) )
    
    
    



    
