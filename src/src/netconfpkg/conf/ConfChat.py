"chat file handling"
import os
import re

from .Conf import Conf # pylint: disable-msg=W0403


class ConfChat(Conf):
    """ConfChat(Conf):
    Not a dictionary!
    This reads chat files, and writes a subset of chat files that
    has all items enclosed in '' and has one expect/send pair on
    each line.
    Uses a list of two-element tuples."""
    def __init__(self, filename):
        Conf.__init__(self, filename, '', '\t ', ' ')
        self.list = None
    def read(self):
        Conf.read(self)
        self.initlist()
    def initlist(self):
        self.list = []
        i = 0
        #hastick = 0
        s = ''
        chatlist = []
        for line in self.lines:
            s = s + line + ' '
        while i < len(s) and s[i] in " \t":
            i = i + 1
        while i < len(s):
            mstr = ''
            # here i points to a new entry
            if s[i] in "'":
                #hastick = 1
                i = i + 1
                while i < len(s) and s[i] not in "'":
                    if s[i] in '\\':
                        if not s[i+1] in " \t'":
                            mstr = mstr + '\\'
                        i = i + 1
                    mstr = mstr + s[i]
                    i = i + 1
                # eat up the ending '
                i = i + 1
            else:
                while i < len(s) and s[i] not in " \t":
                    mstr = mstr + s[i]
                    i = i + 1
            chatlist.append(mstr)
            # eat whitespace between strings
            while i < len(s) and s[i] in ' \t':
                i = i + 1
        # now form self.list from chatlist
        if len(chatlist) % 2:
            chatlist.append('')
        while chatlist:
            self.list.append((chatlist[0], chatlist[1]))
            chatlist[0:2] = []
    def getlist(self):
        return self.list
    def putlist(self, mlist):
        self.list = mlist
    def write(self):
        # create self.lines for Conf.write...
        self.lines = []
        for (p, q) in self.list:
            p = re.sub("'", "\\'", p)
            q = re.sub("'", "\\'", q)
            self.lines.append("'"+p+"' '"+q+"'")
        Conf.write(self)


class ConfChatFile(ConfChat):
    """ConfChatFile(ConfChat):
    This class is a ConfChat which it interprets as a netcfg-written
    chat file with a certain amount of structure.  It interprets it
    relative to information in an "ifcfg-" file (devconf) and has a
    set of abortstrings that can be turned on and off.
    It exports the following data items:
    abortstrings   list of standard strings on which to abort
    abortlist      list of alternative strings on which to abort
    defabort       boolean: use the default abort strings or not
    dialcmd        string containing dial command (ATDT, for instance)
    phonenum       string containing phone number
    chatlist       list containing chat script after CONNECT
    chatfile       ConfChat instance
    """
    def __init__(self, filename, devconf, abortstrings=None):
        ConfChat.__init__(self, filename)
        self.abortstrings = abortstrings
        self.devconf = devconf
        self._initlist()
    def _initlist(self):
        # pylint: disable-msg=W0201
        self.abortlist = []
        self.defabort = 1
        self.dialcmd = ''
        self.phonenum = ''
        self.chatlist = []
        dialexp = re.compile('^ATD[TP]?[-0-9,. #*()+]+')
        if self.list:
            for (p, q) in self.list:
                if not cmp(p, 'ABORT'):
                    if not q in self.abortstrings:
                        self.abortlist.append([p, q])
                elif not cmp(q, self.devconf['INITSTRING']):
                    # ignore INITSTRING
                    pass
                elif not self.dialcmd and dialexp.search(q):
                    #elif not self.dialcmd and tempmatch:
                    # First instance of something that looks like a dial
                    # command and a phone number we take as such.
                    tmp = re.search('[-0-9, . #*()+]+', q)
                    index = tmp.group(1)
                    self.dialcmd = q[:index]
                    self.phonenum = q[index:]
                elif not cmp(p, 'CONNECT'):
                    # ignore dial command
                    pass
                else:
                    self.chatlist.append([p, q])
    def _makelist(self):
        self.list = []
        if self.defabort:
            for string in self.abortstrings:
                self.list.append(('ABORT', string))
        for string in self.abortlist:
            self.list.append(('ABORT', string))
        self.list.append(('', self.devconf['INITSTRING']))
        self.list.append(('OK', self.dialcmd+self.phonenum))
        self.list.append(('CONNECT', ''))
        for pair in self.chatlist:
            self.list.append(pair)
    def write(self):
        self._makelist()
        ConfChat.write(self)



# ConfChatFileClone(ConfChatFile):
#  Creates a chatfile, then removes it if it is identical to the chat
#  file it clones.
class ConfChatFileClone(ConfChatFile):
    def __init__(self, cloneInstance, filename, devconf, abortstrings=None):
        self.ci = cloneInstance
        ConfChatFile.__init__(self, filename, devconf, abortstrings)
        if not self.list:
            self.list = []
            for item in self.ci.list:
                self.list.append(item)
            self._initlist()
    def write(self):
        self._makelist()
        if len(self.list) == len(self.ci.list):
            for i in range(len(self.list)):
                if cmp(self.list[i], self.ci.list[i]):
                    # some element differs, so they are different
                    ConfChatFile.write(self)
                    return
            # the loop completed, so they are the same
            if os.path.isfile(self.filename): 
                os.unlink(self.filename)
        else:
            # lists are different lengths, so they are different
            ConfChatFile.write(self)


# ConfDIP:
#  This reads chat files, and writes a dip file based on that chat script.
#  Takes three arguments:
#   o The chatfile
#   o The name of the dipfile
#   o The ConfSHellVar instance from which to take variables in the dipfile
class ConfDIP:
    def __init__(self, chatfile, dipfilename, configfile):
        self.dipfilename = dipfilename
        self.chatfile = chatfile
        self.cf = configfile
    def write(self):
        mfile = open(self.dipfilename, 'w', -1)
        os.chmod(self.dipfilename, 0600)
        mfile.write('# dip script for interface '
                    + self.cf['DEVICE']+'\n' +
"""\
# DO NOT HAND-EDIT; ALL CHANGES *WILL* BE LOST BY THE netcfg PROGRAM
# This file is created automatically from several other files by netcfg
# Re-run netcfg to modify this file

""" +
          'main:\n' +
          '  get $local ' + self.cf['IPADDR']+'\n' +
          '  get $remote ' + self.cf['REMIP']+'\n' +
          '  port ' + self.cf['MODEMPORT']+'\n' +
          '  speed ' + self.cf['LINESPEED']+'\n')
        if self.cf['MTU']:
            mfile.write('  get $mtu '+self.cf['MTU']+'\n')
        for pair in self.chatfile.list:
            if cmp(pair[0], 'ABORT') and cmp(pair[0], 'TIMEOUT'):
                if pair[0]:
                    mfile.write('  wait '+pair[0]+' 30\n' +
                            '  if $errlvl != 0 goto error\n')
                mfile.write('  send '+pair[1]+'\\r\\n\n' +
                        '  if $errlvl != 0 goto error\n')
        if not cmp(self.cf['DEFROUTE'], 'yes'):
            mfile.write('  default\n')
        mfile.write('  mode '+self.cf['MODE']+'\n' +
          '  exit\n' +
          'error:\n' +
          '  print connection to $remote failed.\n')
        mfile.close()

