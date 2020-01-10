"Profile"
from netconfpkg.NCHostsList import HostsList
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties,
                            Gdtstr, Gdtlist, Gdtbool, gdtlist_properties)

class ActiveIPsecs(Gdtlist):
    "List of active IPsec in the Profile"
    gdtlist_properties(Gdtstr)

class DeviceId(Gdtstr):
    "Id of a Device object"

class ActiveDevices(Gdtlist):
    "List of active Devices in the Profile"
    gdtlist_properties(Gdtstr)

class Domain(Gdtstr):
    "Search Domain in a SearchList"
    
class SearchList(Gdtlist):
    "Domain search list from /etc/resolv.conf"
    gdtlist_properties(Gdtstr)

class DNS(Gdtstruct):
    "DNS setup of a profile"
    gdtstruct_properties([
                          ('Hostname', Gdtstr, "Test doc string"),
                          ('Domainname', Gdtstr, "Test doc string"),
                          ('PrimaryDNS', Gdtstr, "Test doc string"),
                          ('SecondaryDNS', Gdtstr, "Test doc string"),
                          ('TertiaryDNS', Gdtstr, "Test doc string"),
                          ('SearchList', SearchList, "Test doc string"),
                          ])
    
    def __init__(self):
        super(DNS, self).__init__()
        self.Hostname = None
        self.Domainname = None
        self.PrimaryDNS = None
        self.SecondaryDNS = None
        self.TertiaryDNS = None
        self.SearchList = SearchList()
    
class Profile(Gdtstruct):
    "Profile for s-c-network"
    gdtstruct_properties([
                          ('ProfileName', Gdtstr, "Test doc string"),
                          ('Active', Gdtbool, "Test doc string"),
                          ('ActiveDevices', ActiveDevices, "Test doc string"),
                          ('ActiveIPsecs', ActiveIPsecs, "Test doc string"),
                          ('DNS', DNS, "Test doc string"),
                          ('HostsList', HostsList, "Test doc string"),
                          ])
    def __init__(self):
        super(Profile, self).__init__()
        self.ProfileName = None
        self.Active = None
        self.DNS = DNS()
        self.ActiveDevices = ActiveDevices()
        self.ActiveIPsecs = ActiveIPsecs()
        self.HostsList = HostsList()
