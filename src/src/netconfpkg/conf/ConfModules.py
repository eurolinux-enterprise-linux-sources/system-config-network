"Module handling"
# pylint: disable-msg=W0403
import re

from .Conf import Conf, odict, BadFile, VersionMismatch 


class ConfModules(Conf):
    """ConfModules(Conf)
    This reads /etc/modprobe.d/network.conf into a dictionary keyed on device type,
    holding dictionaries: cm['eth0']['alias'] --> 'smc-ultra'
                          cm['eth0']['options'] --> {'io':'0x300', 'irq':'10'}
                          cm['eth0']['post-install'] --> ['/bin/foo', 'arg1',
                                                           'arg2']
    path[*] entries are ignored (but not removed)
    New entries are added at the end to make sure that they
    come after any path[*] entries.
    Comments are delimited by initial '#'
    """
    def __init__(self, filename = '/etc/modprobe.d/network.conf'):
        Conf.__init__(self, filename, '#', '\t ', ' ')
    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = odict()
        keys = ('alias', 'options', 'install', 'remove')
        self.rewind()
        while self.findnextcodeline():
            var = self.getfields()
            # strip comments
            for val in var:
                if val and val.strip().startswith('#'):
                    var = var[:var.index(val)]
                    break
            # assume no -k field
            if len(var) > 2 and var[0] in keys:
                if not self.vars.has_key(var[1]):
                    self.vars[var[1]] = odict({'alias':'', 
                        'options':odict(), 'install':[], 'remove':[]})
                if not cmp(var[0], 'alias'):
                    self.vars[var[1]]['alias'] = var[2]
                elif not cmp(var[0], 'options'):
                    self.vars[var[1]]['options'] = self.splitoptlist(var[2:])
                elif not cmp(var[0], 'install'):
                    self.vars[var[1]]['install'] = var[2:]
                elif not cmp(var[0], 'remove'):
                    self.vars[var[1]]['remove'] = var[2:]
            self.nextline()
        self.rewind()

    def splitoptlist(self, optlist):
        mdict = odict()
        for opt in optlist:
            optup = self.splitopt(opt)
            if optup:
                mdict[optup[0]] = optup[1]
        return mdict
    def splitopt(self, opt):
        eq = opt.find('=')
        if eq > 0:
            return (opt[:eq], opt[eq+1:])
        else:
            return ()
    def joinoptlist(self, mdict):
        optstring = ''
        for key in mdict.keys():
            optstring = optstring + key + '=' + mdict[key] + ' '
        return optstring
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return odict()

    def _quote(self, s):
        s = s.replace('\\', '\\\\')
        s = s.replace('*', '\\*')
        s = s.replace('?', '\\?')
        s = s.replace('.', '\\.')
        s = s.replace('(', '\\(')
        s = s.replace(')', '\\)')
        s = s.replace('^', '\\^')
        s = s.replace('$', '\\$')
        return s

    def __setitem__(self, varname, value):
        # set *every* instance (should only be one, but...) to avoid surprises
        place = self.tell()
        self.vars[varname] = value
        endofline = ""
        replace = ""
        for key in value.keys():
            self.rewind()
            missing = 1
            findexp = str('^[\t ]*%s[\t ]+%s[\t ]+' %
                          (self._quote(key), self._quote(varname)))
            if not cmp(key, 'alias'):
                endofline = value[key]
                replace = key + ' ' + varname + ' ' + endofline
            elif not cmp(key, 'options'):
                endofline = self.joinoptlist(value[key])
                replace = key + ' ' + varname + ' ' + endofline
            elif not cmp(key, 'install'):
                endofline = ' '.join(value[key])
                replace = key + ' ' + varname + ' ' + endofline
            elif not cmp(key, 'remove'):
                endofline = ' '.join(value[key])
                replace = key + ' ' + varname + ' ' + endofline
            else:
                endofline = ""
                replace = ""
                # some idiot apparently put an unrecognized key in
                # the dictionary; ignore it...
                continue

            # FIXED: [146291] GUI adds trailing spaces to "options" lines
            # in /etc/modprobe.conf when adding/deleting wireless devices
            replace = replace.rstrip()

            if endofline:
                # there's something to write...
                while self.findnextline(findexp):
                    cl = self.getline().split(' #')
                    if len(cl) >= 2:
                        comment = " #".join(cl[1:])
                        self.setline(replace + ' #' + comment)
                    else:
                        self.setline(replace)
                    missing = 0
                    self.nextline()
                if missing:
                    self.fsf()
                    self.insertline(replace)
            else:
                # delete any instances of this if they exist.
                while self.findnextline(findexp):
                    self.deleteline()
        self.seek(place)

    def __delitem__(self, varname):
        # delete *every* instance...
        place = self.tell()
        for key in self.vars[varname].keys():
            self.rewind()
            while self.findnextline('^[\t ]*' 
                                    + key 
                                    + '([\t ]-k)?[\t ]+' 
                                    + varname):
                self.deleteline()
        del self.vars[varname]
        self.seek(place)
    def write(self):
        # need to make sure everything is set, because program above may
        # well have done cm['eth0']['post-install'] = ['/bin/foo', '-f',
        #                                              '/tmp/bar']
        # which is completely reasonable, but won't invoke __setitem__
        for key in self.vars.keys():
            self[key] = self.vars[key]
        Conf.write(self)
    def keys(self):
        return self.vars.keys()
    def has_key(self, key):
        return self.vars.has_key(key)


class ConfModInfo(Conf):
    """ConfModInfo(Conf)
    This READ-ONLY class reads /boot/module-info.
    The first line of /boot/module-info is "Version <version>";
    this class reads versions 0 and 1 module-info files.
    """
    def __init__(self, filename = '/boot/module-info'):
        Conf.__init__(self, filename, '#', '\t ', ' ', create_if_missing=0)
    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.rewind()
        device = 0
        modtype = 1
        description = 2
        arguments = 3
        lookingfor = device
        version = self.getfields()
        self.nextline()
        if not cmp(version[1], '0'):
            # Version 0 file format
            while self.findnextcodeline():
                line = self.getline()
                if not line[0] in self.separators:
                    curdev = line
                    self.vars[curdev] = {}
                    lookingfor = modtype
                elif lookingfor == modtype:
                    fields = self.getfields()
                    # first "field" is null (before separators)
                    self.vars[curdev]['type'] = fields[1]
                    if len(fields) > 2:
                        self.vars[curdev]['typealias'] = fields[2]
                    lookingfor = description
                elif lookingfor == description:
                    self.vars[curdev]['description'] = re.sub(
                        '^"', '', re.sub(
                            '^['+self.separators+']', '', re.sub(
                                '"['+self.separators+']*$', '', line)))
                    lookingfor = arguments
                elif lookingfor == arguments:
                    if not self.vars[curdev].has_key('arguments'):
                        self.vars[curdev]['arguments'] = {}
                    # get argument name (first "field" is null again)
                    thislist = []
                    # point at first character of argument description
                    p = line.find('"')
                    while p != -1 and p < len(line):
                        q = line[p+1:].find('"')
                        # deal with escaped quotes (\")
                        while q != -1 and not cmp(line[p+q-1], '\\'):
                            q = line[p+q+1:].find('"')
                        if q == -1:
                            break
                        thislist.append(line[p+1:p+q+1])
                        # advance to beginning of next string, if any
                        r = line[p+q+2:].find('"')
                        if r >= 0:
                            p = p+q+2+r
                        else:
                            # end of the line
                            p = r
                    no = self.getfields()[1]
                    self.vars[curdev]['arguments'][no] = thislist
                self.nextline()
        elif not cmp(version[1], '1'):
            # Version 1 file format
            # Version 1 format uses ' ' and ':' characters as field separators
            # but only uses ' ' in one place, where we explicitly look for it.
            self.separators = ':'
            while self.findnextcodeline():
                line = self.getline()
                fields = self.getfields()
                # pull out module and linetype from the first field...
                linetype = re.split('[ \t]+', fields[0])[1]
                if not cmp(linetype, 'type'):
                    pass
                elif not cmp(linetype, 'alias'):
                    pass
                elif not cmp(linetype, 'desc'):
                    pass
                elif not cmp(linetype, 'argument'):
                    pass
                elif not cmp(linetype, 'supports'):
                    pass
                elif not cmp(linetype, 'arch'):
                    pass
                elif not cmp(linetype, 'pcimagic'):
                    pass
                else:
                    # error: unknown flag...
                    raise BadFile, 'unknown flag' + linetype
        else:
            print 'Only versions 0 and 1 module-info files are supported'
            raise VersionMismatch, str('Only versions 0 '
                        'and 1 module-info files are supported')
        self.rewind()
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return {}
    def keys(self):
        return self.vars.keys()
    def has_key(self, key):
        return self.vars.has_key(key)
    def write(self):
        pass

