"Module handling /etc/{passwd, shadow, group} style files"
import os

from .Conf import Conf, SystemFull # pylint: disable-msg=W0403 


class ConfPw(Conf):
    """ConfPw(Conf)
    This class implements a dictionary based on a :-separated file.
    It takes as arguments the filename and the field number to key on;
    The data provided is a list including all fields including the key.
    Has its own write method to keep files sane.
    """
    def __init__(self, filename, keyfield, numfields):
        self.keyfield = keyfield
        self.numfields = numfields
        Conf.__init__(self, filename, '', ':', ':', 0)
    def read(self):
        Conf.read(self)
        self.initvars()
    def initvars(self):
        # pylint: disable-msg=W0201
        self.vars = {}
        # need to be able to return the keys in order to keep
        # things consistent...
        self.ordered_keys = []
        self.rewind()
        while self.findnextcodeline():
            fields = self.getfields()
            self.vars[fields[self.keyfield]] = fields
            self.ordered_keys.append(fields[self.keyfield])
            self.nextline()
        self.rewind()
    def __setitem__(self, key, value):
        if not self.findlinewithfield(self.keyfield, key):
            self.fsf()
            self.ordered_keys.append(key)
        self.setfields(value)
        self.vars[key] = value
    def __getitem__(self, key):
        if self.vars.has_key(key):
            return self.vars[key]
        return []
    def __delitem__(self, key):
        place = self.tell()
        self.rewind()
        if self.findlinewithfield(self.keyfield, key):
            self.deleteline()
        if self.vars.has_key(key):
            del self.vars[key]
        for i in range(len(self.ordered_keys)):
            if key in self.ordered_keys[i:i+1]:
                self.ordered_keys[i:i+1] = []
                break
        self.seek(place)
    def keys(self):
        return self.ordered_keys
    def has_key(self, key):
        return self.vars.has_key(key)
    def write(self):
        mfile = open(self.filename + '.new', 'w', -1)
        # change the mode of the new file to that of the old one
        if os.path.isfile(self.filename) and self.mode == -1:
            os.chmod(self.filename + '.new', os.stat(self.filename)[0])
        if self.mode >= 0:
            os.chmod(self.filename + '.new', self.mode)
        # add newlines while writing
        for index in range(len(self.lines)):
            mfile.write(self.lines[index] + '\n')
        mfile.close()
        os.rename(self.filename + '.new', self.filename)
    def kchangefield(self, key, fieldno, fieldtext):
        self.rewind()
        self.findlinewithfield(self.keyfield, key)
        Conf.changefield(self, fieldno, fieldtext)
        self.vars[key][fieldno:fieldno+1] = [fieldtext]

class ConfPwO(ConfPw):
    """ConfPwO
    This class presents a data-oriented meta-class for making
    changes to ConfPw-managed files.  Applications should not
    instantiate this class directly.
    """
    def __init__(self, filename, keyfield, numfields, reflector):
        ConfPw.__init__(self, filename, keyfield, numfields)
        self.reflector = reflector

    def __getitem__(self, key):
        if self.vars.has_key(key):
            return self.reflector(self, key)
        else:
            return None

    def __setitem__(self, key, value):
        # items are objects which the higher-level code can't touch
        raise AttributeError, str('Object %s is immutable. Cannot set %s to %s' 
                                  % (self, str(key), str(value)))

    # __delitem__ is inherited from ConfPw
    # Do *not* use setitem for this; adding an entry should be
    # a much different action than accessing an entry or changing
    # fields in an entry.
    def addentry_list(self, key, mlist):
        if self.vars.has_key(key):
            raise AttributeError, key + ' exists'
        ConfPw.__setitem__(self, key, mlist)
    def getfreeid(self, fieldnum):
        freeid = 500
        # first, we try not to re-use id's that have already been assigned.
        for item in self.vars.keys():
            mid = int(self.vars[item][fieldnum])
            if mid >= freeid and mid < 65533: # ignore nobody on some systems
                freeid = mid + 1
        if freeid > 65533:
            # if that didn't work, we go back and find any free id over 500
            ids = {}
            for item in self.vars.keys():
                ids[int(self.vars[item][fieldnum])] = 1
            i = 500
            while i < 65535 and ids.has_key(i):
                i = i + 1
        if freeid > 65533:
            raise SystemFull, 'No IDs available'
        return freeid

class _passwd_reflector:
    # first, we need a helper class...
    def __init__(self, pw, user):
        self.pw = pw
        self.user = user

    def setgecos(self, oldgecos, fieldnum, value):
        gecosfields = oldgecos.split(', ')
        # make sure that we have enough gecos fields
        gecosfields += [''] * (6-len(gecosfields))
#        for i in range(5-len(gecosfields)):
#            gecosfields.append('')
        gecosfields[fieldnum] = value
        return ', '.join(gecosfields[0:5])

    def getgecos(self, oldgecos, fieldnum):
        gecosfields = oldgecos.split(', ')
        # make sure that we have enough gecos fields
        gecosfields += [''] * (6-len(gecosfields))
#        for i in range(5-len(gecosfields)):
#            gecosfields.append('')
        return gecosfields[fieldnum]

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        return self.__setattr__(name, value)

    def __getattr__(self, name):
        if not self.pw.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            return self.pw.vars[self.user][0]
        elif not cmp(name, 'password'):
            return self.pw.vars[self.user][1]
        elif not cmp(name, 'uid'):
            return self.pw.vars[self.user][2]
        elif not cmp(name, 'gid'):
            return self.pw.vars[self.user][3]
        elif not cmp(name, 'gecos'):
            return self.pw.vars[self.user][4]
        elif not cmp(name, 'fullname'):
            return self.getgecos(self.pw.vars[self.user][4], 0)
        elif not cmp(name, 'office'):
            return self.getgecos(self.pw.vars[self.user][4], 1)
        elif not cmp(name, 'officephone'):
            return self.getgecos(self.pw.vars[self.user][4], 2)
        elif not cmp(name, 'homephone'):
            return self.getgecos(self.pw.vars[self.user][4], 3)
        elif not cmp(name, 'homedir'):
            return self.pw.vars[self.user][5]
        elif not cmp(name, 'shell'):
            return self.pw.vars[self.user][6]
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if not cmp(name, 'pw') or not cmp(name, 'user') \
                               or not cmp(name, 'setgecos') \
                               or not cmp(name, 'getgecos'):
            self.__dict__[name] = value
            return None
        if not self.pw.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            # username is not an lvalue...
            raise AttributeError, name + ': key is immutable'
        elif not cmp(name, 'password'):
            self.pw.kchangefield(self.user, 1, value)
        elif not cmp(name, 'uid'):
            self.pw.kchangefield(self.user, 2, str(value))
        elif not cmp(name, 'gid'):
            self.pw.kchangefield(self.user, 3, str(value))
        elif not cmp(name, 'gecos'):
            self.pw.kchangefield(self.user, 4, value)
        elif not cmp(name, 'fullname'):
            self.pw.kchangefield(self.user, 4,
                self.setgecos(self.pw.vars[self.user][4], 0, value))
        elif not cmp(name, 'office'):
            self.pw.kchangefield(self.user, 4,
                self.setgecos(self.pw.vars[self.user][4], 1, value))
        elif not cmp(name, 'officephone'):
            self.pw.kchangefield(self.user, 4,
                self.setgecos(self.pw.vars[self.user][4], 2, value))
        elif not cmp(name, 'homephone'):
            self.pw.kchangefield(self.user, 4,
                self.setgecos(self.pw.vars[self.user][4], 3, value))
        elif not cmp(name, 'homedir'):
            self.pw.kchangefield(self.user, 5, value)
        elif not cmp(name, 'shell'):
            self.pw.kchangefield(self.user, 6, value)
        else:
            raise AttributeError, name

class ConfPasswd(ConfPwO):
    """ConfPasswd(ConfPwO)
    This class presents a data-oriented class for making changes
    to the /etc/passwd file.
    """
    def __init__(self):
        ConfPwO.__init__(self, '/etc/passwd', 0, 7, _passwd_reflector)
    def addentry(self, username, password, uid, gid, gecos, homedir, shell):
        ConfPwO.addentry_list(self, username, 
                              [username, password, uid, gid, 
                              gecos, homedir, shell])
    def addfullentry(self, username, password, uid, gid, fullname, office,
        officephone, homephone, homedir, shell):
        self.addentry(username, password, uid, gid, ', '.join([fullname,
            office, officephone, homephone, '']), homedir, shell)
    def getfreeuid(self):
        try:
            return self.getfreeid(2)
        except:
            raise SystemFull, 'No UIDs available'


class _shadow_reflector:
    # first, we need a helper class...
    def __init__(self, pw, user):
        self.pw = pw
        self.user = user
    def _readstr(self, fieldno):
        return self.pw.vars[self.user][fieldno]
    def _readint(self, fieldno):
        retval = self.pw.vars[self.user][fieldno]
        try:
            if len(retval):
                retval = int(retval) 
                return retval
        except ValueError:
            return -1
        return -1
    def __getitem__(self, name):
        return self.__getattr__(name)
    def __setitem__(self, name, value):
        return self.__setattr__(name, value)
    def __getattr__(self, name):
        if not self.pw.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            return self._readstr(0)
        elif not cmp(name, 'password'):
            return self._readstr(1)
        elif not cmp(name, 'lastchanged'):
            return self._readint(2)
        elif not cmp(name, 'mindays'):
            return self._readint(3)
        elif not cmp(name, 'maxdays'):
            return self._readint(4)
        elif not cmp(name, 'warndays'):
            return self._readint(5)
        elif not cmp(name, 'gracedays'):
            return self._readint(6)
        elif not cmp(name, 'expires'):
            return self._readint(7)
        else:
            raise AttributeError, name
    def __setattr__(self, name, value):
        if not cmp(name, 'pw') or not cmp(name, 'user'):
            self.__dict__[name] = value
            return None
        if not self.pw.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            # username is not an lvalue...
            raise AttributeError, name + ': key is immutable'
        elif not cmp(name, 'password'):
            self.pw.changefield(self.user, 1, value)
        elif not cmp(name, 'lastchanged'):
            if not len(str(value)) or value == -1:
                raise AttributeError, 'illegal value for lastchanged'
            self.pw.changefield(self.user, 2, str(value))
        elif not cmp(name, 'mindays'):
            if not len(str(value)) or value == -1:
                value = ''
            self.pw.changefield(self.user, 3, str(value))
        elif not cmp(name, 'maxdays'):
            if not len(str(value)) or value == -1:
                value = ''
            self.pw.changefield(self.user, 4, str(value))
        elif not cmp(name, 'warndays'):
            if not len(str(value)) or value == -1:
                value = ''
            self.pw.changefield(self.user, 5, str(value))
        elif not cmp(name, 'gracedays'):
            if not len(str(value)) or value == -1:
                value = ''
            self.pw.changefield(self.user, 6, str(value))
        elif not cmp(name, 'expires'):
            if not len(str(value)) or value == -1:
                value = ''
            self.pw.changefield(self.user, 7, str(value))
        else:
            raise AttributeError, name

class ConfShadow(ConfPwO):
    """ConfShadow(ConfPwO)
    This class presents a data-oriented class for making changes
    to the /etc/shadow file.
    """
    def __init__(self):
        ConfPwO.__init__(self, '/etc/shadow', 0, 9, _shadow_reflector)
    def addentry(self, username, password, lastchanged, 
                 mindays, maxdays, warndays, gracedays, expires):
        # we need that final '' so that the final : (delimited the
        # "reserved field" is preserved by ConfPwO.addentry())
        ConfPwO.addentry_list(self, username,
                         [username, password, self._intfield(lastchanged),
                          self._intfield(mindays), self._intfield(maxdays),
                          self._intfield(warndays), self._intfield(gracedays),
                          self._intfield(expires), ''])
    def _intfield(self, value):
        try:            
            return int(value)
        except ValueError:
            if value == -1:
                return ''
            else:
                return str(value)

class _group_reflector:
    # first, we need a helper class...
    def __init__(self, pw, group):
        self.pw = pw
        self.group = group
    def __getitem__(self, name):
        return self.__getattr__(name)
    def __setitem__(self, name, value):
        return self.__setattr__(name, value)
    def __getattr__(self, name):
        if not self.pw.has_key(self.group):
            raise AttributeError, self.group + ' has been deleted'
        if not cmp(name, 'name'):
            return self.pw.vars[self.group][0]
        elif not cmp(name, 'password'):
            return self.pw.vars[self.group][1]
        elif not cmp(name, 'gid'):
            return self.pw.vars[self.group][2]
        elif not cmp(name, 'userlist'):
            return self.pw.vars[self.group][3]
        else:
            raise AttributeError, name
        
    def __setattr__(self, name, value):
        if not cmp(name, 'pw') or not cmp(name, 'group'):
            self.__dict__[name] = value
            return None
        if not self.pw.has_key(self.group):
            raise AttributeError, self.group + ' has been deleted'
        if not cmp(name, 'name'):
            # username is not an lvalue...
            raise AttributeError, name + ': key is immutable'
        elif not cmp(name, 'password'):
            self.pw.changefield(self.group, 1, value)
        elif not cmp(name, 'gid'):
            self.pw.changefield(self.group, 2, str(value))
        elif not cmp(name, 'userlist'):
            self.pw.changefield(self.group, 3, value)
        else:
            raise AttributeError, name

class ConfGroup(ConfPwO):
    """ConfGroup(ConfPwO)
    This class presents a data-oriented class for making changes
    to the /etc/group file.
    May be replaced by a pwdb-based module, we hope.
    """
    def __init__(self):
        ConfPwO.__init__(self, '/etc/group', 0, 4, _group_reflector)
    def addentry(self, group, password, gid, userlist):
        ConfPwO.addentry_list(self, group, [group, password, gid, userlist])
    def getfreegid(self):
        try:
            return self.getfreeid(2)
        except:
            raise SystemFull, 'No GIDs available'

    def nameofgid(self, gid):
        try: 
            gid = int(gid)
            for group in self.vars.keys():
                mgid = int(self.vars[group][2])
                if mgid == gid:
                    return self.vars[group][0]
        except ValueError:
            return ''
        return ''

class _unix_reflector:
    # first, we need a helper class...
    def __init__(self, pw, user):
        self.pw = pw
        self.user = user
    def __getitem__(self, name):
        return self.__getattr__(name)
    def __setitem__(self, name, value):
        return self.__setattr__(name, value)
    def __getattr__(self, name):
        if not self.pw.passwd.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            if self.pw.shadow:
                return self.pw.shadow[self.user].username
            else:
                return self.pw.passwd[self.user].username
        elif not cmp(name, 'password'):
            if self.pw.shadow:
                return self.pw.shadow[self.user].password
            else:
                return self.pw.passwd[self.user].password
        elif not cmp(name, 'uid'):
            return self.pw.passwd[self.user].uid
        elif not cmp(name, 'gid'):
            return self.pw.passwd[self.user].gid
        elif not cmp(name, 'gecos'):
            return self.pw.passwd[self.user].gecos
        elif not cmp(name, 'fullname'):
            return self.pw.passwd[self.user].fullname
        elif not cmp(name, 'office'):
            return self.pw.passwd[self.user].office
        elif not cmp(name, 'officephone'):
            return self.pw.passwd[self.user].officephone
        elif not cmp(name, 'homephone'):
            return self.pw.passwd[self.user].homephone
        elif not cmp(name, 'homedir'):
            return self.pw.passwd[self.user].homedir
        elif not cmp(name, 'shell'):
            return self.pw.passwd[self.user].shell
        elif not cmp(name, 'lastchanged'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].lastchanged
            else:
                return -1
        elif not cmp(name, 'mindays'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].mindays
            else:
                return -1
        elif not cmp(name, 'maxdays'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].maxdays
            else:
                return -1
        elif not cmp(name, 'warndays'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].warndays
            else:
                return -1
        elif not cmp(name, 'gracedays'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].gracedays
            else:
                return -1
        elif not cmp(name, 'expires'):
            if self.pw.shadowexists():
                return self.pw.shadow[self.user].expires
            else:
                return -1
        else:
            raise AttributeError, name
    def __setattr__(self, name, value):
        if not cmp(name, 'pw') or not cmp(name, 'user'):
            self.__dict__[name] = value
            return None
        if not self.pw.passwd.has_key(self.user):
            raise AttributeError, self.user + ' has been deleted'
        if not cmp(name, 'username'):
            # username is not an lvalue...
            raise AttributeError, name + ': key is immutable'
        elif not cmp(name, 'password'):
            if self.pw.shadow:
                self.pw.shadow[self.user].password = value
            else:
                self.pw.passwd[self.user].password = value
        elif not cmp(name, 'uid'):
            self.pw.passwd[self.user].uid = value
        elif not cmp(name, 'gid'):
            self.pw.passwd[self.user].gid = value
        elif not cmp(name, 'gecos'):
            self.pw.passwd[self.user].gecos = value
        elif not cmp(name, 'fullname'):
            self.pw.passwd[self.user].fullname = value
        elif not cmp(name, 'office'):
            self.pw.passwd[self.user].office = value
        elif not cmp(name, 'officephone'):
            self.pw.passwd[self.user].officephone = value
        elif not cmp(name, 'homephone'):
            self.pw.passwd[self.user].homephone = value
        elif not cmp(name, 'homedir'):
            self.pw.passwd[self.user].homedir = value
        elif not cmp(name, 'shell'):
            self.pw.passwd[self.user].shell = value
        elif not cmp(name, 'lastchanged'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].lastchanged = value
        elif not cmp(name, 'mindays'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].mindays = value
        elif not cmp(name, 'maxdays'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].maxdays = value
        elif not cmp(name, 'warndays'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].warndays = value
        elif not cmp(name, 'gracedays'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].gracedays = value
        elif not cmp(name, 'expires'):
            if self.pw.shadowexists():
                self.pw.shadow[self.user].expires = value
        else:
            raise AttributeError, name
# ConfUnix()
#  This class presents a data-oriented class which uses the ConfPasswd
#  and ConfShadow classes (if /etc/shadow exists) to hold data.
#  Designed to be replaced by a pwdb module eventually, we hope.
