qresource:
	pyrcc4 qresource.qrc -o qresource.py

clean :
	find ./ -name "*.pyc" -exec rm -f {} \;
	find ./ -name "*~" -exec rm -f {} \;
	find ./ -name "*.pyo" -exec rm -f {} \;
	find ./ -name "*.bak" -exec rm -f {} \;
	rm -f MANIFEST
	rm -rf dist
	rm -rf build

install:
	python setup.py install --home=~
