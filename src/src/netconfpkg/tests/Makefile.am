TESTS_ENVIRONMENT = PYTHONPATH=${srcdir}/../:@PY_PYTHONPATH@
TESTS = test-Conf.py test-rcn.py test-hosts.py
EXTRA_DIST = $(TESTS) test-root coverage.py test-gui.py hosts hosts2 test-gui-manual.py

CLEANFILES := .coverage stdout stderr $(notdir $(wildcard *,cover)) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard *.pyc))

pylint: $(PYTHON_FILES)
	@if [ -x /usr/bin/pylint ]; then \
		echo "Running pylint -- Please wait, this can last a bit"; \
		pushd $(srcdir); \
		! pylint --rcfile=/dev/null --errors-only netconfpkg $(subst .py,,$(PYTHON_FILES)) 2>/dev/null|tee /dev/tty|egrep '^E:' ;\
		popd; \
	fi

check-local: pylint
	@for i in $(GLADE_FILES)  $(PYTHON_FILES); do test -f $(srcdir)/$$i || (echo $$i is missing;break);done && echo "Source file check PASSED"
	@for i in $(notdir $(wildcard *.py)); do echo $(TESTS) $(EXTRA_DIST)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
