AUTOMAKE_OPTIONS = foreign 1.4
ACLOCAL_AMFLAGS = -I m4

SUBDIRS = doc src po m4

EXTRA_DIST= \
	Makefile.inc \
	system-config-network.spec \
	system-config-network.desktop.in \
	system-config-network.console \
	system-config-network.pam \
	system-control-network.desktop.in \
	system-config-network-cmd.console \
	pycheckrc \
	intltool-extract.in intltool-merge.in intltool-update.in \
	ChangeLog \
	system-config-network.sh TODO \
	COPYING

iconsdir=$(pkgdatadir)

icons_DATA=system-config-network.desktop system-control-network.desktop

icons_in_files=$(icons_DATA:.desktop=.desktop.in)

CLEANFILES=$(icons_DATA) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*))
DISTCLEANFILES=intltool-extract intltool-merge intltool-update translators.txt
MAINTAINERCLEANFILES=ChangeLog

@INTLTOOL_DESKTOP_RULE@

sysdir=$(sysconfdir)/X11/applnk/System

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/security/console.apps
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/pam.d
	$(mkinstalldirs) $(DESTDIR)$(prefix)/bin/

	$(INSTALL_DATA) $(srcdir)/system-config-network.console $(DESTDIR)$(sysconfdir)/security/console.apps/system-config-network 
	$(INSTALL_DATA) $(srcdir)/system-config-network.pam $(DESTDIR)$(sysconfdir)/pam.d/system-config-network
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/system-config-network 

	install -m 0755 $(srcdir)/system-config-network.sh $(DESTDIR)$(sbindir)/system-config-network

#	# system-config-network-cmd needs a special console file
	$(INSTALL_DATA) $(srcdir)/system-config-network-cmd.console $(DESTDIR)$(sysconfdir)/security/console.apps/system-config-network-cmd
	$(INSTALL_DATA) $(srcdir)/system-config-network.pam $(DESTDIR)$(sysconfdir)/pam.d/system-config-network-cmd
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/system-config-network-cmd 

uninstall-local:
	rm -f  $(DESTDIR)$(sbindir)/system-control-network
	for i in system-config-network system-config-network-cmd; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

clean-local:
	rm -f system-config-network.desktop
	rm -f system-control-network.desktop
	rm -f *~ *\#

distclean-local:
	rm -f $(top_builddir)/po/po2tbl.sed

VERSION=@VERSION@
SCMTAG=r$(subst .,-,$(VERSION))-$(subst .,-,$(RPM_RELEASE))
GITBRANCH=master
GZ_BZIP=bz2

include Makefile.inc
