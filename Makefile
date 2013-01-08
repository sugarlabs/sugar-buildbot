check:
	pep8 $(CURDIR)
	pylint --reports=n --disable=C,W,R,E,F --enable=W0611 \
        *.py fabfile
