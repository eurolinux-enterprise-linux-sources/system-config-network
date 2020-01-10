# Copyright (C) 1996-2002 Red Hat, Inc.
# Use of this software is subject to the terms of the GNU General
# Public License

# This module manages standard configuration file handling
# These classes are available:
# Conf:
#  This is the base class.  This is good for working with just about
#  any line-oriented configuration file.
#  Currently does not deal with newline escaping; may never...
# ConfShellVar(Conf):
#  This is a derived class which implements a dictionary for standard
#  VARIABLE=value
#  shell variable setting.
#  Limitations:
#    o one variable per line
#    o assumes everything on the line after the '=' is the value
# ConfShellVarClone(ConfShellVar):
#  Takes a ConfShellVar instance and records in another ConfShellVar
#  "difference file" only those settings which conflict with the
#  original instance.  The delete operator does delete the variable
#  text in the cloned instance file, but that will not really delete
#  the shell variable that occurs, because it does not put an "unset"
#  command in the file.
# ConfESNetwork(ConfShellVar):
#  This is a derived class specifically intended for /etc/sysconfig/network
#  It is another dictionary, but magically fixes /etc/HOSTNAME when the
#  Hostname is changed.
# ConfEHosts(Conf):
#  Yet another dictionary, this one for /etc/hosts
#  Dictionary keys are numeric IP addresses in string form, values are
#  2-item lists, the first item of which is the canonical Hostname,
#  and the second of which is a list of nicknames.
# ConfEResolv(Conf):
#  Yet another dictionary, this one for /etc/resolv.conf
#  This ugly file has two different kinds of entries.  All but one
#  take the form "key list of arguments", but one entry (nameserver)
#  instead takes multiple lines of "key argument" pairs.
#  In this dictionary, all keys have the same name as the keys in
#  the file, EXCEPT that the multiple nameserver entries are all
#  stored under 'nameservers'.  Each value (even singleton values)
#  is a list.
# ConfESStaticRoutes(Conf):
#  Yet another dictionary, this one for /etc/sysconfig/static-routes
#  This file has a syntax similar to that of /etc/gateways;
#  the interface name is added and active/passive is deleted:
#  <interface> net <netaddr> netmask <netmask> gw <gateway>
#  The key is the interface, the value is a list of
#  [<netaddr>, <netmask>, <gateway>] lists
# ConfChat(Conf):
#  Not a dictionary!
#  This reads chat files, and writes a subset of chat files that
#  has all items enclosed in '' and has one expect/send pair on
#  each line.
#  Uses a list of two-element tuples.
# ConfChatFile(ConfChat):
#  This class is a ConfChat which it interprets as a netcfg-written
#  chat file with a certain amount of structure.  It interprets it
#  relative to information in an "ifcfg-" file (devconf) and has a
#  set of abortstrings that can be turned on and off.
#  It exports the following data items:
#    abortstrings   list of standard strings on which to abort
#    abortlist      list of alternative strings on which to abort
#    defabort       boolean: use the default abort strings or not
#    dialcmd        string containing dial command (ATDT, for instance)
#    phonenum       string containing phone number
#    chatlist       list containing chat script after CONNECT
#    chatfile       ConfChat instance
# ConfChatFileClone(ConfChatFile):
#  Creates a chatfile, then removes it if it is identical to the chat
#  file it clones.
# ConfDIP:
#  This reads chat files, and writes a dip file based on that chat script.
#  Takes three arguments:
#   o The chatfile
#   o The name of the dipfile
#   o The ConfSHellVar instance from which to take variables in the dipfile
# ConfModules(Conf)
#  This reads /etc/modprobe.d/dist.conf into a dictionary keyed on device type,
#  holding dictionaries: cm['eth0']['alias'] --> 'smc-ultra'
#                        cm['eth0']['options'] --> {'io':'0x300', 'irq':'10'}
#                        cm['eth0']['post-install'] --> ['/bin/foo', 
#                                                        'arg1', 'arg2']
#  path[*] entries are ignored (but not removed)
#  New entries are added at the end to make sure that they
#  come after any path[*] entries.
#  Comments are delimited by initial '#'
# ConfModInfo(Conf)
#  This READ-ONLY class reads /boot/module-info.
#  The first line of /boot/module-info is "Version = <version>";
#  this class reads versions 0 and 1 module-info files.
# ConfPw(Conf)
#  This class implements a dictionary based on a :-separated file.
#  It takes as arguments the filename and the field number to key on;
#  The data provided is a list including all fields including the key.
#  Has its own write method to keep files sane.
# ConfPasswd(ConfPw)
#  This class presents a data-oriented class for making changes
#  to the /etc/passwd file.
# ConfShadow(ConfPw)
#  This class presents a data-oriented class for making changes
#  to the /etc/shadow file.
# ConfGroup(ConfPw)
#  This class presents a data-oriented class for making changes
#  to the /etc/group file.
#  May be replaced by a pwdb-based module, we hope.
# ConfUnix()
#  This class presents a data-oriented class which uses the ConfPasswd
#  and ConfShadow classes (if /etc/shadow exists) to hold data.
#  Designed to be replaced by a pwdb module eventually, we hope.
# ConfPAP(Conf):
#  Yet another dictionary, this one for /etc/ppp/pap-secrets
#  The key is the remotename, the value is a list of
#  [<user>, <secret>] lists
# ConfCHAP(ConfPAP):
#  Yet another dictionary, this one for /etc/ppp/chap-secrets
#  The key is the remotename, the value is a list of
#  [<local>, <secret>] lists
# ConfSecrets:
#  Has-a ConfPAP and ConfCHAP
#  Yet another dictionary, which reads from pap-secrets and
#  chap-secrets, and writes to both when an entry is set.
#  When conflicts occur while reading, the pap version is
#  used in preference to the chap version (this is arbitrary).
# ConfSysctl:
#  Guess what?  A dictionary, this time with key/value pairs for sysctl vars.
#  Duplicate keys get appended to existing values, and broken out again when
#  the file is written (does that even work?)

# This library exports several Errors, including
# FileMissing
#   Conf raises this error if create_if_missing == 0 and the file does not
#   exist
# IndexError
#   ConfShVar raises this error if unbalanced quotes are found
# BadFile
#   Raised to indicate improperly formatted files
# WrongMethod
#   Raised to indicate that the wrong method is being called.  May indicate
#   that a dictionary class should be written to through methods rather
#   than assignment.
# VersionMismatch
#   An unsupported file version was found.
# SystemFull
#   No more UIDs or GIDs are available
import os
import re


class FileMissing(Exception):
    def __init__(self, filename):
        Exception.__init__(self)
        self.filename = filename

    def __str__(self):
        return self.filename + " does not exist."

class ConfIndexError(IndexError):
    def __init__(self, filename, var):
        IndexError.__init__(self)
        self.filename = filename
        self.var = var

    def __str__(self):
        return "end quote not found in %s: %s" % (self.filename, self.var[0])

class BadFile(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg

WrongMethod = BadFile
VersionMismatch = BadFile
SystemFull = BadFile


# Implementation:
# A configuration file is a list of lines.
# a line is a string.

class Conf:
    def __init__(self, filename, commenttype='#',
                 separators='\t ', separator='\t',
                 merge=1, create_if_missing=1):
        self.commenttype = commenttype
        self.separators = separators
        self.separator = separator
        self.codedict = {}
        self.splitdict = {}
        self.merge = merge
        self.create_if_missing = create_if_missing
        self.line = 0
        self.rcs = 0
        self.mode = -1
        # self.line is a "point" -- 0 is before the first line;
        # 1 is between the first and second lines, etc.
        # The "current" line is the line after the point.
        self.filename = filename
        self.lines = []
        self.read()
    def rewind(self):
        self.line = 0
    def fsf(self):
        self.line = len(self.lines)
    def tell(self):
        return self.line
    def seek(self, line):
        self.line = line
    def nextline(self):
        self.line = min([self.line + 1, len(self.lines)])
    def findnextline(self, regexp=None):
        # returns False if no more lines matching pattern
        while self.line < len(self.lines):
            if regexp:
                if hasattr(regexp, "search"):
                    if regexp.search(self.lines[self.line]):
                        return 1
                elif re.search(regexp, self.lines[self.line]):
                    return 1
            elif not regexp:
                return 1
            self.line = self.line + 1
        # if while loop terminated, pattern not found.
        return 0
    def findnextcodeline(self):
        # optional whitespace followed by non-comment character
        # defines a codeline.  blank lines, lines with only whitespace,
        # and comment lines do not count.
        if not self.codedict.has_key((self.separators, self.commenttype)):
            self.codedict[(self.separators, self.commenttype)] = \
                                           re.compile('^[' + self.separators \
                                                      + ']*' + '[^' + \
                                                      self.commenttype + \
                                                      self.separators + ']+')
        codereg = self.codedict[(self.separators, self.commenttype)]
        return self.findnextline(codereg)
    def findlinewithfield(self, fieldnum, value):
        if self.merge:
            seps = '['+self.separators+']+'
        else:
            seps = '['+self.separators+']'
        rx = '^'

        #for i in range(fieldnum - 1):
        #    rx = rx + '[^'+self.separators+']*' + seps
        rx += ([ ('[^'+self.separators+']*' + seps) ] * fieldnum).join()

        rx = rx + value + '\(['+self.separators+']\|$\)'
        return self.findnextline(rx)
    def getline(self):
        if self.line >= len(self.lines):
            return ''
        return self.lines[self.line]
    def getfields(self):
        # returns list of fields split by self.separators
        if self.line >= len(self.lines):
            return []
        if self.merge:
            seps = '['+self.separators+']+'
        else:
            seps = '['+self.separators+']'
#        print "re.split(%s, %s) = %s" % (self.lines[self.line],
#                                        seps, 
#                                        re.split(seps, self.lines[self.line]))

        if not self.splitdict.has_key(seps):
            self.splitdict[seps] = re.compile(seps)
        regexp = self.splitdict[seps]
        return regexp.split(self.lines[self.line])
    def setfields(self, mlist):
        # replaces current line with line built from list
        # appends if off the end of the array
        if self.line < len(self.lines):
            self.deleteline()
        self.insertlinelist(mlist)
    def insertline(self, line=''):
        self.lines.insert(self.line, line)
    def insertlinelist(self, linelist):
        self.insertline(self.separator.join(linelist))
    def sedline(self, pat, repl):
        if self.line < len(self.lines):
            self.lines[self.line] = re.sub(pat, repl, \
                                           self.lines[self.line])
    def changefield(self, fieldno, fieldtext):
        fields = self.getfields()
        fields[fieldno:fieldno+1] = [fieldtext]
        self.setfields(fields)
    def setline(self, line=None):
        if not line:
            line = []
        self.deleteline()
        self.insertline(line)
    def deleteline(self):
        self.lines[self.line:self.line+1] = []
    def chmod(self, mode=-1):
        self.mode = mode
    def read(self):
        file_exists = 0
        if os.path.isfile(self.filename):
            file_exists = 1
        if not self.create_if_missing and not file_exists:
            raise FileMissing, self.filename
        if file_exists and os.access(self.filename, os.R_OK):
            mfile = open(self.filename, 'r', -1)
            self.lines = mfile.readlines()
            # strip newlines
            for index in range(len(self.lines)):
                if len(self.lines[index]) and self.lines[index][-1] == '\n':
                    self.lines[index] = self.lines[index][:-1]
                if len(self.lines[index]) and self.lines[index][-1] == '\r':
                    self.lines[index] = self.lines[index][:-1]
            mfile.close()
        else:
            self.lines = []
    def write(self):
        # rcs checkout/checkin errors are thrown away, because they
        # aren't this tool's fault, and there's nothing much it could
        # do about them.  For example, if the file is already locked
        # by someone else, too bad!  This code is for keeping a trail,
        # not for managing contention.  Too many deadlocks that way...
        if self.rcs or os.path.exists(os.path.split(self.filename)[0]+'/RCS'):
            self.rcs = 1
            os.system('/usr/bin/co -l '
                      + self.filename 
                      + ' </dev/null >/dev/null 2>&1')
        mfile = open(self.filename, 'w', -1)
        if self.mode >= 0:
            os.chmod(self.filename, self.mode)
        # add newlines
        for index in range(len(self.lines)):
            mfile.write(self.lines[index] + '\n')
        mfile.close()
        if self.rcs:
            mode = os.stat(self.filename)[0]
            os.system('/usr/bin/ci -u -m"control panel update" ' +
                      self.filename+' </dev/null >/dev/null 2>&1')
            os.chmod(self.filename, mode)











class odict(dict):
    def __init__(self, modict = None):
        self._keys = []
        dict.__init__(self)
        if modict:
            dict.update(self, modict)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        #print "[%s] = %s" % (str(key), str(item))
        dict.__setitem__(self, key, item)
        if key not in self._keys:
            self._keys.append(key)

    def clear(self):
        dict.clear(self)
        self._keys = []

    def copy(self):
        modict = dict.copy(self)
        modict._keys = self._keys[:]
        return modict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        dict.setdefault(self, key, failobj)
        if key not in self._keys: 
            self._keys.append(key)

    def update(self, mdict):
        dict.update(self, mdict)
        for key in mdict.keys():
            if key not in self._keys: 
                self._keys.append(key)

    def values(self):
        return [ self.get(x) for x in self._keys ]
#        return map(self.get, self._keys)

