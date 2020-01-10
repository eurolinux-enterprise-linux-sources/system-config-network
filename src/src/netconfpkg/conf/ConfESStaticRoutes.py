"/etc/sysconfig/static-routes handling"
from .Conf import Conf, WrongMethod # pylint: disable-msg=W0403


class ConfESStaticRoutes(Conf):
    """Yet another dictionary, this one for /etc/sysconfig/static-routes
    This file has a syntax similar to that of /etc/gateways;
    the interface name is added and active/passive is deleted:
    <interface> net <netaddr> netmask <netmask> gw <gateway>
    The key is the interface, the value is a list of
    [<netaddr>, <netmask>, <gateway>] lists
    """
    def __init__(self):
        Conf.__init__(self, '/etc/sysconfig/static-routes', '#', '\t ', ' ')
    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.rewind()
        while self.findnextcodeline():
            var = self.getfields()
            if len(var) == 7:
                if not self.vars.has_key(var[0]):
                    self.vars[var[0]] = [[var[2], var[4], var[6]]]
                else:
                    self.vars[var[0]].append([var[2], var[4], var[6]])
            elif len(var) == 5:
                if not self.vars.has_key(var[0]):
                    self.vars[var[0]] = [[var[2], var[4], '']]
                else:
                    self.vars[var[0]].append([var[2], var[4], ''])
            self.nextline()
        self.rewind()
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return [[]]
    def __setitem__(self, varname, value):
        raise WrongMethod, 'Delete or call addroute instead'
    def __delitem__(self, varname):
        # since we re-write the file completely on close, we don't
        # need to alter it piecemeal here.
        del self.vars[varname]
    def delroute(self, device, route):
        # deletes a route from a device if the route exists,
        # and if it is the only route for the device, removes
        # the device from the dictionary
        # Note: This could normally be optimized considerably,
        # except that our input may have come from the file,
        # which others may have hand-edited, and this makes it
        # possible for us to deal with hand-inserted multiple
        # identical routes in a reasonably correct way.
        if self.vars.has_key(device):
            for i in range(len(self.vars[device])):
                if i < len(self.vars[device]) and \
                   not cmp(self.vars[device][i], route):
                    # need first comparison because list shrinks
                    self.vars[device][i:i+1] = []
                    if len(self.vars[device]) == 0:
                        del self.vars[device]
    def addroute(self, device, route):
        # adds a route to a device, deleteing it first to avoid dups
        self.delroute(device, route)
        if self.vars.has_key(device):
            self.vars[device].append(route)
        else:
            self.vars[device] = [route]
    def write(self):
        # forget current version of file
        self.rewind()
        self.lines = []
        for device in self.vars.keys():
            for route in self.vars[device]:
                if len(route) == 3:
                    if len(route[2]):
                        self.insertlinelist((device, 'net', route[0],
                                             'netmask', route[1],
                                             'gw', route[2]))
                    else:
                        self.insertlinelist((device, 'net', route[0],
                                             'netmask', route[1]))
        Conf.write(self)
    def keys(self):
        # no need to return list in order here, I think.
        return self.vars.keys()
    def has_key(self, key):
        return self.vars.has_key(key)

