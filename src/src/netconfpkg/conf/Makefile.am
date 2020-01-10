
PYTHON_FILES = \
	__init__.py \
	ConfChat.py \
	ConfEResolv.py \
	ConfESNetwork.py \
	ConfESStaticRoutes.py \
	ConfModules.py \
	ConfPAP.py \
	ConfPasswd.py \
	Conf.py \
	ConfShellVar.py \
	ConfSMB.py \
	ConfSysctl.py 

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/conf
netconfpkg_PYTHON = $(PYTHON_FILES) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

check-local:
	@for i in $(GLADE_FILES)  $(PYTHON_FILES); do test -f $(srcdir)/$$i || (echo $$i is missing;break);done && echo "Source file check PASSED"
	@for i in $(notdir $(wildcard *.py)); do echo $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false)||exit 1;done && echo "Source file check PASSED"
	
