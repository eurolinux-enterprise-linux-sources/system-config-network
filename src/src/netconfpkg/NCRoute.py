import re
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr)


class Route_base(Gdtstruct):
    gdtstruct_properties([
                          ('Address', Gdtstr, "Test doc string"),
                          ('Netmask', Gdtstr, "Test doc string"),
                          ('Gateway', Gdtstr, "Test doc string"),
                          ('GatewayDevice', Gdtstr, "Test doc string"),
                          ])
    def __init__(self):
        super(Route_base, self).__init__()
        self.Address = None
        self.Netmask = None
        self.Gateway = None
        self.GatewayDevice = None

_ip_pattern = re.compile(
    r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )

_mac_pattern = re.compile(
    r"^([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}$"
    )

def testIP(value):
    # FIXME: split, then check for range
    if _ip_pattern.match(value):
        return True
    else:
        return False

def testMAC(value):
    if _mac_pattern.match(value):
        return True
    else:
        return False

class Route(Route_base):                   
    def test(self):        
        all_ok = super(Route, self).test()
        if not(all_ok):
            raise ValueError
        return True

    def testAddress(self):
        return testIP(self.Address)

    def testGateway(self):
        "check for consistency"
        if not self.Gateway:
            return True
        else: 
            return testIP(self.Gateway)

#    def testGatewayDevice(self, value):
#        "check for consistency"
#        return True

    def testNetmask(self):
        "check for consistency"
        if not self.Netmask:
            return True
        else: 
            return testIP(self.Netmask)
