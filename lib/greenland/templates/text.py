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


import re

EMPTY = re.compile("^[ \t]*$")
WS    = re.compile("^[ \t]*")

def extract_lines(text):
    
    line = text.split("\n")    
    first_was_empty = len(line)>0 and EMPTY.match(line[0])
    while len(line)>0 and EMPTY.match(line[0]):
        del line[0]
    while len(line)>0 and EMPTY.match(line[-1]):
        del line[-1]        

    if len(line) == 0: return line
        
    if not first_was_empty:
        indentation = 0
        if len(line)>1:
            indentation = len( WS.match(line[1]).group(0) )
        first = line[0]
    else:
        indentation = len( WS.match(line[0]).group(0) )
        first       = line[0][indentation:]

    return [ first ] + [ l[indentation:] for l in line[1:] ]

def extract(text, sep='\n', prefix=""):
    return prefix + (sep+prefix).join(extract_lines(text))
