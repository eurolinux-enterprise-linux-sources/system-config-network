"TUI QETH Interface Module"
import snack
from netconfpkg.NCHardwareList import HW_CONF, getHardwareList
from netconfpkg.NC_functions import _, QETH


class NCQethInterfaceTui:
    "TUI QETH Interface Dialog"
    def __init__(self, dev=None):
        """
        The constructor
        @screen A snack screen instance
        """

        self.dev = dev
        self.name = snack.Entry(20, "")
        self.hwdev = snack.Entry(20, "")
        self.dynip = snack.Checkbox("")
        self.statip = snack.Entry(20, "")
        self.netmask = snack.Entry(20, "")
        self.gwy = snack.Entry(20, "")
        self.ioport = snack.Entry(20, "")
        self.ioport1 = snack.Entry(20, "")
        self.ioport2 = snack.Entry(20, "")
        self.options=snack.Entry(20,"")
        self.macaddr=snack.Entry(20,"")
        self.screen = None
        
        if dev:
            self.setState()

    def setState(self, dev=None):
        """
        Set the default values of the fields
        according to the given device
        @dev The NCDevice (type devernet) to use as default values
        """
        if not dev:
            dev = self.dev
            
        if dev:
            if dev.DeviceId:
                self.name.set(dev.DeviceId)
            if dev.Device:
                self.hwdev.set(dev.Device)
            if dev.BootProto:
                bp = dev.BootProto.lower()
                if (bp == "dhcp") or (bp == "bootp"):
                    self.dynip.setValue("*")
            if dev.IP:
                self.statip.set(dev.IP)
            if dev.Netmask:
                self.netmask.set(dev.Netmask)
            if dev.Gateway:
                self.gwy.set(dev.Gateway)

            hardwarelist = getHardwareList()
            for hw in hardwarelist:
                if hw.Name == dev.Device:
                    self.ioport.set(hw.Card.IoPort or '')
                    self.ioport1.set(hw.Card.IoPort1 or '')
                    self.ioport2.set(hw.Card.IoPort2 or '')
                    self.options.set(hw.Card.Options or '')
                    self.macaddr.set(hw.MacAddress or '')
                    break
            
    def useDynamicCheckBox(self):
        """
        Set the static IP field to enabled/disabled
        determined by the dynamic IP field
        """
        
        if self.dynip.selected():
            state = snack.FLAGS_SET
        else:
            state = snack.FLAGS_RESET
        for i in self.statip, self.netmask, self.gwy:
            i.setFlags(snack.FLAG_DISABLED, state)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.dev.DeviceId = self.name.value()
        self.dev.Device = self.hwdev.value()
        hardwarelist = getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.dev.Device:
                break
        else:
            i = hardwarelist.addHardware(QETH)
            hw = hardwarelist[i]
            hw.Status = HW_CONF
            hw.Name = self.dev.Device
            hw.Type = QETH

        # pylint: disable-msg=W0631
        if not hw.Card:
            hw.createCard()
        hw.Card.ModuleName = "qeth"
        hw.Card.IoPort = self.ioport.value()
        hw.Card.IoPort1 = self.ioport1.value()
        hw.Card.IoPort2 = self.ioport2.value()
        ports = "%s,%s,%s" % (hw.Card.IoPort, hw.Card.IoPort1, hw.Card.IoPort2)
        hw.Description = "qeth %s" % ports
        hw.Options = self.options.value()
        hw.MacAddress = self.macaddr.value()

        if self.dynip.value():
            self.dev.BootProto = "dhcp"
            self.dev.IP = None
            self.dev.Netmask = None
            self.dev.Gateway = None
        else:
            self.dev.IP = self.statip.value()
            self.dev.Netmask = self.netmask.value()
            self.dev.Gateway = self.gwy.value()
            self.dev.BootProto = None
    
    def runIt(self, screen):
        """
        Show and run the screen, save files if necesarry
        """
        self.screen = screen
        g1 = snack.Grid(1, 1)
        g2 = snack.Grid(2, 11)
        g2.setField(snack.Label (_("Name")), 0, 0, anchorLeft = 1)
        g2.setField(snack.Label (_("Device")), 0, 1, anchorLeft = 1)
        g2.setField(snack.Label (_("Use DHCP")), 0, 2, anchorLeft = 1)
        g2.setField(snack.Label (_("Static IP")), 0, 3, anchorLeft = 1)
        g2.setField(snack.Label (_("Netmask")), 0, 4, anchorLeft=1)
        g2.setField(snack.Label (_("Default gateway IP")), 0, 5, anchorLeft = 1)
        g2.setField(snack.Label (_("Read Device Bus ID")), 0, 6, anchorLeft = 1)
        g2.setField(snack.Label (_("Data Device Bus ID")), 0, 7, anchorLeft = 1)
        g2.setField(snack.Label (_("Write Device Bus ID")), 0, 8, 
                                   anchorLeft = 1)
        g2.setField(snack.Label (_("Options")),0,9,anchorLeft=1)
        g2.setField(snack.Label (_("MAC Address")),0,10,anchorLeft=1)
        g2.setField(self.name, 1, 0, (1, 0, 0, 0))
        g2.setField(self.hwdev, 1, 1, (1, 0, 0, 0))
        g2.setField(self.dynip, 1, 2, (1, 0, 0, 0), anchorLeft=1)
        g2.setField(self.statip, 1, 3, (1, 0, 0, 0))
        g2.setField(self.netmask, 1, 4, (1, 0, 0, 0))
        g2.setField(self.gwy, 1, 5, (1, 0, 0, 0))
        g2.setField(self.ioport, 1, 6, (1, 0, 0, 0))
        g2.setField(self.ioport1, 1, 7, (1, 0, 0, 0))
        g2.setField(self.ioport2, 1, 8, (1, 0, 0, 0))
        g2.setField(self.options,1,9,(1,0,0,0))
        g2.setField(self.macaddr,1,10,(1,0,0,0))

        self.dynip.setCallback(self.useDynamicCheckBox)
        bb = snack.ButtonBar(self.screen, ((_("Ok"), "ok"),
                                           (_("Cancel"), "cancel")))
        self.setState(self.dev)
        tl = snack.GridForm(screen, _("Devernet Configuration"), 1, 3)
        tl.add(g1, 0, 0, (0, 0, 0, 1), anchorLeft=1)
        tl.add(g2, 0, 1, (0, 0, 0, 1))
        tl.add(bb, 0, 2, growx=1)
        self.useDynamicCheckBox()
        while 1:
            res = tl.run()
            if bb.buttonPressed(res) == "cancel":
                screen.popWindow()
                return False
            elif bb.buttonPressed(res) == "ok":
                screen.popWindow()
                self.processInfo()
                return True

def register_plugin():
    from netconfpkg.plugins.NCPluginDevQeth import setDevQethDialog
    setDevQethDialog(NCQethInterfaceTui)
    
__author__ = "Harald Hoyer <harald@redhat.com>"

