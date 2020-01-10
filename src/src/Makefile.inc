check-local: pylint
	@for i in $(notdir $(wildcard *.py)); do echo $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"

.PHONY: docs pycheck pylint pylintv

docs: $(PYTHON_FILES)
	rm -fr classdoc
	PYTHONPATH=$(srcdir) @PYTHON@ /usr/lib*/python*/pydoc.py -w `find $(srcdir) -type d -o -name '*.py'` 
	mkdir -p classdoc
	mv *.html classdoc

pycheck: $(PYTHON_FILES)
	pychecker --limit 100 -F $(top_srcdir)/pycheckrc $(PYTHON_FILES)

pylint: $(PYTHON_FILES)
	@if [ -x /usr/bin/pylint ]; then \
		echo "Running pylint -- Please wait, this can last a bit"; \
		pushd $(srcdir); \
		! pylint --rcfile=/dev/null --errors-only netconfpkg $(subst .py,,$(PYTHON_FILES)) 2>/dev/null|tee /dev/tty|egrep '^E:' ;\
		popd; \
	fi

pylintv: $(PYTHON_FILES)
	pylint --rcfile=$(top_srcdir)/pylintrc netconfpkg $(subst .py,,$(PYTHON_FILES))


