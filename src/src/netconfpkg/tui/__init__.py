## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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

# pylint: disable-msg=W0122
# pylint: disable-msg=W0141
import locale
import os


_files = map(lambda v: v[:-3], filter(lambda v: v[:8]=="NCPlugin" 
                                      and v[-3:] == ".py" 
                                      and v != "__init__.py" 
                                      and v[0] != '.', 
                                      os.listdir(__path__[0])))

locale.setlocale(locale.LC_ALL, "C")
_files.sort()
locale.setlocale(locale.LC_ALL, "")

for _i in _files:
    _cmd = "from " + _i + " import register_plugin"
    try:
        exec _cmd
    except ImportError:
        pass
    else:
        register_plugin()
        del register_plugin

del _i
del _files
del _cmd

__author__ = "Harald Hoyer <harald@redhat.com>"

