SUBDIRS=gui tui plugins tests conf

PYTHON_FILES = \
	__init__.py \
	exception.py \
	executil.py \
	gdt.py \
	transaction.py \
	ipcalc.py \
	log.py \
	NCAliasList.py \
	NCBackendHal.py \
	NCCallback.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NCException.py \
	NC_functions.py \
	NCHardware.py \
	NCHardwareList.py \
	NCHardwareFactory.py \
	NCHostsList.py \
	NCHost.py \
	NCisdnhardware.py \
	NCIPsec.py \
	NCIPsecList.py \
	NCProfile.py \
	NCProfileList.py \
	NCRoute.py \
	NCWireless.py \
	Control.py \
	NCDeviceFactory.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

check-local:
	@for i in $(notdir $(wildcard *.py)); do echo $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
