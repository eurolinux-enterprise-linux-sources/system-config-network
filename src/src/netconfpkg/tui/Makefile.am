PYTHON_FILES = \
	__init__.py \
	NCPluginEthernetInterface.py \
	NCPluginIsdnInterface.py \
	NCPluginQethInterface.py \
	NCPluginTokenRingInterface.py \
	NCPluginModemInterface.py \
	NCPluginDevices.py \
	NCPluginDNS.py \
	NCTcpIp.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/tui
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.gladep)) $(notdir $(wildcard *.pyc))

check-local:
	@for i in $(notdir $(wildcard *.py)); do echo $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
	
