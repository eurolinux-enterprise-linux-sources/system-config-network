
PYTHON_FILES = \
	__init__.py \
	NCPluginDevADSL.py \
	NCPluginDevEthernet.py \
	NCPluginDevIsdn.py \
	NCPluginDevModem.py \
	NCPluginDevTokenRing.py \
	NCPluginDevWireless.py \
	NCPluginHWEthernet.py \
	NCPluginHWIsdn.py \
	NCPluginHWModem.py \
	NCPluginHWWireless.py \
	NCPluginHWTokenring.py \
	NCPluginHWQeth.py \
	NCPluginDevQeth.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/plugins
netconfpkg_PYTHON = $(PYTHON_FILES) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

check-local:
	@for i in $(notdir $(wildcard *.py)); do echo $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
	