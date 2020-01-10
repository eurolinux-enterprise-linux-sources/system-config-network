## Copyright (C) 2001-2006 Red Hat, Inc.
## Copyright (C) 2001-2006 Harald Hoyer <harald@redhat.com>

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
from netconfpkg import NC_functions
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NCRoute import Route, testIP, testMAC
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.editadress import editAdressDialog
import ethtool


###
### DHCP
###

DHCP = 0
BOOTP = 1
DIALUP = 2

# FIXME: [183338] use SEARCH not resolv.conf

def on_ipBootProto_toggled(widget, xml):
    if widget.name == "ipAutomaticRadio":
        active = widget.get_active()
    else:
        active = not widget.get_active()

    xml.get_widget('ipProtocolOmenu').set_sensitive(active)
    xml.get_widget('dhcpSettingFrame').set_sensitive(active)
    xml.get_widget('ipSettingFrame').set_sensitive(not active)

def dhcp_init (xml, device): # pylint: disable-msg=W0613
    xml_signal_autoconnect(xml, {\
        "on_ipAutomaticRadio_toggled" : (on_ipBootProto_toggled, xml),
        "on_ipStaticRadio_toggled" : (on_ipBootProto_toggled, xml),
        })
    on_ipBootProto_toggled(xml.get_widget('ipAutomaticRadio'), xml)

def dhcp_hydrate (xml, device):
    if not device.DeviceId:
        return

    try:
        device_type = device.BootProto
    except:
        if (device.Type == "ISDN" or device.Type == "Modem" 
            or device.Type == "xDSL"):
            device_type = 'dialup'
        else:
            device_type = 'dhcp'


    xml.get_widget('hostnameEntry').set_text(device.Hostname or '')
    xml.get_widget('ipAddressEntry').set_text(device.IP or '')
    xml.get_widget('ipNetmaskEntry').set_text(device.Netmask or '')
    xml.get_widget('ipGatewayEntry').set_text(device.Gateway or '')
    
    if device_type == 'dialup':
        xml.get_widget("ipProtocolOmenu").set_history(DIALUP)
    elif device_type == 'bootp':
        xml.get_widget("ipProtocolOmenu").set_history(BOOTP)
    else:
        xml.get_widget("ipProtocolOmenu").set_history(DHCP)

    # PEERDNS is True, if unset!!
    xml.get_widget('dnsSettingCB').set_active(device.AutoDNS != False)

    if device.Alias != None:
        device.BootProto = "none"
        xml.get_widget('ipAutomaticRadio').set_active(False)
        xml.get_widget('ipStaticRadio').set_active(True)
        on_ipBootProto_toggled(xml.get_widget('ipAutomaticRadio'), xml)
        xml.get_widget('ipAutomaticRadio').set_sensitive(False)
    else:
        xml.get_widget('ipAutomaticRadio').set_sensitive(True)
        

    if device.BootProto == "static" or device.BootProto == "none":
        xml.get_widget('ipAutomaticRadio').set_active(False)
        xml.get_widget('ipStaticRadio').set_active(True)
        on_ipBootProto_toggled(xml.get_widget('ipAutomaticRadio'), xml)
    else:
        xml.get_widget('ipAutomaticRadio').set_active(True)
        xml.get_widget('ipStaticRadio').set_active(False)
        on_ipBootProto_toggled(xml.get_widget('ipStaticRadio'), xml)

    if device.Mtu != None and xml.get_widget('mtuCB'):
        xml.get_widget('mtuSpin').set_value(device.Mtu)
        xml.get_widget('mtuCB').set_active(True)
    elif xml.get_widget('mtuCB'):
        xml.get_widget('mtuSpin').set_value(device.getRealMtu())
       

    if hasattr(device, "Dialup"):
        if device.Dialup.Mru != None and xml.get_widget('mruCB'):
            xml.get_widget('mruSpin').set_value(device.Dialup.Mru)
            xml.get_widget('mruCB').set_active(True)
    else:
        xml.get_widget('mruCB').set_active(False)
        xml.get_widget('mruSpin').hide()
        xml.get_widget('mruCB').hide()

    if device.PrimaryDNS:
        xml.get_widget('primaryDNSEntry').set_text(device.PrimaryDNS)
    if device.SecondaryDNS:
        xml.get_widget('secondaryDNSEntry').set_text(device.SecondaryDNS)

def dhcp_dehydrate (xml, device):
    if xml.get_widget('ipAutomaticRadio').get_active():
        if GUI_functions.get_history(
                            xml.get_widget ('ipProtocolOmenu')) == DHCP:
            device.BootProto = 'dhcp'
        elif GUI_functions.get_history(
                            xml.get_widget ('ipProtocolOmenu')) == BOOTP:
            device.BootProto = 'bootp'
        elif GUI_functions.get_history(
                            xml.get_widget ('ipProtocolOmenu')) == DIALUP:
            device.BootProto = 'dialup'
        else:
            device.BootProto = 'none'
    else:
        device.BootProto = 'none'

    device.AutoDNS = xml.get_widget('dnsSettingCB').get_active()

    for attr, widget in { 
         'IP' : 'ipAddressEntry',
         'Netmask' : 'ipNetmaskEntry',
         'Gateway' : 'ipGatewayEntry',
         'Hostname' : 'hostnameEntry',
         'PrimaryDNS' : 'primaryDNSEntry',
         'SecondaryDNS' : 'secondaryDNSEntry',
         }.items():
        val = xml.get_widget(widget).get_text().strip()
        if val:
            setattr(device, attr, val)
        else:
            delattr(device, attr)

    # Check errors in input boxes
    if device.BootProto == 'none':
        if hasattr(device, 'IP') and device.IP and not testIP(device.IP.strip()):
            raise ValueError(_("IP address is not in the correct format"))
        if hasattr(device, 'Netmask') and device.Netmask  and not testIP(device.Netmask.strip()):
            raise ValueError(_("Network mask is not in the correct format"))
        if hasattr(device, 'Gateway') and device.Gateway and not testIP(device.Gateway.strip()):
            raise ValueError(_("Gateway is not in the correct format"))
    if hasattr(device, 'PrimaryDNS') and device.PrimaryDNS and not testIP(device.PrimaryDNS.strip()):
        raise ValueError(_("Primary DNS is not in the correct format"))
    if hasattr(device, 'SecondaryDNS') and device.SecondaryDNS and not testIP(device.SecondaryDNS.strip()):
        raise ValueError(_("Secondary DNS is not in the correct format"))
            
    if xml.get_widget('mtuCB').get_active():
        device.Mtu = int(xml.get_widget('mtuSpin').get_value())
    else:
        device.Mtu = None

    if xml.get_widget('mruCB').get_active():
        if device.Dialup:
            device.Dialup.Mru = int(xml.get_widget('mruSpin').get_value())
    elif hasattr(device, "Dialup"):        
        device.Dialup.Mru = None

    if device.BootProto == 'none':
        # None will remove the PEERDNS from the config
        device.AutoDNS = None

###
### ROUTES
###
def route_update(xml, device):
    clist = xml.get_widget('networkRouteList')
    clist.clear()

    if device.StaticRoutes != None:
        for route in device.StaticRoutes:
            clist.append([route.Address, route.Netmask or "", 
                          route.Gateway or ""])
#    else:
#        device.createStaticRoutes()

def on_routeEditButton_clicked(button, xml, device, parent_dialog):
    routes = device.StaticRoutes
    clist  = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0:
        return

    route = routes[clist.selection[0]]

    dialog = editAdressDialog(route)
    dl = dialog.xml.get_widget ("Dialog")

    if parent_dialog:
        dl.set_transient_for(parent_dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    else:
        dl.set_position (gtk.WIN_POS_CENTER)

    while(True):
        button = dl.run()
        if button == gtk.RESPONSE_OK:
            try:
                route.test()
            except ValueError:
                GUI_functions.gui_error_dialog ("Invalid IP format", dl)
                continue
        else:
            # if user pressed CANCEL
            dl.destroy()
            return
        break
    # user pressed OK and all tests passed
    dl.destroy()
    
    route_update(xml, device)


def on_routeDeleteButton_clicked(button, xml, 
                                 device): # pylint: disable-msg=W0613
    if not device.StaticRoutes:
        device.createStaticRoutes()

    routes = device.StaticRoutes

    clist  = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0:
        return

    del routes[clist.selection[0]]
    route_update(xml, device)

def on_routeUpButton_clicked(button, xml, device): # pylint: disable-msg=W0613
    routes = device.StaticRoutes
    clist = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0 or clist.selection[0] == 0:
        return

    select_row = clist.selection[0]
#    dest = clist.get_text(select_row, 0)
#    prefix = clist.get_text(select_row, 1)
#    gateway = clist.get_text(select_row, 2)

    rcurrent = routes[select_row]
    rnew = routes[select_row-1]

    routes[select_row] = rnew
    routes[select_row-1] = rcurrent

    route_update(xml, device)

    clist.select_row(select_row-1, 0)

def on_routeDownButton_clicked(button, 
                               xml, device): # pylint: disable-msg=W0613
    routes = device.StaticRoutes
    clist = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0 or clist.selection[0] == len(routes)-1:
        return

    select_row = clist.selection[0]
#    dest = clist.get_text(select_row, 0)
#    prefix = clist.get_text(select_row, 1)
#    gateway = clist.get_text(select_row, 2)

    rcurrent = routes[select_row]
    rnew = routes[select_row+1]

    routes[select_row] = rnew
    routes[select_row+1] = rcurrent

    route_update(xml, device)

    clist.select_row(select_row+1, 0)

def on_routeAddButton_clicked(button, xml, device, parent_dialog):
    if device.StaticRoutes == None:
        device.createStaticRoutes()
    routes = device.StaticRoutes
    route = Route()
    dialog = editAdressDialog(route)
    dl = dialog.xml.get_widget ("Dialog")

    if parent_dialog:
        dl.set_transient_for(parent_dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    else:
        dl.set_position (gtk.WIN_POS_CENTER)
    
    while(True):
        button = dl.run()
        if button == gtk.RESPONSE_OK:
            try:
                route.test()
            except ValueError:
                GUI_functions.gui_error_dialog ("Invalid IP format", dl)
                continue
        else:
            # if user pressed CANCEL
            dl.destroy()
            return
        break
    # user pressed OK and all tests passed
    dl.destroy()
    
    routes.append(route)
    route_update(xml, device)

def route_init(xml, device, dialog = None):
    xml_signal_autoconnect(xml, { \
        "on_routeAddButton_clicked" : (on_routeAddButton_clicked,
                                       xml, device, dialog),
        "on_routeEditButton_clicked" : (on_routeEditButton_clicked,
                                        xml, device, dialog),
        "on_routeDeleteButton_clicked" : (on_routeDeleteButton_clicked,
                                          xml, device),
        })
    route_update(xml, device)


def route_hydrate(xml, device): # pylint: disable-msg=W0613
    pass

def route_dehydrate(xml, device): # pylint: disable-msg=W0613
    pass


###
### Hardware (ethernet)
###
def on_hardwareAliasesToggle_toggled(widget, xml, device):
    xml.get_widget("hardwareAliasesSpin").set_sensitive (widget.get_active())
    if widget.get_active():
        device.Alias = xml.get_widget(
                        "hardwareAliasesSpin").get_value_as_int()
    else:
        device.Alias = None

def on_hardwareMACToggle_toggled(widget, 
                                 xml, device): # pylint: disable-msg=W0613
    xml.get_widget("hardwareMACEntry").set_sensitive (widget.get_active())
    xml.get_widget("hardwareProbeButton").set_sensitive (widget.get_active())

def on_hardwareProbeButton_clicked(widget, 
                                   xml, device): # pylint: disable-msg=W0613
    omenu = xml.get_widget("hwdvOmenu")
    hw = omenu.get_children()[0].get()
    device = hw.split()[0]
    try: 
        hwaddr = ethtool.get_hwaddr(device)
    except IOError, err:
        error_str = str (err)
        GUI_functions.gui_error_dialog(error_str, omenu.get_toplevel())
    else:
        xml.get_widget("hardwareMACEntry").set_text(hwaddr)

def on_hardwareConfigureButton_clicked(widget, 
                                       xml, device): # pylint: disable-msg=W0613
    pass

def hardware_init(xml, device):
    xml_signal_autoconnect(xml, {\
        "on_hardwareAliasesToggle_toggled" : \
        (on_hardwareAliasesToggle_toggled, xml, device),
        "on_hardwareMACToggle_toggled" : \
        (on_hardwareMACToggle_toggled, xml, device),
        "on_hardwareProbeButton_clicked" : \
        (on_hardwareProbeButton_clicked, xml, device),
        "on_hardwareConfigureButton_clicked" : \
        (on_hardwareConfigureButton_clicked, xml, device)
        })
    xml.get_widget("hardwareSeparator").show()
    xml.get_widget("hardwareTable").show()

def hardware_hydrate(xml, device):
    hwlist = getHardwareList()
    (hwcurr, hwdesc) = NC_functions.create_generic_combo(hwlist, 
                                                         device.Device, 
                                                         mtype = device.Type)
    omenu = xml.get_widget("hwdvOmenu")
    omenu.remove_menu()
    menu = gtk.Menu()
    history = 0
    for i in range (0, len (hwdesc)):
        item = gtk.MenuItem (hwdesc[i])
        item.show()
        menu.append (item)
        if hwdesc[i] == hwcurr:
            history = i
    omenu.set_menu (menu)
    omenu.show_all()
    omenu.set_history (history)
    omenu.show_all()

    if device.Alias != None:
        xml.get_widget("hardwareAliasesSpin").set_value(int(device.Alias))
        xml.get_widget("hardwareAliasesToggle").set_active(False)
        xml.get_widget("hardwareAliasesToggle").set_active(True)
    else:
        xml.get_widget("hardwareAliasesToggle").set_active(True)
        xml.get_widget("hardwareAliasesToggle").set_active(False)

    if device.HardwareAddress != None:
        xml.get_widget("hardwareMACToggle").set_active(False)
        xml.get_widget("hardwareMACToggle").set_active(True)
        xml.get_widget("hardwareMACEntry").set_text(device.HardwareAddress)
        xml.get_widget("hardwareMACEntry").set_sensitive(True)
        xml.get_widget("hardwareProbeButton").set_sensitive(True)
    else:
        xml.get_widget("hardwareMACToggle").set_active(True)
        xml.get_widget("hardwareMACToggle").set_active(False)
        xml.get_widget("hardwareMACEntry").set_text('')
        xml.get_widget("hardwareMACEntry").set_sensitive(False)
        xml.get_widget("hardwareProbeButton").set_sensitive(False)


def hardware_dehydrate(xml, device):
    omenu = xml.get_widget("hwdvOmenu")
    hw = omenu.get_child().get_label()
    device.Device = hw.split()[0]
    if xml.get_widget("hardwareAliasesToggle").get_active():
        device.Alias = xml.get_widget("hardwareAliasesSpin").get_value_as_int()
    else:
        device.Alias = None
    if xml.get_widget("hardwareMACToggle").get_active():
        device.HardwareAddress = xml.get_widget("hardwareMACEntry").get_text()
        if not testMAC(device.HardwareAddress):
            raise ValueError(_("MAC address is not in the correct format"))
    else:
        device.HardwareAddress = None


def dsl_hardware_init(xml, device): # pylint: disable-msg=W0613
    pass

def dsl_hardware_hydrate(xml, device):
    hwlist = getHardwareList()
    (hwcurr, hwdesc) = NC_functions.create_ethernet_combo(hwlist, 
                                                        device.Dialup.EthDevice)
    omenu = xml.get_widget("hwdvOmenu")
    omenu.remove_menu()
    menu = gtk.Menu()
    history = 0
    for i in range (0, len (hwdesc)):
        item = gtk.MenuItem (hwdesc[i])
        item.show()
        menu.append (item)
        if hwdesc[i] == hwcurr:
            history = i
    omenu.set_menu (menu)
    omenu.show_all()
    omenu.set_history (history)
    omenu.show_all()


def dsl_hardware_dehydrate(xml, device):
    omenu = xml.get_widget("hwdvOmenu")
    hw = omenu.get_child().get_label()
    device.Dialup.EthDevice = hw.split()[0]

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/09/24 08:39:46 $"
__version__ = "$Revision: 1.45 $"
