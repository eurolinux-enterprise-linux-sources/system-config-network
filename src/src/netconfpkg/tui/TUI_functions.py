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
import os
import sys
import re
from netconfpkg import NC_functions
from netconfpkg.NCException import NCException
from netconfpkg.NC_functions import (_,  log, NETCONFDIR, PROGNAME,
                                     ETHERNET, MODEM, ISDN, WIRELESS,
                                     DSL, TOKENRING, getDebugLevel,
                                     RESPONSE_YES, RESPONSE_NO,
                                     RESPONSE_CANCEL,
                                     set_generic_error_dialog_func,
                                     set_generic_info_dialog_func,
                                     set_generic_longinfo_dialog_func,
                                     set_generic_yesno_dialog_func,
                                     set_generic_yesnocancel_dialog_func,
                                     set_generic_run_dialog_func,
                                     set_generic_run_func)

from snack import (GridForm,
                   TextboxReflowed,
                   Listbox,
                   ButtonBar,
                   Entry,
                   Grid,
                   Label,
                   ButtonChoiceWindow)

def tui_run_dialog( command, argv, searchPath = 0,
              root = '/', stdin = 0,
              catchfd = 1, closefd = -1, title = None,
              label = None, errlabel = None, dialog = None ):
    import select

    if not os.access (root + command, os.X_OK):
        raise RuntimeError, command + " can not be run"

    t = TextboxReflowed(10, label)
    g = GridForm(dialog, label, 1, 1)
    g.add(t, 0, 0)
    g.draw()
    dialog.refresh()

    (read, write) = os.pipe()

    childpid = os.fork()
    if (not childpid):
        os.environ["CONSOLETYPE"] = 'serial'
        if (root and root != '/'):
            os.chroot (root)
        if isinstance(catchfd, tuple):
            for fd in catchfd:
                os.dup2(write, fd)
        else:
            os.dup2(write, catchfd)
        os.close(write)
        os.close(read)

        if closefd != -1:
            os.close(closefd)

        if stdin:
            os.dup2(stdin, 0)
            os.close(stdin)

        if (searchPath):
            os.execvp(command, argv)
        else:
            os.execv(command, argv)

        sys.exit(1)
    try:
        os.close(write)

        rc = ""
        s = "1"
        while (s):
            try:
                # pylint: disable-msg=W0612
                (fdin, fdout, fderr) = select.select([read], [], [], 0.1)
            except select.error:
                fdin = []

            if len(fdin):
                s = os.read(read, 1024)
                rc = rc + s

    except Exception, e:
        try:
            os.kill(childpid, 15)
            os.kill(childpid, 3)
            os.kill(childpid, 1)
            #os.kill(childpid, 9)
        except OSError: # pylint: disable-msg=W0704
            pass
        raise e

    os.close(read)

    try:
        # pylint: disable-msg=W0612
        (pid, status) = os.waitpid(childpid, 0)
    except OSError, (errno, msg):
        log.log(2, "waitpid failed with errno %s: %s" % (str(errno), msg))

    if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0 ):
        status = os.WEXITSTATUS(status)
    else:
        status = -1

    dialog.popWindow()

    if status:
        if errlabel:
            label = errlabel

        rc = _("Failed to run:\n%s") % " ".join(argv) + '\n' + rc

    elif len(rc):
        rc = _("Succeeded. Please read the output.") + '\n' + rc

    if (status or len(rc)):
        w = ButtonChoiceWindow(dialog, label, rc, buttons=[_("Ok")])

    return (status, rc)

set_generic_run_dialog_func(tui_run_dialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
