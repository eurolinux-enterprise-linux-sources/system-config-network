from .Conf import Conf # pylint: disable-msg=W0403


class ConfEResolv(Conf):
    # /etc/resolv.conf
    def __init__(self):
        Conf.__init__(self, '/etc/resolv.conf', '#', '\t ', ' ')
    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.rewind()
        while self.findnextcodeline():
            var = self.getfields()
            if var[0] == 'nameserver':
                if self.vars.has_key('nameservers'):
                    self.vars['nameservers'].append(var[1])
                else:
                    self.vars['nameservers'] = [ var[1] ]
            else:
                self.vars[var[0]] = var[1:]
            self.nextline()
        self.rewind()
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return []
    def __setitem__(self, varname, value):
        # set first (should be only) instance to values in list value
        place = self.tell()
        self.rewind()
        if varname == 'nameservers':
            if self.findnextline('^nameserver[' + self.separators + ']+'):
                # if there is a nameserver line, save the place,
                # remove all nameserver lines, then put in new ones in order
                placename = self.tell()
                while self.findnextline('^nameserver['+self.separators+']+'):
                    self.deleteline()
                self.seek(placename)
                for nameserver in value:
                    self.insertline('nameserver' + self.separator + nameserver)
                    self.nextline()
                self.seek(place)
            else:
                # no nameservers entries so far
                self.seek(place)
                for nameserver in value:
                    self.insertline('nameserver' + self.separator + nameserver)
        else:
            # not a nameserver, so all items on one line...
            if self.findnextline('^' + varname + '[' + self.separators + ']+'):
                self.deleteline()
                self.insertlinelist([ varname,
                                      self.separator.join(value) ])
                self.seek(place)
            else:
                self.seek(place)
                self.insertlinelist([ varname,
                                      self.separator.join(value) ])
        # no matter what, update our idea of the variable...
        self.vars[varname] = value

    def __delitem__(self, varname):
        # delete *every* instance...
        self.rewind()
        while self.findnextline('^[' + self.separators + ']*' + varname):
            self.deleteline()
        del self.vars[varname]

    def write(self):
        # Need to make sure __setitem__ is called for each item to
        # maintain consistancy, in case some did something like
        # resolv['nameservers'].append('123.123.123.123')
        # or
        # resolv['search'].append('another.domain')
        for key in self.vars.keys():
            self[key] = self.vars[key]

        if self.filename != '/etc/resolv.conf':
            Conf.write(self)
        else:
            #  bug 125712: /etc/resolv.conf modifiers MUST use
            #  change_resolv_conf function to change resolv.conf
            import tempfile
            (fd, self.filename) = tempfile.mkstemp('', '/tmp/')
            Conf.write(self)
            import commands
            commands.getstatusoutput(
            "/bin/bash -c "
            "'. /etc/sysconfig/network-scripts/network-functions;"
            " change_resolv_conf %s'" % self.filename)
            fd.close()
            self.filename = "/etc/resolv.conf"
    def keys(self):
        # no need to return list in order here, I think.
        return self.vars.keys()
    def has_key(self, key):
        return self.vars.has_key(key)
