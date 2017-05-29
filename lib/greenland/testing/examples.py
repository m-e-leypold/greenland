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
import subprocess
import os
from   subprocess import PIPE
from   greenland.errors import Error
from   types import FunctionType

class BrokenExample(Error):
     
    message = "{path}"

    help    = """
              This message is raised when some example is broken
              (e.g. doesn't output text matching a specified regular
              expression).
              """    

    info    = """
              path    : {path}
              failed  : {failed}
              expected: {spec}
              actual  : {actual}
              """
    
def check_examples(examples,basepath="examples"):
     for example in examples:
          path   = os.path.join(basepath,example)
          
          result = subprocess.run(path,stdout=PIPE,stderr=PIPE)

          expectations = examples[example]
          
          for what in expectations:
               actual = result.__dict__[what]
               spec   = expectations[what]

               if   type(spec) in [ str, bytes ]:
                    expected = lambda x: re.compile(spec).search(x)
               elif type(spec) in [ list ]:
                    expected = lambda x: x in spec
               elif type(spec) in [ FunctionType ]:
                   expected = spec
               else:
                   expected = lambda x: x == spec
                    
               if not expected(actual):
                    raise BrokenExample(
                         path=path,
                         failed=what,actual=actual,expected=expected,spec=spec
                    )
