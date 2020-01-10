"TUI Modem Interface Module"
import snack
from netconfpkg.NC_functions import _


class NCModemInterfaceTui:
    "TUI Modem Interface Dialog"
    def __init__(self, modem=None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @modem The modem device. If none given, the first
               modem in devicelist will be used.
               If none are there, one will be added.
        """
        self.name = snack.Entry(20, "")
        self.hwdev = snack.Entry(20, "")
        self.login = snack.Entry(20, "")
        self.phoneno = snack.Entry(20, "")
        self.password = snack.Entry(20, "", password=1)
        self.initstring = snack.Entry(20, "")
        self.modem = modem
        self.screen = None

    def setState(self, modem = None):
        """
        Set the default values of the fields
        according to the given device
        @modem The NCDevice (type modem) to use as default values
        """


        if modem:
            if modem.DeviceId:
                self.name.set(modem.DeviceId)
            if modem.Device:
                self.hwdev.set(modem.Device)
            if modem.Dialup.Login:
                self.login.set(modem.Dialup.Login)
            if modem.Dialup.Password:
                self.password.set(modem.Dialup.Password)
            if modem.Dialup.InitString:
                self.initstring.set(modem.Dialup.InitString)
            if modem.Dialup.PhoneNumber:
                self.phoneno.set(modem.Dialup.PhoneNumber)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.modem.DeviceId = self.name.value()
        self.modem.Device = self.hwdev.value()
        self.modem.Dialup.Login = self.login.value()
        self.modem.Dialup.Password = self.password.value()
        self.modem.Dialup.InitString = self.initstring.value()
        self.modem.Dialup.PhoneNumber = self.phoneno.value()

    def runIt(self, mscreen):
        """
        Show and run the screen, save files if necesarry
        """
        self.screen = mscreen
        g1 = snack.Grid(1, 1)
        g2 = snack.Grid(2, 6)
        g2.setField(snack.Label (_("Name")), 0, 0, anchorLeft=1)
        g2.setField(snack.Label (_("Device")), 0, 1, anchorLeft=1)
        g2.setField(snack.Label (_("ISP Phonenumber")), 0, 2, anchorLeft=1)
        g2.setField(snack.Label (_("ISP Login")), 0, 3, anchorLeft=1)
        g2.setField(snack.Label (_("ISP Password")), 0, 4, anchorLeft=1)
        g2.setField(snack.Label (_("Modem Initstring")), 0, 5, anchorLeft=1)
        g2.setField(self.name, 1, 0, (1, 0, 0, 0))
        g2.setField(self.hwdev, 1, 1, (1, 0, 0, 0))
        g2.setField(self.phoneno, 1, 2, (1, 0, 0, 0), anchorLeft=1)
        g2.setField(self.login, 1, 3, (1, 0, 0, 0))
        g2.setField(self.password, 1, 4, (1, 0, 0, 0))
        g2.setField(self.initstring, 1, 5, (1, 0, 0, 0))
        bb = snack.ButtonBar(self.screen, ((_("Ok"), "ok"), 
                                           (_("Cancel"), "cancel")))
        tl = snack.GridForm(self.screen, _("Modem Configuration"), 1, 3)
        tl.add(g1, 0, 0, (0, 0, 0, 1), anchorLeft=1)
        tl.add(g2, 0, 1, (0, 0, 0, 1))
        tl.add(bb, 0, 2, growx = 1)
        self.setState(self.modem)
        while 1:
            res = tl.run()
            if bb.buttonPressed(res) == "cancel":
                self.screen.popWindow()
                return False

            elif bb.buttonPressed(res) == "ok":
                self.screen.popWindow()
                self.processInfo()
                return True

def register_plugin():
    from netconfpkg.plugins.NCPluginDevModem import setDevModemDialog
    setDevModemDialog(NCModemInterfaceTui)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
