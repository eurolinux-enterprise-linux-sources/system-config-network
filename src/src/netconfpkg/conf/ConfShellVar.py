import re

from .Conf import Conf, ConfIndexError # pylint: disable-msg=W0403


class ConfShellVar(Conf):
    def __init__(self, filename):
        self.nextreg = re.compile('^[\t ]*[A-Za-z_][A-Za-z0-9_]*=')
        self.quotereg = re.compile('[ \t${}*@!~<>?;%^()#&=]')
        Conf.__init__(self, filename, commenttype='#',
                      separators='=', separator='=')

    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.rewind()
        while self.findnextline(self.nextreg):
            # initialize dictionary of variable/name pairs
            var = self.getfields()
            # fields 1..n are False separations on "=" character in string,
            # so we need to join them back together.
            var[1] = "=".join(var[1:len(var)])
            if len(var[1]) and var[1][0] in '\'"':
                # found quote; strip from beginning and end
                quote = var[1][0]
                var[1] = var[1][1:]
                p = -1
                try:
                    while cmp(var[1][p], quote):
                        # ignore whitespace, etc.
                        p = p - 1
                except:
                    raise ConfIndexError (self.filename, var)
                var[1] = var[1][:p]
            else:
                var[1] = re.sub('#.*', '', var[1])

            self.vars[var[0]] = var[1]
            self.nextline()
        self.rewind()
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return ''
    def __setitem__(self, varname, value):
        # prevent tracebacks
        if not value:
            value = ""
        # set *every* instance of varname to value to avoid surprises
        place = self.tell()
        self.rewind()
        missing = 1
        while self.findnextline('^[\t ]*' + varname + '='):
            if self.quotereg.search(value):
                self.sedline('=.*', "='" + value + "'")
            else:
                self.sedline('=.*', '=' + value)
            missing = 0
            self.nextline()
        if missing:
            self.seek(place)
            if self.quotereg.search(value):
                self.insertline(varname + "='" + value + "'")
            else:
                self.insertline(varname + '=' + value)

        self.vars[varname] = value

    def __delitem__(self, varname):
        # delete *every* instance...

        self.rewind()
        while self.findnextline('^[\t ]*' + varname + '='):
            self.deleteline()
        if self.vars.has_key(varname):
            del self.vars[varname]

    def has_key(self, key):
        if self.vars.has_key(key): 
            return 1
        return 0
    def keys(self):
        return self.vars.keys()


# ConfShellVarClone(ConfShellVar):
#  Takes a ConfShellVar instance and records in another ConfShellVar
#  "difference file" only those settings which conflict with the
#  original instance.  The delete operator does delete the variable
#  text in the cloned instance file, but that will not really delete
#  the shell variable that occurs, because it does not put an "unset"
#  command in the file.
class ConfShellVarClone(ConfShellVar):
    def __init__(self, cloneInstance, filename):
        ConfShellVar.__init__(self, filename)
#        Conf.__init__(self, filename, commenttype='#',
#                      separators='=', separator='=')
        self.ci = cloneInstance
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        elif self.ci.has_key(varname):
            return self.ci[varname]
        else:
            return ''
    def __setitem__(self, varname, value):
        if value != self.ci[varname]:
            # differs from self.ci; save a local copy.
            ConfShellVar.__setitem__(self, varname, value)
        else:
            # self.ci already has the variable with the same value,
            # don't duplicate it
            if self.vars.has_key(varname):
                del self[varname]
    # inherit delitem because we don't want to pass it through to self.ci
    def has_key(self, key):
        if self.vars.has_key(key): 
            return True
        if self.ci.has_key(key): 
            return True
        return False
    # FIXME: should we implement keys()?

