#
# executil.py - generic utility functions for executing programs
#
# Erik Troan <ewt@redhat.com>
#
# Copyright 1999-2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import os
import sys
import types
import select
import signal

def execWithCapture(command, argv, searchPath = 0, root = '/', stdin = 0,
		    catchfd = 1, closefd = -1):

    if not os.access (root + command, os.X_OK):
	raise RuntimeError, command + " can not be run"

    (read, write) = os.pipe()

    childpid = os.fork()
    if (not childpid):
        if (root and root != '/'): os.chroot (root)
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

    os.close(write)

    rc = ""
    s = "1"
    while (s):
	select.select([read], [], [])
	s = os.read(read, 1000)
	rc = rc + s

    os.close(read)

    try:
        os.waitpid(childpid, 0)
    except OSError as e:
        print "%s waitpid: %s" % (__name__, e.strerror)

    return rc
