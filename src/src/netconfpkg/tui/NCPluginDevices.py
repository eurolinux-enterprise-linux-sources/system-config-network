"TUI Ethernet Interface Module"
#from netconfpkg.tui.NCTcpIp import NCTcpIpDialog

import snack
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCProfileList import getProfileList
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NC_functions import ETHERNET, ISDN, MODEM, QETH
from netconfpkg.NCDeviceFactory import getDeviceFactory
import os
#
# EthernetWindow class
#
class NCPluginDevicesTui():
    "TUI Device List"
    def __init__(self,plist):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @modem The modem device. If none given, the first
               modem in devicelist will be used.
               If none are there, one will be added.
        """
        self.plist = plist
        self.mscreen = None
        

    def setState(self):
        """
        Build the list of devices
        """
        self.li = snack.Listbox(5, returnExit=1)
        l = 0
        le = self.mscreen.width - 6
        if le <= 0: 
            le = 5
        for dev in getDeviceList():
            if not hasattr(dev, "getDialog") or not dev.getDialog():
                #li.append("No dialog for %s" % dev.Device, None)
                continue
    
            l += 1
            for hw in getHardwareList():
                if hw.Name == dev.Device and hw.Description:
                    self.li.append(("%s (%s) - %s" % (dev.DeviceId,
                                                 dev.Device,
                                                 hw.Description))[:le], dev)
                    break
    
            else:
                self.li.append(("%s (%s) - %s" % (dev.DeviceId,
                                        dev.Device, dev.Type))[:le], dev)
    
        if not l:
            return None
    
        self.li.append(_("<New Device>"), None)
        
    def newDevice(self,mscreen):
        """
        Displays the main screen
        @screen The snack screen instance
        """
        t = snack.TextboxReflowed(25, _("Which device type do you want to add?"))
        bb = snack.ButtonBar(mscreen, ((_("Add"), "add"), (_("Cancel"), "cancel")))
        li = snack.Listbox(5, width=25, returnExit=1)
        li.append(_("Ethernet"), ETHERNET)
    
        machine = os.uname()[4]
        if machine == 's390' or machine == 's390x':
            li.append(_("QETH"), QETH)
        else:
            li.append(_("Modem"), MODEM)
            li.append(_("ISDN"), ISDN)
    
        g = snack.GridForm(mscreen, _("Network Configuration"), 1, 3)
        g.add(t, 0, 0)
        g.add(li, 0, 1)
        g.add(bb, 0, 2)
        res = g.run()
        mscreen.popWindow()
        if bb.buttonPressed(res) != 'cancel':
            todo = li.current()
            df = getDeviceFactory()
            dev = None
            devclass = df.getDeviceClass(todo)
            devlist = getDeviceList()
            if not devclass: 
                return -1
            dev = devclass()
            if dev:
                devlist.append(dev)
                return dev
        return -2

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """
        pass
    
    def selectDevice(self,mscreen):
        #li = self.Listbox(5, returnExit=1)
        g = snack.GridForm(mscreen, _("Select A Device"), 1, 3)
        bb = snack.ButtonBar(mscreen, ((_("Save"), "save"), (_("Cancel"), "cancel")))
        g.add(self.li, 0, 1)
        g.add(bb, 0, 2, growx=1)
        res = g.run()
        mscreen.popWindow()
        if bb.buttonPressed(res) == "save":
            ret = -1
        elif bb.buttonPressed(res) == "cancel":
            ret = None
        else:
            ret = self.li.current()
            if not ret:
                ret = self.newDevice(mscreen)
        return ret

    def runIt(self, mscreen):
        """
        Show and run the screen, save files if necesarry
        """
        self.mscreen = mscreen
        devlist = getDeviceList()
        self.setState()
        while True:
            if devlist.modified():
                self.setState()
            dev = self.selectDevice(mscreen)
            if dev == -1:
                # we want to save
                return True
            elif dev == -2:
                continue
            elif dev == None:
                return False        
        
            dialog = dev.getDialog()
            if dialog.runIt(mscreen):
                dev.commit()     
                devlist.commit() 
                self.plist.activateDevice(dev.DeviceId,
                                     self.plist.getActiveProfile().ProfileName,
                                     state = True)
                self.plist.commit()
            else:
                dev.rollback()     
                devlist.rollback()
