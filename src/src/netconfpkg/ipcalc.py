# Python wrapper for ipcalc command line IP address manipulation tool
# Copyright (c) 2001-2005 Red Hat, Inc. All rights reserved.
#
# This software may be freely redistributed under the terms of the GNU
# public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Author: Preston Brown <pbrown@redhat.com>
import os
import re


class IPCalc:
    """A wrapper class that encapsulates the command line
    functionality of the ipcalc command, providing access to computing
    network prefixes, netmasks, etc. from python."""

    def __init__(self, address, prefix=None, netmask=None):
        """Initialize an IPCalc object.  Address must be provided, and
        in order for most of the other calculations to be possible,
        one of prefix or netmask must also be provided."""
        self._address = address
        self._prefix = prefix
        self._netmask = netmask

    def prefix(self):
        if self._prefix:
            return self._prefix
        else:
            if not self._netmask:
                text = os.popen("ipcalc -m %s" % self._address).read()
                self._netmask = re.match("NETMASK=(\S+)", text).groups()[0]

            text = os.popen("ipcalc -p %s %s" % (
                self._address, self._netmask)).read()
            self._prefix = re.match("PREFIX=(\d+)", text).groups()[0]
            return self._prefix

    def netmask(self):
        if self._netmask:
            return self._netmask
        else:
            if not self._prefix:
                text = os.popen("ipcalc -m %s" % self._address).read()
            else:
                text = os.popen("ipcalc -m %s/%s" % (
                    self._address, self._prefix))
            self._netmask = re.match("NETMASK=(\S+)", text).groups()[0]
            return self._netmask

    def network(self):
        if not self._prefix:
            self.prefix()
        text = os.popen("ipcalc -n %s/%s" % (self._address, 
                                             self._prefix)).read()
        return re.match("NETWORK=(\S+)", text).groups()[0]

    def broadcast(self):
        if not self._prefix:
            self.prefix()
        text = os.popen("ipcalc -b %s/%s" % (self._address, 
                                             self._prefix)).read()
        return re.match("BROADCAST=(\S+)", text).groups()[0]

def test():
    """Test function for the IPCalc class."""

    ipc = IPCalc("207.175.42.15", netmask="255.255.254.0")
    print "prefix:", ipc.prefix()
    print "netmask:", ipc.netmask()
    print "bcast:", ipc.broadcast()
    print "network:", ipc.network()


if __name__ == "__main__":
    test()


__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.8 $"
