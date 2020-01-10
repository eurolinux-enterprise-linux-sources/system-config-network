"TUI ISDN Interface Module"
import snack
from netconfpkg.NC_functions import _


class NCIsdnInterfaceTui:
    "TUI ISDN Interface Dialog"
    def __init__(self, isdn = None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @isdn The ISDN device. If none given, the first
               isdndevice in devicelist will be used.
               If none are there, one will be added.
        """

        self.name = snack.Entry(20, "")
        self.hwdev = snack.Entry(20, "")
        self.login = snack.Entry(20, "")
        self.phoneno = snack.Entry(20, "")
        self.password = snack.Entry(20, "", password = 1)
        self.msn = snack.Entry(20, "")
        self.isdn = isdn

    def setState(self, isdn = None):
        """
        Set the default values of the fields
        according to the given device
        @isdn The Device (type isdn) to use as default values
        """


        if isdn:
            if isdn.DeviceId:
                self.name.set(isdn.DeviceId)
            if isdn.Device:
                self.hwdev.set(isdn.Device)
            if isdn.Dialup.Login:
                self.login.set(isdn.Dialup.Login)
            if isdn.Dialup.Password:
                self.password.set(isdn.Dialup.Password)
            if isdn.Dialup.PhoneNumber:
                self.phoneno.set(isdn.Dialup.PhoneNumber)
            if isdn.Dialup.MSN:
                self.msn.set(isdn.Dialup.MSN)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.isdn.DeviceId = self.name.value()
        self.isdn.Device = self.hwdev.value()
        self.isdn.Dialup.Login = self.login.value()
        self.isdn.Dialup.Password = self.password.value()
        self.isdn.Dialup.PhoneNumber = self.phoneno.value()
        self.isdn.Dialup.MSN = self.msn.value()


    def runIt(self, mscreen):
        """
        Show and run the screen, save files if necesarry
        """
        g1 = snack.Grid(1, 1)
        g2 = snack.Grid(2, 6)
        g2.setField(snack.Label (_("Name")), 0, 0, anchorLeft = 1)
        g2.setField(snack.Label (_("Device")), 0, 1, anchorLeft = 1)
        g2.setField(snack.Label (_("ISP Phonenumber")), 0, 2, anchorLeft = 1)
        g2.setField(snack.Label (_("ISP Login")), 0, 3, anchorLeft = 1)
        g2.setField(snack.Label (_("ISP Password")), 0, 4, anchorLeft = 1)
        g2.setField(snack.Label (_("MSN")), 0, 5, anchorLeft = 1)
        g2.setField(self.name, 1, 0, (1, 0, 0, 0))
        g2.setField(self.hwdev, 1, 1, (1, 0, 0, 0))
        g2.setField(self.phoneno, 1, 2, (1, 0, 0, 0), anchorLeft = 1)
        g2.setField(self.login, 1, 3, (1, 0, 0, 0))
        g2.setField(self.password, 1, 4, (1, 0, 0, 0))
        g2.setField(self.msn, 1, 5, (1, 0, 0, 0))
        bb = snack.ButtonBar(mscreen, 
                             ((_("Ok"), "ok"), (_("Cancel"), "cancel")))
        tl = snack.GridForm(mscreen, _("ISDN Configuration"), 1, 3)
        tl.add(g1, 0, 0, (0, 0, 0, 1), anchorLeft = 1)
        tl.add(g2, 0, 1, (0, 0, 0, 1))
        tl.add(bb, 0, 2, growx = 1)
        self.setState(self.isdn)
        while 1:
            res = tl.run()
            if bb.buttonPressed(res) == "cancel":
                mscreen.popWindow()
                return False

            elif bb.buttonPressed(res)=="ok":
                mscreen.popWindow()
                self.processInfo()
                return True

def register_plugin():
    from netconfpkg.plugins.NCPluginDevIsdn import setDevIsdnDialog
    setDevIsdnDialog(NCIsdnInterfaceTui)
