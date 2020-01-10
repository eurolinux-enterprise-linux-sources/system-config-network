"Module handling /etc/sysctl style files"
import os

from .Conf import Conf # pylint: disable-msg=W0403


class ConfSysctl(Conf):
    def __init__(self, filename):
        Conf.__init__(self, filename, commenttype='#',
                      separators='=', separator='=')
    def read(self):
        Conf.read(self)
        Conf.sedline(self, '\n', '')
        Conf.sedline(self, '  ', ' ')
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        self.rewind()
        while self.findnextcodeline():
            var = self.getfields()
            # fields 1..n are False matches on "=" character in string,
            # which is messed up, but try to deal with it
            var[1] = '='.join(var[1:len(var)])
            # snip off leading and trailing spaces, which are legal (it's
            # how sysctl(1) prints them) but can be confusing, and tend to
            # screw up Python's dictionaries
            var[0] = var[0].strip()
            var[1] = var[1].strip()
            if self.vars.has_key(var[0]):
                self.deleteline()
                self.vars[var[0]] = var[1]
            else:
                self.vars[var[0]] = var[1]
                self.line = self.line + 1
        self.rewind()
    def __setitem__(self, varname, value):
        # set it in the line list
        self.rewind()
        foundit = 0
        while self.findnextcodeline():
            var = self.getfields()
            # snip off leading and trailing spaces, which are legal (it's
            # how sysctl(1) prints them) but can be confusing, and tend to
            # screw up Python's dictionaries
            if(var[0].strip() == varname):
                while(var[0].strip() == varname):
                    self.deleteline()
                    var = self.getfields()
                for part in value.split('\n'):
                    self.insertline(varname + ' = ' + part)
                    self.line = self.line + 1
                foundit = 1
            self.line = self.line + 1
        if(foundit == 0):
            for part in value.split('\n'):
                self.lines.append(varname + ' = ' + part)
        self.rewind()
        # re-read the file, sort of
        self.initvars()
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return ''
    def write(self):
        mfile = open(self.filename, 'w', -1)
        if self.mode >= 0:
            os.chmod(self.filename, self.mode)
        # add newlines
        for index in range(len(self.lines)):
            mfile.write(self.lines[index] + '\n')
        mfile.close()
