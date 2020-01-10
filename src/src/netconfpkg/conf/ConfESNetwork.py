import os

from .ConfShellVar import ConfShellVar  # pylint: disable-msg=W0403


class ConfESNetwork(ConfShellVar):
    # explicitly for /etc/sysconfig/network: HOSTNAME is magical value
    # that writes /etc/HOSTNAME as well
    def __init__ (self):
        ConfShellVar.__init__(self, '/etc/sysconfig/network')
        self.writeHostname = 0
    def __setitem__(self, varname, value):
        ConfShellVar.__setitem__(self, varname, value)
        if varname == 'HOSTNAME':
            self.writeHostname = 1
    def write(self):
        ConfShellVar.write(self)
        if self.writeHostname:
            mfile = open('/etc/HOSTNAME', 'w', -1)
            mfile.write(self.vars['HOSTNAME'] + '\n')
            mfile.close()
            os.chmod('/etc/HOSTNAME', 0644)
    def keys(self):
        # There doesn't appear to be a need to return keys in order
        # here because we normally always have the same entries in this
        # file, and order isn't particularly important.
        return self.vars.keys()
    def has_key(self, key):
        return self.vars.has_key(key)
