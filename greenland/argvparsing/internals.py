<#
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

# TODO: - PosArgs should (optionally) use ordered dicts (and handle convert ...)
#       - various behaviour flags
#       - composition (+)
#       - error checking (too many args, wrong structure)
#       - This module needs to have better documentation.

class ArgumentParser ( object ):

    def __call__(self,args):
        return self.parse(args)
    
    @classmethod
    def compile( cls, *pargs, **optargs):
        return cls(*pargs,**optargs)

    @classmethod
    def collect( cls, args, *pargs, **optargs ):
        p = cls( *pargs, **optargs )
        return p(args)    


class NamedArguments ( ArgumentParser ):

    def __init__ ( self, aliases = { }, types = { }, flags = [ ] ):        
        normal = { }
        for key in aliases:
            a = aliases[key]
            if type(a) == str:
                normal[a] = key
            else:
                for a2 in a:
                    normal[a2] = key            
        self.normal = normal
        self.types  = types
        self.flags  = set(flags)
        

    def get_normal(self,key):
        if key in self.normal:
            return self.normal[key]
        else:
            return key

    def convert(self,key,val):
        if key in self.types:
            return self.types[key](val)
        else:
            if key in self.flags:
                return bool(val)
            else:
                return val

            
class SpecialOptions ( NamedArguments ):
    
    def parse(self,args):
        d = { }

        for i in range(len(args)):
            arg = args[i]
            if arg[0] != "+":
                return ( d, args[i:] )
            try:
                k = arg.index("=")
                key = self.get_normal(arg[1:(k)])
                d[key]=self.convert(key,arg[k+1:])
            except:
                key = self.get_normal(arg[1:])
                d[key]= self.convert(key,True)

        return ( d, [] )

    
class Options ( NamedArguments ):
                 
    def parse(self,args):
        d = { }
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--":
                i += 1
                break
            if len(arg) == 0 or arg[0] != "-":
                break
            if arg[1] == "-":  # gnu style option
                try:
                    k      = arg.index("=")
                    key    = self.get_normal(arg[2:k])
                    d[key] = self.convert(key,arg[k+1:])
                except ValueError:
                    key    = self.get_normal(arg[2:])
                    d[key] = self.convert(key,True)
            else:
                key = self.get_normal(arg[1:])
                if key in self.flags:
                    d[key] = self.convert(key,True)
                else:
                    i += 1
                    if i>=len(args): assert False # XXX bail out, also if "--" and optionally "-"
                    d[key] = self.convert(key,args[i])
            
            i += 1
            
        return d,args[i:]



# TODO: The following should use an OrderedDict, so we can annotate types, too? Or extra types parameter
    
class PosArgs ( ArgumentParser ):

    def __init__( self, required, optional = [], more = True ):
        self.optional = optional
        self.required = required
        self.more     = more
        self.names    = required + optional
        
    def parse( self, args ):

        d   = { }
        i   = 0
        j   = 0
        min = len(self.required)
        n   = len(args)        
        
        while (i<n) and (i<len(self.names)):
            arg = args[i]

            if arg == "--":
                i += 1
                break
            
            d[self.names[i]] = arg
            i += 1

        assert i>=len(self.required)
            
        if not self.more:
            assert (i==n)
        else:
            key       = self.names[-1]
            more_args = [ d[key] ] 
            while (i<n):
                arg = args[i]
                
                if arg == "--":
                    i += 1
                    break
                
                more_args.append(args[i])
                i += 1
            d[key] = more_args
            
        return d,args[i:]

    
    

