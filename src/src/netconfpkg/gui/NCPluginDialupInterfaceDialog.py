## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import gtk
import re
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCDialup import DM_AUTO, DM_MANUAL, DialModes
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NC_functions import _, getNewDialupDevice
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.DeviceConfigDialog import DeviceConfigDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.provider import (providerDialog, 
                                     ISDNproviderDialog,
                                     ModemproviderDialog)
from netconfpkg.gui.tonline import TonlineDialog


class DialupInterfaceDialog(DeviceConfigDialog):
    def __init__(self, device):
        glade_file = "DialupInterfaceDialog.glade"
        DeviceConfigDialog.__init__(self, glade_file, 
                                    device)
        self.edit = False

        xml_signal_autoconnect(self.xml, 
            {
            "on_chooseButton_clicked" : self.on_chooseButton_clicked, 
            "on_helpButton_clicked" : self.on_helpButton_clicked, 
            "on_callbackCB_toggled" : self.on_callbackCB_toggled, 
            "on_pppOptionEntry_changed" : self.on_pppOptionEntry_changed, 
            "on_pppOptionAddButton_clicked" : \
            self.on_pppOptionAddButton_clicked, 
            "on_pppOptionList_select_row" : self.on_pppOptionList_select_row, 
            "on_ipppOptionList_unselect_row" : \
            self.on_ipppOptionList_unselect_row, 
            "on_pppOptionDeleteButton_clicked" : \
            self.on_pppOptionDeleteButton_clicked, 
            "on_tonlineButton_clicked" : self.on_tonlineButton_clicked, 
            "on_showPassword_clicked" : self.on_showPassword_clicked, 
            })

        self.noteBook = self.xml.get_widget("dialupNotebook")
        self.xml.get_widget ("pppOptionList").column_titles_passive ()

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('routeWindow')
        frame = self.sharedtcpip_xml.get_widget ('routeFrame')
        vbox = self.xml.get_widget ('routeVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device, self.dialog)
        self.hydrate ()

    def hydrate(self):
        DeviceConfigDialog.hydrate(self)

        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)

        dialup = self.device.Dialup

        if dialup.ProviderName != None:
            self.xml.get_widget("providerName").set_text(dialup.ProviderName)
        if dialup.Login != None:
            self.xml.get_widget("loginNameEntry").set_text(dialup.Login)
        if dialup.Password != None:
            self.xml.get_widget("passwordEntry").set_text(
                                re.sub(r"\\([^\\]|\\)", r"\1",
                                dialup.Password))

        if dialup.Areacode != None:
            self.xml.get_widget("areaCodeEntry").set_text(dialup.Areacode)
        if dialup.PhoneNumber != None:
            self.xml.get_widget("phoneEntry").set_text(dialup.PhoneNumber)
        if dialup.Prefix != None:
            self.xml.get_widget("prefixEntry").set_text(dialup.Prefix)

        if dialup.Compression:
            self.xml.get_widget("headerCompressionCB").set_active(
                dialup.Compression.VJTcpIp == True)
            self.xml.get_widget("connectionCompressionCB").set_active(
                dialup.Compression.VJID == True)
            self.xml.get_widget("acCompressionCB").set_active(
                dialup.Compression.AdressControl == True)
            self.xml.get_widget("pfCompressionCB").set_active(
                dialup.Compression.ProtoField == True)
            self.xml.get_widget("bsdCompressionCB").set_active(
                dialup.Compression.BSD == True)
            self.xml.get_widget("cppCompressionCB").set_active(
                dialup.Compression.CCP == True)

        if dialup.PPPOptions:
            widget = self.xml.get_widget("pppOptionList")
            widget.clear()
            widget.set_sensitive(len(dialup.PPPOptions)>0)
            for plist in dialup.PPPOptions:
                widget.append([plist])

    def dehydrate(self):
        DeviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        dialup = self.device.createDialup()

        for attr, widget in { 
             'ProviderName' : 'providerName',
             'Login' : 'loginNameEntry',
             'Password' : 'passwordEntry',
             'Areacode' : 'areaCodeEntry',
             'Prefix' : 'prefixEntry',
             'PhoneNumber' : 'phoneEntry',
             }.items():
            val = self.xml.get_widget(widget).get_text().strip()
            if val:
                setattr(dialup, attr, val)
            else:
                if attr != "Password":
                    delattr(dialup, attr)

        if not dialup.Compression:
            dialup.createCompression()

        for attr, widget in { 
             'VJTcpIp' : 'headerCompressionCB',
             'VJID' : 'connectionCompressionCB',
             'AdressControl' : 'acCompressionCB',
             'ProtoField' : 'pfCompressionCB',
             'BSD' : 'bsdCompressionCB',
             'CCP' : 'cppCompressionCB',
             }.items():
            val = self.xml.get_widget(widget).get_active()
            setattr(dialup.Compression, attr, val)
        
        del dialup.PPPOptions
        clist = self.xml.get_widget("pppOptionList")
        if clist.rows:
            dialup.createPPPOptions()
            for i in xrange (clist.rows):
                dialup.PPPOptions.append(clist.get_text(i, 0).strip())

    def on_helpButton_clicked(self, button):
        pass

    def on_msnEntry_changed (self, *args):
        pass

    def on_callbackCB_toggled(self, check):
        self.xml.get_widget("callbackFrame").set_sensitive(check.get_active())
        self.xml.get_widget("dialinNumberEntry").grab_focus()

    def on_prefixEntry_changed (self, *args):
        pass

    def on_areaCodeEntry_changed (self, *args):
        pass

    def on_phoneEntry_changed (self, *args):
        pass

    def on_authMenu_enter (self, *args):
        pass

    def on_dialupProviderNameEntry_changed (self, *args):
        pass

    def on_dialupLoginNameEntry_activate (self, *args):
        pass

    def on_dialupPasswordEntry_changed (self, *args):
        pass

    def on_HeaderCompressionCB_toggled (self, *args):
        pass

    def on_connectionCompressionCB_toggled (self, *args):
        pass

    def on_acCompressionCB_toggled (self, *args):
        pass

    def on_pcCompressionCB_toggled (self, *args):
        pass

    def on_bsdCompressionCB_toggled (self, *args):
        pass

    def on_cppCompressionCB_toggled (self, *args):
        pass

    def on_pppOptionEntry_changed (self, entry):
        option = entry.get_text().strip()
        self.xml.get_widget("pppOptionAddButton").set_sensitive(
            len(option) > 0)

    def on_pppOptionAddButton_clicked (self, 
                                       button): # pylint: disable-msg=W0613
        entry = self.xml.get_widget("pppOptionEntry")
        self.xml.get_widget("pppOptionList").set_sensitive(True)
        self.xml.get_widget("pppOptionList").append([entry.get_text().strip()])
        entry.set_text("")
        entry.grab_focus()

    def on_pppOptionList_select_row(self, 
                            clist, r, c, event): # pylint: disable-msg=W0613
        self.xml.get_widget ("pppOptionDeleteButton").set_sensitive (True)

    def on_ipppOptionList_unselect_row (self,
                        clist, r, c, event): # pylint: disable-msg=W0613
        self.xml.get_widget("pppOptionDeleteButton").set_sensitive(False)

    def on_pppOptionDeleteButton_clicked(self, 
                                         button): # pylint: disable-msg=W0613
        clist = self.xml.get_widget("pppOptionList")
        if clist.selection:
            clist.remove(clist.selection[0])

    def on_chooseButton_clicked(self, button): # pylint: disable-msg=W0613
        providerDialog(self.device)

    def set_title(self, title = _("Dialup Configuration")):
        self.dialog.set_title(title)

    def on_tonlineButton_clicked(self, *args): # pylint: disable-msg=W0613
        self.dehydrate()
        dialup = self.device.Dialup
        dialog = TonlineDialog(dialup.Login, dialup.Password)
        dl = dialog.xml.get_widget ("Dialog")

        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

        if dl.run() != gtk.RESPONSE_OK:
            dl.destroy()
            return

        dl.destroy()
        dialup.Login = dialog.login
        dialup.Password = dialog.password
        self.xml.get_widget("loginNameEntry").set_text(dialup.Login)
        self.xml.get_widget("passwordEntry").set_text(dialup.Password)
        if not self.xml.get_widget("providerName").get_text().strip():
            self.xml.get_widget("providerName").set_text("T-Online")

    def on_showPassword_clicked(self, *args): # pylint: disable-msg=W0613
        self.xml.get_widget("passwordEntry").set_visibility(\
                            self.xml.get_widget("showPassword").get_active())


class ISDNDialupInterfaceDialog(DialupInterfaceDialog):
    def __init__(self, device):
        DialupInterfaceDialog.__init__(self, device)

        page = self.noteBook.page_num(self.xml.get_widget ("modemTab"))
        self.noteBook.get_nth_page(page).hide()

        self.dialog.set_title(_("ISDN Dialup Configuration"))

    def on_chooseButton_clicked(self, button): # pylint: disable-msg=W0613
        dialog = ISDNproviderDialog(self.device)
        dl = dialog.xml.get_widget("Dialog")
        dl.set_transient_for(self.dialog)
        dl.run()
        dl.destroy()
        DialupInterfaceDialog.hydrate(self)
        self.hydrate()

    def hydrate(self):
        DialupInterfaceDialog.hydrate(self)

        dialup = self.device.Dialup

        omenu = self.xml.get_widget("CallbackMode")
        omenu.remove_menu()
        menu = gtk.Menu()

        for txt in [_('in'), _('out')]:
            item = gtk.MenuItem (txt)
            item.show()
            menu.append (item)
        omenu.set_menu (menu)
        omenu.show_all()

        if dialup.PhoneInNumber:
            self.xml.get_widget("dialinNumberEntry").set_text(\
                dialup.PhoneInNumber)

        if dialup.Secure:
            self.xml.get_widget("allowDialinNumberCB").set_active(\
                dialup.Secure)

        if dialup.Callback and dialup.Callback.Type != 'off':
            self.xml.get_widget("callbackCB").set_active(True)
            self.xml.get_widget("callbackFrame").set_sensitive(True)
            if dialup.Callback.Type == 'in':
                self.xml.get_widget('CallbackMode').set_history(0)
            else:
                self.xml.get_widget('CallbackMode').set_history(1)
            self.xml.get_widget('CallbackMode').show_all()

            self.xml.get_widget("callbackDelaySB").set_value(\
                dialup.Callback.Delay)
            self.xml.get_widget("cbcpCB").set_active(\
                dialup.Callback.Compression)
            self.xml.get_widget("cbcpMSNEntry").set_text(\
                dialup.Callback.MSN)

        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutISDNSB").set_value(\
                dialup.HangupTimeout)

        if dialup.DialMode:
            if dialup.DialMode == DM_AUTO:
                dialmode = DialModes[DM_AUTO]
            else:
                dialmode = DialModes[DM_MANUAL]
        else:
            dialmode = DialModes[DM_MANUAL]

        self.xml.get_widget("dialModeISDNEntry").set_text(dialmode)

        if dialup.EncapMode == 'rawip':
            self.xml.get_widget("encapModeEntry").set_text(_('raw IP'))
        else:
            self.xml.get_widget("encapModeEntry").set_text(_('sync PPP'))

        if dialup.MSN:
            self.xml.get_widget("msnEntry").set_text(str(dialup.MSN))

        if dialup.DefRoute != None:
            self.xml.get_widget("defrouteISDNCB").set_active(dialup.DefRoute)

        if dialup.ChannelBundling:
            self.xml.get_widget("channelBundlingCB").set_active(\
                dialup.ChannelBundling == True)
        if dialup.Authentication:
            if dialup.Authentication == '+pap -chap':
                auth = _('pap')
            elif dialup.Authentication == '-pap +chap':
                auth = _('chap')
            elif dialup.Authentication == '+chap +pap' or \
                     dialup.Authentication == '+pap +chap':
                auth = _('chap+pap')
            else:
                auth = _('none')
            self.xml.get_widget("authEntry").set_text(auth)

    def dehydrate(self):
        DialupInterfaceDialog.dehydrate(self)

        dialup = self.device.Dialup

        encap_mode_old = dialup.EncapMode
        if self.xml.get_widget("encapModeEntry").get_text() == _("sync PPP"):
            dialup.EncapMode = "syncppp"
        else:
            dialup.EncapMode = "rawip"

        # get free ISDN device if encap mode is changed
        if encap_mode_old != dialup.EncapMode:
            self.device.Device = getNewDialupDevice(\
                getDeviceList(), self.device)

        dialup.PhoneInNumber = self.xml.get_widget(
            "dialinNumberEntry").get_text().strip()
        if not dialup.PhoneInNumber:
            del dialup.PhoneInNumber
        dialup.Secure = self.xml.get_widget("allowDialinNumberCB").get_active()

        if self.xml.get_widget("callbackCB").get_active():
            dialup.createCallback()
            if self.xml.get_widget('CallbackMode').get_child().get_label() == \
                   _('in'):
                dialup.Callback.Type = 'in'
            else:
                dialup.Callback.Type = 'out'
            dialup.Callback.Delay = self.xml.get_widget(\
                "callbackDelaySB").get_value_as_int()
            dialup.Callback.Hup = False
            dialup.Callback.Compression = self.xml.get_widget(\
                "cbcpCB").get_active()
            dialup.Callback.MSN = self.xml.get_widget(\
                "cbcpMSNEntry").get_text().strip()
            if not dialup.Callback.MSN:
                del dialup.Callback.MSN
        else:
            if dialup.Callback:
                dialup.Callback.Type = "off"

        dialup.HangupTimeout = self.xml.get_widget(\
            "hangupTimeoutISDNSB").get_value_as_int()
        dialup.DialMode = self.xml.get_widget("dialModeISDNEntry").get_text()
        if dialup.DialMode == DialModes[DM_AUTO]:
            dialup.DialMode = DM_AUTO
            dialup.DefRoute = True
        else:
            dialup.DialMode = DM_MANUAL
            dialup.DefRoute = False

        dialup.MSN = self.xml.get_widget("msnEntry").get_text().strip()
        if not dialup.MSN:
            del dialup.MSN

        dialup.ChannelBundling = self.xml.get_widget(\
            "channelBundlingCB").get_active()
        if dialup.ChannelBundling:
            dialup.SlaveDevice = getNewDialupDevice(\
                getDeviceList(), self.device)
        else:
            dialup.SlaveDevice = None
        dialup.DefRoute = self.xml.get_widget("defrouteISDNCB").get_active()

        auth = self.xml.get_widget("authEntry").get_text()
        if auth == _('pap'):
            dialup.Authentication = '+pap -chap'
        elif auth == _('chap'):
            dialup.Authentication = '-pap +chap'
        elif auth == _('chap+pap'):
            dialup.Authentication = '+chap +pap'
        else:
            dialup.Authentication = 'noauth'


class ModemDialupInterfaceDialog(DialupInterfaceDialog):
    def __init__(self, device):
        DialupInterfaceDialog.__init__(self, device)

        self.dialog.set_title(_("Modem Dialup Configuration"))
        page = self.noteBook.page_num(self.xml.get_widget ("isdnTab"))
        self.noteBook.get_nth_page(page).hide()
        page = self.noteBook.page_num(self.xml.get_widget ("callbackTab"))
        self.noteBook.get_nth_page(page).hide()

    def on_chooseButton_clicked(self, button): # pylint: disable-msg=W0613
        dialog = ModemproviderDialog(self.device)
        dl = dialog.xml.get_widget("Dialog")
        dl.set_transient_for(self.dialog)
        dl.run()
        dl.destroy()
        DialupInterfaceDialog.hydrate(self)
        self.hydrate()

    def hydrate(self):
        DialupInterfaceDialog.hydrate(self)
        hardwarelist = getHardwareList()
        devicelist = []
        for hw in hardwarelist:
            if hw.Type == 'Modem':
                devicelist.append(hw.Name)
                continue

        if devicelist:
            self.xml.get_widget("modemPortCombo").set_popdown_strings(\
                devicelist)

        dialup = self.device.Dialup
        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutSB").set_value(\
                dialup.HangupTimeout)
        if dialup.DialMode:
            if dialup.DialMode == DM_AUTO:
                dialmode = DialModes[DM_AUTO]
            else:
                dialmode = DialModes[DM_MANUAL]
        else:
            dialmode = DialModes[DM_MANUAL]
        self.xml.get_widget("dialModeEntry").set_text(dialmode)

        if dialup.InitString:
            self.xml.get_widget("modemInitEntry").set_text(
                dialup.InitString)

        if dialup.Persist:
            self.xml.get_widget("persistCB").set_active(dialup.Persist)

        if dialup.DefRoute != None:
            self.xml.get_widget("defrouteCB").set_active(dialup.DefRoute)

        if dialup.Inherits:
            self.xml.get_widget("modemPortEntry").set_text(dialup.Inherits)

        self.xml.get_widget("stupidModeCB").set_active(\
            self.device.Dialup.StupidMode == True)

    def dehydrate(self):
        DialupInterfaceDialog.dehydrate(self)
        
        if not self.device.Device:
            self.device.Device = getNewDialupDevice(
                getDeviceList(), self.device)

        dialup = self.device.Dialup
        
        dialup.HangupTimeout = self.xml.get_widget(
                               "hangupTimeoutSB").get_value_as_int()

        for attr, widget in { 
             'InitString' : 'modemInitEntry',
             'Inherits' : 'modemPortEntry',
             'DialMode' : 'dialModeEntry',
             }.items():
            val = self.xml.get_widget(widget).get_text().strip()
            if val:
                setattr(dialup, attr, val)
            else:
                delattr(dialup, attr)

        for attr, widget in { 
             'Persist' : 'persistCB',
             'DefRoute' : 'defrouteCB',
             'StupidMode' : 'stupidModeCB',
             }.items():
            val = self.xml.get_widget(widget).get_active()
            setattr(dialup, attr, val)

        if dialup.DialMode == DialModes[DM_AUTO]: 
            dialup.DialMode = DM_AUTO
        else: 
            dialup.DialMode = DM_MANUAL


def register_plugin():
    from netconfpkg.plugins import NCPluginDevIsdn, NCPluginDevModem
    NCPluginDevIsdn.setDevIsdnDialog(ISDNDialupInterfaceDialog)
    NCPluginDevModem.setDevModemDialog(ModemDialupInterfaceDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
