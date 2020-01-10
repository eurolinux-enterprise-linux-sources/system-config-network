# -*- makefile -*-
# -*- coding: utf-8 -*-

.PHONY: changelog check-clean-tree archive tag force-tag srpm newversion potfile push pull diff rpmbase rpmlog pylint log

ChangeLog changelog:
	@git log --since="5 years ago" --no-merges -B HEAD > ChangeLog

check-clean-tree: check
	@git diff --quiet --exit-code|| (echo "****** Local uncommited changes";exit 1) || exit 1
	@git diff --cached --quiet --exit-code|| (echo "****** Local uncommited changes";exit 1) || exit 1

tag: check-clean-tree
	@if [ "$$(git-rev-parse HEAD 2>/dev/null)" != "$$(git-rev-parse $(SCMTAG) 2>/dev/null)" ] ; then \
		git tag $(SCMTAG); \
	fi

force-tag: check-clean-tree
	git tag -f $(SCMTAG)

archive: tag
	@test -d  /tmp/${PACKAGE}-$(VERSION) && chmod u+w -R /tmp/${PACKAGE}-$(VERSION) || :
	@rm -rf /tmp/${PACKAGE}-$(VERSION) /tmp/${PACKAGE}
	@git clone $$orig . /tmp/${PACKAGE}-$(VERSION)
	@cd /tmp/${PACKAGE}-$(VERSION);git checkout -b compile $(SCMTAG);./autogen.sh;make;make distcheck
	@mv /tmp/${PACKAGE}-$(VERSION)/${PACKAGE}-$(VERSION).tar.gz  $(top_builddir)
	@rm -rf /tmp/${PACKAGE}-$(VERSION)
	@echo "The archive is in ${PACKAGE}-$(VERSION).tar.bz2"

srpm: archive
	@LANG=C rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir $(top_builddir)" --define "_specdir `pwd`" -ts $(top_builddir)/$(PACKAGE)-$(VERSION).tar.$(GZ_BZIP)
	@$(MAKE) ${PACKAGE}.spec
	@echo " ${PACKAGE}-$(VERSION).tar.bz2 ${PACKAGE}.spec "

newversion:
	perl -p -i -e 'if (/RELEASE=(.*)/) { $$newrel = $$1 + 1;s/RELEASE=.*/RELEASE=$$newrel/; };' configure.in
	$(MAKE) srpm

potfile:
	chmod u+w -R  po
	sh -c '(find . -maxdepth 1 -type f -name "*.desktop.in";find ./src/netconfpkg/gui -type f -name "*.glade";find ./src -type f -name "*.py"|fgrep -v .ropeproject|fgrep -v version.py|fgrep -v pygettext.py;echo src/version.py.in) |sed -e "s#^\./##g"|sort -u > po/POTFILES.in'
	sh -c '(find . -maxdepth 1 -type l -name "*.desktop.in";find ./src -type l -name "*.py";find ./src/netconfpkg/gui -type l -name "*.glade";echo src/version.py;echo pygettext.py;echo po/pygettext.py) |sed -e "s#^\./##g"|sort -u > po/POTFILES.skip'
	make 
	make -C po update-po

push: distcheck pull
	git push ssh://git.fedoraproject.org/git/hosted/system-config-network.git HEAD:$(GITBRANCH)
	git push ssh://git.fedoraproject.org/git/hosted/system-config-network.git $(SCMTAG)
	git fetch

pull:
	git fetch
	git rebase origin/$(GITBRANCH)

diff:
	git diff origin/$(GITBRANCH)

rebase:
	git fetch
	git rebase -i origin/$(GITBRANCH)

rpmlog:
	@git log --pretty="format:- %s (%ae)" $(SCMTAG).. |sed -e 's/@.*)/)/'
	@echo

pylint:
	make -C src pylint

log:
	@git log origin/$(GITBRANCH)..
