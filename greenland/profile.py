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

"""A minimal program profile implementation.

(Will have to be improved some time later).
"""

class __PropertyTree__( object ):
    def __init__( self, parent = None ):
        self.parent   = parent
        self.verbose  = True
        self.tracing  = True
        self.checking = True

    def get_vtc_flags ( self ):
        return ( self.verbose, self.tracing, self.checking )
    
class __Properties__(object):
    def __init__(self):
        self.root = __PropertyTree__()

properties = __Properties__()


