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

"""Capture caller location from stack. This is mostly useful for
   providing error messages with information pinpointing the source
   code location of interest to the user or programmer of client code.

   This module depends on the standard python module `introspect` and
   has not been tested in situations where the information provided
   `introspect` is not available.
"""

import inspect
from   collections import namedtuple

Location = namedtuple('Location',['file','line','source']) #: A named tuple type describing a source location.

def capture( depth = -1):

    """Capture a location from the stack. Passing `depth = -1` (the
       default) captures the location of the caller of the code
       calling `capture`. On the other side `depth = -2` captures the
       information from the stack frame above this (one call earlier)
       and so on for all negative values of `depth`).
    """
    
    frame    = inspect.currentframe()
    frames   = inspect.getouterframes(frame)
    captured = frames[-depth+1]
    info     = Location(file=captured.filename,line=captured.lineno,source=captured.code_context)
    del captured,frame,frames
    return info
