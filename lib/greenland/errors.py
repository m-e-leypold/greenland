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

"""
This module strives to provide infrastructure for exceptions with
readable and explanatory error messages and to make it easy for the
client to define such messages.

"""

import greenland.templates.text       as template
import greenland.introspection.caller as caller

errors_with_info = True  #: Include info text into :py:meth:`__str__`.
errors_with_help = True  #: Include help page into :py:meth:`__str__`.

def next_stackframe(stackframe, decrement_by = 1):
    if stackframe == None: return None
    return stackframe - decrement_by

class Error(Exception):
    
    """
    A class for human readable errors.  The keyword parameters
    `**__info__` to `__init__` are used to provide additional
    information about the error instance, e.g. the filename which could not
    be opened, name of the remote host that could not be connected to.
    """

    message = None   #: Message template, see `get_message`. This attribute needs to be defined.                     
    info    = None   #: Info template, see `get_info`. This attribute can be left out.
    help    = None   #: Help text template, see `get_help`. This attribute can be left out.

    def __init__(self,__stackframe__=-0,location=None,**__info__):

        """Construct an :py:class:`Error` instance. 

        `__info__` should contain arguments describing the specific
        circumstances in which the error occured, e.g. a the name of a
        file that could not be opened, the systems diagnostic code
        (errno) for the failing operation, required and actual
        permission etc. Info will be used to format the templates
        :py:attr:`message`, :py:attr:`info` and :py:attr:`help`.

        Init captures the location where the instance is constructed
        (that is where the error occured, hopefully) from the call
        stach with :py:mod:`introspect`, if there is call stack
        information available (this is the case at least for
        CPython). 

        `__stackframe__` tells `__init__` which stackframe is
        relevant. Passing a 0 (the default) captures the location
        where the constructor was called. 

        Some frameworks need to pass a different value, e.g. a test
        framework as :py:mod:`greenland.testing` might want to capture
        the location of the test assertion, not the place in the
        framework where the comparison with the desired result
        failed. In this case one needs to pass some negative number as
        `__stackframe__`: py:`-1` means to capture not from the
        location where the constructore was called but from the caller
        of this piece of code (the stackframe above) , py:`-2` means
        to capture from the stackframe even one higher and so on.

        A location captured earlier, e.g. with
        py:mod:`greenland.introspection.caller` can be passed as
        argument `location`. It must be of the type
        py:data:`greenland.introspection.Location` (a named
        tuple). This possibility is only of interest to framework
        writers, too.

        """
        
        self.__dict__.update(__info__)
        self.__info__ = __info__
        self.location = location
        if not location:
            if __stackframe__ != None:
                self.location = caller.capture(__stackframe__-1)
        if self.location:
            self.source   = self.location.source[0].strip()
        self.reset_location(self.location)

    def get_message(self):

        """This is a test"""
        
        return self.message.format(**self.__dict__)

    def get_help(self,sep="\n",prefix=""):
        if self.help: return template.extract(self.help,sep,prefix).format(**self.__dict__)
        else:         return None
            
        
    def get_oneline(self):
        if hasattr(self,'location') and self.location != None:
            t = "{file}:{line}: ".format(file=self.location.file,line=self.location.line)
        else:
            t = ""
        t = t + "{classname}: ".format(classname=self.__class__.__name__) + self.get_message()
        return t

    def reset_location(self,location):
        pass
    
    def raise_here(self,__stackframe__=-0):
        self.location = caller.capture(__stackframe__-1)
        self.source   = self.location.source[0].strip()
        self.reset_location(self.location)
        raise self

    def __str__(self):
        return \
            self.get_message() \
            + (( "\n\n" + self.get_oneline() + "\n\n  " + self.get_info(sep = "\n  ") ) if errors_with_info else ""  ) \
            + (( "\n\n  " + self.get_help(sep = "\n  ") ) if errors_with_help and self.help else "" )
               
    def get_info(self,sep="\n",prefix=""):
        if self.info:
            return template.extract(self.info,sep,prefix).format(**self.__dict__)
        else:
            return prefix + repr(self.__info__)
    
    
# class SomeError(Error):
#     message = "Some error happened, severity={baz}"

#     help    = """
#               This message is raise when some error happens.
#               The value of baz (here: {baz}) indicates the 
#               level of severity.
#               """

#     info    = """
#               src: {location.source[0]}
#               foo: {foo}
#               bar: {baz}
#               """
# e = SomeError(foo=123,baz=456)

# # print(e.get_message())

# try:
#     raise e
# except Exception as x:
#     print(x.get_oneline())
#     print("  =>",x.get_info(sep="\n     "))

# e.raise_here()



