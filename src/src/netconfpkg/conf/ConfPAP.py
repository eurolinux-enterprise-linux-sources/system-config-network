## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import sys

import re
from types import ListType

from . import Conf # pylint: disable-msg=W0403


if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")


class ConfPAP(Conf.Conf):
    __beginline = """\
####### system-config-network will overwrite this part!!! (begin) ##########"""
    __endline = """\
####### system-config-network will overwrite this part!!! (end) ############"""
    __beginlineold = '^####### redhat-config-network will overwrite.*'
    __endlineold = '^####### redhat-config-network will overwrite.*'

    def __init__(self, filename):
        self.__beginlineplace = 0
        self.__endlineplace = 0
        Conf.Conf.__init__(self, filename, '#', ' \t', ' \t')
        self.chmod(0600)

    def read(self):
        Conf.Conf.read(self)
        self.initvars()
        self.chmod(0600)
        # convert old marker to new
        self.sedline(self.__beginlineold, self.__beginline)
        self.sedline(self.__endlineold, self.__endline)

    def findline(self, val):
        # returns False if no more lines matching pattern
        while self.line < len(self.lines):
            if self.lines[self.line] == val:
                return 1
            self.line = self.line + 1
        # if while loop terminated, pattern not found.
        return 0

    def real_rewind(self):
        self.line = 0

    def rewind(self):
        self.line = self.__beginlineplace

    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.__beginlineplace = 0
        self.__endlineplace = 0
        self.real_rewind()

        if not self.findline(self.__beginline):
            self.insertline(self.__beginline)

        self.__beginlineplace = self.tell()

        if not self.findline(self.__endline):
            self.seek(self.__beginlineplace)
            self.nextline()
            self.insertline(self.__endline)

        self.__endlineplace = self.tell()

        self.real_rewind()

        while self.findnextcodeline():
            if self.tell() >= self.__endlineplace:
                break
            # initialize dictionary of variable/name pairs
            # print self.getline()
            var = self.getfields()

            if var and (len(var) >= 3):
                if not self.vars.has_key(var[0]):
                    self.vars[var[0]] = {}
            self.vars[var[0]][var[1]] = var[2]

            self.nextline()

        self.rewind()

    def getfields(self):
        #var = Conf.Conf.getfields(self)
        var = []
        if self.line >= len(self.lines):
            return []
        regexp = re.compile(r'(?P<user>("([^"\\]|\\\S)*?")|([^ "\\]|\\\S)+)( |\t)+'
        r'(?P<server>("([^"\\]|\\\S)*?")|([^ "\\]|\\\S)+|\*)( |\t)+'
        r'(?P<secret>("([^"\\]|\\\S)*?")|([^ "\\]|\\\S)+)')
        # FIXED: 465748 - crash if pap-secrets file contains spaces before login
        m = regexp.match(self.lines[self.line].strip())
        if not m:
            raise Conf.BadFile, "Error occured while parsing %s" % self.filename
        else:
            var = [m.group("user"), m.group("server"), m.group("secret")]
            if len(var) and len(var[0]) and var[0][0] in '\'"':
                # found quote; strip from beginning and end
                quote = var[0][0]
                if var[0][-1] == quote:
                    var[0] = var[0][1:-1]
    
            if len(var) >= 2 and len(var[1]) and var[1][0] in '\'"':
                # found quote; strip from beginning and end
                quote = var[1][0]
                if var[1][-1] == quote:
                    var[1] = var[1][1:-1]
    
            if len(var) >= 3 and len(var[2]) and var[2][0] in '\'"':
                # found quote; strip from beginning and end
                quote = var[2][0]
                if var[2][-1] == quote:
                    var[2] = var[2][1:-1]
            return var

    def insertline(self, line=''):
        place = self.tell()
        if place < self.__beginlineplace:
            self.__beginlineplace = self.__beginlineplace + 1

        if place < self.__endlineplace:
            self.__endlineplace = self.__endlineplace + 1

        self.lines.insert(self.line, line)

    def deleteline(self):
        place = self.tell()
        self.lines[self.line:self.line+1] = []

        if place < self.__beginlineplace:
            self.__beginlineplace = self.__beginlineplace -1

        if place < self.__endlineplace:
            self.__endlineplace = self.__endlineplace - 1

    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return ''

    def __setitem__(self, varname, svalue):
        place = self.tell()
        self.rewind()
        missing = 1

        if isinstance(varname, ListType):
            login = '\"' + varname[0] + '\"'
            server = '\"' + varname[1] + '\"'
        else:
            login = '\"' + varname + '\"'
            server = '*'

        value = '\"' + svalue + '\"'

        while self.findnextcodeline():
            if self.tell() >= self.__endlineplace:
                break

            var = self.getfields()

            if var and (len(var) >= 3):
                if login == var[0] and server == var[1]:
                    self.setfields([ login, server, value ] )
                    missing = 0
            self.nextline()

        if missing:
            self.delallitem(varname)
            self.seek(self.__endlineplace)
            self.insertlinelist([ login, server, value ] )


        if isinstance(varname, ListType):
            if not self.vars.has_key(varname[0]):
                self.vars[varname[0]] = {}
            self.vars[varname[0]][varname[1]] = svalue
        else:
            if not self.vars.has_key(varname):
                self.vars[varname] = {}
            self.vars[varname]["*"] = svalue

        self.seek(place)

    def __delitem__(self, varname):
        place = self.tell()
        self.rewind()
        if isinstance(varname, ListType):
            login = varname[0]
            server = varname[1]
        else:
            login = varname
            server = "*"

        while self.findnextcodeline():
            if self.tell() >= self.__endlineplace:
                break

            var = self.getfields()

            if var and (len(var) >= 3):
                if login == var[0] and server == var[1]:
                    self.deleteline()
            self.nextline()

        if self.vars.has_key(login):
            if self.vars[login].has_key(server):
                del self.vars[login][server]
            if not len(self.vars[login]):
                del self.vars[login]
        self.seek(place)

    def delallitem(self, varname):
        place = self.tell()
        self.rewind()
        # delete *every* instance...
        if isinstance(varname, ListType):
            login = varname[0]
            server = varname[1]
        else:
            login = varname
            server = "*"

        while self.findnextcodeline():
            var = self.getfields()

            if var and (len(var) >= 3):
                if login == var[0] and server == var[1]:
                    self.deleteline()

            self.nextline()

        if self.vars.has_key(login):
            if self.vars[login].has_key(server):
                del self.vars[login][server]
            if not len(self.vars[login]):
                del self.vars[login]

        self.seek(place)

    def has_key(self, key):
        if self.vars.has_key(key):
            return 1
        return 0

    def keys(self):
        return self.vars.keys()
