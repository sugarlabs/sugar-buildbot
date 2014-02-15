sandbox:
	virtualenv-2.7 sandbox && \
	. sandbox/bin/activate && \
	pip install fabric

check:
	pep8 $(CURDIR)
	pylint --reports=n --disable=C,W,R,E,F --enable=W0611 \
        *.py fabfile
