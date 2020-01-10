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
import gtk.glade
import os
import re
from netconfpkg.NCProfileList import getProfileList
from netconfpkg.NC_functions import _
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import (xml_signal_autoconnect,              
                                          gui_error_dialog)


# pylint: disable-msg=W0613

class editIPsecDruid:
    def __init__(self, ipsec=None):
        self.ipsec = ipsec

        glade_file = "editipsec.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None,
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml, {
            "on_ipsecidEntry_insert_text" : \
            (self.on_generic_entry_insert_text,
             r"^[a-z|A-Z|0-9\_:]+$"),
            "on_spiEntry_insert_text" : \
            (self.on_generic_entry_insert_text,
             r"^[0-9]+$"),
            "on_ipsecDruidPageStart_next" :
            self.on_ipsecDruidPageStart_next,
            "on_ipsecDruidNicknamePage_next" :
            self.on_ipsecDruidNicknamePage_next,
            "on_ipsecDruidConnectionTypePage_prepare" :
            self.on_ipsecDruidConnectionTypePage_prepare,
            "on_ipsecDruidConnectionTypePage_next" :
            self.on_ipsecDruidConnectionTypePage_next,
            "on_ipsecDruidEncryptionModePage_prepare" :
            self.on_ipsecDruidEncryptionModePage_prepare,
            "on_ipsecDruidEncryptionModePage_next" :
            self.on_ipsecDruidEncryptionModePage_next,
            "on_ipsecDruidLocalNetworkPage_prepare" :
            self.on_ipsecDruidLocalNetworkPage_prepare,
            "on_ipsecDruidLocalNetworkPage_next" :
            self.on_ipsecDruidLocalNetworkPage_next,
            "on_ipsecDruidRemoteNetworkPage_prepare" :
            self.on_ipsecDruidRemoteNetworkPage_prepare,
            "on_ipsecDruidRemoteNetworkPage_next" :
            self.on_ipsecDruidRemoteNetworkPage_next,
            "on_ipsecDruidKeysPage_prepare" :
            self.on_ipsecDruidKeysPage_prepare,
            "on_ipsecDruidKeysPage_next" :
            self.on_ipsecDruidKeysPage_next,
            "on_ipsecDruidFinishPage_prepare" :
            self.on_ipsecDruidFinishPage_prepare,
            "on_ipsecDruidFinishPage_finish" :
            self.on_ipsecDruidFinishPage_finish,
            "on_generateAHKeyButton_clicked" :
            self.on_generateAHKeyButton_clicked,
            "on_generateESPKeyButton_clicked" :
            self.on_generateESPKeyButton_clicked,
            "on_ipsecDruid_cancel" : self.on_ipsecDruid_cancel,
            })

        self.druid = self.xml.get_widget("Druid")
        self.druidwidget = self.xml.get_widget("ipsecDruid")
        self.canceled = False
        self.druid.show_all()
        self.entries = {
            "localNetworkEntry" : "LocalNetwork",
            "localSubnetEntry" : "LocalNetmask",
            "localGatewayEntry" : "LocalGateway",
            "remoteNetworkEntry" : "RemoteNetwork",
            "remoteSubnetEntry" : "RemoteNetmask",
            "remoteGatewayEntry" : "RemoteGateway",
            "remoteIPEntry" : "RemoteIPAddress",
            "SPI_AH_IN_Entry" : "SPI_AH_IN",
            "SPI_AH_OUT_Entry" : "SPI_AH_OUT",
            "SPI_ESP_IN_Entry" : "SPI_ESP_IN",
            "SPI_ESP_OUT_Entry" : "SPI_ESP_OUT",
            "AHKeyEntry" : "AHKey",
            "ESPKeyEntry" : "ESPKey",
            "ipsecidEntry" : "IPsecId",
            }

        for key, val in self.entries.items():
            if val:
                widget = self.xml.get_widget(key)
                if widget:
                    widget.set_text(getattr(self.ipsec, val) or "")

        if self.ipsec.EncryptionMode == "auto":
            widget = self.xml.get_widget("AHKeyEntry")
            if widget:
                widget.set_text(self.ipsec.IKEKey or "")


        self.xml.get_widget('onBootCB').set_active(self.ipsec.OnBoot == True)


    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, mstr):
        text = partial_text[0:length]
        if re.match(mstr, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_ipsecDruidPageStart_next(self, druid_page, druid):
        return False

    def on_ipsecDruidNicknamePage_next(self, druid_page, druid):
        if not self.xml.get_widget("ipsecidEntry").get_text():
            return True
        else:
            return False

    def on_ipsecDruidConnectionTypePage_prepare(self, druid_page, druid):
        if self.ipsec.ConnectionType == "Host2Host":
            self.xml.get_widget("hosttohostEncryptionRadio").set_active(True)
        else:
            self.xml.get_widget("nettonetEncryptionRadio").set_active(True)

        return False

    def on_ipsecDruidConnectionTypePage_next(self, druid_page, druid):
        if self.xml.get_widget("hosttohostEncryptionRadio").get_active():
            self.ipsec.ConnectionType = "Host2Host"
            self.xml.get_widget("localIPTable").hide()

            for widget in [ "remoteNetworkEntry",
                            "remoteSubnetEntry",
                            "remoteGatewayEntry",
                            "remoteNetworkLabel",
                            "remoteSubnetLabel",
                            "remoteGatewayLabel",
                            ]:
                self.xml.get_widget(widget).hide()
        else:
            self.ipsec.ConnectionType = "Net2Net"
            self.xml.get_widget("localIPTable").show()
            self.xml.get_widget("ipsecDruidLocalNetworkPage").show()
            for widget in [ "remoteNetworkEntry",
                            "remoteSubnetEntry",
                            "remoteGatewayEntry",
                            "remoteNetworkLabel",
                            "remoteSubnetLabel",
                            "remoteGatewayLabel",
                            ]:
                self.xml.get_widget(widget).show()
        return False

    def on_ipsecDruidEncryptionModePage_prepare(self, druid_page, druid):
        if self.ipsec.EncryptionMode == "manual":
            self.xml.get_widget("manualEncryptionRadio").set_active(True)
        else:
            self.xml.get_widget("automaticEncryptionRadio").set_active(True)
        return False

    def on_ipsecDruidEncryptionModePage_next(self, druid_page, druid):
        if self.xml.get_widget("manualEncryptionRadio").get_active():
            self.ipsec.EncryptionMode = "manual"
            for widget in [ "ESPKeyLabel", "ESPKeyEntry", "ESPKeyButton",
                            "spiInTable", "spiOutTable" ]:
                self.xml.get_widget(widget).show()
            self.xml.get_widget("ipsecDruidLocalNetworkPage").show()
        else:
            self.ipsec.EncryptionMode = "auto"
            for widget in [ "ESPKeyLabel", "ESPKeyEntry", "ESPKeyButton",
                            "spiInTable", "spiOutTable" ]:
                self.xml.get_widget(widget).hide()

            if self.ipsec.ConnectionType == "Host2Host":
                self.xml.get_widget("ipsecDruidLocalNetworkPage").hide()
            else:
                self.xml.get_widget("ipsecDruidLocalNetworkPage").show()

        return False

    def on_ipsecDruidLocalNetworkPage_prepare(self, druid_page, druid):
        return False

    def on_ipsecDruidLocalNetworkPage_next(self, druid_page, druid):
        if self.ipsec.EncryptionMode == "manual":
            for widget_name in [ "SPI_AH_IN_Entry", "SPI_ESP_IN_Entry" ]:
                widget = self.xml.get_widget(widget_name)
                val = widget.get_text()

                try:
                    val = int(val)
                    if val < 256:
                        raise ValueError
                except:
                    gui_error_dialog(
                        _("Please enter a unique security parameter "
                          "index between 256 and 4294967295."),
                                     self.druid, widget = druid,
                                     page = druid_page, broken_widget = widget)
                    return 1

        if self.xml.get_widget("hosttohostEncryptionRadio").get_active():
            return 0

        for widget in [ "localNetworkEntry", "localSubnetEntry",
                        "localGatewayEntry" ]:
            if not self.xml.get_widget(widget).get_text():
                return 1
        return 0

    def on_ipsecDruidRemoteNetworkPage_prepare(self, druid_page, druid):
        return False

    def on_ipsecDruidRemoteNetworkPage_next(self, druid_page, druid):
        wlist = [ "remoteIPEntry" ]
        if self.ipsec.ConnectionType == "Net2Net":
            wlist.extend([ "remoteNetworkEntry",
                           "remoteSubnetEntry",
                           "remoteGatewayEntry"])
        for widget in wlist:
            if not self.xml.get_widget(widget).get_text():
                return True

        return False

    def on_ipsecDruidKeysPage_prepare(self, druid_page, druid):
        return False

    def on_ipsecDruidKeysPage_next(self, druid_page, druid):
        wlist = [ "AHKeyEntry" ]
        if self.ipsec.EncryptionMode == "manual":
            wlist.append("ESPKeyEntry")

        for widget in wlist:
            if not self.xml.get_widget(widget).get_text():
                return True

        return False

    def on_ipsecDruidFinishPage_prepare(self, druid_page, druid):
        for key, val in self.entries.items():
            widget = self.xml.get_widget(key)
            entry = (widget and widget.get_text()) or None
            if entry:
                setattr(self.ipsec, val, entry)

        if self.ipsec.EncryptionMode == "auto":
            self.ipsec.ESPKey = None
            self.ipsec.IKEKey = self.ipsec.AHKey
            self.ipsec.AHKey = None
            self.ipsec.SPI_AH_IN = None
            self.ipsec.SPI_AH_OUT = None
            self.ipsec.SPI_ESP_IN = None
            self.ipsec.SPI_ESP_OUT = None
        else:
            self.ipsec.IKEKey = None

        self.ipsec.OnBoot = self.xml.get_widget('onBootCB').get_active()

        if self.ipsec.ConnectionType == "Host2Host":
            for key in [ "LocalNetwork", "LocalNetmask", "LocalGateway",
                         "RemoteNetwork", "RemoteNetmask", "RemoteGateway"]:
                setattr(self.ipsec, key, None)

        s = _("You have selected the following information:") + "\n\n"
        s += str(self.ipsec)
        druid_page.set_text(s)
        return False

    def on_ipsecDruidFinishPage_finish(self, druid_page, druid):
        profilelist = getProfileList()
        for prof in profilelist:
            if self.ipsec.oldname and self.ipsec.oldname in prof.ActiveIPsecs:
                prof.ActiveIPsecs.remove(self.ipsec.oldname)
                prof.ActiveIPsecs.append(self.ipsec.IPsecId)

            if prof.Active == False:
                continue
            if not self.ipsec.oldname:
                prof.ActiveIPsecs.append(self.ipsec.IPsecId)
            break

        profilelist.commit()

        self.druid.hide()
        self.druid.destroy()
        gtk.main_quit()
        return False

    def on_ipsecDruid_cancel(self, *args):
        self.canceled = True
        self.druid.destroy()
        gtk.main_quit()
        return False

    def getKeyFromPassphrase(self, keylen):
        pdialog = self.xml.get_widget("passphraseDialog")
        phraseEntry = self.xml.get_widget("passphraseEntry")

        phraseEntry.set_text('')
        pdialog.show()
        button = pdialog.run()
        pdialog.hide()
        if button != gtk.RESPONSE_OK and button != 0:
            return None

        phrase = phraseEntry.get_text()

        try:
            import nss.nss as nss
            nss.nss_init_nodb()
            shasum = nss.data_to_hex(nss.sha1_digest(phrase))
        except:
            import hashlib
            shasum = hashlib.sha1(phrase).hexdigest()

        if len(shasum) > keylen: 
            shasum = shasum[:keylen]

        return shasum

    def on_generateAHKeyButton_clicked(self, *args):
        shasum = self.getKeyFromPassphrase(20)
        if shasum:
            widget = self.xml.get_widget("AHKeyEntry")
            widget.set_text(shasum)

    def on_generateESPKeyButton_clicked(self, *args):
        shasum = self.getKeyFromPassphrase(24)
        if shasum:
            widget = self.xml.get_widget("ESPKeyEntry")
            widget.set_text(shasum)

__author__ = "Harald Hoyer <harald@redhat.com>"
