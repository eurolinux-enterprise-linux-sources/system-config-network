"Host Module"
import socket
from netconfpkg.NCAliasList import AliasList
from netconfpkg.NC_functions import testHostname
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr)


class Host_base(Gdtstruct):
    gdtstruct_properties([
                          ('IP', Gdtstr, "Test doc string"),
                          ('Hostname', Gdtstr, "Test doc string"),
                          ('AliasList', AliasList, "Test doc string"),
                          ])

    def __init__(self):
        super(Host_base, self).__init__()
        self.IP = None
        self.Hostname = None
        self.AliasList = AliasList()
        
    def createAliasList(self):
        if not self.AliasList:
            self.AliasList = AliasList()
        return self.AliasList

class Host(Host_base):
    HostID = None

    def __init__(self):
        super(Host, self).__init__()
        # special store for the original comment
        self.Comment = None
        # special store for the original line
        self.origLine = None
        
    def testIP(self):
        try:
            socket.inet_pton(socket.AF_INET, self.IP) 
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, self.IP) 
            except socket.error:
                return False
        return True
    
    def testHostname(self):
        return testHostname(self.Hostname) 
            
    def test(self):
        if not self.testIP():
            raise ValueError("IP")
        if not self.testHostname():
            raise ValueError("Hostname")
        if self.AliasList and not self.AliasList.test(): 
            raise ValueError("Alias")
