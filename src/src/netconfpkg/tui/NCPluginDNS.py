"TUI DNS config Module"
from netconfpkg.tui.NCTcpIp import NCTcpIpDialog
import snack

#
# EthernetWindow class
#
class NCPluginDNSTui():
    "TUI DNS config Dialog"
    def __init__(self, plist = None):
        """
        The constructor
        """
        self.hostname = snack.Entry(15, "")
        self.domainname = snack.Entry(15, "")
        self.primaryDNS = snack.Entry(15, "")
        self.secondaryDNS = snack.Entry(15, "")
        self.tertiaryDNS = snack.Entry(15, "")
        #self.SearchList = SearchList()
        self.searchList = snack.Entry(15, "")
        self.prof = plist.getActiveProfile()
    
    def setState(self, prof):
        """
        Set the default values of the fields
        according to the given device
        """
        
        self.hostname.set(prof.DNS.Hostname)
        #self.domainname.set(prof.DNS.Domainname)
        self.primaryDNS.set(prof.DNS.PrimaryDNS)
        self.secondaryDNS.set(prof.DNS.SecondaryDNS)
        self.tertiaryDNS.set(prof.DNS.TertiaryDNS)
        self.searchList.set(" ".join(prof.DNS.SearchList))
        
    def processInfo(self):
        """
        Extracts info from the screen, and puts it into an active profile object
        """
        self.prof.DNS.Hostname = self.hostname.value()
        self.prof.DNS.PrimaryDNS = self.primaryDNS.value()
        self.prof.DNS.SecondaryDNS = self.secondaryDNS.value()
        self.prof.DNS.TertiaryDNS = self.tertiaryDNS.value()
        #self.tertiaryDNS.value()
        s = self.searchList.value()
        newentries = s.split()
        self.prof.DNS.SearchList = self.prof.DNS.SearchList[:0]
        for sp in newentries:
            self.prof.DNS.SearchList.append(sp)
        self.prof.DNS.commit()
    
    def runIt(self, screen):       
        g1 = snack.Grid(1, 1)
        g2 = snack.Grid(2, 5)
        g2.setField(snack.Label (_("Hostname")), 0, 0, anchorLeft = 1)
        g2.setField(snack.Label (_("Primary DNS")), 0, 1, anchorLeft = 1)
        g2.setField(snack.Label (_("Secondary DNS")), 0, 2, anchorLeft = 1)
        g2.setField(snack.Label (_("Tertiary DNS")), 0, 3, anchorLeft = 1)
        g2.setField(snack.Label (_("DNS search path")), 0, 4, anchorLeft = 1)
        #g2.setField(snack.Label (_("Default gateway IP")), 0, 5, anchorLeft = 1)
        g2.setField(self.hostname, 1, 0, (1, 0, 0, 0))
        g2.setField(self.primaryDNS, 1, 1, (1, 0, 0, 0))
        g2.setField(self.secondaryDNS, 1, 2, (1, 0, 0, 0))
        g2.setField(self.tertiaryDNS, 1, 3, (1, 0, 0, 0))
        g2.setField(self.searchList, 1, 4, (1, 0, 0, 0))
        #g2.setField(gwy, 1, 5, (1, 0, 0, 0))
        #dynip.setCallback(useDynamicCheckBox)
        bb = snack.ButtonBar(screen, ((_("Ok"), "ok"),
                                           (_("Cancel"), "cancel")))
        self.setState(self.prof)
        tl = snack.GridForm(screen, _("DNS configuration"), 1, 3)
        tl.add(g1, 0, 0, (0, 0, 0, 1), anchorLeft = 1)
        tl.add(g2, 0, 1, (0, 0, 0, 1))
        tl.add(bb, 0, 2, growx = 1)
        # if
        res = tl.run()
        if bb.buttonPressed(res) == "cancel":
            print "cancel"
            screen.popWindow()
            return False
    
        elif bb.buttonPressed(res) == "ok":
            screen.popWindow()
            self.processInfo()
            return True


#def register_plugin():
#    from netconfpkg.plugins.NCPluginDevEthernet import setDevEthernetDialog     
#    setDevEthernetDialog(NCEthernetInterfaceTui)
